# main.py

import os
from cleaner.loader import load_file
from cleaner.cleaner import clean_dataframe
from cleaner.feature_engineer import add_features


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

    # Add features
    df_features = add_features(df_clean)

    # Generate features output path
    features_path = os.path.join(os.path.dirname(
        input_path), f"features_{filename_no_ext}.csv")

    # Save the featured data
    print(f"Saving featured data to: {features_path}")
    df_features.to_csv(features_path, index=False)
    print("Feature engineering complete!")

    return df_features


if __name__ == "__main__":
    try:
        input_file = input("Enter file path (.csv or .xlsx): ")
        cleaned_df = process_file(input_file)
    except Exception as e:
        print(f"Error: {str(e)}")
