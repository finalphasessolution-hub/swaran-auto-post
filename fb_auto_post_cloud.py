"""
Swaran Collections - CLOUD VERSION (Laptop band ho to bhi chalega)
Ye GitHub Actions pe har 1 ghante chalega, laptop band ho to bhi
Token GitHub Secrets me safe rahega
"""

import requests
import random
import os
from datetime import datetime

PAGE_ID = "1443186738872107"
# GitHub Secrets se token ayega - local me test karna ho to yahan paste kar sakte ho
USER_TOKEN = os.environ.get("FB_USER_TOKEN", "YOUR_USER_TOKEN_HERE")

PRODUCTS = [
    {
        "title": "Trending Pink Premium Cotton Kurta Pant Dupatta Set",
        "price": "₹424",
        "link": "https://www.meesho.com/trending-womens-premium-cotton-printed-straight-kurta-pant-with-dupatta-set-ethnic-wear-daily-wear-office-wear-festive-collection/p/gpqm0s",
        "caption": "✨ TRENDING Today - Pink Premium Kurta Pant Dupatta Set ✨\nPremium Cotton Printed Straight Fit - Rayon Slub Kurta + Pant + Chanderi Silk Dupatta\nPrice just ₹424 - 4.4★ rated\nDM for order or comment LINK\n#SwaranCollections #MeeshoTrending #KurtaPantSet"
    },
    {
        "title": "Teal Blue Floral Chanderi Dupatta Set",
        "price": "₹484",
        "link": "https://www.meesho.com/teal-blue-floral-printed-chanderi-cotton-dupatta-set-with-embroidered-rayon-slub-kurti-pant-ethnic-festive-wear-kurta-set-for-women-meesho-trending-2026/p/ffm7d2",
        "caption": "✨ Meesho Trending Today - Teal Blue Festive Set ✨\nPremium Rayon Slub Kurta + Pant with Chanderi Cotton Floral Dupatta - Embroidered neckline\nPrice just ₹484 - Swaran Collections deal!\n#SwaranCollections #MeeshoTrending2026 #EthnicWear"
    },
    {
        "title": "SHOTEC Yellow Embroidered Kurta Salwar Dupatta",
        "price": "₹476",
        "link": "https://www.flipkart.com/shotek-embroidered-kurta-salwar-dupatta-set/p/itmf56e474a329fc",
        "caption": "🔥 Flipkart Trending - SHOTEC Yellow Embroidered Set 🔥\nEmbroidered Kurta, Salwar & Dupatta Set - Yellow | Rayon Cotton | Gotta Work\nFestive ready - Swaran Collections pick! DM to book\n#FlipkartFashion #Shotek #SwaranCollections"
    },
    {
        "title": "SAIRA NX Self Design Grey Set",
        "price": "₹599",
        "link": "https://www.flipkart.com/saira-nx-self-design-kurta-salwar-dupatta-set/p/itmfba1db84e00d3",
        "caption": "🔥 Flipkart Trending - SAIRA NX Grey Self Design Set 🔥\nSelf Design Kurta Salwar Dupatta Set - Grey, elegant pattern trending now\nPerfect for office & festive - Swaran Collections pick!\n#FlipkartFashion #SairaNX #SwaranCollections"
    }
]

def get_page_token():
    url = f"https://graph.facebook.com/me/accounts?access_token={USER_TOKEN}"
    r = requests.get(url)
    data = r.json()
    if "data" in data:
        for page in data["data"]:
            if page["id"] == PAGE_ID:
                return page["access_token"]
    return None

def post_to_page(page_token, message):
    url = f"https://graph.facebook.com/me/feed"
    data = {"message": message, "access_token": page_token}
    r = requests.post(url, data=data)
    print(f"[{datetime.now()}] Status: {r.status_code} - {r.text}")
    return r.json()

if __name__ == "__main__":
    if "YOUR_USER_TOKEN" in USER_TOKEN:
        print("ERROR: FB_USER_TOKEN secret set nahi hai")
    else:
        page_token = get_page_token()
        if page_token:
            product = random.choice(PRODUCTS)
            full_msg = f"{product['caption']}\n\nPrice: {product['price']}\nLink: {product['link']}\n\nAuto-posted at {datetime.now().strftime('%d-%m-%Y %I:%M %p')} - Cloud Mode (Laptop band bhi chalega)"
            print(f"Posting: {product['title']}")
            post_to_page(page_token, full_msg)
        else:
            print("ERROR: Page token nahi mila")
