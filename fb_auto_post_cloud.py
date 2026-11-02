
"""
Swaran Collections - CLOUD VERSION WITH PHOTO - UPDATED GOOD QUALITY
Update: Mehenga filter HATA DIYA, ab Badhiya + Viral + Maza wala
- Random (repeat nahi)
- Trending + One Day Delivery
- Ladies Suit only (decent, gande wale nahi)
- High Rating + High Discount = Badhiya
"""

import requests
import random
import os
import json
from datetime import datetime
from bs4 import BeautifulSoup

PAGE_ID = "1443186738872107"
USER_TOKEN = os.environ.get("FB_USER_TOKEN", "EAAOhttEXSLcBSZBpOTI4NTGBYW1U55RFTb29d691iZBIUT6JlJ5ihSjx0R6SFBZCxZBkR9OVrmMSu2QYVR545kcxfquv1dW3RwSvcbEQYq4aKZCav4sUOzM5pANMdCL06frqvfZADu7z243BNbhjrcl8YzpRwYLdV7NCjg85obSpT0Yz34SOXsA740cEgZAIi3xUHFHO6GHgkmVwsLFjRBElpNorg2HZAqiAZCjtDg9pz3ZB199j8aN37ff4pwXwR8DSSnTZCDpgigMTlswxP1HV2ZA8")

POSTED_FILE = "/tmp/posted_products_good.json"  # GitHub Actions me /tmp me save hoga

PRODUCTS = [
    {
        "title": "S B Senjaliya Embroidered Kurta Palazzo Dupatta - Pink",
        "price": "₹696",
        "mrp": 2499,
        "sale_price": 696,
        "rating": 3.9,
        "reviews": 166,
        "delivery": "One Day Delivery",
        "trending": True,
        "category": "ladies_suit",
        "link": "https://dl.flipkart.com/s/4wxNEQuuuN",
        "hashtags": "#SwaranCollections #PinkSuit #ViralSuit",
        "caption": "✨ ये वाला तो आग लगा देगा 🔥 - Pink Embroidered Palazzo Set ✨\nS B Senjaliya Premium - Festive Party Special"
    },
    {
        "title": "QUEENLIKE Self Design Kurta Pant Dupatta Set - Red",
        "price": "₹719",
        "mrp": 2799,
        "sale_price": 719,
        "rating": 3.8,
        "reviews": 281,
        "delivery": "One Day Delivery",
        "trending": True,
        "category": "ladies_suit",
        "link": "https://dl.flipkart.com/s/4e4__vuuuN",
        "hashtags": "#SwaranCollections #RedSuit #FestiveWear",
        "caption": "✨ VIRAL RED SUIT - Queenlike Self Design Set ✨\nFull Sleeve Festive & Party Wear - Self Design Work"
    },
    {
        "title": "Teal Blue Chanderi Silk Kurta Set - Heavy Work Festive",
        "price": "₹899",
        "mrp": 2999,
        "sale_price": 899,
        "rating": 4.2,
        "reviews": 450,
        "delivery": "One Day Delivery",
        "trending": True,
        "category": "ladies_suit",
        "link": "https://www.meesho.com/teal-blue-floral-printed-chanderi-cotton-dupatta-set-with-embroidered-rayon-slub-kurti-pant-ethnic-festive-wear-kurta-set-for-women-meesho-trending-2026/p/ffm7d2",
        "hashtags": "#SwaranCollections #TealSuit #Chanderi",
        "caption": "✨ Teal Blue Festive Blast - Chanderi Silk Heavy Work ✨\nPremium Rayon Slub Kurta + Chanderi Dupatta"
    },
    {
        "title": "Black Chikankari Lucknowi Kurta Palazzo - White Work",
        "price": "₹849",
        "mrp": 2799,
        "sale_price": 849,
        "rating": 4.4,
        "reviews": 512,
        "delivery": "One Day Delivery",
        "trending": True,
        "category": "ladies_suit",
        "link": "https://www.flipkart.com/shotek-embroidered-kurta-salwar-dupatta-set/p/itmf56e474a329fc",
        "hashtags": "#SwaranCollections #Chikankari #Lucknowi",
        "caption": "✨ Black & White Chikankari Magic - Lucknowi Special ✨\nWhite Work on Black - Most Demanded Design"
    },
    {
        "title": "Mustard Yellow Anarkali Gown Set - Mirror Work",
        "price": "₹799",
        "mrp": 2599,
        "sale_price": 799,
        "rating": 4.1,
        "reviews": 320,
        "delivery": "One Day Delivery",
        "trending": True,
        "category": "ladies_suit",
        "link": "https://www.meesho.com/women-farsi-salwar-set-3-pcs-heavy-satin-floral-kurti-farshi-palazzo-dupatta-white-black-rose-print-festive-eid-wear-m-l-xl-xxl/p/g7hi09",
        "hashtags": "#SwaranCollections #YellowAnarkali #MirrorWork",
        "caption": "✨ Yellow Anarkali - Mirror Work Festive Look ✨\nFloor Length Gown Style - Party Wear Hit"
    },
    {
        "title": "Heavy Satin Farshi Salwar Set - White Black Rose Print",
        "price": "₹1282",
        "mrp": 3200,
        "sale_price": 1282,
        "rating": 4.3,
        "reviews": 600,
        "delivery": "One Day Delivery",
        "trending": True,
        "category": "ladies_suit",
        "link": "https://www.meesho.com/women-farsi-salwar-set-3-pcs-heavy-satin-floral-kurti-farshi-palazzo-dupatta-white-black-rose-print-festive-eid-wear-m-l-xl-xxl/p/g7hi09",
        "hashtags": "#SwaranCollections #FarshiSalwar #Viral2026",
        "caption": "✨ Most Viral 2026 — Heavy Satin Farshi Salwar Set ✨\nWhite-to-Black Gradient Floral - Eid Special"
    }
]

