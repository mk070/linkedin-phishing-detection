import re
import pandas as pd

def rule4(url):
    """
    Check if the given URL is an IP address in decimal, hexadecimal, or octal format.
    
    Args:
        url (str): The URL to check.
    
    Returns:
        bool: True if the URL is an IP address, False otherwise.
    """
    
    # Remove protocol and trailing slashes from the URL
    url = url.split("//")[-1].split("/")[0].strip()
    
    # Check for decimal IP addresses (e.g., 192.168.1.1)
    decimal_ip_pattern = re.compile(
        r'^((25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$'
    )

    # Check for hexadecimal IP addresses (e.g., 0xC0A80101)
    hex_ip_pattern = re.compile(r'^0x[0-9A-Fa-f]{8}$')
    
    # Check for octal IP addresses (e.g., 0300.0250.0001.0001)
    octal_ip_pattern = re.compile(r'^(0[0-7]{3}\.){3}0[0-7]{3}$')
    
    # Check if the URL matches any of the patterns
    is_decimal_ip = bool(decimal_ip_pattern.match(url))
    is_hex_ip = bool(hex_ip_pattern.match(url))
    is_octal_ip = bool(octal_ip_pattern.match(url))
    
    return is_decimal_ip or is_hex_ip or is_octal_ip

def is_phishing_url(url):
    """
    Check if the given URL is potentially a phishing attack based on IP address detection.
    
    Args:
        url (str): The URL to check.
    
    Returns:
        int: Score indicating if the URL is potentially phishing (1) or safe (0).
    """
    
    # Return 1 for phishing (IP-based) and 0 for safe URLs
    return 1 if rule4(url) else 0

# Test Cases
test_urls = [
    "http://192.168.1.1",
    "http://0xC0A80101",
    "http://0300.0250.0001.0001",
    "http://example.com",
    "https://w6xvbucu6.top/",  # Invalid decimal IP
    "http://0xGHIJKL12",        # Invalid hexadecimal IP
    "http://123.045.067.089",   # Valid but unusual decimal IP
    "https://R2sBBM0e.go.jp@jbjampcejm.sbs/FisCNm",           # Valid decimal IP
]

# Prepare data for the DataFrame
data = [(index + 1, url, is_phishing_url(url)) for index, url in enumerate(test_urls)]

# Create a DataFrame
df = pd.DataFrame(data, columns=["S.No", "Testing URL", "Score"])

# Print the DataFrame
print(df)