"""
Debug the kudos analysis specifically
"""
from analyze_kudos import KudosAnalyzer
import pandas as pd

def debug_analysis():
    analyzer = KudosAnalyzer()
    
    # Load just a small amount of data for testing
    print("Loading data...")
    analyzer.load_data(max_activities=10, fetch_kudos_givers=True)
    
    print(f"Activities DataFrame shape: {analyzer.df.shape if analyzer.df is not None else 'None'}")
    print(f"Kudos DataFrame shape: {analyzer.kudos_df.shape if analyzer.kudos_df is not None else 'None'}")
    
    if analyzer.kudos_df is not None:
        print(f"Kudos DataFrame columns: {analyzer.kudos_df.columns.tolist()}")
        print(f"First few rows:")
        print(analyzer.kudos_df.head())
        print(f"Sample data types:")
        print(analyzer.kudos_df.dtypes)
    
    print("\nNow calling analyze_top_kudos_givers...")
    result = analyzer.analyze_top_kudos_givers(top_n=10)
    
    if result is not None:
        print(f"Result shape: {result.shape}")
        print(f"Result head:")
        print(result.head())

if __name__ == "__main__":
    debug_analysis()