"""
Debug kudos fetching in isolation
"""
from strava_data_fetcher import StravaDataFetcher

def debug_kudos():
    print("=== DEBUGGING KUDOS FETCH ===")
    
    fetcher = StravaDataFetcher()
    
    # Get recent activities
    print("1. Fetching recent activities...")
    activities = fetcher.fetch_all_activities(max_activities=10)  # Just 10 for testing
    
    if not activities:
        print("No activities found!")
        return
    
    print(f"Got {len(activities)} activities")
    
    # Convert to DataFrame to get IDs
    df = fetcher.activities_to_dataframe(activities)
    activity_ids = df['id'].tolist()
    
    print(f"Activity IDs: {activity_ids}")
    print(f"Kudos counts from activities: {df['kudos_count'].tolist()}")
    
    # Now try to fetch kudos
    print("\n2. Fetching kudos data...")
    kudos_data = fetcher.fetch_kudos_givers(activity_ids, max_activities_for_kudos=5)  # Just 5 for testing
    
    print(f"\nFinal result: {len(kudos_data)} kudos entries")
    if kudos_data:
        print("Sample kudos data:")
        for i, kudos in enumerate(kudos_data[:5]):
            print(f"  {i+1}. Activity {kudos['activity_id']}: {kudos['athlete_fullname']}")

if __name__ == "__main__":
    debug_kudos()