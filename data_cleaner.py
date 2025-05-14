import pandas as pd
import numpy as np
import re
import os
from datetime import datetime

# Missing data values
NULL_VALUES = ['', 'null', 'none', 'n/a', 'na',
               '-', '--', '—', '#n/a', '#na', 'nan', '#value!']


def load_file(file_path):
    """Load a file into a pandas DataFrame"""
    try:
        if file_path.lower().endswith('.csv'):
            return pd.read_csv(file_path, encoding='utf-8')
        elif file_path.lower().endswith(('.xls', '.xlsx')):
            return pd.read_excel(file_path)
        else:
            print("Unsupported file format. Please use CSV or Excel files.")
            return None
    except Exception as e:
        print(f"Error loading file: {str(e)}")
        return None


def clean_text(value):
    """Clean text by removing special characters and standardizing"""
    if not isinstance(value, str):
        return value

    # Strip whitespace and clean
    cleaned = value.strip()

    # Remove Unicode characters
    cleaned = re.sub(r'[‚Äî,â€,Ã,Â]', '', cleaned)

    # Remove non-printable characters but keep normal letters, numbers, punctuation
    cleaned = re.sub(r'[^\x20-\x7E]', '', cleaned)

    # Normalize whitespace
    cleaned = re.sub(r'\s+', ' ', cleaned).strip()

    # Check if empty or null-like
    if not cleaned or cleaned.lower() in NULL_VALUES:
        return np.nan

    return cleaned


def clean_company_name(value):
    """Clean and standardize company names"""
    if not isinstance(value, str):
        value = str(value)

    # Clean the text first
    cleaned = clean_text(value)
    if pd.isna(cleaned):
        return np.nan

    # Remove unwanted punctuation but keep periods in abbreviations
    cleaned = re.sub(r'[^\w\s\.]', ' ', cleaned)
    cleaned = re.sub(r'\s+', ' ', cleaned).strip()

    # Apply title case for company names
    cleaned = cleaned.title()

    # Fix common company suffixes that should be capitalized
    for suffix in [' Inc', ' Corp', ' Llc', ' Ltd', ' Plc', ' Sa', ' Ag', ' Se', ' Nv']:
        if cleaned.endswith(suffix):
            cleaned = cleaned[:-len(suffix)] + suffix.upper()

    return cleaned


def normalize_action_code(value):
    """Normalize action codes like BUY/SELL/SPCL"""
    if pd.isna(value):
        return np.nan

    if not isinstance(value, str):
        value = str(value)

    # Clean the text first
    cleaned = clean_text(value)
    if pd.isna(cleaned):
        return np.nan

    # Convert to uppercase for standardization
    cleaned = cleaned.upper()

    # Standardize action codes
    action_map = {
        'B': 'BUY', 'BUY': 'BUY', 'PURCHASE': 'BUY', 'BOUGHT': 'BUY', 'LONG': 'BUY',
        'S': 'SELL', 'SELL': 'SELL', 'SOLD': 'SELL', 'SHORT': 'SELL',
        'SPCL': 'SPCL', 'SPECIAL': 'SPCL',
        'HTB': 'HTB', 'HARD TO BORROW': 'HTB', 'HARDTOBORROW': 'HTB',
        'ETB': 'ETB', 'EASY TO BORROW': 'ETB', 'EASYTOBORROW': 'ETB'
    }

    # Match with standard codes
    for key, std_code in action_map.items():
        if key in cleaned:
            return std_code

    # Return as is if no match found
    return cleaned


def extract_number(value):
    """Extract numeric value from messy strings"""
    if isinstance(value, (int, float)):
        return float(value)

    if not isinstance(value, str):
        return np.nan

    value = clean_text(value)

    if pd.isna(value):
        return np.nan

    value = value.strip('\'"')

    # Remove known currency and fuzzy tokens
    value = re.sub(r'[$£€¥]|USD|EUR|JPY|GBP|CAD|AUD|CHF',
                   '', value, flags=re.IGNORECASE)
    value = re.sub(r'Approx\.?|Approximately|About|Around|Est\.?|Estimated|shares|units',
                   '', value, flags=re.IGNORECASE)

    value = re.sub(r'\s+', '', value)

    # European decimal convert
    if ',' in value and '.' not in value:
        value = value.replace(',', '.')

    # Final extract
    match = re.search(r'[-+]?\d*\.?\d+', value)
    if match:
        try:
            return float(match.group(0))
        except:
            return np.nan

    return np.nan


