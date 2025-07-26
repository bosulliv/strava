"""
Strava Kudos Analysis - Analyze cached activity data
"""
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
import os

class CachedKudosAnalyzer:
    def __init__(self, data_dir="data"):
        self.data_dir = data_dir
        self.activities_file = os.path.join(data_dir, "activities.csv")
        self.kudos_file = os.path.join(data_dir, "kudos.csv")
        self.df = None
        self.kudos_df = None
    
    def load_data(self):
        """Load cached activity and kudos data"""
        if not os.path.exists(self.activities_file):
            raise FileNotFoundError(f"Activities file not found: {self.activities_file}")
        
        print("Loading cached data...")
        self.df = pd.read_csv(self.activities_file)
        
        if os.path.exists(self.kudos_file):
            self.kudos_df = pd.read_csv(self.kudos_file)
            print(f"Loaded {len(self.df)} activities and {len(self.kudos_df)} kudos records")
        else:
            print(f"Loaded {len(self.df)} activities (no kudos data available)")
        
        # Ensure start_date_parsed is datetime
        if 'start_date_parsed' not in self.df.columns and 'start_date' in self.df.columns:
            self.df['start_date_parsed'] = pd.to_datetime(self.df['start_date'])
            self.df['day_of_week'] = self.df['start_date_parsed'].dt.dayofweek
            self.df['hour_of_day'] = self.df['start_date_parsed'].dt.hour
        
        return self.df
    
    def basic_stats(self):
        """Display basic statistics about the data"""
        if self.df is None or self.df.empty:
            print("No data loaded")
            return
        
        print("\n=== BASIC STATISTICS ===")
        print(f"Total activities: {len(self.df)}")
        print(f"Activities with photos: {self.df['has_photos'].sum()}")
        print(f"Activities without photos: {(~self.df['has_photos']).sum()}")
        print(f"Average kudos per activity: {self.df['kudos_count'].mean():.1f}")
        
        # Only show photo comparison if we have both types
        if self.df['has_photos'].sum() > 0 and (~self.df['has_photos']).sum() > 0:
            avg_kudos_with_photos = self.df[self.df['has_photos']]['kudos_count'].mean()
            avg_kudos_without_photos = self.df[~self.df['has_photos']]['kudos_count'].mean()
            print(f"Average kudos (with photos): {avg_kudos_with_photos:.1f}")
            print(f"Average kudos (without photos): {avg_kudos_without_photos:.1f}")
            print(f"Photo effect: {avg_kudos_with_photos / avg_kudos_without_photos:.1f}x more kudos")
        
        print(f"\nDate range: {self.df['start_date'].min()} to {self.df['start_date'].max()}")
        print(f"Most common activity types:")
        print(self.df['type'].value_counts().head())
    
    def photo_effect_analysis(self):
        """Analyze the effect of photos on kudos"""
        if self.df is None or self.df.empty:
            return
        
        print("\n=== PHOTO EFFECT ANALYSIS ===")
        
        # Overall comparison
        with_photos = self.df[self.df['has_photos']]['kudos_count']
        without_photos = self.df[~self.df['has_photos']]['kudos_count']
        
        if len(with_photos) == 0 or len(without_photos) == 0:
            print("Need activities both with and without photos for comparison")
            return
        
        # Statistical test
        stat, p_value = stats.mannwhitneyu(with_photos, without_photos, alternative='two-sided')
        
        print(f"Activities with photos: {len(with_photos)} (avg kudos: {with_photos.mean():.1f})")
        print(f"Activities without photos: {len(without_photos)} (avg kudos: {without_photos.mean():.1f})")
        print(f"Mann-Whitney U test p-value: {p_value:.4f}")
        print(f"Statistical significance: {'Yes' if p_value < 0.05 else 'No'}")
        
        # Effect by activity type
        print(f"\nPhoto effect by activity type:")
        for activity_type in self.df['type'].value_counts().head(5).index:
            type_df = self.df[self.df['type'] == activity_type]
            if type_df['has_photos'].sum() > 5 and (~type_df['has_photos']).sum() > 5:
                with_photos_type = type_df[type_df['has_photos']]['kudos_count'].mean()
                without_photos_type = type_df[~type_df['has_photos']]['kudos_count'].mean()
                effect = with_photos_type / without_photos_type if without_photos_type > 0 else float('inf')
                print(f"  {activity_type}: {effect:.1f}x more kudos with photos")
    
    def similar_activity_comparison(self):
        """Compare similar activities with/without photos"""
        if self.df is None or self.df.empty:
            return
        
        print("\n=== SIMILAR ACTIVITY COMPARISON ===")
        
        # Focus on most common activity types with enough samples
        for activity_type in ['Ride', 'Run', 'Hike']:
            type_df = self.df[self.df['type'] == activity_type].copy()
            
            if len(type_df) < 20:
                continue
            
            print(f"\n{activity_type} Analysis:")
            
            # Create distance bins for comparison
            if 'distance_km' in type_df.columns:
                type_df['distance_bin'] = pd.cut(type_df['distance_km'], bins=5, labels=['Very Short', 'Short', 'Medium', 'Long', 'Very Long'])
                
                for bin_name in type_df['distance_bin'].cat.categories:
                    bin_df = type_df[type_df['distance_bin'] == bin_name]
                    
                    with_photos = bin_df[bin_df['has_photos']]['kudos_count']
                    without_photos = bin_df[~bin_df['has_photos']]['kudos_count']
                    
                    if len(with_photos) >= 3 and len(without_photos) >= 3:
                        effect = with_photos.mean() / without_photos.mean() if without_photos.mean() > 0 else float('inf')
                        print(f"  {bin_name}: {effect:.1f}x more kudos with photos ({len(with_photos)} vs {len(without_photos)} activities)")
    
    def correlation_analysis(self):
        """Analyze correlations between activity features and kudos"""
        if self.df is None or self.df.empty:
            return
        
        print("\n=== CORRELATION ANALYSIS ===")
        
        # Select numeric columns for correlation
        numeric_cols = ['distance_km', 'moving_time_hours', 'total_elevation_gain', 
                       'average_speed', 'pr_count', 'achievement_count', 'kudos_count']
        
        available_cols = [col for col in numeric_cols if col in self.df.columns]
        
        if len(available_cols) < 2:
            print("Insufficient numeric columns for correlation analysis")
            return
        
        corr_df = self.df[available_cols].corr()
        kudos_corr = corr_df['kudos_count'].drop('kudos_count').sort_values(key=abs, ascending=False)
        
        print("Correlations with kudos_count:")
        for feature, correlation in kudos_corr.items():
            print(f"  {feature}: {correlation:.3f}")
    
    def timing_analysis(self):
        """Analyze kudos by posting time"""
        if self.df is None or self.df.empty:
            return
        
        print("\n=== TIMING ANALYSIS ===")
        
        if 'day_of_week' in self.df.columns:
            day_names = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
            day_kudos = self.df.groupby('day_of_week')['kudos_count'].mean()
            
            print("Average kudos by day of week:")
            for day_num, avg_kudos in day_kudos.items():
                print(f"  {day_names[day_num]}: {avg_kudos:.1f}")
        
        if 'hour_of_day' in self.df.columns:
            hour_kudos = self.df.groupby('hour_of_day')['kudos_count'].mean().sort_values(ascending=False)
            print(f"\nBest hours for kudos:")
            for hour, avg_kudos in hour_kudos.head(5).items():
                print(f"  {hour:02d}:00: {avg_kudos:.1f} avg kudos")
    
    def top_kudos_givers_analysis(self):
        """Analyze top kudos givers if data is available"""
        if self.kudos_df is None or self.kudos_df.empty:
            print("\n=== KUDOS GIVERS ANALYSIS ===")
            print("No kudos giver data available")
            return
        
        print("\n=== TOP KUDOS GIVERS ANALYSIS ===")
        
        # Count kudos per athlete
        kudos_counts = self.kudos_df.groupby(['athlete_id', 'athlete_fullname']).size().reset_index(name='kudos_given')
        kudos_counts = kudos_counts.sort_values('kudos_given', ascending=False)
        
        print(f"Total unique kudos givers: {len(kudos_counts)}")
        print(f"Top 10 kudos givers:")
        
        for i, row in kudos_counts.head(10).iterrows():
            percentage = (row['kudos_given'] / len(self.kudos_df)) * 100
            print(f"  {row['athlete_fullname']}: {row['kudos_given']} kudos ({percentage:.1f}%)")
        
        # Calculate concentration
        top_10_percentage = (kudos_counts.head(10)['kudos_given'].sum() / len(self.kudos_df)) * 100
        print(f"\nTop 10 supporters provide {top_10_percentage:.1f}% of all kudos")
    
    def generate_visualizations(self, output_file="cached_kudos_analysis.png"):
        """Generate analysis visualizations"""
        if self.df is None or self.df.empty:
            return
        
        fig, axes = plt.subplots(2, 2, figsize=(15, 12))
        fig.suptitle('Strava Kudos Analysis', fontsize=16)
        
        # Photo effect comparison
        if self.df['has_photos'].sum() > 0 and (~self.df['has_photos']).sum() > 0:
            photo_comparison = self.df.groupby('has_photos')['kudos_count'].mean()
            axes[0, 0].bar(['Without Photos', 'With Photos'], photo_comparison.values)
            axes[0, 0].set_title('Average Kudos: Photos vs No Photos')
            axes[0, 0].set_ylabel('Average Kudos')
        
        # Kudos distribution
        axes[0, 1].hist(self.df['kudos_count'], bins=30, alpha=0.7)
        axes[0, 1].set_title('Distribution of Kudos Count')
        axes[0, 1].set_xlabel('Kudos Count')
        axes[0, 1].set_ylabel('Frequency')
        
        # Activity type comparison
        if len(self.df['type'].value_counts()) > 1:
            type_kudos = self.df.groupby('type')['kudos_count'].mean().sort_values(ascending=False).head(8)
            axes[1, 0].bar(range(len(type_kudos)), type_kudos.values)
            axes[1, 0].set_xticks(range(len(type_kudos)))
            axes[1, 0].set_xticklabels(type_kudos.index, rotation=45)
            axes[1, 0].set_title('Average Kudos by Activity Type')
            axes[1, 0].set_ylabel('Average Kudos')
        
        # Distance vs Kudos scatter (if distance data available)
        if 'distance_km' in self.df.columns:
            scatter = axes[1, 1].scatter(self.df['distance_km'], self.df['kudos_count'], 
                                       c=self.df['has_photos'], alpha=0.6, cmap='coolwarm')
            axes[1, 1].set_xlabel('Distance (km)')
            axes[1, 1].set_ylabel('Kudos Count')
            axes[1, 1].set_title('Distance vs Kudos (Red=Photos, Blue=No Photos)')
            plt.colorbar(scatter, ax=axes[1, 1])
        
        plt.tight_layout()
        plt.savefig(output_file, dpi=300, bbox_inches='tight')
        print(f"\nVisualization saved to {output_file}")
        
        return fig
    
    def run_full_analysis(self):
        """Run complete analysis pipeline"""
        self.load_data()
        self.basic_stats()
        self.photo_effect_analysis()
        self.similar_activity_comparison()
        self.correlation_analysis()
        self.timing_analysis()
        self.top_kudos_givers_analysis()
        self.generate_visualizations()

def main():
    """Main analysis script"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Analyze cached Strava data")
    parser.add_argument("--data-dir", default="data", help="Directory containing cached data")
    parser.add_argument("--output", default="cached_kudos_analysis.png", help="Output file for visualizations")
    
    args = parser.parse_args()
    
    analyzer = CachedKudosAnalyzer(data_dir=args.data_dir)
    
    try:
        analyzer.run_full_analysis()
    except FileNotFoundError as e:
        print(f"Error: {e}")
        print("Run 'python collect_strava_data.py' first to collect data")

if __name__ == "__main__":
    main()