import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.linear_model import Ridge
from sklearn.metrics import mean_squared_error


def run_model_preview(df: pd.DataFrame) -> None:
    """Run a simple Ridge regression model to predict bond price deviations.

    Prints model performance metrics and feature importance.

    Args:
        df: DataFrame containing bond price and feature data
    """
    print("\nRunning Model Preview")
    print("--------------------")

    # Print available columns
    print("\nAvailable columns:")
    print(df.columns.tolist())

    # Find actual price column
    actual_candidates = ['price', 'actual_price',
                         'market_price', 'trade_price']
    actual_col = next(
        (col for col in actual_candidates if col in df.columns), None)

    if actual_col is None:
        # Try fuzzy matching for price column
        price_cols = [col for col in df.columns if 'price' in col.lower(
        ) and 'model' not in col.lower()]
        if price_cols:
            actual_col = price_cols[0]

    # Find theoretical price column
    theoretical_candidates = [
        'model_price', 'theoretical_price', 'calc_price', 'estimated_price']
    theoretical_col = next(
        (col for col in theoretical_candidates if col in df.columns), None)

    if theoretical_col is None:
        # Try fuzzy matching for model price column
        model_cols = [
            col for col in df.columns if 'price' in col.lower() and 'model' in col.lower()]
        if model_cols:
            theoretical_col = model_cols[0]

    if actual_col is None or theoretical_col is None:
        print("\nCould not find required price columns.")
        print("Looked for:")
        print(f"Actual price in: {actual_candidates}")
        print(f"Theoretical price in: {theoretical_candidates}")
        print("Also tried fuzzy matching with 'price' and 'model' keywords")
        return

    print(f"\nUsing columns:")
    print(f"Actual price: {actual_col}")
    print(f"Theoretical price: {theoretical_col}")

    # Clean data
    df = df.dropna(subset=[actual_col, theoretical_col]).copy()
    print(f"Using {len(df)} complete price records")

    # Create target
    df['price_deviation'] = df[actual_col] - df[theoretical_col]

    # Smart feature detection
    desired_features = ['volatility', 'maturity',
                        'spread', 'rating', 'callable', 'parity']
    selected_features = []

    # Find matching columns for each desired feature
    for feature in desired_features:
        for col in df.columns:
            if feature.lower() in col.lower():
                if pd.api.types.is_numeric_dtype(df[col]):
                    selected_features.append(col)
                    print(f"Found {feature} feature: {col}")
                    break
                else:
                    print(f"Skipping non-numeric {feature} feature: {col}")
                    break

    # Check if we have enough features
    if len(selected_features) < 2:
        print("\nWarning: Not enough features found (minimum 2 required)")
        print("Found features:", selected_features)
        return

    print(f"\nSelected features: {', '.join(selected_features)}")

    # Drop rows with NaNs in selected features or target
    df = df.dropna(subset=selected_features + ['price_deviation']).copy()

    # Prepare data
    X = df[selected_features]
    y = df['price_deviation']
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42)

    # Train model
    model = Ridge(alpha=1.0)
    model.fit(X_train, y_train)

    # Get predictions
    y_pred = model.predict(X_test)
    mse = mean_squared_error(y_test, y_pred)

    # Print results
    print("\nModel Results:")
    print(f"Test Set MSE: {mse:.4f}")

    print("\nFeature Coefficients:")
    for feature, coef in zip(selected_features, model.coef_):
        print(f"{feature:20} {coef:>8.4f}")

    # Show prediction examples
    print("\nSample Predictions (Test Set):")
    preview = pd.DataFrame({
        'Actual': y_test.head(),
        'Predicted': y_pred[:5],
        'Difference': y_test.head() - y_pred[:5]
    }).round(4)
    print(preview)
