
"""
Swaran Collections - FINAL - EK BAAR POST = HAMESHA HISTORY - KABHI REPEAT NAHI
Rule: Ek baari post ho jaye toh posted_history.json mein chala jaye, dobara kabhi post na ho
"""

import requests
import random
import os
import json
import time
import re
from datetime import datetime
from bs4 import BeautifulSoup
from urllib.parse import parse_qs, urlparse, quote_plus

PAGE_ID = "1443186738872107"
USER_TOKEN = os.environ.get("FB_USER_TOKEN", "EAAOhttEXSLcBS238P802PESYYCLhLkiIOdNwIifJUNCTKsoyUu0liOBT9zd87vQEaN7rjwmTTS7G0Ms9bDWJr2NvQSkUIWAVfcMKHlBJHrcoqCb7cplGNhwsm9Lfe82dJ1ORNKKEkA6D6GIatXQqaiZB8K7BVTcWDwHaop7m8q9DkKlkYe9wxFoijdHpTtaP9qoezq3jD48u5GeVczCVHS0ly1WZAr")

POSTED_FILE = "posted_history.json"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/122.0.0.0 Safari/537.36",
    "Accept-Language": "en-US,en;q=0.9"
}

GOOGLE_QUERIES = [
    "site:flipkart.com women ethnic set trending latest design 2026",
    "site:flipkart.com ladies kurta palazzo latest",
    "site:flipkart.com designer party wear suit trending",
    "site:meesho.com women ethnic set trending latest design 2026",
    "site:meesho.com ladies kurta palazzo suit latest",
    "site:meesho.com designer party wear suit trending 2026"
]

def get_product_id(url):
    try:
        match = re.search(r'(itmf[a-z0-9]+|itm[a-z0-9]+)', url.lower())
        if match:
            return match.group(1)
        if "/p/" in url:
            parts = url.split("/p/")
            if len(parts) > 1:
                pid = parts[1].split("/")[0].split("?")[0][:40]
                return pid.lower()
        return url.split("?")[0].split("#")[0].lower()
    except:
        return url.lower()

def is_decent_and_good(title):
    t = title.lower()
    dirty = ["bikini", "lingerie", "bralette", "transparent", "mini skirt", "shorts", "bra", "panty", "innerwear", "nighty", "swimsuit"]
    if any(k in t for k in dirty):
        return False
    good = ["kurta", "suit", "salwar", "palazzo", "dupatta", "anarkali", "ethnic", "sharara", "gown", "embroidered", "self design", "chanderi", "silk", "cotton", "festive", "party wear", "elegant", "designer"]
    if not any(k in t for k in good):
        return False
    return True

def google_search(query, max_results=25):
    found = []
    try:
        encoded = quote_plus(query)
        google_url = f"https://www.google.com/search?q={encoded}&num={max_results}&hl=en"
        print(f"Google Search: {query}")
        r = requests.get(google_url, headers=HEADERS, timeout=20)
        soup = BeautifulSoup(r.text, "html.parser")
        for a in soup.find_all("a", href=True):
            href = a["href"]
            actual = ""
            if "/url?q=" in href:
                try:
                    parsed = urlparse(href)
                    qs = parse_qs(parsed.query)
                    if "q" in qs:
                        actual = qs["q"][0]
                except:
                    continue
            elif href.startswith("https://www.flipkart.com") or href.startswith("https://www.meesho.com"):
                actual = href
            else:
                continue
            if (("flipkart.com" in actual) or ("meesho.com" in actual)) and "/p/" in actual:
                actual = actual.split("?")[0].split("&")[0].split("#")[0]
                if actual not in found and len(actual) > 30:
                    found.append(actual)
        print(f"Found {len(found)} links")
        return list(set(found))
    except Exception as e:
        print(f"Google error: {e}")
        return []

def fetch_direct():
    links = []
    try:
        # Flipkart direct
        base = "https://www.flipkart.com/clothing-and-accessories/kurtas-ethnic-sets-and-bottoms/ethnic-sets/womens-ethnic-sets/pr?sid=clo,cur,m4r,otr&sort=popularity"
        for page in range(1, 3):
            url = f"{base}&page={page}"
            print(f"Direct Flipkart page {page}")
            r = requests.get(url, headers=HEADERS, timeout=20)
            soup = BeautifulSoup(r.text, "html.parser")
            for a in soup.find_all("a", href=True):
                href = a["href"]
                if "/p/" in href and "itm" in href:
                    full = "https://www.flipkart.com" + href.split("?")[0]
                    if full not in links:
                        links.append(full)
            time.sleep(2)
        # Meesho direct
        try:
            meesho_url = "https://www.meesho.com/suits-sets/pl/3k0"
            print("Direct Meesho")
            r = requests.get(meesho_url, headers=HEADERS, timeout=20)
            soup = BeautifulSoup(r.text, "html.parser")
            for a in soup.find_all("a", href=True):
                href = a["href"]
                if "/p/" in href and "meesho.com" in href:
                    full = href.split("?")[0]
                    if full not in links:
                        links.append(full)
        except:
            pass
    except Exception as e:
        print(f"Direct error: {e}")
    return list(set(links))

