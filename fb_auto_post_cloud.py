"""
Swaran Collections - CLOUD VERSION WITH PHOTO - UPDATED GOOD QUALITY
Update: Mehenga filter HATA DIYA, ab Badhiya + Viral + Maza wala
- Random (repeat nahi)
- Trending + One Day Delivery
- Ladies Suit only (decent, gande wale nahi)
- High Rating + High Discount = Badhiya
"""

import json
import os
import random
from datetime import datetime

import requests
from bs4 import BeautifulSoup

PAGE_ID = os.environ.get("FB_PAGE_ID", "1443186738872107")
USER_TOKEN = os.environ.get("FB_USER_TOKEN")
POSTED_FILE = os.environ.get("POSTED_FILE", "/tmp/posted_products_good.json")

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
        "caption": "✨ ये वाला तो आग लगा देगा 🔥 - Pink Embroidered Palazzo Set ✨\nS B Senjaliya Premium - Festive Party Special",
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
        "caption": "✨ VIRAL RED SUIT - Queenlike Self Design Set ✨\nFull Sleeve Festive & Party Wear - Self Design Work",
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
        "link": "https://www.meesho.com/teal-blue-floral-printed-chanderi-cotton-dupatta-set-with-embroidered-rayon-slub-kurti-pant-ethnic-festive-wear-kurta-set-for-women-meesho-trending-2026/p/ffm7d",
        "hashtags": "#SwaranCollections #TealSuit #Chanderi",
        "caption": "✨ Teal Blue Festive Blast - Chanderi Silk Heavy Work ✨\nPremium Rayon Slub Kurta + Chanderi Dupatta",
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
        "caption": "✨ Black & White Chikankari Magic - Lucknowi Special ✨\nWhite Work on Black - Most Demanded Design",
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
        "caption": "✨ Yellow Anarkali - Mirror Work Festive Look ✨\nFloor Length Gown Style - Party Wear Hit",
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
        "caption": "✨ Most Viral 2026 — Heavy Satin Farshi Salwar Set ✨\nWhite-to-Black Gradient Floral - Eid Special",
    },
]


def is_badhiya(product):
    if product.get("category") != "ladies_suit":
        return False
    if not product.get("trending"):
        return False
    if "One Day" not in product.get("delivery", ""):
        return False
    if product.get("rating", 0) < 3.8:
        return False

    mrp = product.get("mrp")
    sale_price = product.get("sale_price")
    if mrp and sale_price:
        discount = (1 - (sale_price / mrp)) * 100
    else:
        discount = 0
    if discount < 60:
        return False

    dirty = ["bikini", "lingerie", "bralette", "transparent", "mini", "shorts"]
    if any(keyword in product["title"].lower() for keyword in dirty):
        return False
    return True


def get_posted_titles():
    if not os.path.exists(POSTED_FILE):
        return []

    try:
        with open(POSTED_FILE, "r", encoding="utf-8") as file:
            data = json.load(file)
        if isinstance(data, list):
            return data
        return []
    except Exception:
        return []


def save_posted_titles(posted_titles):
    try:
        os.makedirs(os.path.dirname(POSTED_FILE) or ".", exist_ok=True)
        with open(POSTED_FILE, "w", encoding="utf-8") as file:
            json.dump(posted_titles, file)
    except Exception as exc:
        print(f"Warning: unable to save posted titles: {exc}")


def get_random_badhiya_product():
    posted = get_posted_titles()
    valid = [product for product in PRODUCTS if is_badhiya(product)]
    available = [product for product in valid if product["title"] not in posted]

    if not available:
        posted = []
        available = valid

    selected = random.choice(available)
    posted.append(selected["title"])
    save_posted_titles(posted)
    return selected


