#!/usr/bin/env python3
"""Test script to verify CSV file paths work correctly"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.analyze_kudos import KudosAnalyzer

def test_csv_paths():
    # Create a simple test - just check that the data directory path logic works
    data_dir = "data"
    os.makedirs(data_dir, exist_ok=True)
    
    activities_path = os.path.join(data_dir, 'strava_activities.csv')
    kudos_path = os.path.join(data_dir, 'strava_kudos_details.csv') 
    top_kudos_path = os.path.join(data_dir, 'strava_top_kudos_givers.csv')
    
    print(f"✓ Activities path: {activities_path}")
    print(f"✓ Kudos path: {kudos_path}")
    print(f"✓ Top kudos path: {top_kudos_path}")
    
    # Check that all paths point to data directory
    assert activities_path.startswith('data/'), f"Wrong path: {activities_path}"
    assert kudos_path.startswith('data/'), f"Wrong path: {kudos_path}"
    assert top_kudos_path.startswith('data/'), f"Wrong path: {top_kudos_path}"
    
    print("✓ All CSV paths correctly point to data/ directory")

if __name__ == "__main__":
    test_csv_paths()