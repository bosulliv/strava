"""
Test script to debug kudos API issues
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.strava_data_fetcher import StravaDataFetcher
import pandas as pd

def test_kudos_api():
    print("Testing Strava kudos API...")
    
    try:
        fetcher = StravaDataFetcher()
        
        # Get a few recent activities first
        print("Fetching recent activities...")
        activities = fetcher.get_athlete_activities(per_page=5, page=1)
        
        if not activities:
            print("No activities found!")
            return
        
        print(f"Found {len(activities)} recent activities")
        
        # Test kudos API on the first few activities
        for i, activity in enumerate(activities[:3]):
            activity_id = activity['id']
            kudos_count = activity.get('kudos_count', 0)
            activity_name = activity.get('name', 'Unknown')
            
            print(f"\nActivity {i+1}: {activity_name}")
            print(f"  ID: {activity_id}")
            print(f"  Reported kudos count: {kudos_count}")
            
            if kudos_count > 0:
                print(f"  Trying to fetch kudos details...")
                try:
                    kudos_details = fetcher.get_activity_kudos(activity_id)
                    print(f"  Success! Got {len(kudos_details)} detailed kudos")
                    
                    if kudos_details:
                        print("  Sample kudos:")
                        for j, kudos in enumerate(kudos_details[:3]):
                            name = f"{kudos.get('firstname', '')} {kudos.get('lastname', '')}".strip()
                            print(f"    {j+1}. {name}")
                        break
                except Exception as e:
                    print(f"  Failed: {e}")
            else:
                print(f"  No kudos to fetch for this activity")
    
    except Exception as e:
        print(f"Error in test: {e}")

if __name__ == "__main__":
    test_kudos_api()