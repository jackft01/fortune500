import os
import re
from bs4 import BeautifulSoup, Comment

# --- Constants for Section Patterns ---
# These patterns are EXAMPLES and likely NEED ADJUSTMENT based on real filings.
# Using re.IGNORECASE for case-insensitivity and re.DOTALL so '.' matches newlines.
# Look for "Item X." followed by the title, capturing content until the next "Item".
# This is a simplified approach; real filings have complex structures.

# Pattern for MD&A (Item 7)
# Tries to find "Item 7." Management's Discussion..." and captures until "Item 8."
# It allows for variations like "Item 7.", "Item 7:", "ITEM 7." etc.
# It includes optional non-greedy match `(?:.*?)` for things like "(continued)" or extra spaces/newlines
MDA_PATTERNS = [
    re.compile(r"item\s+7\.(?:.*?)(?:management.s discussion|financial condition)(?:.*?)(item\s+8\.|signature|exhibit index)", re.IGNORECASE | re.DOTALL),
    re.compile(r">item\s+7\.<(?:.*?)(?:management.s discussion|financial condition)(?:.*?)(?:>item\s+8\.<|>signature|>exhibit index)", re.IGNORECASE | re.DOTALL) # More HTML specific
]

# Pattern for Risk Factors (Item 1A)
# Tries to find "Item 1A. Risk Factors" and captures until "Item 1B." or "Item 2."
RISK_PATTERNS = [
    re.compile(r"item\s+1a\.(?:.*?)(?:risk factors)(?:.*?)(item\s+1b\.|item\s+2\.|item\s+3\.|part\s+ii|item\s+5\.|item\s+6\.|item\s+7\.)", re.IGNORECASE | re.DOTALL),
    re.compile(r">item\s+1a\.<(?:.*?)(?:risk factors)(?:.*?)(?:>item\s+1b\.<|>item\s+2\.<|>item\s+3\.<|>part\s+ii|>item\s+5\.|>item\s+6\.|>item\s+7\.)", re.IGNORECASE | re.DOTALL) # More HTML specific
]

SECTION_MAP = {
    "MD&A": MDA_PATTERNS,
    "RiskFactors": RISK_PATTERNS
    # Add more sections here if needed (e.g., Item 1. Business)
}


def find_filing_document(filing_dir):
    """
    Finds the main filing document within a downloaded filing directory.
    Prefers .htm over .txt, looks for files resembling the primary doc.
    """
    primary_doc = None
    for filename in os.listdir(filing_dir):
        # Common patterns for primary filing docs (like 10-k.htm, d#####.htm, filing-details.html)
        # Avoid 'full-submission.txt' unless it's the only option
        lower_filename = filename.lower()
        if lower_filename.endswith(".htm") or lower_filename.endswith(".html"):
                # Check if it's not obviously an exhibit or graphic file
                if 'exhibit' not in lower_filename and 'graph' not in lower_filename:
                    primary_doc = os.path.join(filing_dir, filename)
                # Prefer files that look like the main doc (e.g., 10-k, 10-q)
                if '10-k' in lower_filename or '10-q' in lower_filename or 'filing-details' in lower_filename:
                    return primary_doc # Found a likely candidate
        # Fallback to .txt if no suitable .htm found yet
        elif lower_filename.endswith(".txt") and primary_doc is None and lower_filename != "full-submission.txt":
            primary_doc = os.path.join(filing_dir, filename)

    # If no specific doc found, try full-submission.txt as last resort
    if primary_doc is None and os.path.exists(os.path.join(filing_dir, "full-submission.txt")):
            primary_doc = os.path.join(filing_dir, "full-submission.txt")

    return primary_doc

def read_filing_content(filepath):
    """Reads filing content, trying different encodings."""
    encodings_to_try = ['utf-8', 'latin-1', 'ascii']
    for enc in encodings_to_try:
        try:
            with open(filepath, 'r', encoding=enc) as f:
                return f.read()
        except UnicodeDecodeError:
            continue
        except Exception as e: # Catch other file reading errors
            print(f"Error reading {filepath}: {e}")
            return None # Failed to read
    print(f"Warning: Could not decode file {filepath} with common encodings.")
    return None # Return None if all encodings fail


def clean_html_text(html_content):
    """
    Uses BeautifulSoup to parse HTML and extract clean text.
    Removes scripts, styles, comments, and attempts to handle tables reasonably.
    """
    if not html_content:
        return ""

    soup = BeautifulSoup(html_content, 'lxml') # Use lxml parser

    # Remove unwanted tags
    for element in soup(["script", "style", "head", "title", "meta", "[document]"]):
        element.decompose()
    # Remove comments
    for comment in soup.find_all(string=lambda text: isinstance(text, Comment)):
        comment.extract()

    # Attempt to handle tables better - add space around cells
    for td in soup.find_all('td'):
        td.insert_after(" ") # Add space after cell content
    for th in soup.find_all('th'):
        th.insert_after(" ")

    # Get text, strip leading/trailing whitespace from each line, join lines
    text = ' '.join(line.strip() for line in soup.stripped_strings)

    # Further cleanup: Replace multiple spaces/newlines with a single space
    text = re.sub(r'\s+', ' ', text).strip()
    # Optional: Remove excessively long strings without spaces (potential base64 data)
    text = re.sub(r'\b[A-Za-z0-9+/=]{50,}\b', '', text)

    return text


def extract_section_from_text(text_content, section_patterns):
    """
    Applies regex patterns to extract a section from plain text.
    Returns the first successful match.
    """
    if not text_content:
        return None
    for pattern in section_patterns:
        match = pattern.search(text_content)
        if match:
            # Try to capture the content between the start and end markers
            # This assumes the pattern captures the relevant part in group(0) or similar
            # You might need to refine patterns to use capturing groups for just the content
            # For now, return the whole match found by the pattern
            # Refinement: Extract specific group if pattern uses capturing ()
            # Example: if pattern = re.compile(r"start_marker(.*?)end_marker"), use match.group(1)
            return match.group(0) # Return the full match for now
    return None # No pattern matched