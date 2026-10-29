
"""
Swaran Collections - CLOUD VERSION WITH PHOTO (Laptop band ho to bhi chalega)
Ye GitHub Actions pe har 1 ghante chalega, laptop band ho to bhi
Token GitHub Secrets me safe rahega - Photo ke saath post
"""

import requests
import random
import os
from datetime import datetime
from bs4 import BeautifulSoup

PAGE_ID = "1443186738872107"
USER_TOKEN = os.environ.get("FB_USER_TOKEN", "YOUR_USER_TOKEN_HERE")

PRODUCTS = [
    {
        "title": "Trending Pink Premium Cotton Kurta Pant Dupatta Set",
        "price": "₹424",
        "link": "https://www.meesho.com/trending-womens-premium-cotton-printed-straight-kurta-pant-with-dupatta-set-ethnic-wear-daily-wear-office-wear-festive-collection/p/gpqm0s",
        "hashtags": "#SwaranCollections #MeeshoTrending #KurtaPantSet",
        "caption": "✨ TRENDING Today - Pink Premium Kurta Pant Dupatta Set ✨\nPremium Cotton Printed Straight Fit - Rayon Slub Kurta + Pant + Chanderi Silk Dupatta"
    },
    {
        "title": "Teal Blue Floral Chanderi Dupatta Set",
        "price": "₹484",
        "link": "https://www.meesho.com/teal-blue-floral-printed-chanderi-cotton-dupatta-set-with-embroidered-rayon-slub-kurti-pant-ethnic-festive-wear-kurta-set-for-women-meesho-trending-2026/p/ffm7d2",
        "hashtags": "#SwaranCollections #MeeshoTrending2026 #EthnicWear",
        "caption": "✨ Meesho Trending Today - Teal Blue Festive Set ✨\nPremium Rayon Slub Kurta + Pant with Chanderi Cotton Floral Dupatta - Embroidered neckline"
    },
    {
        "title": "SHOTEC Yellow Embroidered Kurta Salwar Dupatta",
        "price": "₹476",
        "link": "https://www.flipkart.com/shotek-embroidered-kurta-salwar-dupatta-set/p/itmf56e474a329fc",
        "hashtags": "#FlipkartFashion #Shotek #SwaranCollections",
        "caption": "🔥 Flipkart Trending - SHOTEC Yellow Embroidered Set 🔥\nEmbroidered Kurta, Salwar & Dupatta Set - Yellow | Rayon Cotton | Gotta Work"
    },
    {
        "title": "SAIRA NX Self Design Grey Set",
        "price": "₹599",
        "link": "https://www.flipkart.com/saira-nx-self-design-kurta-salwar-dupatta-set/p/itmfba1db84e00d3",
        "hashtags": "#FlipkartFashion #SairaNX #SwaranCollections",
        "caption": "🔥 Flipkart Trending - SAIRA NX Grey Self Design Set 🔥\nSelf Design Kurta Salwar Dupatta Set - Grey, elegant pattern trending now"
    },
    {
        "title": "Heavy Satin Farshi Salwar Set - White Black Rose Print",
        "price": "₹1282",
        "link": "https://www.meesho.com/women-farsi-salwar-set-3-pcs-heavy-satin-floral-kurti-farshi-palazzo-dupatta-white-black-rose-print-festive-eid-wear-m-l-xl-xxl/p/g7hi09",
        "hashtags": "#SwaranCollections #FarshiSalwar #MeeshoTrending",
        "caption": "✨ Most Trending 2026 — Heavy Satin Farshi Salwar Set ✨\nWhite-to-Black Gradient Floral Kurti + Floor-Grazing Farshi Palazzo + Black Satin Dupatta"
    },
    {
        "title": "Anny Deziner Georgette Embroidered Suit Material",
        "price": "₹475 (72% OFF)",
        "link": "https://www.flipkart.com/anny-deziner-georgette-embroidered-embellished-salwar-suit-material/p/itm283d5f5ea0b6a?pid=FABHNP37AX2CFBCY",
        "hashtags": "#FlipkartFashion #AnnyDeziner #SwaranCollections #CommissionEligible",
        "caption": "🔥 Flipkart Trending — Anny Deziner Georgette Embroidered Suit Material 🔥\nUnstitched Georgette — Embroidered + Embellished, Lucknow Chikankari"
    }
]

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
        # Try og:image
        og = soup.find("meta", property="og:image")
        if og and og.get("content"):
            img_url = og["content"]
            if img_url.startswith("//"):
                img_url = "https:" + img_url
            return img_url
        # fallback twitter image
        tw = soup.find("meta", attrs={"name": "twitter:image"})
        if tw and tw.get("content"):
            return tw["content"]
    except Exception as e:
        print(f"Image fetch error {product_url}: {e}")
    return None

def post_with_photo(page_token, product):
    image_url = get_og_image(product["link"])
    
    base_caption = f"""{product['caption']}

Price: {product['price']}
Shop: {product['link']}

DM for order or comment LINK
{product['hashtags']}

Auto-posted at {datetime.now().strftime('%d-%m-%Y %I:%M %p')} - Cloud Mode (Laptop band bhi chalega)"""

    if not image_url:
        print(f"No og:image for {product['title']}, posting as feed with link")
        url = f"https://graph.facebook.com/v20.0/{PAGE_ID}/feed"
        payload = {
            "message": base_caption,
            "link": product["link"],
            "access_token": page_token
        }
        r = requests.post(url, data=payload)
        print(f"[{datetime.now()}] Feed Status: {r.status_code} - {r.text}")
        return r.json()

    # Photo post - Facebook will fetch image from url
    url = f"https://graph.facebook.com/v20.0/{PAGE_ID}/photos"
    payload = {
        "url": image_url,
        "caption": base_caption,
        "access_token": page_token
    }
    r = requests.post(url, data=payload)
    print(f"[{datetime.now()}] Photo Status: {r.status_code} - {r.text}")
    return r.json()

if __name__ == "__main__":
    if "YOUR_USER_TOKEN" in USER_TOKEN:
        print("ERROR: FB_USER_TOKEN secret set nahi hai")
    else:
        page_token = get_page_token()
        if page_token:
            product = random.choice(PRODUCTS)
            print(f"Posting: {product['title']} | {product['link']}")
            result = post_with_photo(page_token, product)
            if "id" in result:
                print(f"Status: 200 - Post ID {result.get('id')} Full: {result.get('post_id','')}")
            else:
                print(f"Failed: {result}")
        else:
            print("ERROR: Page token nahi mila")
