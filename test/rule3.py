import pandas as pd

def check_phishing_keywords(urls, keywords):
    # Initialize results dictionary
    results = {}

    # Check each URL against the keywords
    for url in urls:
        matched = 0
        for keyword in keywords:
            if keyword in url:
                matched = 1
                break  # Stop checking further if a match is found
        results[url] = matched  # Assign score (1 for match, 0 for no match)

    return results

# Define the dataset of phishing keywords
keywords = [
    # Account Management
    "login", "secure", "account", "signin", "credentials", "password", "reset", "update", "confirm", "verification", "safety", "suspicious",

    # Urgency and Offers
    "free", "gift", "prize", "urgent", "immediate", "act now", "limited time", "exclusive",

    # Action Words
    "click", "here", "download", "access", "install", "open", "submit", "request", "claim", "verify",

    # Financial and Transactional Terms
    "banking", "payment", "invoice", "shipping", "transaction", "refund", "transfer", "credit", "debit",

    # Miscellaneous
    "support", "customer service", "update your info", "account activity", "security alert", "breach", "suspicious activity",
    "unauthorized", "reset your password", "new message", "terms and conditions", "click to win", "winner",
]

def analyze_urls(urls):
    results = []

    # Get scores from phishing keyword analysis
    scores = check_phishing_keywords(urls, keywords)

    # Create results list
    for url in urls:
        results.append({"URL": url, "Score": scores[url]})

    return pd.DataFrame(results)

# List of URLs to check
urls_to_check = [
    "https://example.com/login",
    "https://secure-site.com/account/update",
    "https://safe-domain.com/home",
    "https://phishing-site.com/free-gift",
    "https://another-secure.com/verify",
    "https://not-phishing.com/services",
    "https://www.bankofamerica.com/login",
    "https://www.chase.com/account/update",
    "https://www.paypal.com/signin",
    "https://www.wellsfargo.com/secure/verify",
    "https://www.kaggle.com/",
    "https://www.genpact.com/contact-us",
    "https://snsct.org/"
]

# Analyze URLs and print the DataFrame
url_scores_df = analyze_urls(urls_to_check)
print(url_scores_df)