"""
Setup script to help configure Strava API credentials
"""
import os
from strava_auth import StravaAuth

def setup_strava_credentials():
    """Guide user through setting up Strava API credentials"""
    print("=== Strava API Setup ===")
    print("\nTo use the Strava API, you need to:")
    print("1. Create a Strava application at: https://www.strava.com/settings/api")
    print("2. Get your Client ID and Client Secret")
    print("3. Authorize your application to access your data")
    
    print("\nStep 1: Create .env file with your credentials")
    
    # Check if .env exists
    if os.path.exists('.env'):
        print(".env file already exists!")
        response = input("Do you want to update it? (y/n): ")
        if response.lower() != 'y':
            return
    
    # Get credentials from user
    client_id = input("Enter your Strava Client ID: ")
    client_secret = input("Enter your Strava Client Secret: ")
    
    # Write to .env file
    with open('.env', 'w') as f:
        f.write(f"STRAVA_CLIENT_ID={client_id}\n")
        f.write(f"STRAVA_CLIENT_SECRET={client_secret}\n")
        f.write("STRAVA_ACCESS_TOKEN=\n")
        f.write("STRAVA_REFRESH_TOKEN=\n")
    
    print("\n.env file created!")
    
    # Now help with authorization
    print("\nStep 2: Get authorization")
    try:
        auth = StravaAuth()
        auth_url = auth.get_authorization_url()
        
        print(f"\nPlease visit this URL to authorize your application:")
        print(auth_url)
        print("\nAfter clicking 'Authorize', your browser will try to redirect to localhost and fail.")
        print("That's expected! Look at the URL in your browser's address bar.")
        print("It will look like: http://localhost/?state=&code=LONG_CODE_HERE&scope=read,activity:read_all")
        print("\nCopy the code parameter from that URL (everything after 'code=' and before '&')")
        
        auth_code = input("\nPaste the authorization code here: ")
        
        print("Exchanging code for tokens...")
        token_data = auth.exchange_code_for_token(auth_code)
        
        # Update .env file with tokens
        with open('.env', 'r') as f:
            lines = f.readlines()
        
        with open('.env', 'w') as f:
            for line in lines:
                if line.startswith('STRAVA_ACCESS_TOKEN='):
                    f.write(f"STRAVA_ACCESS_TOKEN={token_data['access_token']}\n")
                elif line.startswith('STRAVA_REFRESH_TOKEN='):
                    f.write(f"STRAVA_REFRESH_TOKEN={token_data['refresh_token']}\n")
                else:
                    f.write(line)
        
        print("\nSuccess! Your Strava API is now configured.")
        print("You can now run the analysis with: python analyze_kudos.py")
        
    except Exception as e:
        print(f"Error during setup: {e}")
        print("Please check your credentials and try again.")

if __name__ == "__main__":
    setup_strava_credentials()