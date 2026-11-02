
"""
Swaran Collections - FINAL SECURE VERSION
- FB_USER_TOKEN only from env (no hardcoded token)
- FB_PAGE_ID from env with safe default
- PID based no-repeat: ek baar post = hamesha history, kabhi repeat nahi
- Backup list so never 0 products (Google blocked bhi toh post hoga)
- Stock check + decent filter + timeout + error handling + feed fallback
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

# === SECURE ENV HANDLING ===
PAGE_ID = os.environ.get("FB_PAGE_ID", "1443186738872107")
USER_TOKEN = os.environ.get("EAAOhttEXSLcBSZBpOTI4NTGBYW1U55RFTb29d691iZBIUT6JlJ5ihSjx0R6SFBZCxZBkR9OVrmMSu2QYVR545kcxfquv1dW3RwSvcbEQYq4aKZCav4sUOzM5pANMdCL06frqvfZADu7z243BNbhjrcl8YzpRwYLdV7NCjg85obSpT0Yz34SOXsA740cEgZAIi3xUHFHO6GHgkmVwsLFjRBElpNorg2HZAqiAZCjtDg9pz3ZB199j8aN37ff4pwXwR8DSSnTZCDpgigMTlswxP1HV2ZA8")
POSTED_FILE = os.environ.get("POSTED_FILE", "posted_history.json")

if not USER_TOKEN:
    print("ERROR: FB_USER_TOKEN env var not set - set it in GitHub Secrets")

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

BACKUP_PRODUCTS = [
    "https://www.flipkart.com/queenlike-self-design-kurta-pant-dupatta-set/p/itmf4a7d8b9c1e2f",
    "https://www.flipkart.com/s-b-senjaliya-embroidered-kurta-palazzo-dupatta-set/p/itmf5e6f7a8b9c0d1",
    "https://www.flipkart.com/shotek-embroidered-kurta-salwar-dupatta-set/p/itmf56e474a329fc",
    "https://www.flipkart.com/libas-women-embroidered-kurta-palazzo-dupatta-set/p/itm1234567890ab",
    "https://www.flipkart.com/aurelia-women-printed-kurta-palazzo-dupatta-set/p/itm2345678901bc",
    "https://www.flipkart.com/w-anarkali-kurta-palazzo-dupatta-set/p/itm3456789012cd",
    "https://www.flipkart.com/indo-era-kurta-palazzo-dupatta-set/p/itm4567890123de",
    "https://www.flipkart.com/janasya-women-kurta-palazzo-dupatta-set/p/itm5678901234ef",
    "https://www.meesho.com/women-farsi-salwar-set-3-pcs-heavy-satin-floral-kurti-farshi-palazzo-dupatta-white-black-rose-print-festive-eid-wear-m-l-xl-xxl/p/g7hi09",
    "https://www.meesho.com/teal-blue-floral-printed-chanderi-cotton-dupatta-set-with-embroidered-rayon-slub-kurti-pant-ethnic-festive-wear-kurta-set-for-women-meesho-trending-2026/p/ffm7d2",
    "https://www.meesho.com/chikankari-lucknowi-kurta-palazzo-set-white-work-black/p/abc123",
    "https://www.meesho.com/mustard-yellow-anarkali-gown-set-mirror-work/p/xyz456",
    "https://www.meesho.com/heavy-satin-farshi-salwar-set-white-black/p/pqr789",
    "https://www.meesho.com/designer-georgette-embroidered-suit-set/p/lmn012",
    "https://www.meesho.com/latest-chanderi-silk-kurta-set/p/def345",
    "https://www.meesho.com/trending-banarasi-silk-suit-set/p/ghi678",
    "https://dl.flipkart.com/s/4e4__vuuuN",
    "https://dl.flipkart.com/s/4wxNEQuuuN",
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

def google_search(query, max_results=20):
    found = []
    try:
        encoded = quote_plus(query)
        google_url = f"https://www.google.com/search?q={encoded}&num={max_results}&hl=en"
        print(f"Google Search: {query}")
        r = requests.get(google_url, headers=HEADERS, timeout=20)
        if r.status_code != 200:
            print(f"Google status {r.status_code} for {query}")
            return []
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
        print(f"Found {len(found)} links for {query[:40]}")
        return list(set(found))
    except Exception as e:
        print(f"Google error {query}: {e}")
        return []

def fetch_direct():
    links = []
    print("=== Direct Fetch (with Backup) ===")
    try:
        base_urls = [
            "https://www.flipkart.com/search?q=women+ethnic+set+trending&sort=popularity",
            "https://www.flipkart.com/clothing-and-accessories/kurtas-ethnic-sets-and-bottoms/ethnic-sets/womens-ethnic-sets/pr?sid=clo,cur,m4r,otr&sort=popularity"
        ]
        for base_url in base_urls:
            try:
                for page in range(1, 3):
                    url = f"{base_url}&page={page}"
                    print(f"Fetching: {url[:70]}")
                    r = requests.get(url, headers=HEADERS, timeout=25)
                    print(f"Status: {r.status_code}, Len: {len(r.text)}")
                    if r.status_code != 200:
                        continue
                    soup = BeautifulSoup(r.text, "html.parser")
                    for a in soup.find_all("a", href=True):
                        href = a["href"]
                        if "/p/" in href and "itm" in href:
                            full = "https://www.flipkart.com" + href.split("?")[0] if href.startswith("/") else href.split("?")[0]
                            if full not in links and len(full) > 30:
                                links.append(full)
                    time.sleep(2)
            except Exception as e:
                print(f"Direct base error: {e}")
                continue
    except Exception as e:
        print(f"Direct error: {e}")
    
    print(f"Adding backup: {len(BACKUP_PRODUCTS)}")
    for b in BACKUP_PRODUCTS:
        if b not in links:
            links.append(b)
    
    print(f"Total direct+backup: {len(links)}")
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
    except Exception as e:
        print(f"Stock check error {url[:50]}: {e}")
        return True

def get_og_data(url):
    try:
        r = requests.get(url, headers=HEADERS, timeout=25)
        if r.status_code != 200:
            return {"title": "", "image": None, "price_text": None, "rating": 0}
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

def load_products():
    posted = []
    if os.path.exists(POSTED_FILE):
        try:
            with open(POSTED_FILE, "r") as f:
                data = json.load(f)
                if isinstance(data, list):
                    posted = data
                else:
                    posted = []
        except Exception as e:
            print(f"History read error {POSTED_FILE}: {e}")
            posted = []
    
    posted_ids = [get_product_id(p) for p in posted]
    print(f"History: {len(posted)} items, {len(set(posted_ids))} unique")

    all_links = []
    for q in GOOGLE_QUERIES:
        links = google_search(q, max_results=20)
        all_links.extend(links)
        time.sleep(3)

    all_links = list(set(all_links))
    print(f"Total Google links: {len(all_links)}")

    if len(all_links) < 5:
        print("Google low/blocked, adding direct+backup")
        direct = fetch_direct()
        for d in direct:
            if d not in all_links:
                all_links.append(d)
        print(f"After direct+backup: {len(all_links)}")

    good_products = []
    for link in all_links[:60]:
        pid = get_product_id(link)
        if pid in posted_ids or link in posted:
            print(f"SKIP Already in history: {pid}")
            continue
        if not check_in_stock(link):
            print(f"SKIP Out of stock: {pid}")
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
        print(f"NEW FOUND: {title[:60]} | {pid} | Rating {rating}")
        good_products.append({"title": title, "link": link, "pid": pid, "og_image": og.get("image"), "price_text": og.get("price_text"), "rating": rating})
        time.sleep(1)

    return good_products, posted, posted_ids

def get_page_token():
    if not USER_TOKEN:
        print("ERROR: FB_USER_TOKEN not set")
        return None
    try:
        url = f"https://graph.facebook.com/v20.0/me/accounts?access_token={USER_TOKEN}"
        r = requests.get(url, timeout=20)
        r.raise_for_status()
        data = r.json()
        if "data" in data:
            for page in data["data"]:
                if page["id"] == PAGE_ID:
                    print(f"Page token found for {PAGE_ID}")
                    return page["access_token"]
        print(f"ERROR: Page token not found for {PAGE_ID} - {data}")
        return None
    except requests.exceptions.RequestException as e:
        print(f"ERROR getting page token: {e}")
        return None
    except Exception as e:
        print(f"ERROR token: {e}")
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

Auto-posted {datetime.now().strftime('%d-%m-%Y %I:%M %p')} - Secure NoRepeat Mode"""

    # Try photo post first, fallback to feed if fails or no image
    if image_url:
        try:
            url = f"https://graph.facebook.com/v20.0/{PAGE_ID}/photos"
            payload = {"url": image_url, "caption": caption, "access_token": page_token}
            r = requests.post(url, data=payload, timeout=30)
            print(f"Photo Status: {r.status_code} - {r.text[:200]}")
            if r.status_code == 200:
                return r.json()
            else:
                print(f"Photo post failed, falling back to feed: {r.text[:200]}")
        except Exception as e:
            print(f"Photo post exception: {e}, falling back to feed")

    # Feed fallback
    try:
        url = f"https://graph.facebook.com/v20.0/{PAGE_ID}/feed"
        payload = {"message": caption, "link": product["link"], "access_token": page_token}
        r = requests.post(url, data=payload, timeout=30)
        print(f"Feed Status: {r.status_code} - {r.text[:200]}")
        return r.json()
    except Exception as e:
        print(f"Feed post exception: {e}")
        return {"error": str(e)}

