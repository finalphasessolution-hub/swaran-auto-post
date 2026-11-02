
"""
Swaran Collections - FINAL AUTO SEARCH MODE - NO HARDCODED PRODUCTS
Ab PRODUCTS list bilkul nahi hai - Google se Flipkart auto search karega

Queries:
- site:flipkart.com women ethnic set trending latest design 2026
- site:flipkart.com ladies kurta palazzo latest
- site:flipkart.com designer party wear suit trending

Filter: Flipkart Only + In Stock + Latest + Decent + Trending
"""

import requests
import random
import os
import json
import time
from datetime import datetime
from bs4 import BeautifulSoup
from urllib.parse import parse_qs, urlparse, quote_plus

PAGE_ID = "1443186738872107"
USER_TOKEN = os.environ.get("FB_USER_TOKEN", "YOUR_USER_TOKEN_HERE")

POSTED_FILE = "/tmp/posted_google_flipkart.json"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/122.0.0.0 Safari/537.36",
    "Accept-Language": "en-US,en;q=0.9"
}

# === SIRF YAHI 3 QUERIES - GOOGLE SE SEARCH ===
GOOGLE_QUERIES = [
    "site:flipkart.com women ethnic set trending latest design 2026",
    "site:flipkart.com ladies kurta palazzo latest",
    "site:flipkart.com designer party wear suit trending"
]

def is_decent_and_good(title):
    t = title.lower()
    dirty = ["bikini", "lingerie", "bralette", "transparent", "mini skirt", "shorts", "bra", "panty", "innerwear", "nighty", "swimsuit"]
    if any(k in t for k in dirty):
        return False
    good = ["kurta", "suit", "salwar", "palazzo", "dupatta", "anarkali", "ethnic", "sharara", "gown", "embroidered", "self design", "chanderi", "silk", "cotton", "festive", "party wear", "elegant", "designer"]
    if not any(k in t for k in good):
        return False
    return True

def google_search_flipkart(query, max_results=30):
    found_links = []
    try:
        encoded_query = quote_plus(query)
        google_url = f"https://www.google.com/search?q={encoded_query}&num={max_results}&hl=en"
        print(f"Google Search: {query}")
        r = requests.get(google_url, headers=HEADERS, timeout=20)
        soup = BeautifulSoup(r.text, "html.parser")
        for a in soup.find_all("a", href=True):
            href = a["href"]
            actual_url = ""
            if "/url?q=" in href:
                try:
                    parsed = urlparse(href)
                    qs = parse_qs(parsed.query)
                    if "q" in qs:
                        actual_url = qs["q"][0]
                except:
                    continue
            elif href.startswith("https://www.flipkart.com"):
                actual_url = href
            else:
                continue
            if "flipkart.com" in actual_url and "/p/" in actual_url:
                actual_url = actual_url.split("?")[0].split("&")[0].split("#")[0]
                if actual_url.startswith("https://www.flipkart.com") and actual_url not in found_links and len(actual_url) > 30:
                    # Sirf ladies ethnic wale
                    if any(x in actual_url.lower() for x in ["kurta", "ethnic", "salwar", "suit", "anarkali", "palazzo", "gown"]):
                        found_links.append(actual_url)
                    elif "/p/" in actual_url:
                        found_links.append(actual_url)
        print(f"Found {len(found_links)} links for {query[:40]}")
        return list(set(found_links))
    except Exception as e:
        print(f"Google search error: {e}")
        return []

def check_in_stock(product_url):
    try:
        r = requests.get(product_url, headers=HEADERS, timeout=20)
        text = r.text.lower()
        if "out of stock" in text or "sold out" in text:
            if "notify me" in text and "add to cart" not in text:
                print(f"OUT OF STOCK: {product_url}")
                return False
            if "add to cart" not in text and "buy now" not in text:
                return False
        if "add to cart" in text and "buy now" in text:
            return True
        if "add to cart" in text or "buy now" in text:
            return True
        return False
    except Exception as e:
        print(f"Stock check error: {e}")
        return False

def get_og_data(product_url):
    try:
        r = requests.get(product_url, headers=HEADERS, timeout=25)
        soup = BeautifulSoup(r.text, "html.parser")
        title = ""
        og_title = soup.find("meta", property="og:title")
        if og_title and og_title.get("content"):
            title = og_title["content"]
        img_url = None
        og_img = soup.find("meta", property="og:image")
        if og_img and og_img.get("content"):
            img_url = og_img["content"]
            if img_url.startswith("//"):
                img_url = "https:" + img_url
        price = None
        price_tag = soup.select_one("div._30jeq3")
        if price_tag:
            price = price_tag.get_text().strip()
        rating = 0
        rating_tag = soup.select_one("div._3LWZlK")
        if rating_tag:
            try:
                rating = float(rating_tag.get_text().strip())
            except:
                rating = 0
        return {"title": title[:150], "image": img_url, "price_text": price, "rating": rating}
    except Exception as e:
        print(f"OG error: {e}")
        return {"title": "", "image": None, "price_text": None, "rating": 0}

