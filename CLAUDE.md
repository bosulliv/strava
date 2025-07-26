# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Python data analysis project that analyzes Strava activity data to understand what factors correlate with getting more kudos (likes), specifically examining whether photos increase engagement. The project uses the Strava API to fetch activity data and performs statistical analysis with visualizations.

## Core Architecture

- **Authentication Layer**: `strava_auth.py` - Handles OAuth flow with Strava API including token refresh
- **Data Fetching**: `strava_data_fetcher.py` - Core API client with rate limiting and data transformation
- **Data Collection**: `collect_strava_data.py` - Incremental data collection with persistent storage and metadata tracking
- **Analysis Engine**: `analyze_cached_data.py` - Statistical analysis and visualization of cached data
- **Legacy Analysis**: `analyze_kudos.py` - Original combined collection + analysis script
- **Setup Helper**: `setup_strava_api.py` - Interactive script for initial API credential configuration

## Development Environment

The project uses a Python virtual environment at `strava_env/`. Always activate it before running any scripts:

```bash
source strava_env/bin/activate
```

## Common Commands

**Initial Setup (first time only):**
```bash
python setup_strava_api.py
```

**Collect activity data (incremental):**
```bash
python collect_strava_data.py
```

**Analyze cached data:**
```bash
python analyze_cached_data.py
```

**Data collection options:**
```bash
python collect_strava_data.py --status                    # Show collection status
python collect_strava_data.py --activities-only           # Only fetch activities
python collect_strava_data.py --kudos-only               # Only fetch kudos
python collect_strava_data.py --kudos-batch-size 50      # Fetch kudos for 50 activities
```

**Install dependencies:**
```bash
pip install -r requirements.txt
```

## Key Dependencies

- pandas, numpy - Data manipulation and analysis
- matplotlib, seaborn - Visualization
- requests - API calls
- python-dotenv - Environment variable management
- scipy - Statistical analysis

## API Rate Limiting

The Strava API has strict rate limits (100 requests per 15 minutes, 1000 per day). The code includes automatic rate limiting with exponential backoff and 15-minute waits when limits are hit. All data fetching methods include proper error handling for rate limit responses (HTTP 429).

## Data Files Generated

**Cached Data (in `data/` directory):**
- `activities.csv` - Main activity dataset with incremental updates
- `kudos.csv` - Individual kudos data (who gave kudos to which activities)
- `collection_metadata.json` - Tracks collection status and progress
- `cached_kudos_analysis.png` - Analysis visualizations

**Legacy Files:**
- `strava_activities.csv` - Original format activity data
- `strava_kudos_details.csv` - Original format kudos data
- `strava_top_kudos_givers.csv` - Ranked list of top kudos supporters
- `kudos_analysis.png` - Original analysis visualizations

**Configuration:**
- `.env` - API credentials (not tracked in git)

## Authentication Flow

1. User creates Strava app at https://www.strava.com/settings/api
2. `setup_strava_api.py` guides through OAuth authorization
3. Access and refresh tokens stored in `.env` file
4. `StravaAuth` class handles token refresh automatically

## Testing

No formal test framework is configured. Scripts can be tested by running them individually. Debug scripts exist for troubleshooting:
- `debug_kudos.py` - Troubleshooting API calls
- `debug_analysis.py` - Debugging data analysis
- `test_kudos_api.py` - Testing kudos API functionality