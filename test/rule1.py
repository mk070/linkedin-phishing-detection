import requests
import pandas as pd
import re
from urllib.parse import urlparse

def check_url_availability(url):
    """Checks if the URL is accessible by sending a request."""
    try:
        response = requests.get(url, allow_redirects=True, timeout=5)
        return response.status_code in [200, 301, 302]  # Valid statuses
    except requests.exceptions.RequestException:
        return False  # URL is not accessible

def check_url_indexing(url):
    """Checks if a URL is indexed by search engines."""
    parsed_url = urlparse(url)
    domain = parsed_url.netloc
    search_engines = [
        f"https://www.google.com/search?q=site:{domain}",
        f"https://search.yahoo.com/search?p=site:{domain}",
        f"https://www.bing.com/search?q=site:{domain}"
    ]
    
    found_in_all = True  # Assume found until proven otherwise

    for engine in search_engines:
        try:
            response = requests.get(engine, headers={'User-Agent': 'Mozilla/5.0'}, timeout=5)
            if response.status_code == 200:
                # Check if domain is found in the response text
                if re.search(r'\b' + re.escape(domain) + r'\b', response.text):
                    print(f"URL found in: {engine}")  # Debugging
                else:
                    found_in_all = False  # URL not found in this search engine
                    print(f"URL not found in: {engine}")  # Debugging
            else:
                print(f"Error checking {engine}: Status code {response.status_code}")
                found_in_all = False  # Error in search engine check
        except requests.exceptions.RequestException as e:
            print(f"Error checking {engine}: {e}")
            found_in_all = False  # Error in search engine check
    
    return 0 if found_in_all else 1  # 0 for safe (found in all), 1 for phishing

def analyze_urls(urls):
    """Analyzes a list of URLs and returns a DataFrame with URLs and their Rule 1 scores."""
    results = []

    for url in urls:
        is_accessible = check_url_availability(url)
        Rule1_Score = check_url_indexing(url) if is_accessible else 1  # If not accessible, mark as phishing
        results.append({"URL": url, "Rule1_Score": Rule1_Score})

    return pd.DataFrame(results)

# Example Usage
urls_to_check = [
    "https://www.google.com",
    "http://example.net/path?param=value#fragment",
    "https://bit.ly/3ytgS48",  # Example shortened URL
    "https://this-website-probably-does-not-exist.com",
    "https://download.vidshare.site/download/page/86440",
    "http://www.github.com",
    "http://httpbin.org/redirect/3"
]

# Analyzing the URLs and getting the DataFrame
url_scores_df = analyze_urls(urls_to_check)
print(url_scores_df)
