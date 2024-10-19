# LinkedIn Phishing Detection & URL Analysis

This project automates the detection of phishing URLs from LinkedIn messages and performs detailed URL analysis. It processes CSV files containing LinkedIn messages, extracts URLs, analyzes them, and saves the results in an Excel file. It includes visual feedback during processing through a rotating loader animation and ensures files are processed only once.

## Features

- **Automated URL Extraction**: Extracts URLs from the `CONTENT` column of CSV files containing LinkedIn messages.
- **Continuous File Monitoring**: Watches the `input` folder for new CSV files and processes them automatically.
- **Phishing URL Analysis**: Analyzes each extracted URL for potential phishing risks using the `url_analyser` module.
- **Loading Animation**: Displays a rotating loader during long processes such as extraction and analysis.
- **Results in Excel Format**: Saves the analysis results to an Excel file, excluding `.csv` from the filename.
- **Processed File Logging**: Tracks processed files to prevent reprocessing of the same file.
- **Internet Connection Monitoring**: Automatically checks for an active internet connection before starting and retries until it’s restored.

## Project Structure

```bash
.
├── input/                      # Folder containing input CSV files for processing.
│   └── messages.csv             # Example CSV file with LinkedIn messages.
├── output/                     # Folder where the analysis results are saved.
│   └── url_analysis_results.xlsx # Example output file.
├── processed_files.log          # Log file to track processed CSV files.
├── url_analyser.py              # Custom URL analysis module.
├── app.py                       # Main script for running the project.
├── README.md                    # Project documentation.
```

## How It Works

1. **Input CSV Files**: The system expects CSV files with LinkedIn message data in the `input` folder. Each CSV file should have a `CONTENT` column where messages are stored.
2. **URL Extraction**: URLs are extracted from the `CONTENT` column of the CSV file.
3. **URL Analysis**: The extracted URLs are analyzed for phishing risks or any other defined criteria using the `url_analyser` module.
4. **Results Saving**: The analyzed URLs are saved in an Excel file located in the `output` folder with the format `filename_url_analysis_results.xlsx` (where `filename` is the input CSV files name without `.csv`).
5. **Loading Animation**: While extracting and analyzing URLs, a rotating loader appears in the terminal, indicating progress.
6. **Processed Files Logging**: Once a CSV file has been processed, its filename is logged in `processed_files.log` to prevent duplicate processing.

## Prerequisites

Make sure to install the following dependencies before running the project:

- **Python 3.x**
- **Pandas**: For handling CSV files and data frames.
- **Requests**: For checking the internet connection.
- **OpenPyXL**: For writing Excel files.

Install the required Python packages using the command:

```bash
python -m venv .venv

.venv\Scripts\activate

pip install -r requirements.txt
```
## usage
```bash
python app.py
```

==============================================================================================


# Phishing Detection: Criteria and Implementation Guidelines

This document outlines the criteria for detecting phishing webpages and provides implementation guidelines for each criterion.

## Criteria 1: Google API Validation
- **Description**: IF a URL is in the blacklist(s), THEN it is potentially a phishing webpage.
- **Implementation**:
  - Use the Google Safe Browsing API to check if the URL is blacklisted.
  - If blacklisted, flag the URL as phishing.
  - If not blacklisted, the URL is considered legitimate.

## Criteria 2: External Password Validation
- **Description**: IF a webpage contains a password input field AND the webpage has more external than internal links, THEN the webpage is potentially phishing.
- **Implementation**:
  - Check if the webpage contains a password input field.
  - Gather and count both external and internal links on the webpage.
  - If the number of external links exceeds internal links, flag the webpage as potentially phishing.

## Criteria 3: Redirect-Registration
- **Description**: IF a webpage’s URL is not present in all search engines’ indexes, THEN the webpage is potentially phishing.
- **Implementation**:
  - Submit the URL to three major search engines: Google, Bing, and Yahoo.
  - If the URL is missing from any of these indexes, flag it as phishing.
  - Check the status code for each response (status code 200 = legitimate, otherwise phishing).
  - If a redirect occurs, the process iterates for the final destination URL.

## Criteria 4: IP-Address Validation
- **Description**: IF a webpage’s URL is IP-based (hex-based, octal, or decimal-based), THEN the webpage is potentially a phishing attack.
- **Implementation**:
  - Check the URL for hex-based, octal-based, or decimal-based formats.
  - If the URL matches any of these formats, flag it as potentially phishing.

## Criteria 5: Unwanted Special Characters
- **Description**: IF a URL contains characters `[-, _, 0-9, @, “,”, ;]` OR a non-standard port, THEN the webpage is potentially phishing.
- **Implementation**:
  - Scan the URL for numbers (0-9) and the specified special characters.
  - If found, flag the URL as potentially phishing.
  - Check for non-standard ports (port numbers not 80 or 443). If found, flag the URL.

## Criteria 6: Suspicious Keyword
- **Description**: IF a phishing keyword is present in the URL, THEN the webpage is likely phishing.
- **Implementation**:
  - Check the extracted URL for predefined suspicious keywords (e.g., "login," "password," "verify").
  - If a match is found, classify the URL as a potential phishing attempt.

## Criteria 7: Domain Validation
- **Description**: IF the content of the registration URL is not found in the search engine, THEN the webpage is likely phishing.
- **Implementation**:
  - Redirect the provided URL to a search engine and check if the content exists.
  - If the search engine does not return relevant content, flag the URL as phishing.
  
## Criteria 8: Meta Refresh
- **Description**: IF a URL contains a meta tag and its attribute "http-equiv," THEN it is potentially phishing.
- **Implementation**:
  - Check the extracted URL for a meta tag containing the attribute `http-equiv`.
  - If the specified meta tag is found, flag the URL as potentially phishing.
