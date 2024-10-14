# LinkedIn Data Export Automation

## Overview

This project automates the process of exporting LinkedIn user data using Selenium WebDriver. It supports the following features:
- Logs into LinkedIn accounts using user credentials.
- Requests and downloads a data archive from LinkedIn's data export settings.
- Allows users to selectively export only specific data categories (e.g., Messages).
- Automatically handles cases where the download is not immediately available.
- Saves the downloaded data in a user-specific folder.
- Extracts the downloaded ZIP file into an organized output folder for further processing.

## Features
- **Automatic Login:** Automates the login process to LinkedIn.
- **Data Export:** Requests data archives from LinkedIn and downloads available archives.
- **Selective Export:** Ability to select specific data types for export (e.g., Messages, Contacts).
- **Error Handling:** Handles common errors such as disabled download buttons, timeouts, or connection issues.
- **Data Organization:** Unzips the downloaded data and organizes it in folders named after the respective users.

## Project Directory Structure

```bash

linkedin-data-export/
│
├── downloaded_files/     # Where files will be temporarily stored before moving
├── downloads/            # Stores user-specific downloaded files
├── output/
│   └── user_data/        # Extracted user data from zip files
├── credentials.csv       # User credentials for LinkedIn login
├── requirements.txt      # Python dependencies
├── app.py                # Main script to run the automation
└── README.md             # This README file
```

## Prerequisites

To use this project, you need to install the following:
- Python 3.x
- Selenium WebDriver
- Chrome WebDriver (or any other browser you wish to use)
- Basic understanding of how Python virtual environments work

## Setup

### Step 1: Clone the Repository

```bash
git clone https://github.com/yourusername/linkedin-data-export.git
cd linkedin-data-export
```

### Step 2: Create a Virtual Environment (Optional but recommended)
```bash
python -m venv .venv
source .venv/bin/activate  # For Linux/macOS
# or
.venv\Scripts\activate  # For Windows
```

### Step 3: Install Dependencies
```bash
pip install -r requirements.txt
```
### Step 4: Set Up Selenium WebDriver
Make sure you have the appropriate browser driver (e.g., ChromeDriver) installed. You can download it from ChromeDriver. Place it in a folder accessible through the system's PATH or specify the path in the script.

### Step 5: Add LinkedIn Credentials
You need to provide your LinkedIn credentials. This is stored in a credentials.csv file in the following format:

## Usage
```bash
python app.py
```