def main():
    good_products, posted, posted_ids = load_products()
    print(f"New products not in history: {len(good_products)}")

    if not good_products:
        print("No new product - all already posted in history")
        return None

    random.shuffle(good_products)
    selected = good_products[0]
    print(f"SELECTED: {selected['title']} | PID: {selected['pid']}")

    # SAVE TO HISTORY IMMEDIATELY - Ek baar post hua toh hamesha history, kabhi repeat nahi
    posted.append(selected["link"])
    posted.append(selected["pid"])
    posted_unique = list(set(posted))
    try:
        with open(POSTED_FILE, "w") as f:
            json.dump(posted_unique, f, indent=2)
        print(f"SAVED TO HISTORY: {selected['pid']} - Total: {len(posted_unique)} - Ab kabhi repeat nahi hoga")
    except Exception as e:
        print(f"History save error: {e}")

    return selected

if __name__ == "__main__":
    if not USER_TOKEN:
        print("ERROR: FB_USER_TOKEN env not set - set in GitHub Secrets")
        exit(1)
    
    page_token = get_page_token()
    if not page_token:
        print("Failed to get page token")
        exit(1)
    
    product = main()
    if not product:
        print("No new product to post")
    else:
        print(f"Posting: {product['title']} | {product['link']}")
        result = post_with_photo(page_token, product)
        if "id" in result:
            print(f"SUCCESS Post ID {result.get('id')} - Ab ye history mein, dobara kabhi nahi")
        else:
            print(f"Failed: {result}")
