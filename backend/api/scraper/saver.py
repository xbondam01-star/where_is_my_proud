import pymongo
from datetime import datetime

class MongoSaver:
    def __init__(self, uri="mongodb://localhost:27017"):
        self.client = pymongo.MongoClient(uri)
        self.db = self.client.proud_db
        self.collection = self.db.deals
        
        # Setup TTL Index for Database Cleanup
        # This will automatically delete documents when the valid_until Date is reached.
        # We index 'valid_until_date' and expire items exactly at that time (expireAfterSeconds=0)
        self.collection.create_index(
            [("valid_until_date", pymongo.ASCENDING)],
            expireAfterSeconds=0
        )

    def save_deals(self, parsed_items):
        mandatory_stores = ['albert', 'billa', 'lidl']
        
        mandatory_deals = []
        other_deals = []
        
        # Separate deals by mandatory vs non-mandatory
        for item in parsed_items:
            store_lower = item['store'].lower()
            if any(mand_store in store_lower for mand_store in mandatory_stores):
                mandatory_deals.append(item)
            else:
                other_deals.append(item)

        # Find the minimum price per liter in the mandatory list
        min_mandatory_price = float('inf')
        for deal in mandatory_deals:
            if deal['price_per_liter'] is not None and deal['price_per_liter'] < min_mandatory_price:
                min_mandatory_price = deal['price_per_liter']
                
        if min_mandatory_price == float('inf'):
            print("Warning: No mandatory stores found or no price_per_liter parsed. Taking minimum across all to be safe or skipping filter.")
            min_mandatory_price = None

        deals_to_save = list(mandatory_deals) # We always save mandatory deals

        # Competitive Filtering (The "Good Price" Check)
        for deal in other_deals:
            if min_mandatory_price is None:
                deals_to_save.append(deal) # If no mandatory price, just save it (edge case)
            elif deal['price_per_liter'] and deal['price_per_liter'] < (min_mandatory_price * 0.9):
                print(f"Super Deal Found! {deal['store']} is deeply discounted at {deal['price_per_liter']} Kč/L compared to {min_mandatory_price} Kč/L.")
                deals_to_save.append(deal)
            else:
                print(f"Ignoring {deal['store']} deal of {deal['price_per_liter']} Kč/L (not 10% cheaper than {min_mandatory_price} Kč/L).")

        # Upsert the curated deals
        upserted_count = 0
        deleted_count = 0 # (If we want to manually cleanup old deals, but TTL handles it)
        
        for deal in deals_to_save:
            # We need to save the valid_until as a python datetime for MongoDB TTL to work
            if deal.get('valid_until'):
                try:
                    deal['valid_until_date'] = datetime.strptime(deal['valid_until'], "%Y-%m-%d")
                except ValueError:
                    deal['valid_until_date'] = None

            # UPSERT based on the store and volume_liters. 
            # If the same store has a deal for the same volume, we update it instead of creating duplicates.
            result = self.collection.update_one(
                {
                    "store": deal["store"], 
                    "volume_liters": deal["volume_liters"]
                },
                {"$set": deal},
                upsert=True
            )
            if result.upserted_id or result.modified_count > 0:
                upserted_count += 1
                
        print(f"Upserted/Updated {upserted_count} deals in MongoDB.")
        return deals_to_save
