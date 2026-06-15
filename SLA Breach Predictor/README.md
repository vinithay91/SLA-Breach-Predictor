# 🚀 SLA Breach Predictor

An AI-powered tool that analyzes support tickets for SLA breach risk, helping teams identify and address at-risk tickets before they breach. Supports both CSV file upload and direct Jira integration.

## Features

- **🤖 AI-Powered Scoring**: Uses LLM (OpenAI GPT-3.5 or Anthropic Claude) to analyze ticket complexity and breach risk
- **📁 CSV Upload**: Upload ticket data from CSV files for analysis
- **🎯 Jira Integration**: Automatically fetches tickets directly from Jira using API
- **📊 Colorful Dashboard**: Modern, gradient-based UI with beautiful visualizations
- **⚡ Real-time Analysis**: Automatic AI analysis as soon as tickets are loaded
- **📈 Risk Categorization**: Scores tickets 1-10 with detailed reasoning
- **⏱️ Time Metrics**: Calculates hours open, SLA remaining, and percentage used
- **📝 Jira Updates**: Option to update Jira tickets with risk scores as comments
- **📥 Export Reports**: Generates CSV reports with breach risk analysis

## Installation

### Prerequisites

- Python 3.10+
- OpenAI API key or Anthropic API key
- Jira API token (for Jira integration)

### Setup

1. Clone or download this repository

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Configure environment variables:
```bash
cp .env.example .env
```

4. Edit `.env` and add your API key:
```env
OPENAI_API_KEY=your-openai-api-key-here
# OR
ANTHROPIC_API_KEY=your-anthropic-api-key-here

LLM_PROVIDER=openai  # Choose 'openai' or 'anthropic'

# Jira Configuration (optional, for Jira integration)
JIRA_URL=https://your-domain.atlassian.net
JIRA_EMAIL=your-email@example.com
JIRA_API_TOKEN=your-jira-api-token-here
```

## Usage

### CLI Tool

**Analyze CSV file:**

```bash
python sla_scorer.py tickets.csv
```

**Fetch tickets from Jira and analyze:**

```bash
python sla_scorer.py --source jira --jira-project PROJ
```

**With custom JQL query:**

```bash
python sla_scorer.py --source jira --jql "priority = High AND created >= -7d"
```

**Update Jira tickets with risk scores:**

```bash
python sla_scorer.py --source jira --jira-project PROJ --update-jira
```

The tool will:
- Load tickets from CSV or fetch from Jira
- Calculate time metrics (hours open, SLA remaining)
- Call the LLM to score each ticket's breach risk (1-10)
- Generate a `breach_risk_report.csv` file
- Display a formatted report in the terminal with color-coded risk levels
- Optionally update Jira tickets with risk scores as comments

### Streamlit Dashboard

Launch the colorful interactive dashboard:

```bash
streamlit run streamlit_dashboard.py
```

The dashboard provides:
- 🎨 Modern gradient-based UI with beautiful colors
- 📁 CSV file upload option for manual data
- 🔗 Direct Jira integration to fetch tickets automatically
- 🤖 Automatic AI analysis as soon as tickets are loaded
- 📊 Colorful risk score distribution charts
- ⏱️ SLA time analysis with visual indicators
- 🎫 Color-coded ticket cards by risk level
- 📝 Option to update Jira tickets with risk scores
- 📥 Export reports to CSV

## Jira Integration

### Setting up Jira API Access

