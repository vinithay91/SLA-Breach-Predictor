# 🚀 SLA Breach Predictor

## Project Overview

SLA Breach Predictor is a Generative AI-powered application that predicts the risk of Service Level Agreement (SLA) breaches in support tickets before they occur.

The application uses a Large Language Model (LLM) to analyze ticket information such as priority, ticket age, SLA deadlines, status, and comments. Based on this analysis, it calculates a breach risk score and provides detailed reasoning behind the prediction.

The main objective of this project is to help support teams proactively identify high-risk tickets, reduce SLA violations, improve operational efficiency, and enhance customer satisfaction through AI-powered prediction and automation.

### Live Demo

🎥 Demo Video: https://www.loom.com/share/82c26d5304b341a6b59c04d5e074dd16

---

## Features

* 🤖 AI-Powered Risk Prediction
* 📁 CSV File Upload Support
* ⚡ Real-Time Ticket Analysis
* 📊 Interactive Streamlit Dashboard
* 🎯 Risk Categorization (1–10 Scale)
* ⏱️ SLA Time Metrics Calculation
* 📝 AI-Generated Breach Reasoning
* 📈 Risk Distribution Visualization
* 📥 CSV Report Export
* 🚨 Early Detection of High-Risk Tickets

---

## How It Works

```text
User Uploads Ticket Data
            |
            ↓
     Streamlit Dashboard
            |
            ↓
      Data Processing
            |
            ↓
 Time Metrics Calculation
            |
            ↓
      AI Risk Analysis
            |
            ↓
 Breach Risk Prediction
            |
            ↓
 Report Generation
            |
            ↓
 Dashboard Visualization
```

### Workflow

User uploads a CSV file containing support ticket information.

The application processes and validates the ticket data.

The system calculates important SLA metrics such as:

* Hours Open
* SLA Remaining
* SLA Percentage Used

The AI model analyzes ticket details including priority, status, and comments.

The LLM predicts the likelihood of SLA breach and assigns a risk score from 1 to 10.

AI generates a detailed explanation for the assigned score.

Results are displayed through the Streamlit dashboard.

The final report is exported as a CSV file for future analysis.

---

## Technology Stack

### Frontend

* Streamlit
* HTML
* CSS

### Backend

* Python

### Data Processing

* Pandas
* Datetime

### AI Components

* Large Language Model (LLM)
* Prompt Engineering
* AI Risk Assessment Engine

### Reporting

* CSV Export

---

## AI Model

The application uses a Large Language Model to intelligently analyze support tickets and predict SLA breach risks.

### Models Supported

* OpenAI GPT-3.5 Turbo
* Anthropic Claude

### AI Model Responsibilities

* Understand ticket context
* Analyze urgency and complexity
* Evaluate SLA pressure
* Predict breach probability
* Generate risk scores
* Provide detailed reasoning

---

## Project Architecture

```text
                    User
                      |
                      ↓
             Streamlit Dashboard
                      |
                      ↓
              Data Processing
                      |
                      ↓
        Time Metrics Calculation
                      |
                      ↓
              AI Risk Engine
                      |
                      ↓
          Large Language Model
                      |
                      ↓
      Breach Risk Score & Reason
                      |
                      ↓
          CSV Report Generation
                      |
                      ↓
         Dashboard Visualization
```

---

## Folder Structure

```text
SLA-Breach-Predictor/

│
├── tickets.csv
│
├── sla_scorer.py
│
├── streamlit_dashboard.py
│
├── requirements.txt
│
├── .env.example
│
├── README.md
│
└── breach_risk_report.csv
```

---

## Installation and Setup

### 1. Clone Repository

```bash
git clone <repository-url>
```

### 2. Navigate to Project Directory

```bash
cd SLA-Breach-Predictor
```

### 3. Create Virtual Environment

```bash
python -m venv venv
```

### 4. Activate Virtual Environment

Windows:

```bash
venv\Scripts\activate
```

### 5. Install Dependencies

```bash
pip install -r requirements.txt
```

### 6. Configure Environment Variables

```env
OPENAI_API_KEY=your-api-key

# OR

ANTHROPIC_API_KEY=your-api-key

LLM_PROVIDER=openai
```

### 7. Run Application

```bash
streamlit run streamlit_dashboard.py
```

---

## Input Data

The application accepts support ticket information in CSV format.

### Required Columns

| Column     | Description              | Example                 |
| ---------- | ------------------------ | ----------------------- |
| ticket_id  | Unique ticket identifier | TKT-001                 |
| subject    | Ticket title             | Login issue             |
| priority   | Ticket priority          | High                    |
| created_at | Creation timestamp       | 2026-06-10 09:00        |
| sla_hours  | SLA deadline hours       | 8                       |
| status     | Current status           | Open                    |
| comments   | Additional details       | Multiple users affected |

---

## Sample CSV

```csv
ticket_id,subject,priority,created_at,sla_hours,status,comments
TKT-001,Login fails for enterprise users,High,2026-06-10 09:00,8,Open,"Multiple users reporting authentication issues"
TKT-002,Database connection timeout,Medium,2026-06-12 14:30,24,Open,"Intermittent connection drops during peak hours"
TKT-003,Payment gateway failure,Critical,2026-06-13 08:00,4,Open,"Customers unable to complete transactions"
```

---

## Risk Scoring

The AI assigns risk scores on a scale of 1 to 10.

### Risk Categories

| Score | Risk Level    |
| ----- | ------------- |
| 1-3   | Low Risk      |
| 4-6   | Medium Risk   |
| 7-8   | High Risk     |
| 9-10  | Critical Risk |

### Factors Considered

* Ticket Priority
* Hours Open
* Remaining SLA Time
* SLA Utilization Percentage
* Ticket Status
* Issue Complexity
* Customer Impact
* Ticket Comments

---

## Output

### Dashboard Output

The dashboard displays:

* Total Tickets
* High-Risk Ticket Count
* Risk Distribution Charts
* SLA Utilization Metrics
* Ticket-Wise Analysis
* AI Generated Explanations

### CSV Report

The generated report contains:

* Original Ticket Information
* Hours Open
* SLA Remaining
* SLA Percentage Used
* Breach Risk Score
* Breach Reason

---

## AI Model Benefits

Traditional SLA monitoring relies on static rules and thresholds.

### Traditional Approach

```text
Ticket Data
      ↓
Rule-Based Analysis
      ↓
Static Alerts
```

### AI-Powered Approach

```text
Ticket Data
      ↓
LLM Analysis
      ↓
Risk Prediction
      ↓
Actionable Insights
```

### Benefits

* Intelligent ticket evaluation
* Context-aware risk assessment
* Early breach detection
* Better prioritization
* Reduced manual effort
* Improved SLA compliance

---

## Assumptions

* Ticket information is accurate.
* SLA values are properly configured.
* CSV data follows the required format.
* AI API keys are valid and active.

---

## Limitations

* Prediction quality depends on ticket data quality.
* AI-generated predictions may require human validation.
* Complex business scenarios may need additional rules.
* API rate limits may affect large-scale processing.

---

## Future Enhancements

* Automated Email Alerts
* Historical Trend Analysis
* Real-Time Monitoring
* Advanced Predictive Analytics
* Cloud Deployment
* Enhanced AI Reasoning
* Multi-Language Ticket Analysis
* Integration with Additional Support Platforms

---

## Conclusion

SLA Breach Predictor demonstrates the practical use of Generative AI in IT Service Management and customer support operations.

By combining SLA analytics, ticket data processing, and Large Language Models, the system provides intelligent breach-risk predictions that help organizations proactively manage support tickets, reduce SLA violations, and improve service quality.



