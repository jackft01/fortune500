    # File: scripts/download_filings.py

from sec_edgar_downloader import Downloader
import os
import sys

sys.path.insert(0, "scripts/")

# Make sure to import or define Downloader before using it
# from your_module import Downloader

# --- Configuration ---
# IMPORTANT: Replace with your actual email address for SEC EDGAR User-Agent
YOUR_EMAIL = "jackftaylor693@gmail.com"
# IMPORTANT: Replace with a generic company name or your project name
YOUR_COMPANY_NAME = "Fortune500 Analysis Project"

# Use relative paths from the root of the project
# Assumes you run this script from the root 'fortune500_analyzer/' directory
# If running from 'scripts/', adjust paths accordingly or use absolute paths.
# We'll assume running from the root for consistency.
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # Gets the parent directory of 'scripts/'
SAVE_PATH = os.path.join(ROOT_DIR, "sec_filings")

# List of tickers for companies you want to analyze
# Start small for testing!
TICKERS = ["AAPL", "MSFT", "AMZN"]  # Example: Apple, Microsoft, Amazon

# Filing types (10-K for annual, 10-Q for quarterly)
FILING_TYPES = ["10-K", "10-Q"]

# Date range (adjust as needed)
# Format: YYYY-MM-DD
START_DATE = "2021-01-01"
END_DATE = "2023-12-31"

# Max number of filings to download per company per filing type
# Set amount=None to download all within the date range (can be a lot!)
AMOUNT = 5  # Download the 5 most recent filings of each type

if not os.path.exists(SAVE_PATH):
    os.makedirs(SAVE_PATH)
    print(f"Created directory: {SAVE_PATH}")

# Initialize the downloader
dl = Downloader(YOUR_COMPANY_NAME, YOUR_EMAIL, SAVE_PATH)
print(f"Downloader initialized. Filings will be saved in: {SAVE_PATH}")
print("Starting SEC filing download...")

for ticker in TICKERS:
    print(f"\n--- Processing {ticker} ---")
    for filing_type in FILING_TYPES:
        try:
            print(f"Attempting to download {AMOUNT} {filing_type} filings for {ticker} ({START_DATE} to {END_DATE})...")
            # Get filings after START_DATE and before END_DATE
            num_downloaded = dl.get(
                filing_type,
                ticker,
                after=START_DATE,
                before=END_DATE,
                #amount=AMOUNT,
                download_details=True  # download_details is useful
            )
            print(f"Successfully downloaded {num_downloaded} {filing_type} filings for {ticker}.")
        except Exception as e:
            # Catch potential errors like network issues or invalid tickers
            print(f"Could not download {filing_type} for {ticker}: {e}")
            print("Check ticker validity, date range, and network connection.")

print("\n--- Filing download process finished ---")

# --- Verification ---
print("\nVerifying downloaded directories (partial listing):")
try:
    count = 0
    # The library creates a subfolder 'sec-edgar-filings' inside SAVE_PATH
    actual_filing_root = os.path.join(SAVE_PATH, 'sec-edgar-filings')
    if os.path.exists(actual_filing_root):
        for item in os.listdir(actual_filing_root):
            item_path = os.path.join(actual_filing_root, item)
            if os.path.isdir(item_path) and item in TICKERS:
                print(f"Found directory for ticker: {item}")
                count += 1
                if count >= 5:  # List first 5 found tickers
                    break
    else:
        print(f"Expected download directory {actual_filing_root} not found.")
    if count == 0:
        print(f"No ticker directories found directly under {actual_filing_root}. Check structure.")
except Exception as e:
    print(f"Error during verification: {e}")
