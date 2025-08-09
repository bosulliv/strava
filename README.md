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
   python -m src.setup_strava_api
   ```
   - When you authorize, the browser will fail to load localhost - that's expected!
   - Copy the authorization code from the failed URL and paste it into the script

3. **Collect activity data:**
   ```bash
   python -m src.collect_strava_data
   ```

4. **Run the analysis:**
   ```bash
   python -m src.analyze_cached_data
   ```

## What the Analysis Tells You

The analysis will answer several key questions:

1. **Do photos really get more kudos?** - Statistical comparison of activities with/without photos
2. **What features correlate with kudos?** - Distance, elevation, speed, timing, achievements, etc.
3. **Similar activity comparison** - Comparing activities of similar distance/type to isolate the photo effect
4. **Activity type patterns** - Which types of activities get the most engagement
5. **Top kudos givers** - Who are your top 30 supporters and what percentage of your kudos do they provide?

## Output

The scripts generate files in the `data/` directory:
- Detailed statistical analysis printed to console
- `data/activities.csv` - Main activity dataset with incremental updates
- `data/kudos.csv` - Individual kudos data (who gave kudos to which activities)
- `data/collection_metadata.json` - Tracks collection status and progress
- `data/cached_kudos_analysis.png` - Analysis visualizations

**Legacy files (for compatibility):**
- `data/strava_activities.csv` - Original format activity data
- `data/strava_kudos_details.csv` - Original format kudos data
- `data/strava_top_kudos_givers.csv` - Ranked list of your top kudos supporters
- `data/kudos_analysis.png` - Original analysis visualizations

## Key Research Question

**"Does the picture always get more likes?"**

The analysis specifically looks at similar activities (same type, similar distance) to compare engagement between those with and without photos, controlling for other factors that might influence kudos.

## Directory Structure

- `src/` - Main source code modules
  - `strava_auth.py` - Handles Strava API authentication
  - `strava_data_fetcher.py` - Core API client with rate limiting and data transformation
  - `collect_strava_data.py` - Incremental data collection with persistent storage
  - `analyze_cached_data.py` - Statistical analysis and visualization of cached data
  - `analyze_kudos.py` - Original combined collection + analysis script (legacy)
  - `setup_strava_api.py` - Interactive script for initial API credential configuration
- `test/` - Test scripts for debugging and verification
- `debug/` - Debugging utilities and troubleshooting scripts
- `data/` - Generated data files and analysis outputs
- `.env` - Your API credentials (created during setup)

## Rate Limits

The Strava API has rate limits (100 requests per 15 minutes, 1000 per day). The scripts include automatic rate limiting and will pause if limits are hit.