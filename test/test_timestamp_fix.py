#!/usr/bin/env python3
"""Test the timestamp fix"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import pandas as pd
from src.collect_strava_data import StravaDataCollector

def main():
    collector = StravaDataCollector()
    
    print("Testing timestamp parsing fix...")
    
    # Load existing data 
    existing_df = collector.load_existing_activities()
    print(f"Loaded {len(existing_df)} existing activities")
    
    if not existing_df.empty and 'start_date_parsed' in existing_df.columns:
        print(f"start_date_parsed type: {existing_df['start_date_parsed'].dtype}")
        print("Sample values:")
        print(existing_df['start_date_parsed'].head(3))
        
        # Test sorting
        try:
            sorted_df = existing_df.sort_values('start_date_parsed', ascending=False)
            print("✓ Sorting works!")
        except Exception as e:
            print(f"✗ Sorting failed: {e}")
    else:
        print("No start_date_parsed column found")

if __name__ == "__main__":
    main()