import re
from datetime import datetime

class KupiParser:
    def parse_item(self, text: str) -> dict:
        """Parses a single raw string from Kupi.cz into a structured dictionary."""
        
        # 1. Store Name
        store_match = re.match(r'^([^\d]+)', text)
        store = store_match.group(1).strip() if store_match else "Unknown"

        # 2. Price per Unit
        price_unit_match = re.search(r'cena\s+([\d,]+)\s*Kč', text)
        price_per_unit = float(price_unit_match.group(1).replace(',', '.')) if price_unit_match else None

        # 4. Price per Liter
        # We do this before volume to avoid confusion with potential numbers
        price_liter_match = re.search(r'([\d,]+)\s*Kč\s*/\s*1\s*l', text)
        price_per_liter = float(price_liter_match.group(1).replace(',', '.')) if price_liter_match else None

        # 3. Volume and Multipack
        # We look for something like `/ 0.33 l` or `/ 6x 0.33 l`
        # Because we already extracted unit price, let's look for the slash after the unit format
        # Pattern looks for an optional digits + 'x', then digits/comma + 'l'
        # e.g. / 0.33 l  or  / 6x 0.33 l
        volume_match = re.search(r'/\s*(?:(\d+)x\s*)?([\d,.]+)\s*l', text)
        volume_liters = None
        is_multipack = False
        
        if volume_match:
            multiplier_str = volume_match.group(1)
            base_volume_str = volume_match.group(2).replace(',', '.')
            base_volume = float(base_volume_str)
            
            if multiplier_str:
                is_multipack = True
                # If you want volume_liters to be the base per-item volume, keep base_volume.
                # If you want total volume of multipack, multiply it. The example shows 0.33 for multipack.
                # I will save the single item volume in volume_liters.
                volume_liters = base_volume
            else:
                volume_liters = base_volume

        # 5. Validity Date
        # Match 'platí do ' optionally followed by a day string, then matching the day and month numbers
        date_match = re.search(r'platí do.*?(\d{1,2})\.\s*(\d{1,2})\.', text)
        valid_until = None
        if date_match:
            day = int(date_match.group(1))
            month = int(date_match.group(2))
            
            # Since we are in 2026, let's default to 2026
            current_date = datetime.now()
            year = 2026
            
            # Edge case: If we scrape in December for a January deal
            if current_date.month == 12 and month == 1:
                year += 1
                
            valid_until = f"{year}-{month:02d}-{day:02d}"

        # 6. Packaging & Deposit (Záloha)
        packaging = "unknown"
        deposit_fee = 0.0
        
        if "plech" in text.lower():
            packaging = "can"
        elif "záloha na láhev" in text.lower() or "záloha na láhve" in text.lower():
            packaging = "bottle"
            deposit_match = re.search(r'\+(\d+)\s*Kč', text)
            if deposit_match:
                deposit_fee = float(deposit_match.group(1))

        return {
            "store": store,
            "price_per_unit": price_per_unit,
            "volume_liters": volume_liters,
            "price_per_liter": price_per_liter,
            "valid_until": valid_until,
            "packaging": packaging,
            "deposit_fee": deposit_fee,
            "is_multipack": is_multipack
        }