def clean_percentage(value):
    """Convert percentage values to decimal form"""
    if pd.isna(value):
        return np.nan

    # If already a number, convert to percentage (if >1 and <=100)
    if isinstance(value, (int, float)):
        return value / 100.0 if value > 1 and value <= 100 else value

    # Convert to string and clean
    value_str = str(value).strip().lower()

    # Extract number and convert (1 basis point = 0.0001)
    if 'basis point' in value_str or 'bps' in value_str:
        num = extract_number(value_str)
        if not pd.isna(num):
            return num / 10000.0
        return np.nan

    # Extract the number
    num = extract_number(value_str)
    if pd.isna(num):
        return np.nan

    # Convert percentages to decimal
    if '%' in value_str or 'percent' in value_str or 'pct' in value_str:
        return num / 100.0
    elif num > 1 and num <= 100:
        # Assume it's a percentage if between 1 and 100
        return num / 100.0

    return num


def clean_date(value):
    """Convert dates to MM/DD/YYYY format"""
    if pd.isna(value):
        return np.nan

    # If already a pandas timestamp
    if isinstance(value, pd.Timestamp):
        return value.strftime('%m/%d/%Y')

    # Try to parse the date
    try:
        # Convert to string if not already
        if not isinstance(value, str):
            value = str(value)

        # Clean the string first
        value = clean_text(value)
        if pd.isna(value):
            return np.nan

        # Try different date formats
        formats = [
            '%m/%d/%Y', '%m-%d-%Y', '%Y-%m-%d', '%Y.%m.%d', '%d/%m/%Y',
            '%m/%d/%y', '%d-%b-%y', '%d-%b-%Y', '%B %d, %Y', '%d %B %Y',
            '%b %d, %Y', '%Y%m%d', '%d.%m.%Y', '%d.%m.%y'
        ]

        for fmt in formats:
            try:
                date_obj = datetime.strptime(value, fmt)
                # Check if year is reasonable (between 1900 and current year + 1)
                if date_obj.year < 100:  # Two-digit year
                    if date_obj.year >= 50:  # Assume 1900s
                        date_obj = date_obj.replace(year=date_obj.year + 1900)
                    else:  # Assume 2000s
                        date_obj = date_obj.replace(year=date_obj.year + 2000)

                if 1900 <= date_obj.year <= datetime.now().year + 5:  # Allow dates up to 5 years in future
                    return date_obj.strftime('%m/%d/%Y')
                else:
                    continue  # Try next format if year is unreasonable
            except:
                continue

        # If no format matched, try pandas parser
        date_obj = pd.to_datetime(value, errors='coerce')
        if pd.notna(date_obj) and 1900 <= date_obj.year <= datetime.now().year + 5:
            return date_obj.strftime('%m/%d/%Y')
        else:
            return np.nan
    except:
        return np.nan


def clean_code(value):
    """Clean code values like tickers or CUSIPs"""
    if pd.isna(value):
        return np.nan

    if not isinstance(value, str):
        value = str(value)

    # Clean the string first
    value = clean_text(value)
    if pd.isna(value):
        return np.nan

    # Remove any characters that are not letters or numbers
    cleaned = re.sub(r'[^a-zA-Z0-9]', '', value)

    # Convert to uppercase
    cleaned = cleaned.upper()

    # Check if empty or invalid
    if not cleaned:
        return np.nan

    return cleaned


def clean_conversion_ratio(value):
    """Clean conversion ratio values"""
    if pd.isna(value):
        return np.nan

    # If already a number
    if isinstance(value, (int, float)):
        return float(value)

    # Convert to string and clean
    value_str = str(value).strip().lower()

    # Extract the number part, removing words like "shares", "ratio", etc.
    value_str = re.sub(r'shares|ratio|conversion|approx\.?|approximately|about|around|est\.?|estimated',
                       '', value_str, flags=re.IGNORECASE)

    return extract_number(value_str)


