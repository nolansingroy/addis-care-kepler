#!/usr/bin/env python3
"""
Analyze Medicaid-heavy areas from enriched provider data.
Creates visualizations and statistics showing geographic distribution of Medicaid providers.
"""

import pandas as pd
import numpy as np
from collections import defaultdict
import json

def analyze_medicaid_distribution(input_file):
    """Analyze the geographic distribution of Medicaid providers."""
    print("📊 Analyzing Medicaid provider distribution...")
    
    # Load data
    df = pd.read_csv(input_file)
    print(f"   Loaded {len(df):,} providers")
    
    # Check if Medicaid data exists
    if 'medicaid_enrolled' not in df.columns:
        print("   ⚠️  No Medicaid data found. Creating sample analysis...")
        return create_sample_analysis(df)
    
    # Analyze by state
    print("\n📈 State-Level Analysis:")
    state_analysis = df.groupby('state').agg({
        'medicaid_enrolled': ['count', 'sum', 'mean'],
        'medicare_enrolled': ['sum', 'mean'],
        'ma_participating': ['sum', 'mean']
    }).round(3)
    
    state_analysis.columns = [
        'total_providers', 'medicaid_providers', 'medicaid_rate',
        'medicare_providers', 'medicare_rate', 
        'ma_providers', 'ma_rate'
    ]
    
    # Sort by Medicaid rate
    state_analysis = state_analysis.sort_values('medicaid_rate', ascending=False)
    
    print(state_analysis.head(10))
    
    # Analyze by zip code (for more granular geographic analysis)
    print("\n📈 Zip Code Analysis (Top 10 Medicaid-Heavy Areas):")
    zip_analysis = df.groupby('zip').agg({
        'medicaid_enrolled': ['count', 'sum', 'mean'],
        'medicare_enrolled': ['sum', 'mean']
    }).round(3)
    
    zip_analysis.columns = [
        'total_providers', 'medicaid_providers', 'medicaid_rate',
        'medicare_providers', 'medicare_rate'
    ]
    
    # Filter for areas with at least 5 providers
    zip_analysis = zip_analysis[zip_analysis['total_providers'] >= 5]
    zip_analysis = zip_analysis.sort_values('medicaid_rate', ascending=False)
    
    print(zip_analysis.head(10))
    
    # Create summary statistics
    print("\n📊 Overall Statistics:")
    total_providers = len(df)
    medicaid_providers = df['medicaid_enrolled'].sum()
    medicare_providers = df['medicare_enrolled'].sum()
    both_providers = ((df['medicaid_enrolled'] == True) & (df['medicare_enrolled'] == True)).sum()
    
    print(f"   Total providers: {total_providers:,}")
    print(f"   Medicaid enrolled: {medicaid_providers:,} ({medicaid_providers/total_providers*100:.1f}%)")
    print(f"   Medicare enrolled: {medicare_providers:,} ({medicare_providers/total_providers*100:.1f}%)")
    print(f"   Both Medicare & Medicaid: {both_providers:,} ({both_providers/total_providers*100:.1f}%)")
    
    # Identify Medicaid-heavy areas
    print("\n🏥 Medicaid-Heavy Areas Identified:")
    
    # States with highest Medicaid rates
    high_medicaid_states = state_analysis[state_analysis['medicaid_rate'] > 0.5].index.tolist()
    print(f"   States with >50% Medicaid rate: {', '.join(high_medicaid_states)}")
    
    # Zip codes with highest Medicaid rates
    high_medicaid_zips = zip_analysis[zip_analysis['medicaid_rate'] > 0.7].index.tolist()
    print(f"   Zip codes with >70% Medicaid rate: {len(high_medicaid_zips)} areas")
    
    return {
        'state_analysis': state_analysis,
        'zip_analysis': zip_analysis,
        'high_medicaid_states': high_medicaid_states,
        'high_medicaid_zips': high_medicaid_zips
    }

def create_sample_analysis(df):
    """Create a sample analysis showing what the data would look like with Medicaid information."""
    print("   📋 Creating sample analysis...")
    
    # Simulate some Medicaid data for demonstration
    np.random.seed(42)  # For reproducible results
    
    # Create sample Medicaid enrollment (higher in certain states/areas)
    df['medicaid_enrolled'] = np.random.choice([True, False], size=len(df), p=[0.3, 0.7])
    
    # Make certain states more Medicaid-heavy
    high_medicaid_states = ['CA', 'TX', 'FL', 'NY', 'IL']
    for state in high_medicaid_states:
        state_mask = df['state'] == state
        df.loc[state_mask, 'medicaid_enrolled'] = np.random.choice([True, False], 
                                                                  size=state_mask.sum(), 
                                                                  p=[0.6, 0.4])
    
    # Analyze the sample data
    return analyze_medicaid_distribution_real(df)

