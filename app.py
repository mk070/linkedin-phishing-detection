import os
import threading
import pandas as pd
import re
import time
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

# Load already processed URLs for a specific CSV file
def load_processed_urls(log_file):
    if not os.path.exists(log_file):
        return set()
    
    with open(log_file, 'r') as file:
        processed_urls = file.read().splitlines()
    return set(processed_urls)

# Save processed URLs as they are completed
def log_processed_url(url, log_file):
    with open(log_file, 'a') as file:
        file.write(url + '\n')

# Main function to handle processing of input CSV files and analysis
def process_csv_files():
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
            csv_files = [f for f in os.listdir(input_folder) if f.endswith('.csv')]

            if not csv_files:
                print_colored("No CSV files to process. Waiting for new files...", "yellow")
                time.sleep(30)
                continue

            # Process each new CSV file
            for csv_file in csv_files:
                csv_file_path = os.path.join(input_folder, csv_file)
                log_file = os.path.join(output_dir, f"{os.path.splitext(csv_file)[0]}_processed_urls.log")
                print_colored(f"\n{'=' * 50}\nProcessing CSV file: {csv_file_path}\n{'=' * 50}", "green")

                # Load already processed URLs
                processed_urls = load_processed_urls(log_file)
                print_colored(f"Loaded {len(processed_urls)} previously processed URLs.", "yellow")

                # Set up the stop event for the animation
                stop_event = threading.Event()

                # Start the loading animation in a separate thread
                animation_thread = threading.Thread(target=loading_animation, args=("Extracting links from CSV", stop_event))
                animation_thread.start()

                try:
                    # Extract URLs from the CSV file
                    msg_links = extract_link(csv_file_path)
                    if not msg_links:
                        print_colored("No URLs found in the CSV. Skipping this file...", "red")
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

                    # Initialize an empty DataFrame to store the analysis results
                    output_file = os.path.abspath(os.path.join(output_dir, f"{os.path.splitext(csv_file)[0]}_url_analysis_results.xlsx"))
                    url_scores_df = pd.DataFrame()

                    # Analyze each URL one by one and update the Excel file in real-time
                    for i, link in enumerate(msg_links):
                        # Skip URLs that have already been processed
                        if link in processed_urls:
                            print_colored(f"URL {i+1}/{len(msg_links)} already processed: {link}", "yellow")
                            continue

                        print_colored(f"Analyzing URL {i+1}/{len(msg_links)}: {link}", "yellow")
                        
                        # Analyze the URL
                        result_df = analyze_urls([link])  # This returns a DataFrame with columns from analyze_urls

                        # Append the result to the DataFrame
                        url_scores_df = pd.concat([url_scores_df, result_df], ignore_index=True)

                        # Save the updated results to the Excel file
                        url_scores_df.to_excel(output_file, index=False)
                        print_colored(f"URL {i+1} has been analyzed and results updated.", "green")

                        # Log the processed URL
                        log_processed_url(link, log_file)
                        processed_urls.add(link)  # Update the in-memory set as well

                    print_colored(f"\n{'=' * 50}\nAll URLs from {csv_file} have been analyzed.\nResults saved to {output_file}\n{'=' * 50}", "green")

                finally:
                    # Stop the animation after processing is complete
                    stop_event.set()
                    animation_thread.join()

        except Exception as e:
            print_colored(f"Unexpected error: {e}. Restarting the process in 60 seconds...", "red")
            time.sleep(60)

# Run the CSV processing
if __name__ == "__main__":
    process_csv_files()
