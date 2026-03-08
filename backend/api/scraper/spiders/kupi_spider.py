import requests
from bs4 import BeautifulSoup

# Phase 1: Fetching the Raw HTML
URL = "https://www.kupi.cz/sleva/pivo-svetly-lezak-proud"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

def fetch_beer_discounts():
    try:
        # Execute GET request
        response = requests.get(URL, headers=HEADERS)
        response.raise_for_status()
        html_content = response.text

        # Phase 2: Initializing the DOM Parser
        soup = BeautifulSoup(html_content, 'html.parser')

        # Phase 3 & 4: Locating Items
        # Find all items containing the target classes
        items = soup.find_all(class_='discount_row log_discount only_discount')
        
        if not items:
            print("Warning: Could not find any items with class 'discount_row log_discount only_discount'.")
            return None

        ALLOWED_MARKETS = [
            'albert',
            'lidl',
            'tesco',
            'billa',
            'penny market',
            'globus'
        ]

        extracted_data = []
        for item in items:
            # Phase 5: Data Extraction & Output
            # Extract all nested text content, strip away extra spaces
            text = item.get_text(separator=' ', strip=True)
            
            # Print the text to console if it's not empty
            if text:
                # Basic cleanup (replacing multiple spaces with single space)
                clean_text = ' '.join(text.split())
                
                # Filter by explicitly allowed markets (case-insensitive)
                lower_text = clean_text.lower()
                market_found = any(market in lower_text for market in ALLOWED_MARKETS)

                if market_found:
                    print(f"--- Item ---")
                    print(clean_text)
                    extracted_data.append(clean_text)

        return extracted_data

    except requests.exceptions.RequestException as e:
        print(f"Warning: Failed to fetch data. Error: {e}")
        return None
