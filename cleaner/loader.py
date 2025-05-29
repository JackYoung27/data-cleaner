import pandas as pd
import numpy as np
import re
import os
from datetime import datetime

NULL_VALUES = ['', 'null', 'none', 'n/a', 'na',
               '-', '--', '—', '#n/a', '#na', 'nan', '#value!']

def load_file(file_path):
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