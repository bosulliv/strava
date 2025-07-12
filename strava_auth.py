"""
Strava API Authentication Helper
"""
import os
import requests
from dotenv import load_dotenv

load_dotenv()

class StravaAuth:
    def __init__(self):
        self.client_id = os.getenv('STRAVA_CLIENT_ID')
        self.client_secret = os.getenv('STRAVA_CLIENT_SECRET')
        self.access_token = os.getenv('STRAVA_ACCESS_TOKEN')
        self.refresh_token = os.getenv('STRAVA_REFRESH_TOKEN')
        
        if not all([self.client_id, self.client_secret]):
            raise ValueError("Please set STRAVA_CLIENT_ID and STRAVA_CLIENT_SECRET in your .env file")
    
    def get_authorization_url(self):
        """Get the authorization URL for OAuth flow"""
        scope = "read,activity:read_all"
        redirect_uri = "http://localhost"  # This will fail but show the code in URL
        
        auth_url = (
            f"https://www.strava.com/oauth/authorize?"
            f"client_id={self.client_id}&"
            f"response_type=code&"
            f"redirect_uri={redirect_uri}&"
            f"scope={scope}"
        )
        return auth_url
    
    def exchange_code_for_token(self, authorization_code):
        """Exchange authorization code for access token"""
        token_url = "https://www.strava.com/oauth/token"
        
        data = {
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'code': authorization_code,
            'grant_type': 'authorization_code'
        }
        
        response = requests.post(token_url, data=data)
        response.raise_for_status()
        
        token_data = response.json()
        return token_data
    
    def refresh_access_token(self):
        """Refresh the access token using refresh token"""
        if not self.refresh_token:
            raise ValueError("No refresh token available")
        
        token_url = "https://www.strava.com/oauth/token"
        
        data = {
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'refresh_token': self.refresh_token,
            'grant_type': 'refresh_token'
        }
        
        response = requests.post(token_url, data=data)
        response.raise_for_status()
        
        token_data = response.json()
        self.access_token = token_data['access_token']
        self.refresh_token = token_data['refresh_token']
        
        return token_data
    
    def get_headers(self):
        """Get headers for API requests"""
        if not self.access_token:
            raise ValueError("No access token available. Please authenticate first.")
        
        return {
            'Authorization': f'Bearer {self.access_token}',
            'Content-Type': 'application/json'
        }