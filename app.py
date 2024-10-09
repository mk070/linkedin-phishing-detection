import os
import pandas as pd
import re
import shutil
import zipfile
import csv
import requests
from urllib.parse import urlparse
import socket
import time
import pickle
from datetime import datetime
from seleniumbase import Driver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.common.exceptions import TimeoutException, ElementClickInterceptedException
from final_check import analyze_urls

def print_colored(text, color):
    colors = {
        "green": "\033[92m",
        "red": "\033[91m",
        "yellow": "\033[93m",
        "reset": "\033[0m",
    }
    print(f"{colors[color]}{text}{colors['reset']}")

def loading_animation(message):
    print(message, end='', flush=True)
    for _ in range(3):
        print('.', end='', flush=True)
        time.sleep(1)
    print()

def check_internet_connection(url="https://www.google.com", timeout=5):
    while True:
        try:
            requests.get(url, timeout=timeout)
            print_colored("Internet connection is active.", "green")
            return True
        except requests.ConnectionError:
            print_colored("No internet connection. Retrying in 10 seconds...", "yellow")
            time.sleep(10)

def ensure_csv_headers(file_path, headers):
    file_exists = os.path.exists(file_path)
    if not file_exists or os.path.getsize(file_path) == 0:
        with open(file_path, 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(headers)

output_dir = 'output'
os.makedirs(output_dir, exist_ok=True)

output_csv_path = os.path.join(output_dir, 'login_status.csv')
required_headers = ['username', 'login_time', 'status', 'error_message']

ensure_csv_headers(output_csv_path, required_headers)

def log_login_status(username, status, error_message=''):
    with open(output_csv_path, 'a', newline='') as file:
        writer = csv.writer(file)
        login_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        writer.writerow([username, login_time, status, error_message])

def is_user_logged_in(username):
    cookie_file = f"cookies/{username}_cookies.pkl"
    if os.path.exists(cookie_file):
        print_colored(f"Cookies found for {username}, skipping login.", "yellow")
        return True

    if os.path.exists(output_csv_path) and os.path.getsize(output_csv_path) > 0:
        with open(output_csv_path, 'r') as file:
            reader = csv.DictReader(file)
            for row in reader:
                if row.get('username') == username and row.get('status') == 'Success':
                    print_colored(f"{username} already has a successful login in the login_status.csv, skipping login.", "yellow")
                    return True
    return False

# function to check rule-1
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

def extract_link(file_path):


  # Load your CSV file
  df = pd.read_csv(file_path)

  # Function to extract usernames and links from the 'CONTENT' column
  def extract_usernames_links(content):
      # Regex pattern to capture any URL in the content
      pattern = r'(https?://[^\s<>"\']+)'
      matches = re.findall(pattern, content)
      return matches

  # Apply the function to the 'CONTENT' column
  df['USERNAMES_AND_LINKS'] = df['CONTENT'].apply(lambda x: extract_usernames_links(str(x)))

  # Filter out empty lists
  links = [link for link in df['USERNAMES_AND_LINKS'] if link]
  flat_list = [link for sublist in links for link in sublist]

  # Print the final list of links
  return flat_list

def export_linkedin_data(driver, username):
    try:
        # Open LinkedIn Data Export page
        driver.get("https://www.linkedin.com/mypreferences/d/download-my-data")

        # Switch to the iframe containing the export settings
        WebDriverWait(driver, 30).until(
            EC.frame_to_be_available_and_switch_to_it((By.CSS_SELECTOR, "iframe.settings-iframe--frame"))
        )
        print_colored("Switched to the iframe containing the data export settings.", "green")

        # Wait for the download button to become clickable
        try:
            WebDriverWait(driver, 600).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "button.download-btn"))
            )
            download_button = driver.find_element(By.CSS_SELECTOR, "button.download-btn")

            # Ensure that the button is not disabled
            if download_button.is_enabled():
                print_colored("Download button is already available. Proceeding to download the archive.", "green")

                # Click the download button
                driver.execute_script("arguments[0].click();", download_button)

                # Wait for the download to complete
                download_directory = os.path.join(os.getcwd(), 'downloaded_files')
                print_colored(f"Checking download directory: {download_directory}", "green")

                # Wait for the downloaded file to appear in the download directory
                timeout = 600  # Set a maximum wait time of 10 minutes
                polling_interval = 10  # Check every 10 seconds
                elapsed_time = 0
                downloaded_file = None

                while elapsed_time < timeout:
                    for file in os.listdir(download_directory):
                        if file.endswith('.zip'):
                            downloaded_file = os.path.join(download_directory, file)
                            break

                    if downloaded_file and os.path.exists(downloaded_file):
                        print_colored(f"Found downloaded file: {downloaded_file}", "green")
                        break
                    else:
                        time.sleep(polling_interval)
                        elapsed_time += polling_interval
                        print_colored(f"Waiting for the file to download... {elapsed_time} seconds elapsed.", "yellow")

                if downloaded_file and os.path.exists(downloaded_file):
                    output_directory = os.path.join(os.getcwd(), 'downloads')
                    os.makedirs(output_directory, exist_ok=True)

                    # Create the new file path using the username
                    new_file_path = os.path.join(output_directory, f"{username}_LinkedIn_data.zip")
                    shutil.move(downloaded_file, new_file_path)
                    print_colored(f"Data downloaded and saved as {new_file_path}.", "green")

                    # Unzip the downloaded file and store it in output\user_data\{username} folder
                    unzip_directory = os.path.join(os.getcwd(), 'output', 'user_data', username)
                    os.makedirs(unzip_directory, exist_ok=True)

                    with zipfile.ZipFile(new_file_path, 'r') as zip_ref:
                        zip_ref.extractall(unzip_directory)
                    print_colored(f"Data extracted to {unzip_directory}.", "green")
                    csv_file_path = os.path.join(unzip_directory, 'messages.csv')
                    print("CSV file path: ", csv_file_path)

                    msg_links = extract_link(csv_file_path)
                    # Print each link one by one
                    print('Links from msg:')
                    for link in msg_links:
                        print(link)
                    
                    
                    # Analyzing the URLs and getting the DataFrame
                    url_scores_df = analyze_urls(msg_links)

                    # # Save the DataFrame to an Excel file
                    output_file = "url_analysis_results.xlsx"
                    url_scores_df.to_excel(output_file, index=False)


                    print(f"Results have been saved to {output_file}")

                else:
                    print_colored(f"Downloaded file not found in {download_directory} within the timeout period. Please check the download location.", "red")

            else:
                print_colored("Download button is disabled. Please wait until it becomes active or request a new archive.", "red")

        except (TimeoutException, ElementClickInterceptedException) as e:
            print_colored(f"Encountered an issue: {e}. Attempting to request a new archive.", "yellow")

            # Request a new archive if the download button is not available
            specific_radio_button = WebDriverWait(driver, 30).until(
                EC.presence_of_element_located((By.ID, "fast-file-only"))
            )
            driver.execute_script("arguments[0].click();", specific_radio_button)
            print_colored("Selected the specific radio button.", "green")

            checkboxes = WebDriverWait(driver, 30).until(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR, "input[type='checkbox']"))
            )

            for checkbox in checkboxes:
                if checkbox.get_attribute('id') == "file_group_INBOX" and not checkbox.is_selected():
                    driver.execute_script("arguments[0].click();", checkbox)

            print_colored("Selected only the 'Messages' data category for export.", "green")

            request_button = WebDriverWait(driver, 30).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "button.request-archive-btn"))
            )
            driver.execute_script("arguments[0].click();", request_button)
            print_colored("Clicked the 'Request archive' button.", "green")

            WebDriverWait(driver, 600).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "button.download-btn"))
            )
            download_button = driver.find_element(By.CSS_SELECTOR, "button.download-btn")
            driver.execute_script("arguments[0].click();", download_button)
            print_colored("Data download initiated. Waiting for download to complete...", "green")

    except TimeoutException:
        print_colored("Timeout while waiting for data export elements. Please check your internet connection and LinkedIn settings.", "red")
    except Exception as e:
        print_colored(f"An error occurred during data export: {e}", "red")
    finally:
        driver.switch_to.default_content()
        driver.quit()

