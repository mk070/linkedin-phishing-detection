import os
import shutil
import zipfile
import csv
import requests
import time
import pickle
from datetime import datetime
from seleniumbase import Driver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.common.exceptions import StaleElementReferenceException

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

def export_linkedin_data(driver, username):
    try:
        # Open LinkedIn Data Export page
        driver.get("https://www.linkedin.com/mypreferences/d/download-my-data")

        # Switch to the iframe containing the export settings
        WebDriverWait(driver, 30).until(
            EC.frame_to_be_available_and_switch_to_it((By.CSS_SELECTOR, "iframe.settings-iframe--frame"))
        )
        print_colored("Switched to the iframe containing the data export settings.", "green")

        # Check if the download button is already available
        try:
            download_button = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "button.download-btn"))
            )
            print_colored("Download button is already available. Proceeding to download the archive.", "green")

            # Click the download button
            download_button.click()

            # Wait for the download to complete
            download_directory = os.path.join(os.getcwd(), 'downloaded_files')
            print_colored(f"Checking download directory: {download_directory}", "green")

            # Wait for the downloaded file to appear in the download directory
            timeout = 300  # Set a maximum wait time of 5 minutes
            polling_interval = 5  # Check every 5 seconds
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
            else:
                print_colored(f"Downloaded file not found in {download_directory} within the timeout period. Please check the download location.", "red")

        except TimeoutException:
            print_colored("Download button not found. Proceeding to request a new archive.", "yellow")

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
                if not checkbox.is_selected():
                    driver.execute_script("arguments[0].click();", checkbox)

            print_colored("Selected all data categories for export.", "green")

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