1. **Generate Jira API Token:**
   - Go to [Atlassian Account Settings](https://id.atlassian.com/manage-profile/security/api-tokens)
   - Click "Create API token"
   - Label it (e.g., "SLA Breach Predictor")
   - Copy the generated token

2. **Configure Environment Variables:**
   Add the following to your `.env` file:
   ```env
   JIRA_URL=https://your-domain.atlassian.net
   JIRA_EMAIL=your-email@example.com
   JIRA_API_TOKEN=your-generated-api-token
   ```

3. **Test Jira Connection:**
   ```bash
   python jira_client.py
   ```

### Using Jira with CLI

**Fetch tickets from a specific project:**
```bash
python sla_scorer.py --source jira --jira-project PROJ
```

**Use custom JQL query:**
```bash
python sla_scorer.py --source jira --jql "priority = High AND created >= -7d"
```

**Update Jira tickets with risk scores:**
```bash
python sla_scorer.py --source jira --jira-project PROJ --update-jira
```

### Using Streamlit Dashboard

1. Launch the dashboard: `streamlit run streamlit_dashboard.py`
2. Select data source in sidebar:
   - **CSV File**: Upload your tickets.csv file
   - **Jira**: Configure Jira connection and fetch tickets
3. For Jira:
   - Enter your Jira project key (e.g., "PROJ")
   - Optionally provide a custom JQL query
   - Set the maximum number of tickets to fetch
   - Check "Update Jira Tickets with Risk Scores" if you want to write back to Jira
4. Click the fetch/upload button to load tickets
5. AI will automatically analyze the tickets
6. View risk scores, charts, and detailed analysis
7. Optionally update Jira tickets with risk scores (Jira mode only)
8. Export results to CSV

## CSV Format

The input CSV file should have the following columns:

| Column | Description | Example |
|--------|-------------|---------|
| ticket_id | Unique ticket identifier | TKT-001 |
| subject | Ticket subject/title | Login fails for enterprise users |
| priority | Priority level | High, Medium, Low, Critical |
| created_at | Ticket creation timestamp | 2026-06-10 09:00 |
| sla_hours | SLA deadline in hours | 8 |
| status | Current ticket status | Open, In Progress, Closed |
| comments | Additional ticket details | Multiple users reporting issues |

### Sample CSV

```csv
ticket_id,subject,priority,created_at,sla_hours,status,comments
TKT-001,Login fails for enterprise users,High,2026-06-10 09:00,8,Open,"Multiple users reporting authentication issues"
TKT-002,Database connection timeout,Medium,2026-06-12 14:30,24,Open,"Intermittent connection drops during peak hours"
TKT-003,Payment gateway not responding,Critical,2026-06-13 08:00,4,Open,"Customers unable to complete transactions"
```

## Risk Scoring

The AI scores tickets on a scale of 1-10:

- **1-3 (Low Risk)**: Plenty of SLA time remaining, low priority
- **4-6 (Medium Risk)**: Moderate SLA pressure or medium priority
- **7-8 (High Risk)**: Limited SLA time remaining or high priority
- **9-10 (Critical Risk)**: SLA about to breach or already breached, critical priority

## Output

### CLI Output

The CLI displays:
- Color-coded risk levels (red for critical, yellow for high, green for low)
- Sorted list of tickets by risk score (highest first)
- Summary statistics (total tickets, risk distribution)
- Detailed reasoning for each score

### CSV Report

The `breach_risk_report.csv` includes:
- Original ticket data
- Time metrics (hours_open, sla_remaining, sla_percentage_used)
- breach_risk_score (1-10)
- breach_reason (AI-generated explanation)

## Automation

### Cron Job

Run the scorer hourly and email alerts for high-risk tickets:

```bash
# Add to crontab
0 * * * * cd /path/to/sla-predictor && python sla_scorer.py && python email_alerts.py
```

### GitHub Actions

Create a workflow file `.github/workflows/sla-check.yml`:

```yaml
name: SLA Breach Check
on:
  schedule:
    - cron: '0 * * * *'
  workflow_dispatch:

jobs:
  check:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.10'
      - name: Install dependencies
        run: pip install -r requirements.txt
      - name: Run SLA scorer
        env:
          OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
        run: python sla_scorer.py
```

## Email Alerts (Optional)

To send email alerts for tickets with score >= 7, create `email_alerts.py`:

```python
import smtplib
import pandas as pd
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os

def send_alerts():
    df = pd.read_csv('breach_risk_report.csv')
    high_risk = df[df['breach_risk_score'] >= 7]
    
    if len(high_risk) == 0:
        return
    
    # Email configuration
    SMTP_SERVER = os.getenv('SMTP_SERVER')
    SMTP_PORT = int(os.getenv('SMTP_PORT', 587))
    SMTP_USER = os.getenv('SMTP_USER')
    SMTP_PASSWORD = os.getenv('SMTP_PASSWORD')
    ALERT_EMAIL = os.getenv('ALERT_EMAIL')
    
    # Create email
    msg = MIMEMultipart()
    msg['From'] = SMTP_USER
    msg['To'] = ALERT_EMAIL
    msg['Subject'] = f'🚨 SLA Breach Alert: {len(high_risk)} high-risk tickets'
    
    body = f"High-risk tickets detected:\n\n"
    for _, row in high_risk.iterrows():
        body += f"{row['ticket_id']} - Score: {row['breach_risk_score']}/10\n"
        body += f"Reason: {row['breach_reason']}\n\n"
    
    msg.attach(MIMEText(body, 'plain'))
    
    # Send email
    with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
        server.starttls()
        server.login(SMTP_USER, SMTP_PASSWORD)
        server.send_message(msg)

if __name__ == "__main__":
    send_alerts()
```

## Project Structure

```
sla-breach-predictor/
├── tickets.csv                      # Sample ticket data
├── sla_scorer.py                   # CLI tool
├── streamlit_dashboard.py          # Streamlit dashboard
├── requirements.txt                # Python dependencies
├── .env.example                    # Environment variables template
├── README.md                       # This file
└── breach_risk_report.csv          # Generated output report
```

## Troubleshooting

### API Key Errors
- Ensure your `.env` file is in the project root
- Verify the API key is correct and active
- Check that `LLM_PROVIDER` matches your API key type

### CSV Parsing Errors
- Ensure CSV has all required columns
- Check that `created_at` is in a valid datetime format
- Verify the file is saved as UTF-8 encoded CSV

### LLM Rate Limits
- If you hit rate limits, consider:
  - Using Anthropic Claude instead of OpenAI
  - Adding delays between API calls
  - Implementing batch processing

## License

This project is provided as-is for educational and production use.

## Contributing

Feel free to submit issues and enhancement requests!