def get_page_token():
    if not USER_TOKEN:
        print("ERROR: FB_USER_TOKEN secret set nahi hai")
        return None

    url = f"https://graph.facebook.com/v20.0/me/accounts?access_token={USER_TOKEN}"
    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        data = response.json()
    except requests.RequestException as exc:
        print(f"ERROR: Facebook page token fetch failed: {exc}")
        return None

    if "data" in data:
        for page in data["data"]:
            if page.get("id") == PAGE_ID:
                return page.get("access_token")

    print(f"ERROR: Page token nahi mila - {data}")
    return None


def get_og_image(product_url):
    try:
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
        response = requests.get(product_url, headers=headers, timeout=20)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")

        og = soup.find("meta", property="og:image")
        if og and og.get("content"):
            img_url = og["content"]
            if img_url.startswith("//"):
                img_url = "https:" + img_url
            return img_url

        twitter = soup.find("meta", attrs={"name": "twitter:image"})
        if twitter and twitter.get("content"):
            return twitter["content"]
    except Exception as exc:
        print(f"Image fetch error {product_url}: {exc}")
    return None


def post_text_update(page_token, product):
    caption = f"""{product['caption']}

Price: {product['price']} (MRP ₹{product['mrp']}) - {int((1 - product['sale_price'] / product['mrp']) * 100)}% OFF
Rating: {product['rating']}★ ({product['reviews']} Reviews)
Delivery: {product['delivery']} 🚚

Shop: {product['link']}

👇 Is rate pe dubara nahi milega - Jaldi Order Karo 👇
DM for order or comment LINK
{product['hashtags']}

Auto-posted at {datetime.now().strftime('%d-%m-%Y %I:%M %p')} - Badhiya Quality Mode"""
    url = f"https://graph.facebook.com/v20.0/{PAGE_ID}/feed"
    payload = {"message": caption, "link": product["link"], "access_token": page_token}

    try:
        response = requests.post(url, data=payload, timeout=30)
        response.raise_for_status()
        print(f"[{datetime.now()}] Feed Status: {response.status_code} - {response.text}")
        return response.json()
    except requests.RequestException as exc:
        print(f"[{datetime.now()}] Feed request failed: {exc}")
        return {"error": str(exc)}


def post_with_photo(page_token, product):
    image_url = get_og_image(product["link"])
    caption = f"""{product['caption']}

Price: {product['price']} (MRP ₹{product['mrp']}) - {int((1 - product['sale_price'] / product['mrp']) * 100)}% OFF
Rating: {product['rating']}★ ({product['reviews']} Reviews)
Delivery: {product['delivery']} 🚚

Shop: {product['link']}

👇 Is rate pe dubara nahi milega - Jaldi Order Karo 👇
DM for order or comment LINK
{product['hashtags']}

Auto-posted at {datetime.now().strftime('%d-%m-%Y %I:%M %p')} - Badhiya Quality Mode"""

    if not image_url:
        print(f"No og:image for {product['title']}, posting as feed")
        return post_text_update(page_token, product)

    url = f"https://graph.facebook.com/v20.0/{PAGE_ID}/photos"
    payload = {"url": image_url, "caption": caption, "access_token": page_token}

    try:
        response = requests.post(url, data=payload, timeout=30)
        response.raise_for_status()
        print(f"[{datetime.now()}] Photo Status: {response.status_code} - {response.text}")
        return response.json()
    except requests.RequestException as exc:
        print(f"[{datetime.now()}] Photo post failed: {exc}")
        print("Retrying as feed post")
        return post_text_update(page_token, product)


if __name__ == "__main__":
    if not USER_TOKEN:
        print("ERROR: FB_USER_TOKEN secret set nahi hai")
    else:
        page_token = get_page_token()
        if page_token:
            product = get_random_badhiya_product()
            print(f"Posting BADHIYA: {product['title']} | {product['link']}")
            result = post_with_photo(page_token, product)
            if result.get("id"):
                print(f"Status: 200 - Post ID {result.get('id')}")
            else:
                print(f"Failed: {result}")
