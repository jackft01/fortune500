import yfinance as yf
import pandas as pd
import os
import sys # Import sys for error handling

# --- Configuration ---
TICKERS = ["AAPL", "MSFT", "AMZN"]
BENCHMARK_TICKER = "^GSPC"
ALL_TICKERS = TICKERS + [BENCHMARK_TICKER]

START_DATE = "2020-12-01"
END_DATE = "2024-04-01" # Ensure this covers filings + future prediction window

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SAVE_DIR = os.path.join(ROOT_DIR, "data", "market_data")

# Keep filenames descriptive, 'Close' now implies Adjusted Close
CLOSE_FILENAME = "market_data_close.csv" # Renamed for clarity
VOLUME_FILENAME = "market_data_volume.csv"
RETURNS_FILENAME = "market_data_daily_returns.csv"

# --- Download Logic ---
if not os.path.exists(SAVE_DIR):
    os.makedirs(os.path.dirname(SAVE_DIR), exist_ok=True)
    os.makedirs(SAVE_DIR)
    print(f"Created directory: {SAVE_DIR}")

print(f"Downloading market data for: {', '.join(ALL_TICKERS)}")
print(f"Period: {START_DATE} to {END_DATE}")
print("Note: yfinance auto_adjust=True is default, 'Close' price is adjusted.")

try:
    # Download historical data (auto_adjust=True is default)
    data = yf.download(ALL_TICKERS, start=START_DATE, end=END_DATE, progress=True)

    if data.empty:
        print("No data downloaded. Check tickers, date range, and network connection.")
        sys.exit(1) # Exit if no data

    # --- Check for required columns ('Close' and 'Volume') ---
    required_columns = ['Close', 'Volume']
    missing_cols = False
    # Need to handle both MultiIndex (multiple tickers) and single index (one ticker) column structures
    if isinstance(data.columns, pd.MultiIndex):
        # Check if 'Close' and 'Volume' are present as top-level column names
        if not all(col in data.columns.levels[0] for col in required_columns):
            print(f"Error: Missing required top-level columns in downloaded data. Found: {data.columns.levels[0]}")
            missing_cols = True
    else: # Single index case (less likely with multiple tickers, but good to check)
            if not all(col in data.columns for col in required_columns):
                print(f"Error: Missing required columns in downloaded data. Found: {data.columns}")
                missing_cols = True

    if missing_cols:
        print("Cannot proceed without 'Close' and 'Volume' columns.")
        sys.exit(1) # Exit if required columns aren't there

    # --- Separate Close and Volume data ---
    # This structure assumes yfinance returns a MultiIndex dataframe when multiple tickers are requested
    if isinstance(data.columns, pd.MultiIndex):
        print("MultiIndex columns detected. Extracting 'Close' and 'Volume'.")
        close_data = data['Close'] # Use 'Close' which is auto-adjusted
        volume_data = data['Volume']
    else: # Handle case where only one ticker might be downloaded successfully
            print("SingleIndex columns detected. Extracting 'Close' and 'Volume'.")
            # Ensure resulting variables are DataFrames for consistency
            close_data = data[['Close']]
            volume_data = data[['Volume']]


    # --- Save Data ---
    # Save Close (Adjusted) data
    save_path_close = os.path.join(SAVE_DIR, CLOSE_FILENAME)
    close_data.to_csv(save_path_close)
    print(f"Close (Adjusted) data saved to: {save_path_close}")

    # Save Volume data
    save_path_vol = os.path.join(SAVE_DIR, VOLUME_FILENAME)
    volume_data.to_csv(save_path_vol)
    print(f"Volume data saved to: {save_path_vol}")

    # --- Calculate and save returns (using the adjusted 'Close' data) ---
    returns_data = close_data.pct_change().dropna()
    returns_save_path = os.path.join(SAVE_DIR, RETURNS_FILENAME)
    returns_data.to_csv(returns_save_path)
    print(f"Daily returns data saved to: {returns_save_path}")

except Exception as e:
    print(f"An error occurred during market data download: {e}")
    # Print traceback for more details on other errors
    import traceback
    traceback.print_exc()


print("\n--- Market data download finished ---")