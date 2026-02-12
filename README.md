🚀 Teampulse AI
AI-Powered Meeting Intelligence Platform

Teampulse AI is a Django-based intelligent meeting analytics system that transforms raw meeting data into actionable insights using NLP, sentiment analysis, and automated reporting.

It is designed to help teams measure health, detect risks early, and make data-driven decisions.

🎯 Problem It Solves

Modern teams generate large amounts of meeting data but lack structured insights.

Teampulse AI solves this by:

Converting meeting transcripts into structured analytics

Measuring team sentiment and engagement

Detecting potential risks and negative trends

Automatically generating executive-ready reports

🧠 Core Features
📊 Sentiment & Emotional Analysis

Uses VADER NLP for real-time sentiment scoring

Identifies positive, neutral, and negative patterns

⚠ Risk Detection Engine

Flags high-risk communication signals

Detects negative trends in team dynamics

📈 Trend Analytics

Tracks performance patterns across meetings

Compares meeting-to-meeting engagement metrics

📄 Automated Report Generation

PDF reports using ReportLab

Excel exports using OpenPyXL

Structured executive dashboards

📧 Email Automation

Secure SMTP integration

Sends automated meeting summaries

Uses environment variable-based credential protection

🏗 Technical Architecture

Backend Framework:

Django (MVC Architecture)

AI & NLP:

VADER Sentiment Analysis

Document Processing:

python-docx

ReportLab

OpenPyXL

Security:

Environment variable configuration via python-dotenv

No hardcoded credentials

Secure App Password configuration

📂 Project Structure
Teampulse_AI/
│
├── manage.py
├── meetings/
│   ├── analyzers.py
│   ├── risk_detector.py
│   ├── report_generator.py
│   ├── trend_analyzer.py
│   ├── templates/
│   └── migrations/
│
├── teampulse/
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
│
└── .gitignore
⚙️ Installation & Setup
1 Create Virtual Environment
python -m venv venv
venv\Scripts\activate
2 Install Dependencies
pip install -r requirements.txt
3 Configure Environment Variables
Create a .env file in project root:
4 Run Migrations
python manage.py migrate
5 Run Server
python manage.py runserver

🔐 Security Best Practices Implemented

Environment-based secret management

SMTP authentication using Google App Password

No sensitive data pushed to GitHub

Clean .gitignore configuration

Production-ready email configuration

🚀 Potential Production Enhancements

User authentication & role-based dashboards

OpenAI integration for AI-generated summaries

Real-time WebSocket meeting tracking

Deployment to AWS / Render / Railway

PostgreSQL integration

Data visualization dashboards (Chart.js / D3.js)

💼 Why This Project Matters

Teampulse AI demonstrates:

Full-stack Django development

NLP integration

Secure configuration management

Report automation

Clean Git workflow

Production-level thinking

👩‍💻 Author

Princy Angeline J
Django Developer | AI-Focused Backend Engineer
Passionate about building intelligent, scalable systems.
