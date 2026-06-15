#!/usr/bin/env python3
"""
SLA Breach Predictor - Streamlit Dashboard
Interactive dashboard for visualizing SLA breach risk scores.
"""

import os
import pandas as pd
from datetime import datetime
import streamlit as st
from dotenv import load_dotenv
import re

# Load environment variables
load_dotenv()

# Page configuration
st.set_page_config(
    page_title="SLA Breach Predictor",
    page_icon="⚠️",
    layout="wide"
)

# Custom CSS - Colorful Modern Design
st.markdown("""
<style>
    /* Main container styling */
    .main {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    }
    
    /* Metric cards with gradient backgrounds */
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 25px;
        border-radius: 15px;
        margin: 15px 0;
        box-shadow: 0 10px 30px rgba(102, 126, 234, 0.3);
        color: white;
        transition: transform 0.3s ease;
    }
    
    .metric-card:hover {
        transform: translateY(-5px);
    }
    
    /* Risk level cards */
    .high-risk {
        background: linear-gradient(135deg, #ff6b6b 0%, #ee5a5a 100%);
        border-left: 6px solid #ff4757;
        border-radius: 12px;
        padding: 20px;
        margin: 10px 0;
        box-shadow: 0 8px 20px rgba(255, 107, 107, 0.3);
    }
    
    .medium-risk {
        background: linear-gradient(135deg, #feca57 0%, #ff9f43 100%);
        border-left: 6px solid #ff9f43;
        border-radius: 12px;
        padding: 20px;
        margin: 10px 0;
        box-shadow: 0 8px 20px rgba(254, 202, 87, 0.3);
    }
    
    .low-risk {
        background: linear-gradient(135deg, #2ecc71 0%, #27ae60 100%);
        border-left: 6px solid #2ecc71;
        border-radius: 12px;
        padding: 20px;
        margin: 10px 0;
        box-shadow: 0 8px 20px rgba(46, 204, 113, 0.3);
    }
    
    /* Style table headers with gradient */
    .stDataFrame [data-testid="stDataFrame"] thead th {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        font-weight: bold;
        text-align: left;
        padding: 15px;
        border-radius: 8px 8px 0 0;
    }
    
    .stDataFrame [data-testid="stDataFrame"] thead th:first-child {
        border-top-left-radius: 8px;
    }
    
    .stDataFrame [data-testid="stDataFrame"] thead th:last-child {
        border-top-right-radius: 8px;
    }
    
    /* Button styling */
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 10px;
        padding: 12px 24px;
        font-weight: bold;
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        transform: scale(1.05);
        box-shadow: 0 8px 20px rgba(102, 126, 234, 0.4);
    }
    
    /* Input styling */
    .stTextInput > div > div > input,
    .stSelectbox > div > div > select {
        border-radius: 8px;
        border: 2px solid #667eea;
    }
    
    /* Header styling */
    h1 {
        color: #667eea;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
    }
    
    /* Sidebar styling */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #667eea 0%, #764ba2 100%);
    }
    
    [data-testid="stSidebar"] > div:first-child {
        background: rgba(255, 255, 255, 0.1);
    }
</style>
""", unsafe_allow_html=True)


