# IPO Automation Bot 🚀

An intelligent automation system designed to monitor daily IPO listings via the Finnhub API. It filters for high-value opportunities (Offer Amount > Threshold), performs automated due diligence using AI (Gemini + Tavily), and dispatches rich HTML email alerts.
[▶ Watch Demo Video](https://drive.google.com/your-link)
## 🎥 Demo

[▶ Watch Demo Video](https://drive.google.com/your-link](https://drive.google.com/file/d/15_uZDHHlOfrxBUed8jGN4qfp3HfTUpUb/view?usp=sharing)

## 🏗 Architecture
This project uses a modular **ETL (Extract-Transform-Load)** design pattern, optimized for maintainability and Azure Functions deployment.

* `main.py`: Orchestrator (Entry Point).
* `config.py`: Centralized configuration (Env vars & CLI Args).
* `data_fetcher.py`: Finnhub API integration and valuation logic.
* `enrichment.py`: **Dual-Search Strategy** (Tavily) & **AI Analysis** (Gemini).
* `email_service.py`: HTML report generation and SMTP dispatch.

---

## ⚙️ Setup & Installation

### 1. Python Environment
Ensure Python 3.9+ is installed. It is recommended to use a Virtual Environment.

**Windows:**
```powershell
python -m venv venv
.\venv\Scripts\Activate
pip install -r requirements.txt
```

**Mac/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2. Credentials Setup
1.  Copy `.env.example` to a new file named `.env`.
2.  Fill in your API Keys (`FINNHUB`, `TAVILY`, `GEMINI`) and Email credentials.
3.  Configure your recipients in `RECEIVER_EMAILS`.

---

## 🏃 Usage & Configuration

The bot's behavior is primarily controlled via the `.env` file to ensure seamless deployment in serverless environments.

### 1. Verification Run (Historical Data)
To verify the logic against known data (e.g., Feb 2 to Feb 6), **uncomment** the date variables in your `.env` file:

```ini
# .env
START_DATE=2026-02-02
END_DATE=2026-02-06
```

Then run the script:
```bash
python main.py
```

### 2. Production Run (Today)
To run against live data, **comment out** or remove the date variables in `.env`. The bot will automatically default to the current date ("Today").

```ini
# .env
# START_DATE=...
# END_DATE=...
```

Then run:
```bash
python main.py
```

### 3. Manual Override
You can override the `.env` settings to force a specific run date using the CLI argument. This is useful for ad-hoc backtesting.

```bash
python main.py --date 2026-02-06
```

---

## 🧠 AI Enrichment Modes
Control the depth of research via the `ENRICHMENT_MODE` variable in `.env`:

| Mode | Description | Cost / Speed |
| :--- | :--- | :--- |
| **NONE** | Basic filtering only. No external search. | Fastest / Free |
| **WEB_ONLY** | Adds "Research Source" links to the email. | Fast / Low Cost |
| **AI_FULL** | **(Recommended)** Performs dual-search to find official sites + news, then uses Gemini to summarize business model and sentiment. | Slower / Higher Value |

---

## ☁️ Deployment Guide

### Option A: Azure Functions (Recommended)
This script is architected to run as a **Timer Trigger** Azure Function.

1.  **Create Function App:** Select Python (Consumption Plan) in Azure Portal.
2.  **Deploy Code:** Push the project folder. Ensure `main.py` is invoked by the function handler.
3.  **Configuration:** Go to **Settings > Environment Variables** in the Azure Portal.
    * Add all keys from your `.env` file (`FINNHUB_API_KEY`, `GEMINI_API_KEY`, etc.).
    * *Security Note: Do NOT upload the `.env` file itself.*
    * *Tip: Do not set `START_DATE` in Azure settings if you want it to run daily.*
4.  **Schedule:** Set the CRON expression to `0 0 9 * * *` (9:00 AM Daily).

### Option B: Windows Task Scheduler (Local)
1.  Open **Task Scheduler** > **Create Basic Task**.
2.  **Trigger:** Daily at 9:00 AM.
3.  **Action:** Start a Program.
    * **Program/Script:** `C:\Path\To\Your\Project\venv\Scripts\python.exe`
    * **Arguments:** `main.py`
    * **Start in:** `C:\Path\To\Your\Project\`

---

## 📧 Gmail App Password Guide
Since Google no longer allows "Less Secure Apps," you must use an App Password.

1.  Go to your **Google Account** > **Security**.
2.  Enable **2-Step Verification** (if not already on).
3.  Search for **"App Passwords"** in the search bar.
4.  Create a new app password (name it "IPO Bot").
5.  Copy the 16-character code into your `.env` file as `SMTP_PASS`.
