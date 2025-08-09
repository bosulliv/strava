#!/usr/bin/env python3
"""Test automatic token refresh functionality"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.strava_data_fetcher import StravaDataFetcher

def main():
    fetcher = StravaDataFetcher()
    
    print("Testing automatic token refresh...")
    
    # Test that refresh method works
    try:
        original_token = fetcher.auth.access_token
        print(f"Original token: {original_token[:20]}...")
        
        fetcher.refresh_and_update_token()
        
        new_token = fetcher.auth.access_token
        print(f"New token: {new_token[:20]}...")
        
        if original_token != new_token:
            print("✓ Token was refreshed successfully")
        else:
            print("⚠ Token appears unchanged")
            
        # Test API call works
        activities = fetcher.get_athlete_activities(per_page=2, page=1)
        print(f"✓ API call successful, got {len(activities)} activities")
        
    except Exception as e:
        print(f"✗ Test failed: {e}")

if __name__ == "__main__":
    main()