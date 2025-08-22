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

**Note:** Scripts can be run as modules (`python -m src.script_name`) or directly (`python src/script_name.py`)

## Development Environment

The project uses a Python virtual environment at `strava_env/`. Always activate it before running any scripts:

```bash
source strava_env/bin/activate
```

## Common Commands

**Initial Setup (first time only):**
```bash
python -m src.setup_strava_api
```

**Collect activity data (incremental):**
```bash
python -m src.collect_strava_data
```

**Analyze cached data:**
```bash
python -m src.analyze_cached_data
```

**Run legacy analysis (combined collection + analysis):**
```bash
python -m src.analyze_kudos
```

**Data collection options:**
```bash
python -m src.collect_strava_data --status                    # Show collection status
python -m src.collect_strava_data --activities-only           # Only fetch activities
python -m src.collect_strava_data --kudos-only               # Only fetch kudos
python -m src.collect_strava_data --kudos-batch-size 50      # Fetch kudos for 50 activities
python -m src.collect_strava_data --max-activities 100       # Limit total activities fetched
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

1. User creates Strava app at https://www.strava.com/settings/api (use http://localhost as redirect URI)
2. `setup_strava_api.py` guides through OAuth authorization process
3. Browser will fail to load localhost during auth - copy authorization code from failed URL
4. Access and refresh tokens stored in `.env` file
5. `StravaAuth` class handles automatic token refresh when tokens expire

## Security Requirements

**MANDATORY**: Use the security-code-reviewer agent for ALL significant code changes, API integrations, and file operations. This project handles sensitive personal data and API credentials.

**Security Agent Usage:**
- **ALWAYS** run security review after writing authentication code
- **ALWAYS** run security review after modifying API client code  
- **ALWAYS** run security review after adding file operations
- **ALWAYS** run security review before committing changes

**Critical Findings Policy:**
- All CRITICAL security findings MUST be fixed immediately
- HIGH priority findings should be addressed before feature work continues
- Document security decisions in commit messages

**Automatic Security Triggers:**
- Any code touching `strava_auth.py` → mandatory security review
- Any new `.env` file operations → mandatory security review  
- Any API response handling changes → mandatory security review
- Any file path operations → mandatory security review

**Data Sensitivity Notes:**
- `.env` contains API credentials and is git-ignored
- Data files contain personal activity information and are git-ignored
- All API calls include proper token refresh and rate limiting

## Testing

No formal test framework is configured. Scripts can be tested by running them individually. Test and debug scripts exist for troubleshooting:

**Test Scripts:**
- `test/test_kudos_api.py` - Testing kudos API functionality
- `test/test_auto_refresh.py` - Testing automatic token refresh  
- `test/test_timestamp_fix.py` - Testing timestamp parsing fixes
- `test/test_csv_paths.py` - Testing CSV file handling
- `test/test_image_paths.py` - Testing image file operations

**Debug Scripts:**
- `debug/debug_kudos.py` - Troubleshooting API calls
- `debug/debug_analysis.py` - Debugging data analysis
- `debug/debug_timestamp.py` - Debugging timestamp issues

## Data Architecture

**Incremental Collection System:**
- `StravaDataCollector` manages incremental data fetching to avoid re-downloading existing data
- `collection_metadata.json` tracks collection state and progress
- Activities and kudos are collected separately to optimize API usage
- Rate limiting includes 15-minute waits when API limits are hit

**Data Pipeline:**
1. **Authentication**: `StravaAuth` handles OAuth flow and token management
2. **Fetching**: `StravaDataFetcher` retrieves activities and kudos with rate limiting
3. **Collection**: `StravaDataCollector` manages incremental updates and persistence
4. **Analysis**: Analysis scripts process cached data for insights and visualizations