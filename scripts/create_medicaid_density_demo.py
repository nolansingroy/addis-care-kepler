#!/usr/bin/env python3
"""
Create realistic Medicare/Medicaid density demo for Kepler visualization
"""

import pandas as pd
import numpy as np
import json

def create_medicare_medicaid_demo():
    """Create realistic Medicare/Medicaid enrollment data for demonstration"""
    
    print("🏥 Creating Medicare/Medicaid Density Demo...")
    
    # Load the geocoded data
    df = pd.read_csv('data/processed/providers_geocoded_tmp.csv')
    print(f"   Loaded {len(df):,} providers")
    
    # Create realistic Medicare/Medicaid enrollment patterns
    np.random.seed(42)  # For reproducible results
    
    # Initialize Medicare/Medicaid columns
    df['medicare_enrolled'] = False
    df['medicaid_enrolled'] = False
    df['ma_participating'] = False
    df['ma_plan_count'] = 0
    
    # Realistic enrollment patterns based on provider type and state
    for idx, row in df.iterrows():
        provider_type = row['provider_type']
        state = row['state']
        
        # HCBS providers are more likely to accept Medicare/Medicaid
        if provider_type == 'HCBS':
            # Medicare enrollment (higher for HCBS)
            if np.random.random() < 0.75:  # 75% of HCBS accept Medicare
                df.at[idx, 'medicare_enrolled'] = True
            
            # Medicaid enrollment (very high for HCBS)
            if np.random.random() < 0.85:  # 85% of HCBS accept Medicaid
                df.at[idx, 'medicaid_enrolled'] = True
            
            # Medicare Advantage participation
            if df.at[idx, 'medicare_enrolled'] and np.random.random() < 0.60:
                df.at[idx, 'ma_participating'] = True
                df.at[idx, 'ma_plan_count'] = np.random.randint(1, 8)
        
        # ALF providers have different patterns
        elif provider_type == 'ALF':
            # Medicare enrollment (lower for ALF)
            if np.random.random() < 0.45:  # 45% of ALF accept Medicare
                df.at[idx, 'medicare_enrolled'] = True
            
            # Medicaid enrollment (moderate for ALF)
            if np.random.random() < 0.55:  # 55% of ALF accept Medicaid
                df.at[idx, 'medicaid_enrolled'] = True
            
            # Medicare Advantage participation
            if df.at[idx, 'medicare_enrolled'] and np.random.random() < 0.40:
                df.at[idx, 'ma_participating'] = True
                df.at[idx, 'ma_plan_count'] = np.random.randint(1, 5)
        
        # State-specific adjustments
        if state in ['CA', 'TX', 'FL', 'NY']:
            # Higher Medicaid acceptance in these states
            if np.random.random() < 0.1:  # 10% chance to increase Medicaid acceptance
                df.at[idx, 'medicaid_enrolled'] = True
        
        if state in ['MN', 'WA', 'OR']:
            # Higher Medicare acceptance in these states
            if np.random.random() < 0.1:  # 10% chance to increase Medicare acceptance
                df.at[idx, 'medicare_enrolled'] = True
    
    # Add derived columns for visualization
    df['enrollment_status'] = df.apply(lambda row: 
        'Both Medicare & Medicaid' if row['medicare_enrolled'] and row['medicaid_enrolled']
        else 'Medicare Only' if row['medicare_enrolled']
        else 'Medicaid Only' if row['medicaid_enrolled']
        else 'Neither', axis=1)
    
    df['medicaid_density'] = df.groupby('zip')['medicaid_enrolled'].transform('sum')
    df['medicare_density'] = df.groupby('zip')['medicare_enrolled'].transform('sum')
    
    # Save the enriched data
    output_file = 'data/enriched/providers_medicare_medicaid_demo.csv'
    df.to_csv(output_file, index=False)
    
    # Print summary statistics
    print("\n📊 Medicare/Medicaid Enrollment Summary:")
    print(f"   Total providers: {len(df):,}")
    print(f"   Medicare enrolled: {df['medicare_enrolled'].sum():,} ({df['medicare_enrolled'].mean()*100:.1f}%)")
    print(f"   Medicaid enrolled: {df['medicaid_enrolled'].sum():,} ({df['medicaid_enrolled'].mean()*100:.1f}%)")
    print(f"   MA participating: {df['ma_participating'].sum():,} ({df['ma_participating'].mean()*100:.1f}%)")
    print(f"   Both Medicare & Medicaid: {((df['medicare_enrolled'] == True) & (df['medicaid_enrolled'] == True)).sum():,}")
    
    print("\n🏥 Enrollment by Provider Type:")
    enrollment_by_type = df.groupby('provider_type').agg({
        'medicare_enrolled': 'mean',
        'medicaid_enrolled': 'mean',
        'ma_participating': 'mean'
    }).round(3)
    print(enrollment_by_type)
    
    print("\n🗺️ Enrollment by State:")
    enrollment_by_state = df.groupby('state').agg({
        'medicare_enrolled': 'sum',
        'medicaid_enrolled': 'sum',
        'npi': 'count'
    }).rename(columns={'npi': 'total_providers'})
    enrollment_by_state['medicare_rate'] = (enrollment_by_state['medicare_enrolled'] / enrollment_by_state['total_providers'] * 100).round(1)
    enrollment_by_state['medicaid_rate'] = (enrollment_by_state['medicaid_enrolled'] / enrollment_by_state['total_providers'] * 100).round(1)
    print(enrollment_by_state)
    
    # Create Kepler-ready file
    kepler_file = 'data/enriched/kepler_medicare_medicaid_demo.csv'
    kepler_df = df[['npi', 'org_or_person_name', 'address_full', 'lat', 'lon', 
                   'state', 'zip', 'provider_type', 'medicare_enrolled', 'medicaid_enrolled',
                   'enrollment_status', 'medicaid_density', 'medicare_density']].copy()
    
    # Add color coding for Kepler
    kepler_df['medicaid_color'] = kepler_df['medicaid_enrolled'].map({
        True: '#FF6B6B',  # Red for Medicaid
        False: '#4ECDC4'  # Blue for non-Medicaid
    })
    
    kepler_df['medicare_color'] = kepler_df['medicare_enrolled'].map({
        True: '#45B7D1',  # Blue for Medicare
        False: '#96CEB4'  # Green for non-Medicare
    })
    
    kepler_df.to_csv(kepler_file, index=False)
    
    print(f"\n✅ Demo data created!")
    print(f"   Main file: {output_file}")
    print(f"   Kepler file: {kepler_file}")
    
    print("\n🗺️ For Kepler Visualization:")
    print("   1. Upload 'data/enriched/kepler_medicare_medicaid_demo.csv' to Kepler.gl")
    print("   2. Color by 'enrollment_status' for provider type")
    print("   3. Size by 'medicaid_density' for concentration")
    print("   4. Filter by 'medicaid_enrolled' to show only Medicaid providers")
    
    print("\n📊 Key Insights Available:")
    print("   • Medicaid provider density by ZIP code")
    print("   • Geographic coverage gaps for Medicaid")
    print("   • Provider type distribution (HCBS vs ALF)")
    print("   • State-by-state Medicaid acceptance rates")
    print("   • Network adequacy assessment")
    
    return df

if __name__ == "__main__":
    create_medicare_medicaid_demo()
