import re
import pandas as pd

def rule5(url):
    # Check for special characters in the domain or path
    special_characters_pattern = r'[-_0-9@“,”;!+%]'  # Added additional characters
    non_standard_port_pattern = r':(?!80|443)(\d+)'  # Matches non-standard ports
    ip_address_pattern = r'http://\d{1,3}(?:\.\d{1,3}){3}(:\d+)?'  # Matches IP address URLs
    
    # Check for IP addresses
    if re.match(ip_address_pattern, url):
        return 1  # Potential phishing URL (IP address)
    
    # Check for special characters or non-standard ports
    if re.search(special_characters_pattern, url) or re.search(non_standard_port_pattern, url):
        return 1  # Potential phishing URL
    
    return 0  # Likely safe URL

# Test examples
test_urls = [
    "http://example-site.com/_login?user=admin;session=123",  # True
    "https://w6xvbucu6.top/",                                   # False
    "http://example.com:8080/home",                            # True
    "https://R2sBBM0e.go.jp@jbjampcejm.sbs/FisCNm",           # True (IP address)
    "http://valid-site.com/user_123",                          # True (underscore)
    "http://valid.com/login"                                   # False (standard)
]

# Create a DataFrame to store the results
results = []

# Collect results
for sno, url in enumerate(test_urls, start=1):
    score = rule5(url)
    results.append({'sno': sno, 'url': url, 'score': score})

# Convert the results to a DataFrame
df = pd.DataFrame(results)

# Display the DataFrame
print(df)