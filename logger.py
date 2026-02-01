import logging
import os
import datetime

def setup_logger(name="IPO_Bot"):
    log_dir = "logs"
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    today_str = datetime.date.today().strftime('%Y-%m-%d')
    log_file = os.path.join(log_dir, f"log_{today_str}.txt")

    formatter = logging.Formatter('%(asctime)s [%(levelname)s] %(message)s')

    # File Handler (UTF-8)
    file_handler = logging.FileHandler(log_file, encoding='utf-8')
    file_handler.setFormatter(formatter)

    # Console Handler (UTF-8 safe)
    stream_handler = logging.StreamHandler()
    if hasattr(stream_handler.stream, 'reconfigure'):
        stream_handler.stream.reconfigure(encoding='utf-8')
    stream_handler.setFormatter(formatter)

    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    
    if logger.hasHandlers():
        logger.handlers.clear()
        
    logger.addHandler(file_handler)
    logger.addHandler(stream_handler)
    
    return logger

logger = setup_logger()