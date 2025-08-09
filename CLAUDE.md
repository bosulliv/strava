# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Python data analysis project that analyzes Strava activity data to understand what factors correlate with getting more kudos (likes), specifically examining whether photos increase engagement. The project uses the Strava API to fetch activity data and performs statistical analysis with visualizations.

## Core Architecture

- **Authentication Layer**: `src/strava_auth.py` - Handles OAuth flow with Strava API including token refresh
- **Data Fetching**: `src/strava_data_fetcher.py` - Core API client with rate limiting and data transformation
- **Data Collection**: `src/collect_strava_data.py` - Incremental data collection with persistent storage and metadata tracking
- **Analysis Engine**: `src/analyze_cached_data.py` - Statistical analysis and visualization of cached data
- **Legacy Analysis**: `src/analyze_kudos.py` - Original combined collection + analysis script
- **Setup Helper**: `src/setup_strava_api.py` - Interactive script for initial API credential configuration

## Directory Structure

- `src/` - Main source code modules and executable scripts (hybrid approach)
- `test/` - Test scripts for debugging and verification
- `debug/` - Debugging utilities and troubleshooting scripts
- `data/` - Generated data files and analysis outputs

**Note:** Scripts can be run directly from project root using `python src/script_name.py`

## Development Environment

The project uses a Python virtual environment at `strava_env/`. Always activate it before running any scripts:

```bash
source strava_env/bin/activate
```

## Common Commands

**Initial Setup (first time only):**
```bash
python src/setup_strava_api.py
```

**Collect activity data (incremental):**
```bash
python src/collect_strava_data.py
```

**Analyze cached data:**
```bash
python src/analyze_cached_data.py
```

**Run legacy analysis (combined collection + analysis):**
```bash
python src/analyze_kudos.py
```

**Data collection options:**
```bash
python src/collect_strava_data.py --status                    # Show collection status
python src/collect_strava_data.py --activities-only           # Only fetch activities
python src/collect_strava_data.py --kudos-only               # Only fetch kudos
python src/collect_strava_data.py --kudos-batch-size 50      # Fetch kudos for 50 activities
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

**Legacy Files (also in `data/` directory):**
- `data/strava_activities.csv` - Original format activity data
- `data/strava_kudos_details.csv` - Original format kudos data
- `data/strava_top_kudos_givers.csv` - Ranked list of top kudos supporters
- `data/kudos_analysis.png` - Original analysis visualizations

**Configuration:**
- `.env` - API credentials (not tracked in git)

## Authentication Flow

1. User creates Strava app at https://www.strava.com/settings/api
2. `setup_strava_api.py` guides through OAuth authorization
3. Access and refresh tokens stored in `.env` file
4. `StravaAuth` class handles token refresh automatically

## Testing

No formal test framework is configured. Scripts can be tested by running them individually. Test and debug scripts exist for troubleshooting:

**Test Scripts:**
- `test/test_kudos_api.py` - Testing kudos API functionality
- `test/test_auto_refresh.py` - Testing automatic token refresh
- `test/test_timestamp_fix.py` - Testing timestamp parsing fixes

**Debug Scripts:**
- `debug/debug_kudos.py` - Troubleshooting API calls
- `debug/debug_analysis.py` - Debugging data analysis
- `debug/debug_timestamp.py` - Debugging timestamp issues