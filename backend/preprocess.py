"""
Data Preprocessing Script
Converts raw Kaggle dataset to processed format
"""

import pandas as pd
import sys


def preprocess_dataset(input_path: str, output_path: str):
    """
    Preprocess perfume dataset
    
    Parameters:
    -----------
    input_path : str
        Path to raw CSV file
    output_path : str
        Path to save processed CSV
    """
    print(f"Loading data from {input_path}...")
    df = pd.read_csv(input_path, encoding='ISO-8859-1', sep=';', engine='python')
    
    print(f"Loaded {len(df)} perfumes")
    
    # Rename columns
    column_mapping = {
        'Perfume': 'name',
        'Top': 'top_notes',
        'Middle': 'middle_notes',
        'Base': 'base_notes',
        'Rating Value': 'rating',
        'Rating Count': 'review_count'
    }
    df = df.rename(columns=column_mapping)
    
    # Combine main accords
    accord_cols = ['mainaccord1', 'mainaccord2', 'mainaccord3', 'mainaccord4', 'mainaccord5']
    df['main_accords'] = df[accord_cols].fillna('').agg(','.join, axis=1)
    df['main_accords'] = df['main_accords'].str.strip(',').str.replace(',,', ',')
    
    # Fix European decimal format
    df['rating'] = df['rating'].astype(str).str.replace(',', '.', regex=False)
    df['rating'] = pd.to_numeric(df['rating'], errors='coerce').fillna(0)
    
    df['review_count'] = df['review_count'].astype(str).str.replace(',', '', regex=False)
    df['review_count'] = pd.to_numeric(df['review_count'], errors='coerce').fillna(0).astype(int)
    
    # Standardize brand names
    df['brand_clean'] = df['Brand'].str.lower().str.strip()
    
    # Save processed data
    print(f"Saving processed data to {output_path}...")
    df.to_csv(output_path, index=False, encoding='utf-8')
    
    print("Data preprocessing complete")
    print(f"  Total perfumes: {len(df)}")
    print(f"  Unique brands: {df['Brand'].nunique()}")
    print(f"  Rating range: {df['rating'].min():.2f} - {df['rating'].max():.2f}")
    print(f"  Avg rating: {df['rating'].mean():.2f}")
    print(f"  Avg reviews: {df['review_count'].mean():.0f}")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python preprocess.py <input_csv> <output_csv>")
        print("Example: python preprocess.py fra_cleaned.csv perfumes_processed.csv")
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_file = sys.argv[2]
    
    preprocess_dataset(input_file, output_file)