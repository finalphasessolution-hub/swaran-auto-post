
import os
import requests
from bs4 import BeautifulSoup
import random
import re

# Config
PAGE_ID = "1443186738872107"
USER_TOKEN = os.getenv("FB_USER_TOKEN")

PRODUCTS = [
    {
        "title": "Heavy Satin Farshi Salwar Set - White Black Rose Print",
        "price": "₹1282",
        "link": "https://www.meesho.com/women-farsi-salwar-set-3-pcs-heavy-satin-floral-kurti-farshi-palazzo-dupatta-white-black-rose-print-festive-eid-wear-m-l-xl-xxl/p/g7hi09",
        "hashtags": "#SwaranCollections #FarshiSalwar #MeeshoTrending"
    },
    {
        "title": "Anny Deziner Georgette Embroidered Suit Material",
        "price": "₹475 (72% OFF)",
        "link": "https://www.flipkart.com/anny-deziner-georgette-embroidered-embellished-salwar-suit-material/p/itm283d5f5ea0b6a?pid=FABHNP37AX2CFBCY",
        "hashtags": "#FlipkartFashion #AnnyDeziner #SwaranCollections"
    }
]

def get_page_token(user_token):
    url = f"https://graph.facebook.com/v20.0/me/accounts?access_token={user_token}"
    r = requests.get(url)
    data = r.json()
    if "data" not in data:
        print("ERROR: Page token nahi mila", data)
        return None
    for page in data["data"]:
        if page["id"] == PAGE_ID:
            return page["access_token"]
    print("ERROR: Page token nahi mila - Page ID not in me/accounts", data)
    return None

def get_og_image(product_url):
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        r = requests.get(product_url, headers=headers, timeout=15)
        soup = BeautifulSoup(r.text, "html.parser")
        og = soup.find("meta", property="og:image")
        if og and og.get("content"):
            return og["content"]
        # fallback: first img
        img = soup.find("img")
        if img and img.get("src"):
            src = img["src"]
            if src.startswith("//"):
                src = "https:" + src
            return src
    except Exception as e:
        print(f"Image fetch error for {product_url}: {e}")
    return None

def post_with_photo(page_token, product):
    image_url = get_og_image(product["link"])
    if not image_url:
        print(f"No image found for {product['title']}, posting as feed")
        # fallback to feed post
        url = f"https://graph.facebook.com/v20.0/{PAGE_ID}/feed"
        message = f"""✨ {product['title']} ✨
Price: {product['price']}
Shop Now: {product['link']}

DM for order!
{product['hashtags']}"""
        payload = {"message": message, "link": product["link"], "access_token": page_token}
        r = requests.post(url, data=payload)
        print("Feed post response:", r.json())
        return r.json()

    # post as photo with caption
    url = f"https://graph.facebook.com/v20.0/{PAGE_ID}/photos"
    caption = f"""✨ {product['title']} ✨
Price: {product['price']}

Shop Now: {product['link']}

DM for order or comment LINK
{product['hashtags']}

Auto-posted at {__import__('datetime').datetime.now().strftime('%d-%m-%Y %I:%M %p')} - Cloud Mode (Laptop band bhi chalega)"""
    payload = {
        "url": image_url,
        "caption": caption,
        "access_token": page_token
    }
    r = requests.post(url, data=payload)
    print("Photo post response:", r.json())
    return r.json()

def main():
    if not USER_TOKEN:
        print("ERROR: FB_USER_TOKEN secret set nahi hai")
        return
    page_token = get_page_token(USER_TOKEN)
    if not page_token:
        return
    product = random.choice(PRODUCTS)
    print(f"Posting: {product['title']}")
    result = post_with_photo(page_token, product)
    if "id" in result:
        print(f"Status: 200 - Post ID {result['id']}")
    else:
        print(f"Failed: {result}")

if __name__ == "__main__":
    main()
