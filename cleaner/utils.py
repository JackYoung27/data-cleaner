import pandas as pd
import numpy as np
import os
import re
from datetime import datetime

NULL_VALUES = ['', 'null', 'none', 'n/a', 'na',
               '-', '--', '—', '#n/a', '#na', 'nan', '#value!']


def clean_text(value):
    if not isinstance(value, str):
        return value
    cleaned = value.strip()
    cleaned = re.sub(r'[‚Äî,â€,Ã,Â]', '', cleaned)
    cleaned = re.sub(r'[^\x20-\x7E]', '', cleaned)
    cleaned = re.sub(r'\s+', ' ', cleaned).strip()
    if not cleaned or cleaned.lower() in NULL_VALUES:
        return np.nan
    return cleaned


def clean_company_name(value):
    if not isinstance(value, str):
        value = str(value)
    cleaned = clean_text(value)
    if pd.isna(cleaned):
        return np.nan
    cleaned = re.sub(r'[^\w\s\.]', ' ', cleaned)
    cleaned = re.sub(r'\s+', ' ', cleaned).strip()
    cleaned = cleaned.title()
    for suffix in [' Inc', ' Corp', ' Llc', ' Ltd', ' Plc', ' Sa', ' Ag', ' Se', ' Nv']:
        if cleaned.endswith(suffix):
            cleaned = cleaned[:-len(suffix)] + suffix.upper()
    return cleaned


def normalize_action_code(value):
    if pd.isna(value):
        return np.nan
    if not isinstance(value, str):
        value = str(value)
    cleaned = clean_text(value)
    if pd.isna(cleaned):
        return np.nan
    cleaned = cleaned.upper()
    action_map = {
        'B': 'BUY', 'BUY': 'BUY', 'PURCHASE': 'BUY', 'BOUGHT': 'BUY', 'LONG': 'BUY',
        'S': 'SELL', 'SELL': 'SELL', 'SOLD': 'SELL', 'SHORT': 'SELL',
        'SPCL': 'SPCL', 'SPECIAL': 'SPCL',
        'HTB': 'HTB', 'HARD TO BORROW': 'HTB', 'HARDTOBORROW': 'HTB',
        'ETB': 'ETB', 'EASY TO BORROW': 'ETB', 'EASYTOBORROW': 'ETB'
    }
    for key, std_code in action_map.items():
        if key in cleaned:
            return std_code
    return cleaned


def extract_number(value):
    if isinstance(value, (int, float)):
        return float(value)
    if not isinstance(value, str):
        return np.nan
    value = clean_text(value)
    if pd.isna(value):
        return np.nan
    value = value.strip('"\'')
    value = re.sub(r'[$£€¥]|USD|EUR|JPY|GBP|CAD|AUD|CHF',
                   '', value, flags=re.IGNORECASE)
    value = re.sub(r'Approx\.?|Approximately|About|Around|Est\.?|Estimated|shares|units',
                   '', value, flags=re.IGNORECASE)
    value = re.sub(r'\s+', '', value)
    if ',' in value and '.' not in value:
        value = value.replace(',', '.')
    match = re.search(r'[-+]?\d*\.?\d+', value)
    if match:
        try:
            return float(match.group(0))
        except:
            return np.nan
    return np.nan


def clean_percentage(value):
    if pd.isna(value):
        return np.nan
    if isinstance(value, (int, float)):
        return value / 100.0 if value > 1 and value <= 100 else value
    value_str = str(value).strip().lower()
    if 'basis point' in value_str or 'bps' in value_str:
        num = extract_number(value_str)
        if not pd.isna(num):
            return num / 10000.0
        return np.nan
    num = extract_number(value_str)
    if pd.isna(num):
        return np.nan
    if '%' in value_str or 'percent' in value_str or 'pct' in value_str:
        return num / 100.0
    elif num > 1 and num <= 100:
        return num / 100.0
    return num


def clean_date(value):
    if pd.isna(value):
        return np.nan
    if isinstance(value, pd.Timestamp):
        return value.strftime('%m/%d/%Y')
    try:
        if not isinstance(value, str):
            value = str(value)
        value = clean_text(value)
        if pd.isna(value):
            return np.nan
        formats = [
            '%m/%d/%Y', '%m-%d-%Y', '%Y-%m-%d', '%Y.%m.%d', '%d/%m/%Y',
            '%m/%d/%y', '%d-%b-%y', '%d-%b-%Y', '%B %d, %Y', '%d %B %Y',
            '%b %d, %Y', '%Y%m%d', '%d.%m.%Y', '%d.%m.%y'
        ]
        for fmt in formats:
            try:
                date_obj = datetime.strptime(value, fmt)
                if date_obj.year < 100:
                    if date_obj.year >= 50:
                        date_obj = date_obj.replace(year=date_obj.year + 1900)
                    else:
                        date_obj = date_obj.replace(year=date_obj.year + 2000)
                if 1900 <= date_obj.year <= datetime.now().year + 5:
                    return date_obj.strftime('%m/%d/%Y')
            except:
                continue
        date_obj = pd.to_datetime(value, errors='coerce')
        if pd.notna(date_obj) and 1900 <= date_obj.year <= datetime.now().year + 5:
            return date_obj.strftime('%m/%d/%Y')
        return np.nan
    except:
        return np.nan


def clean_code(value):
    if pd.isna(value):
        return np.nan
    if not isinstance(value, str):
        value = str(value)
    value = clean_text(value)
    if pd.isna(value):
        return np.nan
    cleaned = re.sub(r'[^a-zA-Z0-9]', '', value).upper()
    return cleaned if cleaned else np.nan


def clean_conversion_ratio(value):
    if pd.isna(value):
        return np.nan
    if isinstance(value, (int, float)):
        return float(value)
    value_str = str(value).strip().lower()
    value_str = re.sub(r'shares|ratio|conversion|approx\.?|approximately|about|around|est\.?|estimated',
                       '', value_str, flags=re.IGNORECASE)
    return extract_number(value_str)