class SLADashboard:
    def __init__(self):
        self.llm_provider = os.getenv('LLM_PROVIDER', 'openai').lower()
        self.client = None
        self.jira_client = None
        
        # Initialize LLM client based on provider (optional)
        if self.llm_provider == 'openai':
            from openai import OpenAI
            api_key = os.getenv('OPENAI_API_KEY')
            if api_key and api_key != 'your-openai-api-key-here':
                self.client = OpenAI(api_key=api_key)
        elif self.llm_provider == 'anthropic':
            import anthropic
            api_key = os.getenv('ANTHROPIC_API_KEY')
            if api_key and api_key != 'your-anthropic-api-key-here':
                self.client = anthropic.Anthropic(api_key=api_key)
    
    def load_data(self, csv_path='tickets.csv'):
        """Load tickets from CSV file."""
        try:
            df = pd.read_csv(csv_path)
            return df
        except FileNotFoundError:
            st.error(f"File {csv_path} not found. Please ensure tickets.csv exists in the current directory.")
            return None
    
    def load_data_from_jira(self, project_key=None, jql_query=None, max_results=100):
        """Load tickets from Jira."""
        try:
            from jira_client import JiraClient
            self.jira_client = JiraClient()
            df = self.jira_client.fetch_tickets(
                jql_query=jql_query,
                project_key=project_key,
                max_results=max_results
            )
            return df
        except Exception as e:
            st.error(f"Error loading data from Jira: {e}")
            return None
    
    def calculate_time_metrics(self, df):
        """Calculate hours_open and sla_remaining for each ticket."""
        now = datetime.now()
        
        # Convert created_at to datetime
        df['created_at'] = pd.to_datetime(df['created_at'])
        
        # Calculate hours open
        df['hours_open'] = (now - df['created_at']).dt.total_seconds() / 3600
        
        # Calculate SLA remaining
        df['sla_remaining'] = df['sla_hours'] - df['hours_open']
        
        # Calculate percentage of SLA used
        df['sla_percentage_used'] = (df['hours_open'] / df['sla_hours']) * 100
        
        # Format time in hours and minutes
        df['hours_open_formatted'] = df['hours_open'].apply(self.format_time_hm)
        df['sla_remaining_formatted'] = df['sla_remaining'].apply(self.format_time_hm)
        
        return df
    
    def format_time_hm(self, hours):
        """Format decimal hours to hours and minutes."""
        if hours < 0:
            hours_abs = abs(hours)
            h = int(hours_abs)
            m = int((hours_abs - h) * 60)
            return f"-{h}h {m}m"
        else:
            h = int(hours)
            m = int((hours - h) * 60)
            return f"{h}h {m}m"
    
    def build_prompt(self, ticket):
        """Build prompt for LLM scoring."""
        prompt = f"""You are an expert support operations analyst. Rate the SLA breach risk for this ticket on a scale of 1-10.

Ticket Details:
- Subject: {ticket['subject']}
- Priority: {ticket['priority']}
- Status: {ticket['status']}
- Hours Open: {ticket['hours_open']:.1f} hours
- SLA Remaining: {ticket['sla_remaining']:.1f} hours
- Comments: {ticket.get('comments', 'No comments')}

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
            st.error(f"Error calling LLM: {e}")
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
            st.error(f"Error parsing LLM response: {e}")
            return 5, "Parse error - using default score"
    
    def score_tickets_rule_based(self, df):
        """Score each ticket using rule-based logic (no API required)."""
        scores = []
        reasons = []
        
        for idx, row in df.iterrows():
            sla_remaining = row['sla_remaining']
            priority = row['priority'].lower()
            
            # Base score based on SLA remaining
            if sla_remaining <= 0:
                base_score = 9  # Already breached
            elif sla_remaining <= 2:
                base_score = 8  # Critical - less than 2 hours
            elif sla_remaining <= 6:
                base_score = 7  # High - less than 6 hours
            elif sla_remaining <= 12:
                base_score = 6  # Medium-high
            elif sla_remaining <= 24:
                base_score = 5  # Medium
            elif sla_remaining <= 48:
                base_score = 4  # Low-medium
            else:
                base_score = 3  # Low
            
            # Adjust based on priority
            if priority == 'critical':
                score = min(10, base_score + 2)
            elif priority == 'high':
                score = min(10, base_score + 1)
            elif priority == 'medium':
                score = base_score
            elif priority == 'low':
                score = max(1, base_score - 1)
            else:
                score = base_score
            
            # Generate reason
            if sla_remaining <= 0:
                reason = f"SLA already breached by {abs(sla_remaining):.1f} hours"
            elif sla_remaining <= 2:
                reason = f"Critical: Only {sla_remaining:.1f} hours remaining, {priority} priority"
            elif sla_remaining <= 6:
                reason = f"High risk: {sla_remaining:.1f} hours remaining, {priority} priority"
            elif sla_remaining <= 24:
                reason = f"Moderate risk: {sla_remaining:.1f} hours remaining, {priority} priority"
            else:
                reason = f"Low risk: {sla_remaining:.1f} hours remaining, {priority} priority"
            
            scores.append(score)
            reasons.append(reason)
        
        df['breach_risk_score'] = scores
        df['breach_reason'] = reasons
        
        return df
    
    def score_tickets(self, df):
        """Score each ticket using LLM or rule-based fallback."""
        if self.client is None:
            return self.score_tickets_rule_based(df)
        
        scores = []
        reasons = []
        
        progress_bar = st.progress(0)
        total_tickets = len(df)
        
        for idx, row in df.iterrows():
            progress = (idx + 1) / total_tickets
            progress_bar.progress(progress)
            
            prompt = self.build_prompt(row)
            response = self.call_llm(prompt)
            score, reason = self.parse_llm_response(response)
            
            scores.append(score)
            reasons.append(reason)
        
        df['breach_risk_score'] = scores
        df['breach_reason'] = reasons
        
        return df
    
    def display_metrics(self, df):
        """Display summary metrics with colorful cards."""
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.markdown("""
            <div class="metric-card">
                <h3 style="margin: 0; font-size: 2rem;">🎫</h3>
                <p style="margin: 5px 0; font-size: 1.5rem; font-weight: bold;">{}</p>
                <p style="margin: 0; opacity: 0.9;">Total Tickets</p>
            </div>
            """.format(len(df)), unsafe_allow_html=True)
        
        with col2:
            critical = len(df[df['breach_risk_score'] >= 8])
            st.markdown("""
            <div class="high-risk">
                <h3 style="margin: 0; font-size: 2rem;">🚨</h3>
                <p style="margin: 5px 0; font-size: 1.5rem; font-weight: bold;">{}</p>
                <p style="margin: 0; opacity: 0.9;">Critical Risk (8-10)</p>
            </div>
            """.format(critical), unsafe_allow_html=True)
        
        with col3:
            high = len(df[(df['breach_risk_score'] >= 6) & (df['breach_risk_score'] < 8)])
            st.markdown("""
            <div class="medium-risk">
                <h3 style="margin: 0; font-size: 2rem;">⚠️</h3>
                <p style="margin: 5px 0; font-size: 1.5rem; font-weight: bold;">{}</p>
                <p style="margin: 0; opacity: 0.9;">High Risk (6-7)</p>
            </div>
            """.format(high), unsafe_allow_html=True)
        
        with col4:
            avg_score = df['breach_risk_score'].mean()
            risk_color = "#ff6b6b" if avg_score >= 7 else "#feca57" if avg_score >= 4 else "#2ecc71"
            st.markdown("""
            <div style="background: linear-gradient(135deg, {} 0%, {} 100%); padding: 25px; border-radius: 15px; margin: 15px 0; box-shadow: 0 10px 30px rgba(0,0,0,0.2); color: white;">
                <h3 style="margin: 0; font-size: 2rem;">📊</h3>
                <p style="margin: 5px 0; font-size: 1.5rem; font-weight: bold;">{:.1f}/10</p>
                <p style="margin: 0; opacity: 0.9;">Avg Risk Score</p>
            </div>
            """.format(risk_color, risk_color, avg_score), unsafe_allow_html=True)
    
    def display_ticket_table(self, df):
        """Display tickets in a formatted table."""
        st.subheader("📋 Ticket Risk Analysis")
        
        # Sort by score descending
        df_sorted = df.sort_values('breach_risk_score', ascending=False)
        
        # Create display dataframe with formatted columns
        display_df = df_sorted[[
            'ticket_id', 
            'subject', 
            'priority', 
            'status',
            'hours_open_formatted',
            'sla_remaining_formatted',
            'breach_risk_score',
            'comments'
        ]].copy()
        
        # Rename columns for display
        display_df.columns = [
            'Ticket ID',
            'Subject',
            'Priority',
            'Status',
            'Hours Open',
            'SLA Remaining',
            'Risk Score',
            'Comments'
        ]
        
        # Add risk level column
        def get_risk_level(score):
            if score >= 8:
                return "🔴 CRITICAL"
            elif score >= 6:
                return "� HIGH"
            elif score >= 4:
                return "🟡 MEDIUM"
            else:
                return "🟢 LOW"
        
        display_df['Risk Level'] = display_df['Risk Score'].apply(get_risk_level)
        
        # Reorder columns
        display_df = display_df[
            ['Ticket ID', 'Subject', 'Priority', 'Status', 'Hours Open', 
             'SLA Remaining', 'Risk Score', 'Risk Level', 'Comments']
        ]
        
        # Display as interactive table
        st.dataframe(
            display_df,
            use_container_width=True,
            hide_index=True,
            column_config={
                'Risk Score': st.column_config.ProgressColumn(
                    'Risk Score',
                    help='Breach risk score from 1-10',
                    format='%d/10',
                    min_value=0,
                    max_value=10
                ),
                'Risk Level': st.column_config.TextColumn('Risk Level'),
                'Comments': st.column_config.TextColumn('Comments', width='large')
            }
        )
    
    def display_charts(self, df):
        """Display visualizations with colorful styling."""
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### 📊 Risk Score Distribution")
            risk_counts = pd.cut(
                df['breach_risk_score'],
                bins=[0, 3, 6, 8, 10],
                labels=['Low (1-3)', 'Medium (4-6)', 'High (7-8)', 'Critical (9-10)']
            ).value_counts()
            
            # Create colorful bar chart
            chart_data = pd.DataFrame({
                'Risk Level': risk_counts.index,
                'Count': risk_counts.values
            })
            
            st.bar_chart(chart_data.set_index('Risk Level'), color='#667eea')
        
        with col2:
            st.markdown("### ⏱️ SLA Time Analysis")
            sla_data = df[['ticket_id', 'sla_remaining', 'hours_open']].head(10)
            sla_data = sla_data.set_index('ticket_id')
            
            # Create colorful time analysis
            st.bar_chart(sla_data[['sla_remaining', 'hours_open']], color=['#2ecc71', '#ff6b6b'])
    
    def run(self):
        """Run the Streamlit dashboard."""
        st.title("🚀 SLA Breach Predictor Dashboard")
        st.markdown("### AI-Powered SLA Risk Analysis")
        st.markdown("---")
        
        # Data source selection in sidebar
        with st.sidebar:
            st.header("📊 Data Source")
            data_source = st.radio(
                "Select Data Source",
                ["📁 CSV File", "🔗 Jira"],
                help="Choose between uploading a CSV file or fetching directly from Jira"
            )
            
            st.markdown("---")
            
            if data_source == "🔗 Jira":
                st.header("🔧 Jira Configuration")
                st.markdown("Configure your Jira connection")
                
                jira_project = st.text_input(
                    "📋 Project Key",
                    placeholder="e.g., PROJ",
                    help="Your Jira project key"
                )
                
                jql_query = st.text_input(
                    "🔍 Custom JQL Query",
                    placeholder="Optional: Leave empty for default",
                    help="Custom JQL query for filtering tickets"
                )
                
                max_results = st.slider(
                    "🎫 Max Tickets to Fetch",
                    min_value=10,
                    max_value=500,
                    value=100,
                    step=10
                )
                
                update_jira = st.checkbox(
                    "📝 Update Jira Tickets with Risk Scores",
                    value=False,
                    help="Add risk scores as comments to Jira tickets"
                )
            
            st.markdown("---")
            st.markdown("### ℹ️ Info")
            st.markdown("This dashboard uses AI to analyze tickets and predict SLA breach risks.")
        
        df = None
        
        # Main content area
        col1, col2, col3 = st.columns([1, 2, 1])
        
        with col2:
            if data_source == "📁 CSV File":
                st.markdown("### 📁 Upload CSV File")
                st.markdown("Upload your tickets CSV file to analyze SLA breach risk.")
                
                uploaded_file = st.file_uploader(
                    "Upload tickets.csv",
                    type=['csv'],
                    help="CSV file with columns: ticket_id, subject, priority, created_at, sla_hours, status, comments"
                )
                
                if uploaded_file is not None:
                    df = self.load_data(uploaded_file)
                    st.success(f"✅ Successfully loaded {len(df)} tickets from CSV!")
                    st.balloons()
            
            elif data_source == "🔗 Jira":
                st.markdown("### 🔗 Fetch from Jira")
                st.markdown("Enter your Jira project details above and click the button below to start analysis.")
                
                if st.button("📥 Fetch & Analyze Tickets", type="primary", use_container_width=True):
                    with st.spinner("🔄 Fetching tickets from Jira..."):
                        df = self.load_data_from_jira(
                            project_key=jira_project if jira_project else None,
                            jql_query=jql_query if jql_query else None,
                            max_results=max_results
                        )
                    
                    if df is not None:
                        st.success(f"✅ Successfully loaded {len(df)} tickets from Jira!")
                        st.session_state['update_jira'] = update_jira
                        st.session_state['data_source'] = 'jira'
                        st.balloons()
        
        if df is not None:
            # Calculate time metrics
            df = self.calculate_time_metrics(df)
            
            # Score tickets automatically
            with st.spinner("🤖 AI Analysis in progress..."):
                df = self.score_tickets(df)
            
            st.success("✅ Analysis complete!")
            st.session_state['analyzed_df'] = df
            
            # Display results if available
            if 'analyzed_df' in st.session_state:
                df = st.session_state['analyzed_df']
                
                # Update Jira if requested (only for Jira data source)
                if st.session_state.get('data_source') == 'jira' and st.session_state.get('update_jira', False):
                    if st.button("📝 Update Jira Tickets with Risk Scores", type="primary", use_container_width=True):
                        with st.spinner("🔄 Updating Jira tickets..."):
                            for idx, row in df.iterrows():
                                if 'jira_key' in row:
                                    self.jira_client.update_ticket_with_risk_score(
                                        row['jira_key'],
                                        row['breach_risk_score'],
                                        row['breach_reason']
                                    )
                        st.success("✅ Jira tickets updated successfully!")
                        st.balloons()
                
                # Display metrics with colorful cards
                st.markdown("### 📊 Risk Analysis Summary")
                self.display_metrics(df)
                
                # Display charts
                st.markdown("### 📈 Visual Analytics")
                self.display_charts(df)
                
                # Add filters
                st.markdown("### 🔍 Filter & Explore Tickets")
                col1, col2 = st.columns(2)
                
                with col1:
                    priority_filter = st.multiselect(
                        "🎯 Filter by Priority",
                        options=df['priority'].unique(),
                        default=df['priority'].unique().tolist()
                    )
                
                with col2:
                    # Common status options
                    common_statuses = ['Open', 'In Progress', 'Closed', 'Resolved', 'On Hold', 'Pending']
                    existing_statuses = [s for s in common_statuses if s in df['status'].unique()]
                    if not existing_statuses:
                        existing_statuses = df['status'].unique().tolist()
                    
                    status_filter = st.multiselect(
                        "📋 Filter by Status",
                        options=common_statuses,
                        default=existing_statuses
                    )
                
                # Apply filters
                filtered_df = df[
                    (df['priority'].isin(priority_filter)) &
                    (df['status'].isin(status_filter))
                ]
                
                # Display ticket table
                st.markdown("### 🎫 Ticket Details")
                self.display_ticket_table(filtered_df)
                
                # Download option
                st.markdown("### 📥 Export Results")
                csv = df.to_csv(index=False)
                st.download_button(
                    label="📊 Download Analysis Report",
                    data=csv,
                    file_name="breach_risk_report.csv",
                    mime="text/csv",
                    use_container_width=True
                )
        else:
            # Welcome message
            st.markdown("""
            ### 🎉 Welcome to SLA Breach Predictor!
            
            This AI-powered dashboard analyzes your Jira tickets to predict SLA breach risks.
            
            **To get started:**
            1. ⚙️ Configure your Jira settings in the sidebar
            2. � Click "Fetch & Analyze Tickets" to load your data
            3. 🤖 AI will automatically analyze each ticket
            4. 📊 View risk scores, charts, and detailed analysis
            5. 📝 Optionally update Jira tickets with risk scores
            
            **Features:**
            - 🚀 Real-time AI analysis using LLM
            - 📈 Visual risk distribution charts
            - 🔍 Smart filtering by priority and status
            - 📝 Direct Jira integration for updates
            - 📊 Export reports to CSV
            """)


def main():
    """Main entry point."""
    dashboard = SLADashboard()
    dashboard.run()


if __name__ == "__main__":
    main()
