# read_card_complete.py

from desfire_ev1.desfire_ev1_card import DesfireCard
from desfire_ev1.files import FileManager
from desfire_ev1.utils import from_4bytes

def read_complete_card():
    """Read mission and articles from card"""
    
    # Configuration
    MISSION_APP_ID = [0x00, 0x00, 0x02]
    ARTICLE_APP_ID = [0x00, 0x00, 0x03]
    KEY_NUMBER = [0x00]
    KEY_VALUE = bytes([0x00] * 8)
    
    try:
        # Initialize
        print("Connecting to card...")
        card = DesfireCard()
        file_mgr = FileManager(card)
        
        # ===== READ MISSION =====
        print("\n[1/2] Reading mission information...")
        card.select_application(MISSION_APP_ID)
        card.authenticate(KEY_NUMBER, KEY_VALUE)
        
        mission_data = file_mgr.read_data(0x01, 0, 57)
        mission = {
            'mission_id': bytes(mission_data[0:8]).decode('utf-8').strip(),
            'truck_id': bytes(mission_data[8:16]).decode('utf-8').strip(),
            'status': mission_data[16],
            'source': bytes(mission_data[17:37]).decode('utf-8').strip(),
            'destination': bytes(mission_data[37:57]).decode('utf-8').strip()
        }
        
        # ===== READ ARTICLES =====
        print("[2/2] Reading articles...")
        card.select_application(ARTICLE_APP_ID)
        card.authenticate(KEY_NUMBER, KEY_VALUE)
        
        articles_data = file_mgr.read_records(0x01, 0, 0)
        articles = []
        
        for i in range(0, len(articles_data), 8):
            if i + 8 <= len(articles_data):
                record = articles_data[i:i+8]
                code = bytes(record[0:4]).decode('utf-8').strip()
                quantity = from_4bytes(record[4:8])
                articles.append({'code': code, 'quantity': quantity})
        
        # ===== DISPLAY =====
        status_names = {0: "Pending", 1: "In Transit", 2: "Delivered"}
        
        print("\n" + "="*60)
        print("CARD CONTENTS")
        print("="*60)
        print("\n--- MISSION ---")
        print(f"ID:          {mission['mission_id']}")
        print(f"Truck:       {mission['truck_id']}")
        print(f"Status:      {status_names.get(mission['status'], 'Unknown')}")
        print(f"From:        {mission['source']}")
        print(f"To:          {mission['destination']}")
        
        print("\n--- ARTICLES ---")
        print(f"{'Code':<10} {'Quantity':>10}")
        print("-"*60)
        for article in articles:
            print(f"{article['code']:<10} {article['quantity']:>10}")
        print("-"*60)
        print(f"Total articles: {len(articles)}")
        print("="*60 + "\n")
        
        return {'mission': mission, 'articles': articles}
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return None


if __name__ == "__main__":
    data = read_complete_card()
    
    if data:
        print("✅ Card read successfully!")
    else:
        print("❌ Failed to read card")
