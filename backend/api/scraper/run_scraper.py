import json
from api.scraper.spiders.kupi_spider import fetch_beer_discounts
from api.scraper.parser import KupiParser
from api.scraper.saver import MongoSaver
import logging

logger = logging.getLogger(__name__)

def run_scrape_job():
    logger.info("Starting scheduled scrape job...")
    raw_data = fetch_beer_discounts()
    
    if not raw_data:
        logger.warning("No data fetched from Kupi.cz")
        return
        
    logger.info(f"Successfully loaded {len(raw_data)} raw records")
    
    parser = KupiParser()
    parsed_items = []
    
    for text in raw_data:
        parsed_items.append(parser.parse_item(text))
        
    saver = MongoSaver()
    final_deals = saver.save_deals(parsed_items)
    
    logger.info(f"Scrape job complete. Saved/Updated {len(final_deals)} curated deals.")

