"""
Strava Data Collector - Incrementally collect and store activity data
"""
import pandas as pd
import json
import os
from datetime import datetime, timezone
from strava_data_fetcher import StravaDataFetcher

class StravaDataCollector:
    def __init__(self, data_dir="data"):
        self.fetcher = StravaDataFetcher()
        self.data_dir = data_dir
        self.activities_file = os.path.join(data_dir, "activities.csv")
        self.kudos_file = os.path.join(data_dir, "kudos.csv")
        self.metadata_file = os.path.join(data_dir, "collection_metadata.json")
        
        # Create data directory if it doesn't exist
        os.makedirs(data_dir, exist_ok=True)
        
        # Load existing metadata
        self.metadata = self.load_metadata()
    
    def load_metadata(self):
        """Load collection metadata or create default"""
        if os.path.exists(self.metadata_file):
            with open(self.metadata_file, 'r') as f:
                return json.load(f)
        else:
            return {
                "last_activity_fetch": None,
                "last_activity_id": None,
                "activities_with_kudos": [],
                "kudos_fetch_completed": False,
                "total_activities": 0,
                "last_updated": None
            }
    
    def save_metadata(self):
        """Save collection metadata"""
        self.metadata["last_updated"] = datetime.now(timezone.utc).isoformat()
        with open(self.metadata_file, 'w') as f:
            json.dump(self.metadata, f, indent=2)
    
    def load_existing_activities(self):
        """Load existing activities CSV if it exists"""
        if os.path.exists(self.activities_file):
            return pd.read_csv(self.activities_file)
        else:
            return pd.DataFrame()
    
    def load_existing_kudos(self):
        """Load existing kudos CSV if it exists"""
        if os.path.exists(self.kudos_file):
            return pd.read_csv(self.kudos_file)
        else:
            return pd.DataFrame()
    
    def fetch_new_activities(self, max_new_activities=None):
        """Fetch activities that haven't been collected yet"""
        print("=== FETCHING ACTIVITIES ===")
        
        existing_df = self.load_existing_activities()
        existing_ids = set(existing_df['id'].tolist()) if not existing_df.empty else set()
        
        print(f"Found {len(existing_ids)} existing activities")
        
        # Fetch all activities from API
        all_activities = self.fetcher.fetch_all_activities(max_activities=max_new_activities)
        
        # Filter to new activities only
        new_activities = [a for a in all_activities if a['id'] not in existing_ids]
        
        if not new_activities:
            print("No new activities found")
            return existing_df
        
        print(f"Found {len(new_activities)} new activities")
        
        # Convert new activities to DataFrame
        new_df = self.fetcher.activities_to_dataframe(new_activities)
        
        # Combine with existing data
        if existing_df.empty:
            combined_df = new_df
        else:
            combined_df = pd.concat([existing_df, new_df], ignore_index=True)
            # Remove duplicates just in case
            combined_df = combined_df.drop_duplicates(subset=['id'])
        
        # Sort by start date (newest first)
        if 'start_date_parsed' in combined_df.columns:
            combined_df = combined_df.sort_values('start_date_parsed', ascending=False)
        
        # Save updated activities
        combined_df.to_csv(self.activities_file, index=False)
        
        # Update metadata
        if not combined_df.empty:
            latest_activity = combined_df.iloc[0]
            self.metadata["last_activity_id"] = int(latest_activity['id'])
            self.metadata["last_activity_fetch"] = latest_activity['start_date']
            self.metadata["total_activities"] = len(combined_df)
        
        self.save_metadata()
        
        print(f"Activities saved to {self.activities_file}")
        print(f"Total activities in dataset: {len(combined_df)}")
        
        return combined_df
    
    def fetch_kudos_for_activities(self, activity_ids=None, batch_size=20):
        """Fetch kudos data for specified activities or continue from where we left off"""
        print("=== FETCHING KUDOS ===")
        
        activities_df = self.load_existing_activities()
        if activities_df.empty:
            print("No activities found. Run fetch_new_activities first.")
            return pd.DataFrame()
        
        existing_kudos_df = self.load_existing_kudos()
        activities_with_kudos = set(existing_kudos_df['activity_id'].tolist()) if not existing_kudos_df.empty else set()
        
        if activity_ids is None:
            # Get activities that don't have kudos data yet, prioritize by kudos_count
            activities_needing_kudos = activities_df[~activities_df['id'].isin(activities_with_kudos)]
            
            if activities_needing_kudos.empty:
                print("All activities already have kudos data")
                return existing_kudos_df
            
            # Sort by kudos_count descending to prioritize high-engagement activities
            activities_needing_kudos = activities_needing_kudos.sort_values('kudos_count', ascending=False)
            activity_ids = activities_needing_kudos['id'].tolist()[:batch_size]
        
        print(f"Fetching kudos for {len(activity_ids)} activities")
        print(f"Activity IDs: {activity_ids[:5]}{'...' if len(activity_ids) > 5 else ''}")
        
        # Fetch kudos data
        kudos_data = self.fetcher.fetch_kudos_givers(activity_ids, max_activities_for_kudos=len(activity_ids))
        
        if not kudos_data:
            print("No kudos data retrieved")
            return existing_kudos_df
        
        # Convert to DataFrame
        new_kudos_df = pd.DataFrame(kudos_data)
        
        # Combine with existing kudos data
        if existing_kudos_df.empty:
            combined_kudos_df = new_kudos_df
        else:
            combined_kudos_df = pd.concat([existing_kudos_df, new_kudos_df], ignore_index=True)
            # Remove duplicates
            combined_kudos_df = combined_kudos_df.drop_duplicates(subset=['activity_id', 'athlete_id'])
        
        # Save updated kudos data
        combined_kudos_df.to_csv(self.kudos_file, index=False)
        
        # Update metadata
        self.metadata["activities_with_kudos"] = list(set(combined_kudos_df['activity_id'].tolist()))
        self.save_metadata()
        
        print(f"Kudos data saved to {self.kudos_file}")
        print(f"Total kudos records: {len(combined_kudos_df)}")
        print(f"Activities with kudos data: {len(self.metadata['activities_with_kudos'])}")
        
        return combined_kudos_df
    
    def get_collection_status(self):
        """Display current collection status"""
        print("=== COLLECTION STATUS ===")
        
        activities_df = self.load_existing_activities()
        kudos_df = self.load_existing_kudos()
        
        print(f"Total activities: {len(activities_df)}")
        print(f"Activities with kudos data: {len(set(kudos_df['activity_id'].tolist())) if not kudos_df.empty else 0}")
        print(f"Total kudos records: {len(kudos_df)}")
        
        if not activities_df.empty:
            print(f"Date range: {activities_df['start_date'].min()} to {activities_df['start_date'].max()}")
            print(f"Activity types: {', '.join(activities_df['type'].value_counts().head().index.tolist())}")
        
        print(f"Last updated: {self.metadata.get('last_updated', 'Never')}")
        
        return {
            "total_activities": len(activities_df),
            "activities_with_kudos": len(set(kudos_df['activity_id'].tolist())) if not kudos_df.empty else 0,
            "total_kudos": len(kudos_df),
            "metadata": self.metadata
        }

def main():
    """Main collection script"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Collect Strava data incrementally")
    parser.add_argument("--activities-only", action="store_true", help="Only fetch activities, skip kudos")
    parser.add_argument("--kudos-only", action="store_true", help="Only fetch kudos for existing activities")
    parser.add_argument("--kudos-batch-size", type=int, default=20, help="Number of activities to fetch kudos for")
    parser.add_argument("--max-activities", type=int, help="Maximum number of activities to fetch")
    parser.add_argument("--status", action="store_true", help="Show collection status and exit")
    
    args = parser.parse_args()
    
    collector = StravaDataCollector()
    
    if args.status:
        collector.get_collection_status()
        return
    
    if not args.kudos_only:
        # Fetch activities
        collector.fetch_new_activities(max_new_activities=args.max_activities)
    
    if not args.activities_only:
        # Fetch kudos
        collector.fetch_kudos_for_activities(batch_size=args.kudos_batch_size)
    
    # Show final status
    collector.get_collection_status()

if __name__ == "__main__":
    main()