def is_badhiya(p):
    if p.get("category") != "ladies_suit":
        return False
    if not p.get("trending"):
        return False
    if "One Day" not in p.get("delivery", ""):
        return False
    if p.get("rating", 0) < 3.8:
        return False
    discount = (1 - p["sale_price"]/p["mrp"])*100 if p.get("mrp") else 0
    if discount < 60:
        return False
    dirty = ["bikini", "lingerie", "bralette", "transparent", "mini", "shorts"]
    if any(k in p["title"].lower() for k in dirty):
        return False
    return True

def get_random_badhiya_product():
    posted = []
    if os.path.exists(POSTED_FILE):
        try:
            with open(POSTED_FILE, "r") as f:
                posted = json.load(f)
        except:
            posted = []
    valid = [p for p in PRODUCTS if is_badhiya(p)]
    available = [p for p in valid if p["title"] not in posted]
    if not available:
        posted = []
        available = valid
    selected = random.choice(available)
    posted.append(selected["title"])
    try:
        with open(POSTED_FILE, "w") as f:
            json.dump(posted, f)
    except:
        pass
    return selected

def get_page_token():
    url = f"https://graph.facebook.com/v20.0/me/accounts?access_token={USER_TOKEN}"
    r = requests.get(url)
    data = r.json()
    if "data" in data:
        for page in data["data"]:
            if page["id"] == PAGE_ID:
                return page["access_token"]
    print(f"ERROR: Page token nahi mila - {data}")
    return None

def get_og_image(product_url):
    try:
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
        r = requests.get(product_url, headers=headers, timeout=20)
        soup = BeautifulSoup(r.text, "html.parser")
        og = soup.find("meta", property="og:image")
        if og and og.get("content"):
            img_url = og["content"]
            if img_url.startswith("//"):
                img_url = "https:" + img_url
            return img_url
        tw = soup.find("meta", attrs={"name": "twitter:image"})
        if tw and tw.get("content"):
            return tw["content"]
    except Exception as e:
        print(f"Image fetch error {product_url}: {e}")
    return None

def post_with_photo(page_token, product):
    image_url = get_og_image(product["link"])
    base_caption = f"""{product['caption']}

Price: {product['price']} (MRP ₹{product['mrp']}) - {int((1-product['sale_price']/product['mrp'])*100)}% OFF
Rating: {product['rating']}★ ({product['reviews']} Reviews)
Delivery: {product['delivery']} 🚚

Shop: {product['link']}

👇 Is rate pe dubara nahi milega - Jaldi Order Karo 👇
DM for order or comment LINK
{product['hashtags']}

Auto-posted at {datetime.now().strftime('%d-%m-%Y %I:%M %p')} - Badhiya Quality Mode"""

    if not image_url:
        print(f"No og:image for {product['title']}, posting as feed")
        url = f"https://graph.facebook.com/v20.0/{PAGE_ID}/feed"
        payload = {"message": base_caption, "link": product["link"], "access_token": page_token}
        r = requests.post(url, data=payload)
        print(f"[{datetime.now()}] Feed Status: {r.status_code} - {r.text}")
        return r.json()

    url = f"https://graph.facebook.com/v20.0/{PAGE_ID}/photos"
    payload = {"url": image_url, "caption": base_caption, "access_token": page_token}
    r = requests.post(url, data=payload)
    print(f"[{datetime.now()}] Photo Status: {r.status_code} - {r.text}")
    return r.json()

if __name__ == "__main__":
    if "YOUR_USER_TOKEN" in USER_TOKEN:
        print("ERROR: FB_USER_TOKEN secret set nahi hai")
    else:
        page_token = get_page_token()
        if page_token:
            product = get_random_badhiya_product()
            print(f"Posting BADHIYA: {product['title']} | {product['link']}")
            result = post_with_photo(page_token, product)
            if "id" in result:
                print(f"Status: 200 - Post ID {result.get('id')}")
            else:
                print(f"Failed: {result}")
                
permissions:
  contents: write

concurrency:
  group: swaran-auto-post
  cancel-in-progress: false

