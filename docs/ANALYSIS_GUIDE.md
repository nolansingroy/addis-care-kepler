# Analysis Guide

## Getting Started with Healthcare Provider Data Analysis

This guide provides step-by-step instructions for analyzing the healthcare provider dataset using various tools and techniques.

## 🛠️ Prerequisites

### Required Software
- **Python 3.8+** with pip
- **Jupyter Notebook** or **Google Colab**
- **Kepler.gl** (web-based or desktop)
- **NotebookML** (for AI-powered analysis)

### Python Dependencies
```bash
pip install -r requirements.txt
```

## 📊 Data Loading

### Load the Dataset
```python
import pandas as pd

# Load the main dataset
df = pd.read_csv('data/processed/providers_geocoded_tmp.csv')

# Basic info
print(f"Total providers: {len(df):,}")
print(f"Columns: {list(df.columns)}")
```

### Quick Data Overview
```python
# Provider types
print(df['provider_type'].value_counts())

# States covered
print(df['state'].value_counts())

# Geocoding success
print(df['geocode_status'].value_counts())
```

## 🗺️ Geographic Analysis

### Provider Density by State
```python
state_analysis = df.groupby('state').agg({
    'npi': 'count',
    'provider_type': lambda x: (x == 'HCBS').sum()
}).rename(columns={'npi': 'total_providers', 'provider_type': 'hcbs_providers'})

state_analysis['hcbs_percentage'] = (state_analysis['hcbs_providers'] / state_analysis['total_providers'] * 100).round(1)
print(state_analysis.sort_values('total_providers', ascending=False))
```

### Provider Density by ZIP Code
```python
zip_analysis = df.groupby('zip').agg({
    'npi': 'count',
    'provider_type': lambda x: (x == 'HCBS').sum()
}).rename(columns={'npi': 'total_providers', 'provider_type': 'hcbs_providers'})

# Filter for areas with multiple providers
zip_analysis = zip_analysis[zip_analysis['total_providers'] >= 5]
print(zip_analysis.sort_values('total_providers', ascending=False).head(10))
```

### Geographic Coverage Analysis
```python
import numpy as np

# Calculate provider density
df['provider_density'] = df.groupby('zip')['npi'].transform('count')

# Identify high-density areas
high_density = df[df['provider_density'] >= 10]
print(f"High-density areas: {len(high_density['zip'].unique())} ZIP codes")

# Identify low-density areas
low_density = df[df['provider_density'] <= 2]
print(f"Low-density areas: {len(low_density['zip'].unique())} ZIP codes")
```

## 🏥 Provider Type Analysis

### HCBS vs ALF Distribution
```python
# Overall distribution
provider_dist = df['provider_type'].value_counts()
print("Provider Type Distribution:")
print(provider_dist)

# By state
state_provider_dist = df.groupby(['state', 'provider_type']).size().unstack(fill_value=0)
print("\nProvider Distribution by State:")
print(state_provider_dist)
```

### Taxonomy Code Analysis
```python
# Most common taxonomy codes
top_taxonomies = df['taxonomy_primary'].value_counts().head(10)
print("Top 10 Taxonomy Codes:")
print(top_taxonomies)

# Taxonomy codes by provider type
taxonomy_by_type = df.groupby(['provider_type', 'taxonomy_primary']).size().unstack(fill_value=0)
print("\nTaxonomy Codes by Provider Type:")
print(taxonomy_by_type)
```

## 📈 Market Analysis

### Competitive Landscape
```python
# Provider concentration by market
market_concentration = df.groupby('zip').agg({
    'npi': 'count',
    'org_or_person_name': 'nunique'
}).rename(columns={'npi': 'total_providers', 'org_or_person_name': 'unique_organizations'})

market_concentration['competition_level'] = pd.cut(
    market_concentration['unique_organizations'],
    bins=[0, 1, 3, 10, 100],
    labels=['Monopoly', 'Low Competition', 'Moderate Competition', 'High Competition']
)

print("Market Competition Analysis:")
print(market_concentration['competition_level'].value_counts())
```

### Underserved Areas Identification
```python
# Find areas with no providers
all_zips = set(df['zip'].unique())
provider_zips = set(df['zip'].unique())
no_provider_zips = all_zips - provider_zips

print(f"ZIP codes with providers: {len(provider_zips):,}")
print(f"ZIP codes without providers: {len(no_provider_zips):,}")

# Areas with only one provider type
single_type_areas = df.groupby('zip')['provider_type'].nunique()
single_type_areas = single_type_areas[single_type_areas == 1]
print(f"Areas with only one provider type: {len(single_type_areas):,}")
```

