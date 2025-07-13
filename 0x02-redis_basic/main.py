#!/usr/bin/env python3
"""
Demonstration script for the advanced web cache and tracker in web.py.
Fetches a URL, prints the content, and shows how many times the URL was actually fetched (not served from cache).
"""
from web import get_page
import redis

url = "http://slowwly.robertomurray.co.uk/delay/3000/url/https://www.example.com/"

print("Fetching page...")
content = get_page(url)
print("Page content (truncated to 200 chars):\n", content[:200], "...\n")

r = redis.Redis()
count = r.get(f"count:{url}")
if isinstance(count, bytes):
    count = int(count.decode("utf-8"))
else:
    count = 0
print(f"URL '{url}' was fetched {count} time(s) from the web (not cache).") 