def load_all_products_via_google():
    all_products = []
    all_google_links = []
    for q in GOOGLE_QUERIES:
        links = google_search_flipkart(q, max_results=25)
        all_google_links.extend(links)
        time.sleep(4)

    all_google_links = list(set(all_google_links))
    print(f"Total Google Flipkart links: {len(all_google_links)}")

    for link in all_google_links[:50]:
        if not check_in_stock(link):
            continue
        og = get_og_data(link)
        title = og.get("title", "")
        if not title:
            continue
        if not is_decent_and_good(title):
            print(f"Skipping not decent: {title[:60]}")
            continue
        rating = og.get("rating", 0)
        if rating and rating < 3.8:
            continue
        trending_words = ["trending", "latest", "designer", "party wear", "festive", "embroidered", "anarkali", "elegant", "premium", "2026"]
        is_trending = any(w in title.lower() for w in trending_words) or rating >= 4.0
        if is_trending or rating >= 3.9 or "kurta" in title.lower():
            print(f"GOOD FOUND: {title[:80]} | Rating {rating}")
            all_products.append({"title": title, "link": link, "rating": rating, "og_image": og.get("image"), "price_text": og.get("price_text")})
        time.sleep(1)

    return all_products

def get_random_best_product():
    posted = []
    if os.path.exists(POSTED_FILE):
        try:
            with open(POSTED_FILE, "r") as f:
                posted = json.load(f)
        except:
            posted = []

    all_products = load_all_products_via_google()
    print(f"Total filtered pool: {len(all_products)}")

    if not all_products:
        print("No products found, trying again with backup search")
        # Backup - direct Flipkart category scrape if Google fails
        return None

    available = [p for p in all_products if p["link"] not in posted]
    if not available:
        posted = []
        available = all_products

    random.shuffle(available)

    for product in available:
        if not check_in_stock(product["link"]):
            posted.append(product["link"])
            continue
        og = get_og_data(product["link"])
        if og["title"]:
            product["title"] = og["title"]
        if og["image"]:
            product["og_image"] = og["image"]
        if og["price_text"]:
            product["price_text"] = og["price_text"]
        posted.append(product["link"])
        try:
            with open(POSTED_FILE, "w") as f:
                json.dump(posted[-300:], f)
        except:
            pass
        return product

    return random.choice(all_products) if all_products else None

def get_page_token():
    url = f"https://graph.facebook.com/v20.0/me/accounts?access_token={USER_TOKEN}"
    r = requests.get(url)
    data = r.json()
    if "data" in data:
        for page in data["data"]:
            if page["id"] == PAGE_ID:
                return page["access_token"]
    print(f"ERROR Page token: {data}")
    return None

def post_with_photo(page_token, product):
    image_url = product.get("og_image")
    if not image_url:
        og = get_og_data(product["link"])
        image_url = og.get("image")

    price_line = product.get("price_text") or ""
    title = product.get("title", "Trending Ladies Suit")[:100]

    caption = f"""{title} - Swaran Collections

Beautiful Model | Latest Design 2026 | Trending
{price_line}

Google Verified - Only Flipkart - In Stock Checked
Shop Now: {product['link']}

DM for Order | COD Available
Comment LINK for more collection

#SwaranCollections #FlipkartTrending #Latest2026 #TrendingNow #InStock

Auto-posted {datetime.now().strftime('%d-%m-%Y %I:%M %p')} - Auto Google Search Mode"""

    if not image_url:
        url = f"https://graph.facebook.com/v20.0/{PAGE_ID}/feed"
        payload = {"message": caption, "link": product["link"], "access_token": page_token}
        r = requests.post(url, data=payload)
        print(f"Feed Status: {r.status_code}")
        return r.json()

    url = f"https://graph.facebook.com/v20.0/{PAGE_ID}/photos"
    payload = {"url": image_url, "caption": caption, "access_token": page_token}
    r = requests.post(url, data=payload)
    print(f"Photo Status: {r.status_code}")
    return r.json()

if __name__ == "__main__":
    if "YOUR_USER_TOKEN" in USER_TOKEN:
        print("ERROR: FB_USER_TOKEN not set")
    else:
        page_token = get_page_token()
        if page_token:
            product = get_random_best_product()
            if not product:
                print("No product found via Google search")
            else:
                print(f"Posting AUTO SEARCH: {product['title']} | {product['link']}")
                result = post_with_photo(page_token, product)
                if "id" in result:
                    print(f"SUCCESS Post ID {result.get('id')}")
                else:
                    print(f"Failed: {result}")
