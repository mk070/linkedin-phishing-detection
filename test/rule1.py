import requests
from urllib.parse import urlparse
import socket

def check_url(url, max_redirects=5):
    """Checks a URL for various safety indicators, including redirects, 
    status codes, URL shorteners, domain information, and attempts 
    a basic search engine indexing check (unreliable).

    Args:
        url: The URL to check.
        max_redirects: Maximum number of redirects to follow.

    Returns:
        str: A message indicating whether the URL appears safe or suspicious 
             along with a brief explanation. 
    """
    try:
        response = requests.get(url, allow_redirects=True, timeout=5)

        print(f"URL: {url}")

        # --- Redirection Check ---
        if response.history:
            print(f"Request was redirected {len(response.history)} times:")
            for i, resp in enumerate(response.history):
                print(f"  {i+1}. Status: {resp.status_code}, URL: {resp.url}")
            print(f"Final Destination: Status: {response.status_code}, URL: {response.url}")
        else:
            print(f"Request was not redirected: Status: {response.status_code}, URL: {response.url}")

        # --- Basic Safety Checks ---
        safety_concerns = []

        # 1. Status Code Check
        if response.status_code not in [200, 301, 302]:
            safety_concerns.append(f"Unusual status code: {response.status_code}")

        # 2. URL Shortener Check (not foolproof)
        shorteners = ["bit.ly", "tinyurl.com", "ow.ly", "goo.gl"] 
        if any(shortener in response.url for shortener in shorteners):
            safety_concerns.append("URL uses a URL shortening service.")

        # 3. Domain Information
        try:
            parsed_url = urlparse(response.url)
            ip_address = socket.gethostbyname(parsed_url.hostname)
            print(f"IP Address: {ip_address}") 
        except socket.gaierror:
            safety_concerns.append("Unable to resolve domain to IP address.")

        # --- Search Engine Indexing Check (Unreliable) ---
        search_engines = ["https://www.google.com/search?q=site:",
                          "https://search.yahoo.com/search?p=site:",
                          "https://www.bing.com/search?q=site:"]

        for engine in search_engines:
            search_url = f"{engine}{parsed_url.netloc}"
            try:
                response = requests.get(search_url, headers={'User-Agent': 'Mozilla/5.0'})
                if response.status_code == 200:
                    if url in response.text: 
                        print(f"URL found in index of: {engine}") 
                    else:
                        print(f"URL not found in initial results of: {engine}")
                else:
                    print(f"Error checking {engine}: Status code {response.status_code}")
            except Exception as e:
                print(f"Error checking {engine}: {e}")

        # --- Safety Assessment Message ---
        if safety_concerns:
            return f"Suspicious URL! Concerns:\n  - {'; '.join(safety_concerns)}"
        else:
            return "This URL appears safe to proceed with, but exercise caution."

    except requests.exceptions.RequestException as e:
        return f"Error checking URL: {e}"

# Example Usage:
urls_to_check = [
    "https://snsihub.ai/",
    "http://example.net/path?param=value#fragment",
    "https://bit.ly/3ytgS48", 
    "https://this-website-probably-does-not-exist.com",
    "https://download.vidshare.site/download/page/86440",
    "http://www.github.com",
    "http://httpbin.org/redirect/3"
]

for someurl in urls_to_check:
    assessment = check_url(someurl)
    print(assessment) 
    print("-" * 40)