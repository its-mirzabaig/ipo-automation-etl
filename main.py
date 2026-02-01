from config import CONFIG
from logger import logger
from data_fetcher import get_ipo_data, filter_ipos
from enrichment import enrich_data
from email_service import send_email

def main():
    logger.info("=== 🤖 AUTOMATION WORKFLOW STARTED ===")
    
    logger.info(f"📅 Configuration: Running from {CONFIG['START_DATE']} to {CONFIG['END_DATE']}")

    # 1. Fetch & Filter
    raw_data = get_ipo_data(CONFIG["START_DATE"], CONFIG["END_DATE"])
    matches = filter_ipos(raw_data)
    
    # 2. Enrich (Dual Search + AI)
    if matches:
        matches = enrich_data(matches)
    
    # 3. Dispatch
    send_email(matches)
    
    logger.info("=== WORKFLOW COMPLETED ===")

if __name__ == "__main__":
    main()