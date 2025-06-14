# Trade Data Cleaner

## Overview

This script is built to clean and normalize messy trade data from .csv or .xlsx files. It handles real-world formatting issues including inconsistent date formats, incorrect tickers, reversed company names, percentage anomalies, and text issues.

The cleaning logic is applicable to a broad range of structured financial data.

This project is modularized into:
- `loader.py` – for file reading
- `cleaner.py` – for cleaning logic
- `utils.py` – for shared helpers and constants
- `feature_engineer.py` – for generating financial modeling features
- `model_preview.py` – runs Ridge regression to test explanatory power of features
- `main.py` – for running the full end-to-end pipeline

## Key Features

### Cleaning
- Standardizes date formats to MM/DD/YYYY
- Normalizes tickers, CUSIPs, ISINs, and issuer names
- Converts percentages (%, basis points, etc.) to decimal values
- Extracts numeric values from strings like "$105.75" or "one thousand"
- Corrects company names
- Cleans all text fields of Unicode and special characters
- Drops columns that are 100% empty
- Saves cleaned data as cleaned_(filename).csv in the same directory

### Feature Engineering
If the relevant columns exist, the pipeline also generates:
- `daily_return`: percent change in `price`
- `rolling_vol_20d`: 20-day rolling standard deviation of return
- `benchmark_spread`: `yield - benchmark_yield`
- `near_parity`: binary flag for prices within $5 of par value
- `called_early`: binary flag if `call_date` is before `maturity_date`
- If `par_value` is missing, the script assumes a default value of 100.
- Feature computations like `called_early` and `benchmark_spread` are only performed when required columns are present.
- A blank column named `----` is inserted before all generated feature columns to visually separate them from the original data.

### Model Preview
After feature engineering, the pipeline:
- Detects `actual_price` and `theoretical_price` columns (e.g., `price`, `model_price`)
- Computes `price_deviation = actual - theoretical`
- Selects usable numeric features using keyword matching (e.g., `volatility`, `spread`, `parity`)
- Drops rows with missing or non-numeric data
- Trains a Ridge regression model to predict the deviation
- Prints:
  - Test set MSE (Mean Squared Error)
  - Feature coefficients
  - 3 example predictions (actual vs predicted)

This helps assess whether your features meaningfully explain pricing error.

## How to Run

1. Open a terminal.

2. Navigate to the folder containing `main.py`.

3. Activate your virtual environment (if applicable), then run the script:

       python main.py

4. When prompted, enter the full path to the raw input file (CSV or Excel):

       Enter file path (.csv or .xlsx): /path/to/your_file.xlsx

5. Output will be saved as:

       cleaned_your_file.csv

## Dependencies

- Python 3.10 or higher
- pandas
- numpy
- openpyxl
- scikit-learn

Install dependencies using:

    pip install -r requirements.txt

## Supported Columns

The cleaner will automatically detect and process columns with names like:

- Ticker, CUSIP, ISIN
- Trade Date, Execution Timestamp, Call Date, Maturity Date
- Notional Amount, Price, Quantity
- Conversion Ratio, Coupon, Yield, Benchmark Yield
- Issuer, Side, Venue

Column detection is based on keyword matching in column names.

## Output

- The cleaned file will be saved as a .csv in the same directory as the input file.

## Contact

Jack Young  
youngjh@iu.edu
