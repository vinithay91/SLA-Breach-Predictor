"""
LLM Helper functions for SLA Breach Predictor
"""

import os
from openai import OpenAI


class LLMHelper:
    """Helper class for LLM interactions"""
    
    def __init__(self):
        """Initialize LLM client with API key from environment"""
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    
    def analyze_ticket_risk(self, ticket_data):
        """
        Analyze ticket data for SLA breach risk using LLM
        
        Args:
            ticket_data: Dictionary containing ticket information
            
        Returns:
            Dictionary with risk analysis results
        """
        prompt = f"""
        Analyze the following ticket for SLA breach risk:
        Ticket ID: {ticket_data.get('ticket_id')}
        Priority: {ticket_data.get('priority')}
        Created: {ticket_data.get('created_at')}
        SLA Deadline: {ticket_data.get('sla_deadline')}
        Status: {ticket_data.get('status')}
        
        Provide a risk score (0-1) and brief explanation.
        """
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are an expert at SLA risk analysis."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=200
            )
            return {"analysis": response.choices[0].message.content}
        except Exception as e:
            return {"error": str(e)}
    
    def generate_report(self, analysis_results):
        """
        Generate a comprehensive report from analysis results
        
        Args:
            analysis_results: List of analysis results
            
        Returns:
            Generated report text
        """
        prompt = f"""
        Generate a comprehensive SLA breach risk report based on these analyses:
        {analysis_results}
        
        Include summary, key findings, and recommendations.
        """
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are an expert report writer."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=500
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"Error generating report: {str(e)}"