## 🗺️ Visualization with Kepler.gl

### Basic Setup
1. **Upload Data**: Go to [kepler.gl](https://kepler.gl/) and upload `data/processed/providers_geocoded_tmp.csv`
2. **Configure Layer**: Set up a point layer with:
   - **Latitude**: `lat`
   - **Longitude**: `lon`
   - **Color by**: `provider_type`
   - **Size by**: `provider_density`

### Advanced Visualizations

#### Provider Type Heatmap
```python
# Create heatmap data
heatmap_data = df.groupby(['lat', 'lon']).size().reset_index(name='provider_count')
heatmap_data.to_csv('data/processed/provider_heatmap.csv', index=False)
```

#### State Comparison Map
```python
# Aggregate by state for choropleth
state_summary = df.groupby('state').agg({
    'npi': 'count',
    'provider_type': lambda x: (x == 'HCBS').sum()
}).reset_index()
state_summary.to_csv('data/processed/state_summary.csv', index=False)
```

## 🤖 AI-Powered Analysis with NotebookML

### Sample Questions to Ask

#### Provider Distribution
- "How many providers are in each state?"
- "What's the breakdown between HCBS and ALF providers?"
- "Which zip codes have the most providers?"
- "Show me providers in California"

#### Geographic Analysis
- "Which areas have the highest provider density?"
- "Are there any geographic gaps in coverage?"
- "Map providers by state"
- "Find providers within 50 miles of [specific city]"

#### Market Intelligence
- "Identify underserved areas with few providers"
- "Which markets have the most competition?"
- "Find potential expansion opportunities"
- "Create a heatmap of provider density"

#### Quality Assessment
- "How many providers have valid coordinates?"
- "Which states have the best geocoding success rates?"
- "Are there any duplicate providers?"
- "Check for missing data in key fields"

## 📊 Statistical Analysis

### Descriptive Statistics
```python
# Provider counts by state
state_stats = df.groupby('state').agg({
    'npi': 'count',
    'provider_type': lambda x: (x == 'HCBS').sum(),
    'lat': ['mean', 'std'],
    'lon': ['mean', 'std']
}).round(3)

print("State Statistics:")
print(state_stats)
```

### Correlation Analysis
```python
# Provider density vs state characteristics
import matplotlib.pyplot as plt

# Create correlation matrix for numeric variables
numeric_cols = ['lat', 'lon']
correlation_matrix = df[numeric_cols].corr()
print("Correlation Matrix:")
print(correlation_matrix)
```

## 🔍 Advanced Analysis

### Network Analysis
```python
# Provider proximity analysis
from scipy.spatial.distance import cdist
import numpy as np

# Calculate distances between providers
coords = df[['lat', 'lon']].values
distances = cdist(coords, coords)

# Find providers within 10 miles of each other
within_10_miles = (distances < 0.1).sum(axis=1)
df['nearby_providers'] = within_10_miles - 1  # Subtract self

print(f"Providers with neighbors within 10 miles: {len(df[df['nearby_providers'] > 0])}")
```

### Predictive Modeling
```python
# Example: Predict provider type based on location
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier

# Prepare features
X = df[['lat', 'lon']]
y = df['provider_type']

# Split data
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Train model
model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(X_train, y_train)

# Evaluate
accuracy = model.score(X_test, y_test)
print(f"Model accuracy: {accuracy:.3f}")
```

## 📈 Reporting

### Generate Summary Report
```python
def generate_summary_report(df):
    """Generate a comprehensive summary report."""
    report = {
        'total_providers': len(df),
        'states_covered': df['state'].nunique(),
        'provider_types': df['provider_type'].value_counts().to_dict(),
        'geocoding_success_rate': (df['geocode_status'] == 'OK').mean(),
        'top_states': df['state'].value_counts().head(5).to_dict(),
        'avg_providers_per_zip': df.groupby('zip').size().mean()
    }
    return report

report = generate_summary_report(df)
print("Summary Report:")
for key, value in report.items():
    print(f"{key}: {value}")
```

## 🚀 Next Steps

### Data Enhancement
1. **Add Medicare/Medicaid enrollment data**
2. **Include provider quality metrics**
3. **Add population demographics**
4. **Include health outcomes data**

### Advanced Analytics
1. **Network optimization modeling**
2. **Predictive demand forecasting**
3. **Health equity analysis**
4. **Cost-benefit analysis**

### Visualization Enhancements
1. **Interactive dashboards**
2. **Real-time data updates**
3. **Custom mapping layers**
4. **Advanced filtering options**
