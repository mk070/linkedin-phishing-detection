import os
import threading
import pandas as pd
import re
import time
import csv
import requests
from urllib.parse import urlparse
from url_analyser import analyze_urls

# Print text with a specific color for better readability
def print_colored(text, color):
    colors = {
        "green": "\033[92m",
        "red": "\033[91m",
        "yellow": "\033[93m",
        "reset": "\033[0m",
    }
    print(f"{colors[color]}{text}{colors['reset']}")

# Loading animation for long processes
def loading_animation(message, stop_event):
    print_colored(message, "yellow")
    while not stop_event.is_set():
        for _ in range(3):
            if stop_event.is_set():
                break
            print('.', end='', flush=True)
            time.sleep(1)
        print('\r', end='', flush=True)  # Carriage return to overwrite previous animation
    print()  # Print a new line when animation stops


# Check internet connection continuously until active
def check_internet_connection(url="https://www.google.com", timeout=5):
    while True:
        try:
            requests.get(url, timeout=timeout)
            print_colored("Internet connection is active.", "green")
            return True
        except requests.ConnectionError:
            print_colored("No internet connection. Retrying in 10 seconds...", "yellow")
            time.sleep(10)

# Ensure CSV file has required headers, create the file if not present
def ensure_csv_headers(file_path, headers):
    file_exists = os.path.exists(file_path)
    if not file_exists or os.path.getsize(file_path) == 0:
        with open(file_path, 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(headers)

# Extract URLs from the content of a CSV file
def extract_link(file_path):
    df = pd.read_csv(file_path)

    # Function to extract URLs from the 'CONTENT' column
    def extract_usernames_links(content):
        pattern = r'(https?://[^\s<>"\']+)'
        matches = re.findall(pattern, content)
        return matches

    # Apply the function to the 'CONTENT' column
    df['USERNAMES_AND_LINKS'] = df['CONTENT'].apply(lambda x: extract_usernames_links(str(x)))

    # Flatten the list of lists
    links = [link for sublist in df['USERNAMES_AND_LINKS'] for link in sublist]
    return links

# Track already processed CSV files to avoid reprocessing
def get_processed_csv_files(log_file='processed_files.log'):
    if not os.path.exists(log_file):
        return set()
    
    with open(log_file, 'r') as file:
        processed_files = file.read().splitlines()
    return set(processed_files)

def log_processed_file(file_name, log_file='processed_files.log'):
    with open(log_file, 'a') as file:
        file.write(file_name + '\n')

# Main function to handle processing of input CSV files and analysis
def process_csv_files():
    processed_files = get_processed_csv_files()

    # Create output directory
    output_dir = 'output'
    os.makedirs(output_dir, exist_ok=True)

    # Loop for continuous file processing
    while True:
        try:
            # Check internet connection before proceeding
            check_internet_connection()

            # Get all CSV files in the input folder
            input_folder = 'input'
            csv_files = [f for f in os.listdir(input_folder) if f.endswith('.csv') and f not in processed_files]

            if not csv_files:
                print_colored("No new CSV files to process. Waiting for new files...", "yellow")
                time.sleep(30)
                continue

            # Process each new CSV file
            for csv_file in csv_files:
                csv_file_path = os.path.join(input_folder, csv_file)
                print_colored(f"\n{'=' * 50}\nProcessing CSV file: {csv_file_path}\n{'=' * 50}", "green")

                # Set up the stop event for the animation
                stop_event = threading.Event()

                # Start the loading animation in a separate thread
                animation_thread = threading.Thread(target=loading_animation, args=("Extracting links from CSV", stop_event))
                animation_thread.start()

                try:
                    msg_links = extract_link(csv_file_path)
                    if not msg_links:
                        print_colored("No URLs found in the CSV. Skipping this file...", "red")
                        log_processed_file(csv_file)
                        stop_event.set()  # Stop the animation
                        animation_thread.join()
                        continue

                    print_colored(f"Extracted {len(msg_links)} links:", "green")
                    for link in msg_links:
                        print(link)

                    # Start the loading animation for URL analysis
                    stop_event.clear()  # Reset the stop event
                    print_colored(f"\n{'=' * 50}\nAnalyzing URLs from CSV: {csv_file_path}\n{'=' * 50}", "green")

                    animation_thread = threading.Thread(target=loading_animation, args=("Analyzing URLs from CSV", stop_event))
                    animation_thread.start()
                    
                    # Analyze URLs
                    url_scores_df = analyze_urls(msg_links)

                    # Save results to Excel
                    output_file = os.path.abspath(os.path.join(output_dir, f"{csv_file.replace('.csv', '')}_url_analysis_results.xlsx"))
                    url_scores_df.to_excel(output_file, index=False)
                    print_colored(f"Results have been saved to {output_file}", "green")

                    # Stop the animation after processing is complete
                    stop_event.set()
                    animation_thread.join()

                finally:
                    # Mark file as processed
                    log_processed_file(csv_file)
                    stop_event.set()
                    animation_thread.join()

        except Exception as e:
            print_colored(f"Unexpected error: {e}. Restarting the process in 60 seconds...", "red")
            time.sleep(60)

# Run the CSV processing
if __name__ == "__main__":
    process_csv_files()
