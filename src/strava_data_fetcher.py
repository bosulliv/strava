"""
Strava Data Fetcher - Retrieves activity data from Strava API
"""
import requests
import pandas as pd
import time
import os
from datetime import datetime
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.strava_auth import StravaAuth

class StravaDataFetcher:
    def __init__(self):
        self.auth = StravaAuth()
        self.base_url = "https://www.strava.com/api/v3"
    
    def refresh_and_update_token(self):
        """Refresh access token and update .env file"""
        try:
            token_data = self.auth.refresh_access_token()
            
            # Update .env file
            env_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env')
            with open(env_path, 'r') as f:
                lines = f.readlines()
            
            with open(env_path, 'w') as f:
                for line in lines:
                    if line.startswith('STRAVA_ACCESS_TOKEN='):
                        f.write(f'STRAVA_ACCESS_TOKEN={token_data["access_token"]}\n')
                    elif line.startswith('STRAVA_REFRESH_TOKEN='):
                        f.write(f'STRAVA_REFRESH_TOKEN={token_data["refresh_token"]}\n')
                    else:
                        f.write(line)
            
            print("Token refreshed and .env updated")
        except Exception as e:
            print(f"Token refresh failed: {e}")
            raise
        
    def get_athlete_activities(self, per_page=50, page=1):
        """Fetch athlete activities"""
        url = f"{self.base_url}/athlete/activities"
        headers = self.auth.get_headers()
        
        params = {
            'per_page': per_page,
            'page': page
        }
        
        response = requests.get(url, headers=headers, params=params)
        
        # Handle token expiry
        if response.status_code == 401:
            print("Token expired, refreshing...")
            self.refresh_and_update_token()
            headers = self.auth.get_headers()
            response = requests.get(url, headers=headers, params=params)
        
        response.raise_for_status()
        return response.json()
    
    def get_activity_details(self, activity_id):
        """Get detailed information about a specific activity"""
        url = f"{self.base_url}/activities/{activity_id}"
        headers = self.auth.get_headers()
        
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        
        return response.json()
    
    def get_activity_kudos(self, activity_id):
        """Get list of athletes who gave kudos to an activity"""
        url = f"{self.base_url}/activities/{activity_id}/kudos"
        headers = self.auth.get_headers()
        
        response = requests.get(url, headers=headers)
        
        # Handle token expiry
        if response.status_code == 401:
            print("Token expired, refreshing...")
            self.refresh_and_update_token()
            headers = self.auth.get_headers()
            response = requests.get(url, headers=headers)
        
        print(f"Kudos API call for activity {activity_id}: Status {response.status_code}")
        
        if response.status_code == 200:
            kudos_data = response.json()
            print(f"  -> Got {len(kudos_data)} kudos")
            if kudos_data and len(kudos_data) > 0:
                print(f"  -> Sample kudos data keys: {list(kudos_data[0].keys()) if kudos_data else 'No data'}")
            return kudos_data
        else:
            print(f"  -> Error: {response.text}")
            response.raise_for_status()
        
        return []
    
    def fetch_all_activities(self, max_activities=None):
        """Fetch all activities with rate limiting"""
        all_activities = []
        page = 1
        
        print("Fetching activities...")
        
        while True:
            try:
                activities = self.get_athlete_activities(per_page=50, page=page)
                
                if not activities:
                    break
                
                all_activities.extend(activities)
                print(f"Fetched page {page}, total activities: {len(all_activities)}")
                
                if max_activities and len(all_activities) >= max_activities:
                    all_activities = all_activities[:max_activities]
                    break
                
                page += 1
                time.sleep(0.5)  # Rate limiting
                
            except requests.exceptions.HTTPError as e:
                if e.response.status_code == 429:
                    print("Rate limited. Waiting 15 minutes...")
                    time.sleep(900)  # Wait 15 minutes
                    continue
                else:
                    raise
        
        return all_activities
    
    def fetch_detailed_activities(self, activity_ids):
        """Fetch detailed data for specific activities"""
        detailed_activities = []
        
        for i, activity_id in enumerate(activity_ids):
            try:
                detail = self.get_activity_details(activity_id)
                detailed_activities.append(detail)
                
                if (i + 1) % 10 == 0:
                    print(f"Fetched details for {i + 1}/{len(activity_ids)} activities")
                
                time.sleep(0.5)  # Rate limiting
                
            except requests.exceptions.HTTPError as e:
                if e.response.status_code == 429:
                    print("Rate limited. Waiting 15 minutes...")
                    time.sleep(900)
                    continue
                else:
                    print(f"Error fetching activity {activity_id}: {e}")
                    continue
        
        return detailed_activities
    
    def fetch_kudos_givers(self, activity_ids, max_activities_for_kudos=20):
        """Fetch who gave kudos to activities (limited to avoid rate limits)"""
        kudos_data = []
        
        # Limit to most recent activities to avoid hitting rate limits
        limited_ids = activity_ids[:max_activities_for_kudos]
        
        print(f"Fetching kudos data for {len(limited_ids)} most recent activities...")
        print(f"Activity IDs to process: {limited_ids[:5]}...")  # Show first 5 IDs
        
        for i, activity_id in enumerate(limited_ids):
            try:
                kudos_list = self.get_activity_kudos(activity_id)
                
                if kudos_list:  # Only process if we got data
                    for j, kudos in enumerate(kudos_list):
                        # Debug: print the actual structure for the first kudos
                        if len(kudos_data) == 0:  # Only print for very first kudos to avoid spam
                            print(f"  -> Debug: Kudos object keys: {list(kudos.keys())}")
                            print(f"  -> Debug: Sample kudos object: {kudos}")
                        
                        # Generate a synthetic athlete ID based on name since Strava doesn't provide IDs in kudos endpoint
                        fullname = f"{kudos.get('firstname', '')} {kudos.get('lastname', '')}".strip()
                        synthetic_id = hash(fullname) % (10**8)  # Generate consistent ID from name
                        
                        kudos_data.append({
                            'activity_id': activity_id,
                            'athlete_id': synthetic_id,
                            'athlete_firstname': kudos.get('firstname', ''),
                            'athlete_lastname': kudos.get('lastname', ''),
                            'athlete_fullname': fullname
                        })
                
                if (i + 1) % 5 == 0:  # More frequent updates
                    print(f"Processed {i + 1}/{len(limited_ids)} activities for kudos, found {len(kudos_data)} total kudos")
                
                time.sleep(1.0)  # Longer delay between requests
                
            except requests.exceptions.HTTPError as e:
                if e.response.status_code == 429:
                    print("Rate limited. Waiting 15 minutes...")
                    time.sleep(900)
                    continue
                elif e.response.status_code == 403:
                    print(f"Access forbidden for activity {activity_id} (may be private)")
                    continue
                else:
                    print(f"HTTP Error {e.response.status_code} for activity {activity_id}: {e}")
                    continue
            except Exception as e:
                print(f"Unexpected error fetching kudos for activity {activity_id}: {e}")
                continue
        
        print(f"\nKudos fetch complete. Total kudos found: {len(kudos_data)}")
        return kudos_data
    
    def activities_to_dataframe(self, activities):
        """Convert activities list to pandas DataFrame"""
        if not activities:
            return pd.DataFrame()
        
        # Extract key fields
        activity_data = []
        
        for activity in activities:
            data = {
                'id': activity.get('id'),
                'name': activity.get('name'),
                'type': activity.get('type'),
                'sport_type': activity.get('sport_type'),
                'start_date': activity.get('start_date'),
                'distance': activity.get('distance'),
                'moving_time': activity.get('moving_time'),
                'elapsed_time': activity.get('elapsed_time'),
                'total_elevation_gain': activity.get('total_elevation_gain'),
                'kudos_count': activity.get('kudos_count', 0),
                'comment_count': activity.get('comment_count', 0),
                'athlete_count': activity.get('athlete_count', 0),
                'photo_count': activity.get('photo_count', 0),
                'total_photo_count': activity.get('total_photo_count', 0),
                'has_photos': activity.get('total_photo_count', 0) > 0,
                'average_speed': activity.get('average_speed'),
                'max_speed': activity.get('max_speed'),
                'average_heartrate': activity.get('average_heartrate'),
                'max_heartrate': activity.get('max_heartrate'),
                'pr_count': activity.get('pr_count', 0),
                'achievement_count': activity.get('achievement_count', 0),
                'visibility': activity.get('visibility'),
                'commute': activity.get('commute', False),
                'manual': activity.get('manual', False),
                'private': activity.get('private', False),
                'flagged': activity.get('flagged', False)
            }
            
            # Parse start date
            if data['start_date']:
                data['start_date_parsed'] = pd.to_datetime(data['start_date'])
                data['day_of_week'] = data['start_date_parsed'].dayofweek
                data['hour_of_day'] = data['start_date_parsed'].hour
            
            activity_data.append(data)
        
        df = pd.DataFrame(activity_data)
        
        # Calculate derived metrics
        if not df.empty:
            df['distance_km'] = df['distance'] / 1000
            df['moving_time_hours'] = df['moving_time'] / 3600
            df['pace_min_per_km'] = df['moving_time'] / 60 / df['distance_km']
            df['speed_kmh'] = df['distance_km'] / df['moving_time_hours']
        
        return df