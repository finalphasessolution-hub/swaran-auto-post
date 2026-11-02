"""Swaran Collections Facebook auto-poster.

Safety rules:
- Credentials must come from environment variables / GitHub Secrets.
- A product is recorded only after Facebook confirms a successful post.
- Previously used URLs/product IDs are never silently cleared when exhausted.
- Links that cannot be checked are skipped rather than posted blindly.
"""

import json
import os
import random
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlparse, urlunparse

import requests
from bs4 import BeautifulSoup

GRAPH_VERSION = "v20.0"
PAGE_ID = os.environ.get("FB_PAGE_ID", "").strip()
USER_TOKEN = os.environ.get("FB_USER_TOKEN", "").strip()
POSTED_FILE = Path(os.environ.get("POSTED_FILE", "posted_history.json"))
ALLOWED_DOMAINS = {"flipkart.com", "meesho.com"}
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36"
    )
}

# These are the supplied candidate listings. Price, rating, discount and delivery
# details are user-provided and are NOT independently verified by this script.
# The two conflicting Meesho entries that used the exact same URL were removed
# from this candidate list until their product/link match can be confirmed.
PRODUCTS = [
    {
        "title": "S B Senjaliya Embroidered Kurta Palazzo Dupatta - Pink",
        "price": "₹696", "mrp": 2499, "sale_price": 696,
        "rating": 3.9, "reviews": 166, "delivery": "One Day Delivery",
        "trending": True, "category": "ladies_suit",
        "link": "https://dl.flipkart.com/s/4wxNEQuuuN",
        "hashtags": "#SwaranCollections #PinkSuit #ViralSuit",
        "caption": "✨ Pink Embroidered Palazzo Set ✨\nS B Senjaliya - Festive Party Wear",
    },
    {
        "title": "QUEENLIKE Self Design Kurta Pant Dupatta Set - Red",
        "price": "₹719", "mrp": 2799, "sale_price": 719,
        "rating": 3.8, "reviews": 281, "delivery": "One Day Delivery",
        "trending": True, "category": "ladies_suit",
        "link": "https://dl.flipkart.com/s/4e4__vuuuN",
        "hashtags": "#SwaranCollections #RedSuit #FestiveWear",
        "caption": "✨ Queenlike Self Design Kurta Set - Red ✨\nFestive & Party Wear",
    },
    {
        "title": "Teal Blue Chanderi Cotton Kurta Pant Dupatta Set",
        "price": "₹899", "mrp": 2999, "sale_price": 899,
        "rating": 4.2, "reviews": 450, "delivery": "One Day Delivery",
        "trending": True, "category": "ladies_suit",
        "link": "https://www.meesho.com/teal-blue-floral-printed-chanderi-cotton-dupatta-set-with-embroidered-rayon-slub-kurti-pant-ethnic-festive-wear-kurta-set-for-women-meesho-trending-2026/p/ffm7d2",
        "hashtags": "#SwaranCollections #TealSuit #Chanderi",
        "caption": "✨ Teal Blue Chanderi Kurta Set ✨\nFestive Ethnic Wear",
    },
    {
        "title": "Black Chikankari Lucknowi Kurta Palazzo - White Work",
        "price": "₹849", "mrp": 2799, "sale_price": 849,
        "rating": 4.4, "reviews": 512, "delivery": "One Day Delivery",
        "trending": True, "category": "ladies_suit",
        "link": "https://www.flipkart.com/shotek-embroidered-kurta-salwar-dupatta-set/p/itmf56e474a329fc",
        "hashtags": "#SwaranCollections #Chikankari #Lucknowi",
        "caption": "✨ Black & White Chikankari Kurta Set ✨\nLucknowi Style",
    },
]


def host_is_allowed(url):
    try:
        host = (urlparse(url).hostname or "").lower().rstrip(".")
        return any(host == domain or host.endswith("." + domain) for domain in ALLOWED_DOMAINS)
    except Exception:
        return False


def normalize_url(url):
    """Normalize a URL for comparison, ignoring query/fragment and trailing slash."""
    try:
        parsed = urlparse(str(url).strip())
        if parsed.scheme.lower() not in {"http", "https"} or not parsed.hostname:
            return ""
        host = parsed.hostname.lower().rstrip(".")
        path = re.sub(r"/+", "/", parsed.path or "/").rstrip("/") or "/"
        return urlunparse(("https", host, path, "", "", ""))
    except Exception:
        return ""
