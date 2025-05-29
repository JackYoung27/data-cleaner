import os
import re
import numpy as np
import pandas as pd
from .utils import (
    clean_text, clean_company_name, normalize_action_code, extract_number,
    clean_percentage, clean_date, clean_code, clean_conversion_ratio
)


def clean_dataframe(df):
    print("Cleaning dataframe...")

    df = df.copy()
    df.columns = [str(col).lower().strip().replace(' ', '_')
                  for col in df.columns]

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

    for col in df.select_dtypes(include=['object']).columns:
        df[col] = df[col].apply(clean_text)

    print("Cleaning specialized columns...")
    for col in company_cols:
        df[col] = df[col].apply(clean_company_name)
    for col in action_cols:
        df[col] = df[col].apply(normalize_action_code)
    for col in date_cols:
        df[col] = df[col].apply(clean_date)
    for col in percent_cols:
        df[col] = pd.to_numeric(df[col].apply(
            clean_percentage), errors='coerce').round(2)
    for col in price_cols:
        df[col] = pd.to_numeric(df[col].apply(
            extract_number), errors='coerce').round(2)
    for col in number_cols:
        df[col] = pd.to_numeric(df[col].apply(
            extract_number), errors='coerce').round(2)
    for col in code_cols:
        df[col] = df[col].apply(clean_code)
    for col in conversion_cols:
        df[col] = pd.to_numeric(df[col].apply(
            clean_conversion_ratio), errors='coerce').round(2)

    print("Processing remaining columns...")
    for col in df.columns:
        if col not in date_cols + percent_cols + price_cols + number_cols + code_cols + conversion_cols + company_cols + action_cols:
            sample = df[col].dropna().head(20).tolist()
            if sample:
                if all(isinstance(x, (int, float)) or (isinstance(x, str) and re.search(r'[-+]?\d*\.?\d+', x)) for x in sample):
                    df[col] = pd.to_numeric(df[col].apply(
                        extract_number), errors='coerce').round(2)
                elif all(isinstance(x, str) and re.search(r'\d{1,2}[/-]\d{1,2}[/-]\d{2,4}|\d{4}[/-]\d{1,2}[/-]\d{1,2}', x) for x in sample):
                    df[col] = df[col].apply(clean_date)
                elif any(isinstance(x, str) and ('%' in x or 'percent' in x.lower() or 'bps' in x.lower()) for x in sample):
                    df[col] = pd.to_numeric(df[col].apply(
                        clean_percentage), errors='coerce').round(2)
                elif any(isinstance(x, str) and len(x.split()) > 1 and any(suffix in x.lower() for suffix in ['inc', 'corp', 'llc', 'ltd', 'plc']) for x in sample):
                    df[col] = df[col].apply(clean_company_name)
                elif any(isinstance(x, str) and x.upper() in ['BUY', 'SELL', 'SPCL', 'HTB', 'ETB'] for x in sample):
                    df[col] = df[col].apply(normalize_action_code)

    cols_to_drop = [col for col in df.columns if df[col].isna().all()]
    if cols_to_drop:
        print(f"Dropping {len(cols_to_drop)} columns that are 100% empty")
        df = df.drop(columns=cols_to_drop)

    print(
        f"Final shape after cleaning: {df.shape[0]} rows, {df.shape[1]} columns")
    return df