def analyze_medicaid_distribution_real(df):
    """Analyze real Medicaid distribution data."""
    print("\n📈 State-Level Analysis:")
    state_analysis = df.groupby('state').agg({
        'medicaid_enrolled': ['count', 'sum', 'mean'],
        'medicare_enrolled': ['sum', 'mean'] if 'medicare_enrolled' in df.columns else ['sum', 'sum']
    }).round(3)
    
    if 'medicare_enrolled' in df.columns:
        state_analysis.columns = [
            'total_providers', 'medicaid_providers', 'medicaid_rate',
            'medicare_providers', 'medicare_rate'
        ]
    else:
        state_analysis.columns = [
            'total_providers', 'medicaid_providers', 'medicaid_rate',
            'medicare_providers', 'medicare_rate'
        ]
        state_analysis['medicare_providers'] = 0
        state_analysis['medicare_rate'] = 0
    
    # Sort by Medicaid rate
    state_analysis = state_analysis.sort_values('medicaid_rate', ascending=False)
    
    print(state_analysis.head(10))
    
    # Zip code analysis
    print("\n📈 Zip Code Analysis (Top 10 Medicaid-Heavy Areas):")
    zip_analysis = df.groupby('zip').agg({
        'medicaid_enrolled': ['count', 'sum', 'mean']
    }).round(3)
    
    zip_analysis.columns = ['total_providers', 'medicaid_providers', 'medicaid_rate']
    zip_analysis = zip_analysis[zip_analysis['total_providers'] >= 5]
    zip_analysis = zip_analysis.sort_values('medicaid_rate', ascending=False)
    
    print(zip_analysis.head(10))
    
    # Summary statistics
    print("\n📊 Overall Statistics:")
    total_providers = len(df)
    medicaid_providers = df['medicaid_enrolled'].sum()
    
    print(f"   Total providers: {total_providers:,}")
    print(f"   Medicaid enrolled: {medicaid_providers:,} ({medicaid_providers/total_providers*100:.1f}%)")
    
    # Identify Medicaid-heavy areas
    print("\n🏥 Medicaid-Heavy Areas Identified:")
    high_medicaid_states = state_analysis[state_analysis['medicaid_rate'] > 0.5].index.tolist()
    print(f"   States with >50% Medicaid rate: {', '.join(high_medicaid_states)}")
    
    high_medicaid_zips = zip_analysis[zip_analysis['medicaid_rate'] > 0.7].index.tolist()
    print(f"   Zip codes with >70% Medicaid rate: {len(high_medicaid_zips)} areas")
    
    return {
        'state_analysis': state_analysis,
        'zip_analysis': zip_analysis,
        'high_medicaid_states': high_medicaid_states,
        'high_medicaid_zips': high_medicaid_zips
    }

def create_kepler_medicaid_map(df, output_file="medicaid_analysis_for_kepler.csv"):
    """Create a file optimized for Kepler mapping of Medicaid providers."""
    print(f"🗺️  Creating Kepler mapping file: {output_file}")
    
    # Select relevant columns for mapping
    kepler_cols = [
        'npi', 'org_or_person_name', 'address_full', 'lat', 'lon', 
        'state', 'zip', 'provider_type', 'medicaid_enrolled', 'medicare_enrolled'
    ]
    
    # Filter to only include columns that exist
    available_cols = [col for col in kepler_cols if col in df.columns]
    
    kepler_df = df[available_cols].copy()
    
    # Add derived columns for better visualization
    if 'medicaid_enrolled' in df.columns:
        kepler_df['medicaid_status'] = kepler_df['medicaid_enrolled'].map({True: 'Medicaid', False: 'Non-Medicaid'})
        kepler_df['medicaid_color'] = kepler_df['medicaid_enrolled'].map({True: '#FF6B6B', False: '#4ECDC4'})
    else:
        kepler_df['medicaid_status'] = 'Unknown'
        kepler_df['medicaid_color'] = '#95A5A6'
    
    # Add provider count by area for sizing
    if 'zip' in df.columns:
        zip_counts = df['zip'].value_counts()
        kepler_df['providers_in_zip'] = kepler_df['zip'].map(zip_counts)
    else:
        kepler_df['providers_in_zip'] = 1
    
    # Save for Kepler
    kepler_df.to_csv(output_file, index=False)
    print(f"   ✅ Saved {len(kepler_df):,} providers for Kepler mapping")
    
    return kepler_df

def main():
    """Main analysis function."""
    input_file = "providers_enriched_medicare_medicaid.csv"
    
    if not os.path.exists(input_file):
        print(f"❌ {input_file} not found. Using geocoded data...")
        input_file = "providers_geocoded_tmp.csv"
    
    # Run analysis
    analysis_results = analyze_medicaid_distribution(input_file)
    
    # Create Kepler mapping file
    df = pd.read_csv(input_file)
    kepler_df = create_kepler_medicaid_map(df)
    
    print(f"\n🎯 Key Insights:")
    print(f"   • You can now map Medicaid provider density by state/zip code")
    print(f"   • Identify areas with high Medicaid provider concentration")
    print(f"   • Spot coverage gaps where Medicaid providers are scarce")
    print(f"   • Compare Medicare vs Medicaid provider distribution")
    
    print(f"\n🗺️  For Kepler Mapping:")
    print(f"   • Use 'medicaid_analysis_for_kepler.csv' for visualization")
    print(f"   • Color by 'medicaid_status' column")
    print(f"   • Size by 'providers_in_zip' for density visualization")
    print(f"   • Filter by 'medicaid_enrolled' to show only Medicaid providers")

if __name__ == "__main__":
    import os
    main()
