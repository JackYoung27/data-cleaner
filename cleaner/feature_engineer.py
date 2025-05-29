import pandas as pd
import numpy as np


def add_features(df):
    """Add financial features to a cleaned DataFrame if required columns are present."""
    # Work on a copy to avoid modifying original
    df = df.copy()

    # Add spacer column to separate original data from features
    df['----'] = ''

    # Price-based features
    if 'price' in df.columns:
        # Calculate daily returns if we have at least 2 price points
        if len(df['price'].dropna()) >= 2:
            df['daily_return'] = df['price'].pct_change().round(2)

            # Only compute volatility if we have enough return data points
            if len(df['daily_return'].dropna()) >= 20:
                df['rolling_vol_20d'] = df['daily_return'].rolling(
                    window=20).std().round(2)
            else:
                print("Warning: Insufficient data for rolling volatility calculation")

        # Handle par value with default fallback
        if 'par_value' not in df.columns:
            print("Warning: par_value not found, defaulting to 100")
            df['par_value'] = 100

        # Near parity indicator using actual or default par value
        df['near_parity'] = (df['price'] - df['par_value']
                             ).abs().lt(5).astype(int)

    # Yield spread - only if benchmark yield exists
    if 'yield' in df.columns:
        if 'benchmark_yield' in df.columns:
            df['benchmark_spread'] = (
                df['yield'] - df['benchmark_yield']).round(2)
        else:
            print("Warning: benchmark_yield not found, skipping spread calculation")

    # Early call indicator - safe handling of missing dates
    if 'maturity_date' in df.columns:
        try:
            maturity_date = pd.to_datetime(
                df['maturity_date'], errors='coerce')

            if 'call_date' in df.columns:
                call_date = pd.to_datetime(df['call_date'], errors='coerce')
                # Only compute where both dates are valid
                valid_dates = ~(call_date.isna() | maturity_date.isna())
                df['called_early'] = pd.Series(
                    False, index=df.index)  # Default to False
                df.loc[valid_dates, 'called_early'] = call_date[valid_dates].lt(
                    maturity_date[valid_dates])
                df['called_early'] = df['called_early'].astype(int)
            else:
                print("Warning: call_date not found, skipping early call detection")
        except Exception as e:
            print(f"Warning: Error in date processing: {str(e)}")

    return df
