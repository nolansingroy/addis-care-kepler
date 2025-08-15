#!/usr/bin/env python3
import pandas as pd
import numpy as np

# Load the geocoded data
df = pd.read_csv('providers_geocoded_tmp.csv')
print(f"📊 Loaded {len(df):,} providers")

# Create sample Medicaid data for demonstration
np.random.seed(42)
df['medicaid_enrolled'] = np.random.choice([True, False], size=len(df), p=[0.3, 0.7])

# Make certain states more Medicaid-heavy (realistic pattern)
high_medicaid_states = ['CA', 'TX', 'FL', 'NY', 'IL']
for state in high_medicaid_states:
    state_mask = df['state'] == state
    df.loc[state_mask, 'medicaid_enrolled'] = np.random.choice([True, False], 
                                                              size=state_mask.sum(), 
                                                              p=[0.6, 0.4])

# Analyze by state
state_analysis = df.groupby('state').agg({
    'medicaid_enrolled': ['count', 'sum', 'mean']
}).round(3)

state_analysis.columns = ['total_providers', 'medicaid_providers', 'medicaid_rate']
state_analysis = state_analysis.sort_values('medicaid_rate', ascending=False)

print('\n📊 Sample Medicaid Analysis (What it would show):')
print('=' * 60)
print(state_analysis.head(10))

# Identify Medicaid-heavy areas
high_medicaid_states = state_analysis[state_analysis['medicaid_rate'] > 0.5].index.tolist()
print(f'\n🏥 Medicaid-Heavy States Identified:')
print(f'   States with >50% Medicaid rate: {", ".join(high_medicaid_states)}')

# Zip code analysis
zip_analysis = df.groupby('zip').agg({
    'medicaid_enrolled': ['count', 'sum', 'mean']
}).round(3)

zip_analysis.columns = ['total_providers', 'medicaid_providers', 'medicaid_rate']
zip_analysis = zip_analysis[zip_analysis['total_providers'] >= 5]
zip_analysis = zip_analysis.sort_values('medicaid_rate', ascending=False)

print(f'\n📈 Top 5 Medicaid-Heavy Zip Codes:')
print(zip_analysis.head(5))

print(f'\n📈 This would show you:')
print(f'   • Which states have the highest Medicaid provider density')
print(f'   • Geographic patterns in Medicaid coverage')
print(f'   • Areas that might need more Medicaid providers')
print(f'   • Provider distribution by state/zip code')
print(f'   • Coverage gaps where Medicaid providers are scarce')

print(f'\n🗺️  For Kepler Mapping:')
print(f'   • Color providers by Medicaid status (Red=Medicaid, Blue=Non-Medicaid)')
print(f'   • Size points by provider density in each area')
print(f'   • Filter to show only Medicaid providers')
print(f'   • Create heatmaps showing Medicaid provider concentration')
