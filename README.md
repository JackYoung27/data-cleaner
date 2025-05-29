# Trade Data Cleaner

## Overview

This script is built to clean and normalize messy trade data from .csv or .xlsx files. It handles real-world formatting issues including inconsistent date formats, incorrect tickers, reversed company names, percentage anomalies, and text issues.

The cleaning logic is applicable to a broad range of structured financial data.

## Key Features
- Standardizes date formats to MM/DD/YYYY
- Normalizes tickers, CUSIPs, ISINs, and issuer names
- Converts percentages (%, basis points, etc.) to decimal values
- Extracts numeric values from strings like "$105.75" or "one thousand"
- Corrects company names
- Cleans all text fields of Unicode and special characters
- Drops columns that are 100% empty
- Saves cleaned data as cleaned_(filename).csv in the same directory

## How to Run

1. Open a terminal.

2. Navigate to the folder containing data_cleaner.py.

3. Run the script:

       python data_cleaner.py

4. When prompted, enter the full path to the raw input file (CSV or Excel):

       Enter file path (.csv or .xlsx): /path/to/[your data].xlsx

5. Output will be saved as:

       cleaned_[your data].csv

## Dependencies

- Python 3.10 or higher
- pandas
- numpy
- re
- datetime
- os

Install dependencies using:

    pip install pandas numpy

## Supported Column

The cleaner will automatically detect and process columns with names like:

- Ticker, CUSIP, ISIN
- Trade Date, Execution Timestamp
- Notional Amount, Price, Quantity
- Conversion Ratio, Coupon, Yield
- Issuer, Side, Venue

Column detection is based on keyword matching in column names.

## Output

- The cleaned file will be saved as a .csv in the same directory as the input file.

## Contact

Jack Young  
youngjh@iu.edu