# Main loop to handle multiple logins and data export
while True:
    try:
        with open('credentials.csv', 'r') as file:
            reader = csv.DictReader(file)
            credentials_list = list(reader)

        driver = Driver(uc=True)

        for credentials in credentials_list:
            username = credentials['username']
            password = credentials['password']

            if is_user_logged_in(username):
                continue

            check_internet_connection()

            try:
                loading_animation(f"Logging in for {username}... ")

                driver.get("https://www.linkedin.com/login")

                username_field = WebDriverWait(driver, 30).until(
                    EC.presence_of_element_located((By.ID, "username"))
                )
                username_field.send_keys(username)

                password_field = driver.find_element(By.ID, "password")
                password_field.send_keys(password)
                password_field.send_keys(Keys.RETURN)

                try:
                    WebDriverWait(driver, 35).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, "img.global-nav__me-photo"))
                    )
                    print_colored(f"You are now logged into LinkedIn for {username}!", "green")
                    log_login_status(username, 'Success')
                    
                    cookies = driver.get_cookies()
                    os.makedirs('cookies', exist_ok=True)
                    cookie_file = f"cookies/{username}_cookies.pkl"
                    with open(cookie_file, 'wb') as cookiesfile:
                        pickle.dump(cookies, cookiesfile)

                    export_linkedin_data(driver,username)

                except TimeoutException:
                    print_colored(f"Login failed for {username}: Could not verify the presence of a success indicator.", "red")
                    log_login_status(username, 'Failed', 'Could not verify successful login.')
                    continue

            except Exception as e:
                log_login_status(username, 'Failed', f"Login error: {e}")
                print_colored(f"Login error for {username}: {e}", "red")

            try:
                driver.get("https://www.linkedin.com/m/logout/")
                time.sleep(2)
            except Exception as e:
                print_colored(f"Logout error for {username}: {e}", "red")

        driver.quit()
        print("Completed one iteration of logins. Restarting in 60 seconds...")
        time.sleep(60)

    except Exception as e:
        log_login_status('N/A', 'Error', f"Unexpected error in main loop: {e}")
        print_colored(f"Unexpected error occurred in main loop: {e}. Restarting the process in 60 seconds...", "red")
        time.sleep(60)
