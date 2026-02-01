import finnhub
from config import CONFIG
from logger import logger

def get_ipo_data(start, end):
    try:
        client = finnhub.Client(api_key=CONFIG["API_KEY"])
        logger.info(f"📡 Connecting to Finnhub API ({start} -> {end})...")
        response = client.ipo_calendar(_from=start, to=end)
        data = response.get('ipoCalendar', [])
        logger.info(f"✅ API Success: Received {len(data)} records.")
        return data
    except Exception as e:
        logger.error(f"❌ API Connection Failed: {e}")
        return []

def calculate_value(ipo):
    symbol = ipo.get('symbol', 'UNKNOWN')
    
    # 1. Trust API Total
    if ipo.get('totalSharesValue'):
        return float(ipo['totalSharesValue'])
    
    # 2. Fallback Calculation
    try:
        shares = float(ipo.get('numberOfShares') or 0)
        price_raw = str(ipo.get('price') or "0")
        
        if '-' in price_raw:
            price = float(price_raw.split('-')[1]) # Use max of range
        else:
            price = float(price_raw)
            
        return price * shares
    except Exception as e:
        logger.warning(f"⚠️ Value calc failed for {symbol}: {e}")
        return 0.0

def filter_ipos(data):
    matches = []
    logger.info(f"--- 🔍 Analyzing {len(data)} Candidates ---")

    for ipo in data:
        name = ipo.get('name', 'N/A')
        symbol = ipo.get('symbol', 'N/A')
        value = calculate_value(ipo)
        
        # --- IMPROVED LOGGING LOGIC ---
        if value > 0:
            val_display = f"${value:,.0f}"
        else:
            val_display = "Not Specified (API Data Missing)"
            
        log_msg = f"{symbol} ({name}) | Val: {val_display}"

        if value > CONFIG["THRESHOLD"]:
            logger.info(f"🟢 MATCH: {log_msg}")
            matches.append({
                "symbol": symbol,
                "name": name,
                "value": value,
                "date": ipo.get('date', 'N/A')
            })
        else:
            logger.info(f"⚪ SKIP:  {log_msg}")

    return matches