#!/usr/bin/env python3
"""Debug script to examine raw activity data and timestamp issues"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import pandas as pd
from src.strava_data_fetcher import StravaDataFetcher

def main():
    fetcher = StravaDataFetcher()
    
    # Fetch just a few activities from API
    print("=== RAW API DATA ===")
    raw_activities = fetcher.get_athlete_activities(per_page=3, page=1)
    
    print(f"Fetched {len(raw_activities)} raw activities")
    for i, activity in enumerate(raw_activities[:2]):
        print(f"\nActivity {i+1}:")
        print(f"  ID: {activity.get('id')}")
        print(f"  Name: {activity.get('name')}")
        print(f"  Raw start_date: {activity.get('start_date')} (type: {type(activity.get('start_date'))})")
        
    print("\n=== CONVERTED TO DATAFRAME ===")
    df = fetcher.activities_to_dataframe(raw_activities)
    print(f"DataFrame shape: {df.shape}")
    
    if not df.empty:
        print(f"start_date column type: {df['start_date'].dtype}")
        print(f"start_date_parsed column type: {df['start_date_parsed'].dtype}")
        print(f"Sample start_date values:")
        print(df[['start_date', 'start_date_parsed']].head(2))
    
    print("\n=== EXISTING CSV DATA ===")
    try:
        existing_df = pd.read_csv('data/activities.csv')
        print(f"Existing CSV shape: {existing_df.shape}")
        
        if 'start_date_parsed' in existing_df.columns:
            print(f"Existing start_date_parsed column type: {existing_df['start_date_parsed'].dtype}")
            print("Sample existing start_date_parsed values:")
            print(existing_df['start_date_parsed'].head(3))
        else:
            print("No start_date_parsed column in existing data")
            
    except FileNotFoundError:
        print("No existing activities.csv file found")

if __name__ == "__main__":
    main()