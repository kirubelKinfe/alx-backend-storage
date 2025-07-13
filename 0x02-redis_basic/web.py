"""
This module provides a function to fetch and cache web pages using Redis, tracking the number of times each URL is accessed.
The cache expires after 10 seconds. Decorators are used to implement caching and access counting.
"""
#!/usr/bin/env python3
import redis
import requests
from typing import Callable
from functools import wraps

# Initialize Redis client
redis_client = redis.Redis()

def count_access(method: Callable) -> Callable:
    """Return a decorator that counts how many times a URL is accessed by incrementing a Redis key."""
    @wraps(method)
    def wrapper(url: str) -> str:
        """Increment the access count for the given URL and call the original method."""
        count_key = f"count:{url}"
        redis_client.incr(count_key)
        return method(url)
    return wrapper

def cache_page(method: Callable) -> Callable:
    """Return a decorator that caches the HTML content of a URL in Redis for 10 seconds and counts access only on cache miss."""
    @wraps(method)
    def wrapper(url: str) -> str:
        """Return the cached page if available, otherwise fetch, cache, and return the page, incrementing the access count only on cache miss."""
        cache_key = f"cache:{url}"
        count_key = f"count:{url}"
        cached_content = redis_client.get(cache_key)
        if cached_content is not None:
            if isinstance(cached_content, bytes):
                return cached_content.decode("utf-8")
            return str(cached_content)
        # Only increment count if not cached
        redis_client.incr(count_key)
        content = method(url)
        # Ensure content is stored as bytes
        if isinstance(content, str):
            redis_client.setex(cache_key, 10, content.encode("utf-8"))
            return content
        else:
            redis_client.setex(cache_key, 10, content)
            return content.decode("utf-8") if isinstance(content, bytes) else str(content)
    return wrapper

@cache_page
def get_page(url: str) -> str:
    """Fetch the HTML content of the specified URL using requests and return it as a string."""
    response = requests.get(url)
    return response.text