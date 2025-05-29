import pandas as pd


def compute_daily_returns(df: pd.DataFrame) -> pd.DataFrame:
    if 'price' in df.columns:
        df['daily_return'] = df['price'].pct_change()
    return df


def add_rolling_volatility(df: pd.DataFrame, window: int = 20) -> pd.DataFrame:
    if 'daily_return' in df.columns:
        df['volatility'] = df['daily_return'].rolling(window).std()
    return df


def compute_spread_to_par(df: pd.DataFrame) -> pd.DataFrame:
    if 'price' in df.columns and 'par' in df.columns:
        df['spread_to_par'] = (df['price'] - df['par']) / df['par']
    return df


def add_binary_flags(df: pd.DataFrame) -> pd.DataFrame:
    if 'price' in df.columns and 'par' in df.columns:
        df['near_parity'] = (df['price'] >= 0.98 * df['par']
                             ) & (df['price'] <= 1.02 * df['par'])
    if 'call_date' in df.columns and 'maturity_date' in df.columns:
        df['called_early'] = df['call_date'] < df['maturity_date']
    return df


def add_features(df: pd.DataFrame) -> pd.DataFrame:
    df = compute_daily_returns(df)
    df = add_rolling_volatility(df)
    df = compute_spread_to_par(df)
    df = add_binary_flags(df)
    return df
