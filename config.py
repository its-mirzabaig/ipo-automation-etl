import os
import argparse
import datetime
from dotenv import load_dotenv

load_dotenv()

def load_config():
    # 1. CLI Override (Highest Priority)
    parser = argparse.ArgumentParser(description="IPO Automation Bot")
    parser.add_argument("--date", type=str, help="Override run for a specific date (YYYY-MM-DD)")
    args = parser.parse_args()

    today_str = datetime.date.today().strftime('%Y-%m-%d')

    # 2. Determine Date Range
    if args.date:
        # CLI Manual Override
        start_date = args.date
        end_date = args.date
    else:
        # Check Environment Variables
        env_start = os.getenv("START_DATE")
        env_end = os.getenv("END_DATE")

        if env_start and env_end:
            # Configured Range (e.g. for Verification or Backtesting)
            start_date = env_start
            end_date = env_end
        else:
            # Default to Today (Production)
            start_date = today_str
            end_date = today_str

    # 3. Parse Email List
    raw_emails = os.getenv("RECEIVER_EMAILS", "")
    email_list = [e.strip() for e in raw_emails.split(',') if e.strip()]

    return {
        "API_KEY": os.getenv("FINNHUB_API_KEY"),
        "GEMINI_KEY": os.getenv("GEMINI_API_KEY"),
        "TAVILY_KEY": os.getenv("TAVILY_API_KEY"),
        "SMTP_EMAIL": os.getenv("SMTP_EMAIL"),
        "SMTP_PASS": os.getenv("SMTP_PASS"),
        "RECEIVER_EMAILS": email_list,
        "THRESHOLD": float(os.getenv("IPO_THRESHOLD", 200_000_000)),
        "ENRICHMENT_MODE": os.getenv("ENRICHMENT_MODE", "WEB_ONLY").upper(),
        "START_DATE": start_date,
        "END_DATE": end_date
    }

CONFIG = load_config()