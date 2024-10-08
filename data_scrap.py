from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from seleniumbase import Driver


def export_linkedin_data(driver):

    try:
        # Open LinkedIn Data Export page
        driver.get("https://www.linkedin.com/mypreferences/d/download-my-data")

        # Wait for the page to load and the second radio option to appear
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, "//input[@type='radio'][2]")))

        # Select the second radio button for custom data export
        custom_data_radio = driver.find_element(By.XPATH, "//input[@type='radio'][2]")
        custom_data_radio.click()

        # Select all the checkboxes under custom export option
        checkboxes = driver.find_elements(By.XPATH, "//input[@type='checkbox']")
        for checkbox in checkboxes:
            checkbox.click()

        # Click the "Request archive" button
        request_button = driver.find_element(By.XPATH, "//button[text()='Request archive']")
        request_button.click()

        # Wait until the "Download archive" button is enabled (this might take time)
        WebDriverWait(driver, 600).until(EC.element_to_be_clickable((By.XPATH, "//button[text()='Download archive']")))

        # Click the "Download archive" button
        download_button = driver.find_element(By.XPATH, "//button[text()='Download archive']")
        download_button.click()

        # Wait for download to start (give it some time to finish)
        time.sleep(30)

    finally:
        # Close the browser
        driver.quit()

# Call the function to run the process
