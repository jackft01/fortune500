import os
import pandas as pd
import sys
from tqdm import tqdm # For progress bar

# Ensure the 'src' directory is in the Python path
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC_DIR = os.path.join(ROOT_DIR, 'src')
if SRC_DIR not in sys.path:
    sys.path.append(SRC_DIR)

# Import our custom parsing functions
try:
    from parsing import (
        find_filing_document,
        read_filing_content,
        clean_html_text,
        extract_section_from_text,
        SECTION_MAP # Import the dictionary of section patterns
    )
except ImportError:
        print("ERROR: Could not import from src.parsing. Make sure src/parsing.py exists and src is in the Python path.")
        sys.exit(1)


# --- Configuration ---
FILINGS_ROOT = os.path.join(ROOT_DIR, "sec_filings", "sec-edgar-filings") # Path to the actual filings
OUTPUT_DIR = os.path.join(ROOT_DIR, "data", "processed_filings")
OUTPUT_FILENAME = "processed_filings_sections.csv"

# Limit the number of filings to process during testing (set to None to process all)
MAX_FILINGS_TO_PROCESS = None # Or set to a number like 50

# --- Processing Logic ---
if not os.path.exists(FILINGS_ROOT):
    print(f"ERROR: Raw filings directory not found: {FILINGS_ROOT}")
    print("Please run the download_filings.py script first.")
    sys.exit(1)

if not os.path.exists(OUTPUT_DIR):
    os.makedirs(OUTPUT_DIR)
    print(f"Created output directory: {OUTPUT_DIR}")

processed_data = []
filings_processed_count = 0

print("Starting filing preprocessing...")
# Use os.walk to go through the ticker/filing_type/accession_number structure
for dirpath, dirnames, filenames in tqdm(os.walk(FILINGS_ROOT), desc="Processing Filings"):
    # Check if the current directory looks like an accession number directory
    # (typically contains digits and maybe dashes) and has files
    basename = os.path.basename(dirpath)
    if basename and basename[0].isdigit() and filenames:
        # Try to extract Ticker, Filing Type, Filing Date from path
        try:
            parts = dirpath.split(os.sep)
            # Example path: .../sec-edgar-filings/AAPL/10-K/0000320193-23-000106
            accession_number = basename
            filing_type = parts[-2] # e.g., '10-K'
            ticker = parts[-3]      # e.g., 'AAPL'
            # Note: Getting exact filing date might require parsing metadata or the file itself.
            # Using accession number as a unique identifier for now.
        except IndexError:
            # print(f"Warning: Could not parse metadata from path: {dirpath}")
            continue # Skip directories with unexpected structure

        # Find the main document within this accession number folder
        filing_path = find_filing_document(dirpath)

        if not filing_path:
            # print(f"Warning: Could not find suitable filing document in {dirpath}")
            continue # Skip if no document found

        # Read the content
        raw_content = read_filing_content(filing_path)
        if not raw_content:
            # print(f"Warning: Could not read content from {filing_path}")
            continue # Skip if content couldn't be read

        # Clean the text (especially if HTML)
        # Determine if it's likely HTML (simple check)
        if filing_path.lower().endswith(".htm") or filing_path.lower().endswith(".html") or "<html" in raw_content[:1000].lower():
            cleaned_content = clean_html_text(raw_content)
        else:
            # For plain text, just do basic whitespace normalization
            cleaned_content = re.sub(r'\s+', ' ', raw_content).strip()

        if not cleaned_content:
                # print(f"Warning: Content became empty after cleaning for {filing_path}")
                continue

        # Extract defined sections using regex on the cleaned text
        for section_name, patterns in SECTION_MAP.items():
            extracted_section_text = extract_section_from_text(cleaned_content, patterns)

            if extracted_section_text:
                processed_data.append({
                    "ticker": ticker,
                    "filing_type": filing_type,
                    "accession_number": accession_number,
                    # Placeholder for filing_date - needs better extraction later
                    "filing_date_approx": accession_number.split('-')[1], # Extract year/month part
                    "section": section_name,
                    "text": extracted_section_text # Store the extracted section
                })
            #else:
                # Optional: Log when a section wasn't found
                # print(f"Info: Section '{section_name}' not found via regex in {accession_number} for {ticker}")


        filings_processed_count += 1
        if MAX_FILINGS_TO_PROCESS is not None and filings_processed_count >= MAX_FILINGS_TO_PROCESS:
            print(f"\nReached maximum filings limit ({MAX_FILINGS_TO_PROCESS}). Stopping.")
            break # Exit outer loop

    # Break inner loops if max count reached
    if MAX_FILINGS_TO_PROCESS is not None and filings_processed_count >= MAX_FILINGS_TO_PROCESS:
        break


print(f"\nProcessed {filings_processed_count} filings.")

if not processed_data:
    print("Warning: No sections were successfully extracted. Check regex patterns in src/parsing.py and inspect raw filings.")
else:
    # Convert list of dicts to DataFrame
    df = pd.DataFrame(processed_data)

    # --- Save the processed data ---
    output_path = os.path.join(OUTPUT_DIR, OUTPUT_FILENAME)
    df.to_csv(output_path, index=False)
    print(f"Successfully saved processed sections to: {output_path}")
    print(f"\nPreview of processed data:\n{df.head()}")
    print(f"\nExtracted sections distribution:\n{df['section'].value_counts()}")

print("\n--- Filing preprocessing finished ---")