def check_in_stock(url):
    try:
        if "meesho.com" in url:
            r = requests.get(url, headers=HEADERS, timeout=20)
            txt = r.text.lower()
            if "out of stock" in txt or "sold out" in txt:
                return False
            return True
        r = requests.get(url, headers=HEADERS, timeout=20)
        txt = r.text.lower()
        if "out of stock" in txt or "sold out" in txt:
            if "notify me" in txt and "add to cart" not in txt:
                return False
            if "add to cart" not in txt and "buy now" not in txt:
                return False
        if "add to cart" in txt or "buy now" in txt:
            return True
        return False
    except:
        return False

def get_og_data(url):
    try:
        r = requests.get(url, headers=HEADERS, timeout=25)
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
    except:
        return {"title": "", "image": None, "price_text": None, "rating": 0}

def load_products():
    # Step 1: Read posted history - EK BAAR POST HUA TOH HAMESHA KE LIYE HISTORY MEIN
    posted = []
    if os.path.exists(POSTED_FILE):
        try:
            with open(POSTED_FILE, "r") as f:
                posted = json.load(f)
        except:
            posted = []
    
    posted_ids = [get_product_id(p) for p in posted]
    print(f"Already posted in history: {len(posted)} items, {len(set(posted_ids))} unique products")

    # Step 2: Google se naye products lao
    all_links = []
    for q in GOOGLE_QUERIES:
        links = google_search(q, max_results=20)
        all_links.extend(links)
        time.sleep(3)

    all_links = list(set(all_links))
    print(f"Total Google links: {len(all_links)}")

    if len(all_links) == 0:
        print("Google blocked, direct fetch")
        all_links = fetch_direct()
        print(f"Direct links: {len(all_links)}")

    # Step 3: Filter - sirf wohi jo history mein nahi hai
    good_products = []
    for link in all_links[:60]:
        pid = get_product_id(link)
        # EK BAAR POST HUA TOH KABHI DOBARA NAHI
        if pid in posted_ids or link in posted:
            print(f"SKIPPING - Already in history: {pid}")
            continue
        
        if not check_in_stock(link):
            print(f"SKIPPING - Out of stock: {pid}")
            continue
        
        og = get_og_data(link)
        title = og.get("title", "")
        if not title:
            continue
        if not is_decent_and_good(title):
            continue
        
        rating = og.get("rating", 0)
        if rating and rating < 3.8:
            continue
        
        print(f"NEW PRODUCT FOUND (not in history): {title[:60]} | {pid}")
        good_products.append({"title": title, "link": link, "pid": pid, "og_image": og.get("image"), "price_text": og.get("price_text"), "rating": rating})
        time.sleep(1)

    return good_products, posted, posted_ids

def main():
    # Load and filter
    good_products, posted, posted_ids = load_products()
    print(f"New products available (not in history): {len(good_products)}")

    if not good_products:
        print("Koi naya product nahi mila jo history mein na ho - saare post ho chuke hain")
        print("History clear karni padegi ya naye products ka wait karna padega")
        return None

    # Random ek product chuno jo history mein nahi hai
    random.shuffle(good_products)
    selected = good_products[0]
    
    print(f"SELECTED NEW PRODUCT: {selected['title']} | PID: {selected['pid']}")

    # TURANT HISTORY MEIN DAAL DO - EK BAARI POST HUA TOH DOBARA KABHI NAHI
    posted.append(selected["link"])
    posted.append(selected["pid"])
    # Unique banao
    posted_unique = list(set(posted))
    
    try:
        with open(POSTED_FILE, "w") as f:
            json.dump(posted_unique, f, indent=2)
        print(f"SAVED TO HISTORY: {selected['pid']} - Ab kabhi repeat nahi hoga. Total history: {len(posted_unique)}")
    except Exception as e:
        print(f"History save error: {e}")

    return selected

def get_page_token():
    url = f"https://graph.facebook.com/v20.0/me/accounts?access_token={USER_TOKEN}"
    r = requests.get(url)
    data = r.json()
    if "data" in data:
        for page in data["data"]:
            if page["id"] == PAGE_ID:
                return page["access_token"]
    print(f"ERROR token: {data}")
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

Google Verified - Only Flipkart/Meesho - In Stock
Shop Now: {product['link']}

DM for Order | COD Available
Comment LINK for more

#SwaranCollections #FlipkartTrending #MeeshoTrending #Latest2026 #TrendingNow #InStock #NoRepeat

Auto-posted {datetime.now().strftime('%d-%m-%Y %I:%M %p')} - Ek Baar Post = Hamesha History"""

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
            product = main()
            if not product:
                print("No new product to post - all already in history")
            else:
                print(f"Posting: {product['title']} | {product['link']}")
                result = post_with_photo(page_token, product)
                if "id" in result:
                    print(f"SUCCESS Post ID {result.get('id')} - Ab ye history mein chala gaya, dobara kabhi nahi ayega")
                else:
                    print(f"Failed: {result}")
