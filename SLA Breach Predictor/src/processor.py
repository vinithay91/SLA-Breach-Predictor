#!/usr/bin/env python3
"""
SLA Breach Predictor - CLI Tool
Scores support tickets for SLA breach risk using LLM analysis.
Supports both CSV and Jira as data sources.
"""

import os
import sys
import pandas as pd
from datetime import datetime
from dotenv import load_dotenv
import re
import argparse

# Load environment variables
load_dotenv()

class SLAScorer:
    def __init__(self, csv_path='tickets.csv', data_source='csv', jira_project=None, jql_query=None, update_jira=False):
        self.csv_path = csv_path
        self.data_source = data_source
        self.jira_project = jira_project
        self.jql_query = jql_query
        self.update_jira = update_jira
        self.df = None
        self.llm_provider = os.getenv('LLM_PROVIDER', 'openai').lower()
        self.jira_client = None
        
        # Initialize LLM client based on provider
        if self.llm_provider == 'openai':
            from openai import OpenAI
            api_key = os.getenv('OPENAI_API_KEY')
            if not api_key:
                raise ValueError("OPENAI_API_KEY not found in environment variables")
            self.client = OpenAI(api_key=api_key)
        elif self.llm_provider == 'anthropic':
            import anthropic
            api_key = os.getenv('ANTHROPIC_API_KEY')
            if not api_key:
                raise ValueError("ANTHROPIC_API_KEY not found in environment variables")
            self.client = anthropic.Anthropic(api_key=api_key)
        else:
            raise ValueError(f"Unsupported LLM provider: {self.llm_provider}")
        
        # Initialize Jira client if using Jira data source
        if self.data_source == 'jira':
            from jira_client import JiraClient
            self.jira_client = JiraClient()
    
    def load_data(self):
        """Load tickets from CSV file or Jira."""
        if self.data_source == 'jira':
            print(f"Loading tickets from Jira...")
            self.df = self.jira_client.fetch_tickets(
                jql_query=self.jql_query,
                project_key=self.jira_project,
                max_results=100
            )
            print(f"Loaded {len(self.df)} tickets from Jira")
        else:
            self.df = pd.read_csv(self.csv_path)
            print(f"Loaded {len(self.df)} tickets from {self.csv_path}")
        return self.df
    
    def calculate_time_metrics(self):
        """Calculate hours_open and sla_remaining for each ticket."""
        now = datetime.now()
        
        # Convert created_at to datetime
        self.df['created_at'] = pd.to_datetime(self.df['created_at'])
        
        # Calculate hours open
        self.df['hours_open'] = (now - self.df['created_at']).dt.total_seconds() / 3600
        
        # Calculate SLA remaining
        self.df['sla_remaining'] = self.df['sla_hours'] - self.df['hours_open']
        
        # Calculate percentage of SLA used
        self.df['sla_percentage_used'] = (self.df['hours_open'] / self.df['sla_hours']) * 100
        
        return self.df
    
    def build_prompt(self, ticket):
        """Build prompt for LLM scoring."""
        prompt = f"""You are an expert support operations analyst. Rate the SLA breach risk for this ticket on a scale of 1-10.

Ticket Details:
- Subject: {ticket['subject']}
- Priority: {ticket['priority']}
- Status: {ticket['status']}
- Hours Open: {ticket['hours_open']:.1f} hours
- SLA Remaining: {ticket['sla_remaining']:.1f} hours
- Comments: {ticket['comments']}

Scoring Guidelines:
- Score 1-3: Low risk - Plenty of SLA time remaining, low priority
- Score 4-6: Medium risk - Moderate SLA pressure or medium priority
- Score 7-8: High risk - Limited SLA time remaining or high priority
- Score 9-10: Critical risk - SLA about to breach or already breached, critical priority

Provide your response in this exact format:
Score: X/10
Reason: [brief explanation of the risk assessment]"""
        
        return prompt
    
    def call_llm(self, prompt):
        """Call LLM API to get breach risk score."""
        try:
            if self.llm_provider == 'openai':
                response = self.client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": "You are a support operations expert specializing in SLA risk assessment."},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.3,
                    max_tokens=200
                )
                return response.choices[0].message.content
            
            elif self.llm_provider == 'anthropic':
                response = self.client.messages.create(
                    model="claude-3-haiku-20240307",
                    max_tokens=200,
                    messages=[
                        {"role": "user", "content": prompt}
                    ]
                )
                return response.content[0].text
        except Exception as e:
            print(f"Error calling LLM: {e}")
            return "Score: 5/10\nReason: LLM API error - using default score"
    
    def parse_llm_response(self, response):
        """Parse LLM response to extract score and reason."""
        try:
            # Extract score
            score_match = re.search(r'Score:\s*(\d+)/10', response, re.IGNORECASE)
            if score_match:
                score = int(score_match.group(1))
            else:
                # Try to find any number 1-10
                score_match = re.search(r'\b([1-9]|10)\b', response)
                score = int(score_match.group(1)) if score_match else 5
            
            # Extract reason
            reason_match = re.search(r'Reason:\s*(.+)', response, re.IGNORECASE)
            if reason_match:
                reason = reason_match.group(1).strip()
            else:
                reason = "Could not parse reason from LLM response"
            
            return score, reason
        except Exception as e:
            print(f"Error parsing LLM response: {e}")
            return 5, "Parse error - using default score"
    
    def score_tickets(self):
        """Score each ticket using LLM."""
        scores = []
        reasons = []
        
        print("\nScoring tickets with LLM...")
        for idx, row in self.df.iterrows():
            print(f"  Processing {row['ticket_id']}... ", end='', flush=True)
            
            prompt = self.build_prompt(row)
            response = self.call_llm(prompt)
            score, reason = self.parse_llm_response(response)
            
            scores.append(score)
            reasons.append(reason)
            print(f"Score: {score}/10")
        
        self.df['breach_risk_score'] = scores
        self.df['breach_reason'] = reasons
        
        return self.df
    
    def generate_report(self, output_file='breach_risk_report.csv'):
        """Generate and save the breach risk report."""
        # Sort by score descending
        self.df = self.df.sort_values('breach_risk_score', ascending=False)
        
        # Save to CSV
        self.df.to_csv(output_file, index=False)
        print(f"\nReport saved to {output_file}")
        
        return self.df
    
    def update_jira_tickets(self):
        """Update Jira tickets with breach risk scores."""
        if not self.update_jira or self.data_source != 'jira':
            return
        
        print("\nUpdating Jira tickets with risk scores...")
        for idx, row in self.df.iterrows():
            if 'jira_key' in row:
                self.jira_client.update_ticket_with_risk_score(
                    row['jira_key'],
                    row['breach_risk_score'],
                    row['breach_reason']
                )
        print("Jira tickets updated successfully")
    
    def print_results(self):
        """Print formatted results to terminal."""
        print("\n" + "="*100)
        print("SLA BREACH RISK REPORT".center(100))
        print("="*100)
        
        for idx, row in self.df.iterrows():
            score = row['breach_risk_score']
            sla_remaining = row['sla_remaining']
            
            # Color coding for high risk
            if score >= 8:
                risk_level = "\033[91mCRITICAL\033[0m"
            elif score >= 6:
                risk_level = "\033[93mHIGH\033[0m"
            elif score >= 4:
                risk_level = "\033[96mMEDIUM\033[0m"
            else:
                risk_level = "\033[92mLOW\033[0m"
            
            print(f"\n{row['ticket_id']} | {risk_level} | Score: {score}/10")
            print(f"  Subject: {row['subject']}")
            print(f"  Priority: {row['priority']} | SLA Remaining: {sla_remaining:.1f}h")
            print(f"  Reason: {row['breach_reason']}")
            print("-" * 100)
        
        # Summary statistics
        print(f"\nSUMMARY:")
        print(f"  Total Tickets: {len(self.df)}")
        print(f"  Critical Risk (8-10): {len(self.df[self.df['breach_risk_score'] >= 8])}")
        print(f"  High Risk (6-7): {len(self.df[(self.df['breach_risk_score'] >= 6) & (self.df['breach_risk_score'] < 8)])}")
        print(f"  Medium Risk (4-5): {len(self.df[(self.df['breach_risk_score'] >= 4) & (self.df['breach_risk_score'] < 6)])}")
        print(f"  Low Risk (1-3): {len(self.df[self.df['breach_risk_score'] < 4])}")
        print("="*100 + "\n")
    
    def run(self):
        """Run the complete SLA scoring pipeline."""
        print(f"SLA Breach Predictor using {self.llm_provider.upper()}")
        print(f"Data Source: {self.data_source.upper()}")
        print("-" * 50)
        
        self.load_data()
        self.calculate_time_metrics()
        self.score_tickets()
        self.generate_report()
        self.update_jira_tickets()
        self.print_results()
        
        return self.df


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description='SLA Breach Predictor - Score tickets for breach risk')
    parser.add_argument('csv_path', nargs='?', default='tickets.csv', help='Path to CSV file (default: tickets.csv)')
    parser.add_argument('--source', choices=['csv', 'jira'], default='csv', help='Data source: csv or jira (default: csv)')
    parser.add_argument('--jira-project', help='Jira project key (e.g., PROJ)')
    parser.add_argument('--jql', help='Custom JQL query for Jira')
    parser.add_argument('--update-jira', action='store_true', help='Update Jira tickets with risk scores')
    
    args = parser.parse_args()
    
    try:
        scorer = SLAScorer(
            csv_path=args.csv_path,
            data_source=args.source,
            jira_project=args.jira_project,
            jql_query=args.jql,
            update_jira=args.update_jira
        )
        scorer.run()
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
