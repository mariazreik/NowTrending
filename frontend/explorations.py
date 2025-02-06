import pandas as pd
import numpy as np
import sys
import os
import re

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from frontend.transformation import transform_twitter_trend, transform_twitter_locations, transform_google_locations, transform_google_trend

import re
import numpy as np

def extract_numeric(meta_desc):
    # Remove commas in case there are any (e.g., "9,969")
    meta_desc = meta_desc.replace(',', '')
    
    # Use regex to capture the numeric part (including decimals) and an optional suffix (K or M)
    match = re.search(r'(\d+(?:\.\d+)?)\s*([KM])?', meta_desc, re.IGNORECASE)
    if match:
        # Convert the captured numeric part to a float
        try:
            number = float(match.group(1))
        except ValueError:
            return np.nan
        
        suffix = match.group(2)
        if suffix:
            suffix = suffix.upper()
            if suffix == 'K':  # Thousands
                number *= 1000
            elif suffix == 'M':  # Millions
                number *= 1000000
        return number
    else:
        return np.nan

def twitter_data():
    # Assuming transform_twitter_trend() gives you a DataFrame
    df = transform_twitter_trend()
    df_loc = transform_twitter_locations()
    
    # Drop duplicates based on the 'trend' column
    df = df.drop_duplicates(subset=['trend'])

    # Remove rows where 'meta_description' is missing or empty
    df = df[df['meta_description'].notna() & (df['meta_description'] != '')]

    # Merge the DataFrames on 'location_id' using an inner join
    merged_df = pd.merge(df_loc, df, on='location_id', how='inner')
    
    # Create a new column 'meta_description_numeric' for sorting by extracting the numeric value
    merged_df['meta_description_numeric'] = merged_df['meta_description'].apply(extract_numeric)
    
    # Sort by the numeric part of the 'meta_description' in descending order
    df_sorted = merged_df.sort_values('meta_description_numeric', ascending=False)

    # Select only the columns you want to display
    df_sorted = df_sorted[['trend', 'meta_description', 'domain_context', 'url', 'country']]
    df_sorted.rename(columns={'trend': 'Trend', 
                              'meta_description': 'Popularity', 
                              'url': 'URL'}, inplace=True)
    
    # Output the sorted DataFrame (top 10 rows, if that's your intent)
    return df_sorted


def top5_per_context():
    # First, ensure your DataFrame is sorted by last_updated in descending order
    df = transform_twitter_trend()
    df_sorted = df[['trend', 'domain_context', 'last_updated', 'url']]
    df_sorted = df_sorted.sort_values('last_updated', ascending=False)
    df_sorted = df_sorted[df_sorted['domain_context'].notna() & (df_sorted['domain_context'] != '')]
    
    # Then, for each domain_context group, take the first 5 rows
    top5_per_context = df_sorted.groupby('domain_context').head(5).reset_index(drop=True)
    
    # Rename columns for clarity
    top5_per_context.rename(columns={'trend':'Trend', 'domain_context':'Category'}, inplace=True)
    
    # Drop duplicate trends only (if that's what you intend)
    top5_per_context.drop_duplicates(subset=['Trend'], inplace=True)

    return top5_per_context


def trend_growth():
    df = transform_twitter_trend()
    
    # Count occurrences of each trend
    trend_counts = df['trend'].value_counts()
    
    # Filter trends that appear more than 3 times
    valid_trends = trend_counts[trend_counts > 3].index
    
    # Filter the dataframe to keep only valid trends
    df_filtered = df[df['trend'].isin(valid_trends)]
    
    # Select relevant columns
    df_sorted = df_filtered[['trend', 'meta_description', 'last_updated']]
    
    return df_sorted

def google_loc():
    df_loc = transform_google_locations()
    df_trend = transform_google_trend()
    df_loc.rename(columns={'id' :'google_location_id', 'country':'Country'},inplace=True)
    df_merged = pd.merge(df_loc, df_trend, on='google_location_id', how='inner')
    df_merged.rename(columns={'trend' :'Trend'}, inplace=True)
    df_sorted = df_merged[['Trend', 'Country', 'last_updated']]
    return df_sorted