"""
Strava Kudos Analysis - Analyze correlation between activity features and kudos
"""
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
from strava_data_fetcher import StravaDataFetcher

class KudosAnalyzer:
    def __init__(self):
        self.fetcher = StravaDataFetcher()
        self.df = None
        self.kudos_df = None
    
    def load_data(self, max_activities=None, fetch_kudos_givers=True):
        """Load activity data from Strava API"""
        print("Fetching activities from Strava...")
        activities = self.fetcher.fetch_all_activities(max_activities=max_activities)
        self.df = self.fetcher.activities_to_dataframe(activities)
        
        print(f"Loaded {len(self.df)} activities")
        
        # Fetch kudos givers for recent activities
        if fetch_kudos_givers and not self.df.empty:
            activity_ids = self.df['id'].tolist()
            print(f"Starting kudos fetch for {len(activity_ids)} activities...")
            kudos_data = self.fetcher.fetch_kudos_givers(activity_ids, max_activities_for_kudos=20)
            
            if kudos_data:
                self.kudos_df = pd.DataFrame(kudos_data)
                print(f"Loaded kudos data: {len(self.kudos_df)} total kudos from recent activities")
            else:
                print("No kudos data available")
        
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
        print(f"Average kudos (with photos): {self.df[self.df['has_photos']]['kudos_count'].mean():.1f}")
        print(f"Average kudos (without photos): {self.df[~self.df['has_photos']]['kudos_count'].mean():.1f}")
        
        print("\nActivity types:")
        print(self.df['type'].value_counts().head(10))
    
    def photo_impact_analysis(self):
        """Analyze the impact of photos on kudos"""
        if self.df is None or self.df.empty:
            print("No data loaded")
            return
        
        print("\n=== PHOTO IMPACT ANALYSIS ===")
        
        # Overall comparison
        with_photos = self.df[self.df['has_photos']]['kudos_count']
        without_photos = self.df[~self.df['has_photos']]['kudos_count']
        
        print(f"Activities with photos: {len(with_photos)}")
        print(f"Average kudos with photos: {with_photos.mean():.2f} (median: {with_photos.median():.1f})")
        print(f"Activities without photos: {len(without_photos)}")
        print(f"Average kudos without photos: {without_photos.mean():.2f} (median: {without_photos.median():.1f})")
        
        # Statistical test
        if len(with_photos) > 0 and len(without_photos) > 0:
            t_stat, p_value = stats.ttest_ind(with_photos, without_photos)
            print(f"T-test p-value: {p_value:.6f}")
            print(f"Photos significantly increase kudos: {'Yes' if p_value < 0.05 else 'No'}")
        
        # By activity type
        print("\n--- By Activity Type ---")
        for activity_type in self.df['type'].value_counts().head(5).index:
            subset = self.df[self.df['type'] == activity_type]
            if len(subset) > 10:  # Only analyze types with sufficient data
                with_photos_type = subset[subset['has_photos']]['kudos_count']
                without_photos_type = subset[~subset['has_photos']]['kudos_count']
                
                if len(with_photos_type) > 0 and len(without_photos_type) > 0:
                    print(f"{activity_type}:")
                    print(f"  With photos: {with_photos_type.mean():.1f} kudos (n={len(with_photos_type)})")
                    print(f"  Without photos: {without_photos_type.mean():.1f} kudos (n={len(without_photos_type)})")
                    
                    # T-test for this activity type
                    t_stat, p_value = stats.ttest_ind(with_photos_type, without_photos_type)
                    print(f"  P-value: {p_value:.4f}")
    
    def correlation_analysis(self):
        """Analyze correlations between features and kudos"""
        if self.df is None or self.df.empty:
            print("No data loaded")
            return
        
        print("\n=== CORRELATION ANALYSIS ===")
        
        # Select numeric columns for correlation
        numeric_cols = [
            'kudos_count', 'distance_km', 'moving_time_hours', 'total_elevation_gain',
            'average_speed', 'max_speed', 'average_heartrate', 'max_heartrate',
            'pr_count', 'achievement_count', 'photo_count', 'total_photo_count',
            'comment_count', 'athlete_count', 'day_of_week', 'hour_of_day'
        ]
        
        # Filter to columns that exist in the dataframe
        available_cols = [col for col in numeric_cols if col in self.df.columns and self.df[col].notna().any()]
        
        if len(available_cols) < 2:
            print("Not enough numeric data for correlation analysis")
            return
        
        corr_data = self.df[available_cols].corr()['kudos_count'].sort_values(ascending=False)
        
        print("Correlation with kudos count:")
        for feature, correlation in corr_data.items():
            if feature != 'kudos_count':
                print(f"  {feature}: {correlation:.3f}")
    
    def similar_activities_analysis(self):
        """Find similar activities and compare those with/without photos"""
        if self.df is None or self.df.empty:
            print("No data loaded")
            return
        
        print("\n=== SIMILAR ACTIVITIES ANALYSIS ===")
        print("Controlling for distance to isolate photo effect...")
        
        # Focus on most common activity type
        main_activity_type = self.df['type'].value_counts().index[0]
        subset = self.df[self.df['type'] == main_activity_type].copy()
        
        print(f"Analyzing {main_activity_type} activities (n={len(subset)})")
        
        if len(subset) < 10:
            print("Not enough activities for comparison")
            return
        
        # Analyze distance vs photos correlation first
        if 'distance_km' in subset.columns and 'total_photo_count' in subset.columns:
            distance_photo_corr = subset['distance_km'].corr(subset['total_photo_count'])
            print(f"Correlation between distance and photo count: {distance_photo_corr:.3f}")
            if distance_photo_corr > 0.3:
                print("⚠️  Strong correlation detected - longer rides do have more photos!")
        
        # Create distance bins to control for confounding
        subset['distance_bin'] = pd.cut(subset['distance_km'], bins=min(10, len(subset)//5), labels=False)
        
        photo_advantage = []
        significant_bins = 0
        
        print("\nDistance-controlled comparison:")
        for bin_num in sorted(subset['distance_bin'].unique()):
            if pd.isna(bin_num):
                continue
                
            bin_activities = subset[subset['distance_bin'] == bin_num]
            
            if len(bin_activities) < 4:  # Need at least 4 activities in bin
                continue
            
            with_photos = bin_activities[bin_activities['has_photos']]['kudos_count']
            without_photos = bin_activities[~bin_activities['has_photos']]['kudos_count']
            
            if len(with_photos) > 0 and len(without_photos) > 0:
                distance_range = bin_activities['distance_km'].agg(['min', 'max'])
                avg_with = with_photos.mean()
                avg_without = without_photos.mean()
                
                # Statistical test for this bin
                t_stat, p_value = stats.ttest_ind(with_photos, without_photos)
                significance = "📸 Significant" if p_value < 0.05 else "No significant difference"
                
                print(f"\nDistance {distance_range['min']:.1f}-{distance_range['max']:.1f}km:")
                print(f"  With photos: {avg_with:.1f} kudos (n={len(with_photos)})")
                print(f"  Without photos: {avg_without:.1f} kudos (n={len(without_photos)})")
                print(f"  Difference: {avg_with - avg_without:.1f} kudos")
                print(f"  P-value: {p_value:.4f} - {significance}")
                
                if p_value < 0.05:
                    significant_bins += 1
                
                if avg_without > 0:
                    photo_advantage.append((avg_with - avg_without) / avg_without * 100)
        
        if photo_advantage:
            print(f"\n=== SUMMARY ===")
            print(f"Distance-controlled photo advantage: {np.mean(photo_advantage):.1f}%")
            print(f"Significant bins (p<0.05): {significant_bins} out of {len([x for x in photo_advantage])}")
            
            if significant_bins == 0:
                print("🔍 No statistically significant photo effect when controlling for distance!")
                print("This suggests distance is the primary driver of kudos, not photos.")
            elif significant_bins < len(photo_advantage) / 2:
                print("📊 Mixed results - photo effect varies by distance range.")
            else:
                print("📸 Photos do seem to increase kudos even when controlling for distance!")
    
    def analyze_top_kudos_givers(self, top_n=30):
        """Analyze who gives the most kudos"""
        if self.kudos_df is None or self.kudos_df.empty:
            print("\n=== TOP KUDOS GIVERS ===")
            print("No kudos data available. Run with fetch_kudos_givers=True to get this analysis.")
            return
        
        print(f"\n=== TOP {top_n} KUDOS GIVERS ===")
        
        # Count kudos by athlete (use fullname as primary key since athlete_id might be missing)
        kudos_counts = (self.kudos_df.groupby('athlete_fullname')
                       .size()
                       .reset_index(name='kudos_given')
                       .sort_values('kudos_given', ascending=False))
        
        print(f"Total unique people who gave kudos: {len(kudos_counts)}")
        print(f"Total kudos tracked: {kudos_counts['kudos_given'].sum()}")
        
        # Show top kudos givers
        top_givers = kudos_counts.head(top_n)
        
        print(f"\nTop {top_n} kudos givers:")
        print("-" * 50)
        for i, row in top_givers.iterrows():
            name = row['athlete_fullname'] if row['athlete_fullname'].strip() else "Unknown Athlete"
            print(f"{i + 1:2d}. {name:<30} {row['kudos_given']:3d} kudos")
        
        # Analysis of kudos distribution
        print(f"\n=== KUDOS DISTRIBUTION ANALYSIS ===")
        total_kudos = kudos_counts['kudos_given'].sum()
        
        if total_kudos > 0:
            top_10_kudos = kudos_counts.head(10)['kudos_given'].sum()
            top_5_kudos = kudos_counts.head(5)['kudos_given'].sum()
            
            print(f"Top 5 givers account for: {top_5_kudos/total_kudos*100:.1f}% of all kudos")
            print(f"Top 10 givers account for: {top_10_kudos/total_kudos*100:.1f}% of all kudos")
        else:
            print("No kudos data to analyze distribution.")
        
        # Show activities that got kudos from top givers
        if len(top_givers) > 0:
            top_giver_name = top_givers.iloc[0]['athlete_fullname']
            top_giver_activities = self.kudos_df[self.kudos_df['athlete_fullname'] == top_giver_name]['activity_id'].unique()
            
            print(f"\n{top_giver_name} (your #1 supporter) gave kudos to {len(top_giver_activities)} of your recent activities")
        
        return kudos_counts
    
    def generate_visualizations(self):
        """Generate visualizations of the analysis"""
        if self.df is None or self.df.empty:
            print("No data loaded")
            return
        
        # Set up the plotting style
        plt.style.use('default')
        fig, axes = plt.subplots(2, 2, figsize=(15, 12))
        
        # 1. Kudos distribution by photo presence
        ax1 = axes[0, 0]
        self.df.boxplot(column='kudos_count', by='has_photos', ax=ax1)
        ax1.set_title('Kudos Distribution: With vs Without Photos')
        ax1.set_xlabel('Has Photos')
        ax1.set_ylabel('Kudos Count')
        
        # 2. Correlation heatmap
        ax2 = axes[0, 1]
        numeric_cols = ['kudos_count', 'distance_km', 'total_elevation_gain', 
                       'photo_count', 'pr_count', 'achievement_count']
        available_cols = [col for col in numeric_cols if col in self.df.columns]
        
        if len(available_cols) > 1:
            corr_matrix = self.df[available_cols].corr()
            sns.heatmap(corr_matrix, annot=True, cmap='coolwarm', center=0, ax=ax2)
            ax2.set_title('Feature Correlation Matrix')
        
        # 3. Activity type vs kudos
        ax3 = axes[1, 0]
        top_types = self.df['type'].value_counts().head(5).index
        subset = self.df[self.df['type'].isin(top_types)]
        subset.boxplot(column='kudos_count', by='type', ax=ax3)
        ax3.set_title('Kudos by Activity Type')
        ax3.set_xlabel('Activity Type')
        ax3.set_ylabel('Kudos Count')
        plt.setp(ax3.xaxis.get_majorticklabels(), rotation=45)
        
        # 4. Photos vs kudos scatter
        ax4 = axes[1, 1]
        if 'total_photo_count' in self.df.columns:
            ax4.scatter(self.df['total_photo_count'], self.df['kudos_count'], alpha=0.6)
            ax4.set_xlabel('Total Photo Count')
            ax4.set_ylabel('Kudos Count')
            ax4.set_title('Photos vs Kudos Scatter Plot')
        
        plt.tight_layout()
        plt.savefig('kudos_analysis.png', dpi=300, bbox_inches='tight')
        plt.close()  # Close the figure to free memory
    
    def run_full_analysis(self, max_activities=None, fetch_kudos_givers=True):
        """Run the complete analysis"""
        print("Starting Strava Kudos Analysis...")
        
        # Load data
        self.load_data(max_activities=max_activities, fetch_kudos_givers=fetch_kudos_givers)
        
        if self.df is None or self.df.empty:
            print("No data available for analysis")
            return
        
        # Run analyses
        self.basic_stats()
        self.photo_impact_analysis()
        self.correlation_analysis()
        self.similar_activities_analysis()
        
        # Analyze top kudos givers
        kudos_counts = self.analyze_top_kudos_givers(top_n=30)
        
        # Generate visualizations
        try:
            self.generate_visualizations()
            print("\nVisualization saved as 'kudos_analysis.png'")
        except Exception as e:
            print(f"Could not generate visualizations: {e}")
        
        # Save data
        self.df.to_csv('strava_activities.csv', index=False)
        print("Data saved to 'strava_activities.csv'")
        
        if self.kudos_df is not None and not self.kudos_df.empty:
            self.kudos_df.to_csv('strava_kudos_details.csv', index=False)
            print("Kudos data saved to 'strava_kudos_details.csv'")
            
            if kudos_counts is not None and not kudos_counts.empty:
                kudos_counts.to_csv('strava_top_kudos_givers.csv', index=False)
                print("Top kudos givers saved to 'strava_top_kudos_givers.csv'")

if __name__ == "__main__":
    analyzer = KudosAnalyzer()
    analyzer.run_full_analysis(max_activities=50)  # Reduced for testing with kudos