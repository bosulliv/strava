# Strava Kudos Analysis

This project analyzes your Strava activity data to understand what factors correlate with getting more kudos (likes), with a particular focus on whether photos increase engagement.

## Setup

1. **Activate the virtual environment:**
   ```bash
   source strava_env/bin/activate
   ```

2. **Set up Strava API access:**
   - Go to https://www.strava.com/settings/api
   - Create a new application (use http://localhost as the redirect URI)
   - Run the setup script and follow the prompts:
   ```bash
   python setup_strava_api.py
   ```
   - When you authorize, the browser will fail to load localhost - that's expected!
   - Copy the authorization code from the failed URL and paste it into the script

3. **Run the analysis:**
   ```bash
   python analyze_kudos.py
   ```

## What the Analysis Tells You

The analysis will answer several key questions:

1. **Do photos really get more kudos?** - Statistical comparison of activities with/without photos
2. **What features correlate with kudos?** - Distance, elevation, speed, timing, achievements, etc.
3. **Similar activity comparison** - Comparing activities of similar distance/type to isolate the photo effect
4. **Activity type patterns** - Which types of activities get the most engagement
5. **Top kudos givers** - Who are your top 30 supporters and what percentage of your kudos do they provide?

## Output

The script generates:
- Detailed statistical analysis printed to console
- `strava_activities.csv` - Your activity data for further analysis
- `strava_kudos_details.csv` - Individual kudos data (who gave kudos to which activities)
- `strava_top_kudos_givers.csv` - Ranked list of your top kudos supporters
- `kudos_analysis.png` - Visualizations of the findings

## Key Research Question

**"Does the picture always get more likes?"**

The analysis specifically looks at similar activities (same type, similar distance) to compare engagement between those with and without photos, controlling for other factors that might influence kudos.

## Files

- `strava_auth.py` - Handles Strava API authentication
- `strava_data_fetcher.py` - Fetches and processes activity data
- `analyze_kudos.py` - Main analysis script
- `setup_strava_api.py` - Setup helper for API credentials
- `.env` - Your API credentials (created during setup)

## Rate Limits

The Strava API has rate limits (100 requests per 15 minutes, 1000 per day). The scripts include automatic rate limiting and will pause if limits are hit.