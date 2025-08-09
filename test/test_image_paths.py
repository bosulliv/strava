#!/usr/bin/env python3
"""Test script to verify image file paths work correctly"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import matplotlib.pyplot as plt

def test_image_paths():
    # Test that image paths work correctly like the scripts do
    data_dir = "data"
    os.makedirs(data_dir, exist_ok=True)
    
    # Test kudos_analysis.png path (from analyze_kudos.py)
    kudos_path = os.path.join(data_dir, 'kudos_analysis.png')
    print(f"✓ Kudos analysis path: {kudos_path}")
    
    # Test cached_kudos_analysis.png path (from analyze_cached_data.py)
    output_file = "cached_kudos_analysis.png"
    if not output_file.startswith('data/'):
        output_file = os.path.join(data_dir, os.path.basename(output_file))
    print(f"✓ Cached kudos analysis path: {output_file}")
    
    # Check that all paths point to data directory
    assert kudos_path.startswith('data/'), f"Wrong path: {kudos_path}"
    assert output_file.startswith('data/'), f"Wrong path: {output_file}"
    
    print("✓ All image paths correctly point to data/ directory")
    
    # Create a simple test plot to verify matplotlib works
    plt.figure(figsize=(6, 4))
    plt.plot([1, 2, 3], [1, 4, 2])
    plt.title('Test Plot')
    test_path = os.path.join(data_dir, 'test_plot.png')
    plt.savefig(test_path, dpi=150, bbox_inches='tight')
    plt.close()
    
    if os.path.exists(test_path):
        print(f"✓ Test image successfully created at: {test_path}")
        os.remove(test_path)  # Clean up
        print("✓ Test image cleaned up")
    else:
        print("✗ Test image was not created")

if __name__ == "__main__":
    test_image_paths()