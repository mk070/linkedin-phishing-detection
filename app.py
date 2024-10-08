import os
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
from data_scrap import export_linkedin_data

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

                username_field = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.ID, "username"))
                )
                username_field.send_keys(username)

                password_field = driver.find_element(By.ID, "password")
                password_field.send_keys(password)
                password_field.send_keys(Keys.RETURN)

                try:
                    captcha_element = WebDriverWait(driver, 15).until(
                        EC.presence_of_element_located((By.XPATH, "//input[@id='captcha']"))
                    )
                    print_colored(f"Captcha detected for {username}. Waiting for manual completion...", "yellow")
                    while True:
                        try:
                            WebDriverWait(driver, 5).until(
                                EC.presence_of_element_located((By.CSS_SELECTOR, "img.global-nav__me-photo"))
                            )
                            break
                        except TimeoutException:
                            pass
                except TimeoutException:
                    pass

                try:
                    WebDriverWait(driver, 15).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, "img.global-nav__me-photo"))
                    )
                    print_colored(f"You are now logged into LinkedIn for {username}!", "green")
                    log_login_status(username, 'Success')
                    
                    cookies = driver.get_cookies()
                    os.makedirs('cookies', exist_ok=True)
                    cookie_file = f"cookies/{username}_cookies.pkl"
                    with open(cookie_file, 'wb') as cookiesfile:
                        pickle.dump(cookies, cookiesfile)

                    export_linkedin_data(driver)

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