def clean_dataframe(df):
    """Clean the entire dataframe"""
    print("Cleaning dataframe...")

    # Make a copy to avoid modifying the original
    df = df.copy()

    # Clean column names
    df.columns = [str(col).lower().strip().replace(' ', '_')
                  for col in df.columns]

    # Identify column types based on name
    date_cols = [col for col in df.columns if any(term in col.lower() for term in [
                                                  'date', 'time', 'day', 'month', 'year', 'maturity'])]
    percent_cols = [col for col in df.columns if any(
        term in col.lower() for term in ['percent', 'rate', 'yield', 'coupon'])]
    price_cols = [col for col in df.columns if 'price' in col.lower()]
    number_cols = [col for col in df.columns if any(
        term in col.lower() for term in ['cost', 'value', 'amount', 'quantity', 'qty'])]
    code_cols = [col for col in df.columns if any(term in col.lower() for term in [
                                                  'ticker', 'symbol', 'cusip', 'isin', 'code'])]
    conversion_cols = [col for col in df.columns if any(
        term in col.lower() for term in ['conversion', 'shares', 'ratio'])]
    company_cols = [col for col in df.columns if any(
        term in col.lower() for term in ['company', 'issuer', 'name', 'entity'])]
    action_cols = [col for col in df.columns if any(term in col.lower() for term in [
                                                    'side', 'status', 'direction', 'availability', 'action', 'type'])]

    # Clean all string values
    for col in df.select_dtypes(include=['object']).columns:
        df[col] = df[col].apply(clean_text)

    # Apply specialized cleaning functions to identified columns
    print("Cleaning specialized columns...")
    for col in company_cols:
        df[col] = df[col].apply(clean_company_name)

    for col in action_cols:
        df[col] = df[col].apply(normalize_action_code)

    for col in date_cols:
        df[col] = df[col].apply(clean_date)

    for col in percent_cols:
        df[col] = df[col].apply(clean_percentage)
        df[col] = pd.to_numeric(df[col], errors='coerce')

    for col in price_cols:
        original_valid_count = df[col].count()
        df[col] = df[col].apply(extract_number)
        df[col] = pd.to_numeric(df[col], errors='coerce')

        # Check for significant data loss
        new_valid_count = df[col].count()
        if original_valid_count > 0:
            missing_pct = (original_valid_count -
                           new_valid_count) / original_valid_count * 100
            if missing_pct > 80:
                print(
                    f"WARNING: Price column '{col}' lost {missing_pct:.1f}% of values during cleaning")

    for col in number_cols:
        df[col] = df[col].apply(extract_number)
        df[col] = pd.to_numeric(df[col], errors='coerce')

    for col in code_cols:
        df[col] = df[col].apply(clean_code)

    for col in conversion_cols:
        df[col] = df[col].apply(clean_conversion_ratio)
        df[col] = pd.to_numeric(df[col], errors='coerce')

    # Try to convert remaining columns to appropriate types
    print("Processing remaining columns...")
    for col in df.columns:
        if col not in date_cols + percent_cols + price_cols + number_cols + code_cols + conversion_cols + company_cols + action_cols:
            # Sample values to determine type
            sample = df[col].dropna().head(20).tolist()

            if sample:
                # Check if column might be numeric
                if all(isinstance(x, (int, float)) or (isinstance(x, str) and re.search(r'[-+]?\d*\.?\d+', x)) for x in sample):
                    df[col] = df[col].apply(extract_number)
                    df[col] = pd.to_numeric(df[col], errors='coerce')

                # Check if column might be dates
                elif all(isinstance(x, str) and re.search(r'\d{1,2}[/-]\d{1,2}[/-]\d{2,4}|\d{4}[/-]\d{1,2}[/-]\d{1,2}', x) for x in sample):
                    df[col] = df[col].apply(clean_date)

                # Check if column might be percentages
                elif any(isinstance(x, str) and ('%' in x or 'percent' in x.lower() or 'bps' in x.lower()) for x in sample):
                    df[col] = df[col].apply(clean_percentage)
                    df[col] = pd.to_numeric(df[col], errors='coerce')

                # Check if column might contain company names
                elif any(isinstance(x, str) and len(x.split()) > 1 and any(suffix in x.lower() for suffix in ['inc', 'corp', 'llc', 'ltd', 'plc']) for x in sample):
                    df[col] = df[col].apply(clean_company_name)

                # Check if column might contain action codes
                elif any(isinstance(x, str) and x.upper() in ['BUY', 'SELL', 'SPCL', 'HTB', 'ETB'] for x in sample):
                    df[col] = df[col].apply(normalize_action_code)

    # Drop columns that are 100% empty (all values are NaN)
    cols_to_drop = [col for col in df.columns if df[col].isna().all()]
    if cols_to_drop:
        print(f"Dropping {len(cols_to_drop)} columns that are 100% empty")
        df = df.drop(columns=cols_to_drop)

    print(
        f"Final shape after cleaning: {df.shape[0]} rows, {df.shape[1]} columns")
    return df


def process_file(input_path, output_path=None):
    """Process a file from start to finish"""
    print(f"Processing file: {input_path}")

    # Load the file
    df = load_file(input_path)
    if df is None:
        print("File loading failed")
        return None

    # Generate output filename if not provided
    if output_path is None:
        base_filename = os.path.basename(input_path)
        filename_no_ext = os.path.splitext(base_filename)[0]
        output_path = os.path.join(os.path.dirname(
            input_path), f"cleaned_{filename_no_ext}.csv")

    # Clean the data
    df_clean = clean_dataframe(df)

    # Save the cleaned data
    print(f"Saving cleaned data to: {output_path}")
    df_clean.to_csv(output_path, index=False)
    print("Cleaning complete!")
    return df_clean


if __name__ == "__main__":
    try:
        input_file = input("Enter file path (.csv or .xlsx): ")
        cleaned_df = process_file(input_file)
    except Exception as e:
        print(f"Error: {str(e)}")
