import pandas as pd
import numpy as np

# Load the REAL data (not simulated)
df = pd.read_csv('data/processed/providers_geocoded_tmp.csv')

print("🏥 ADDIS CARE REAL DATA ANALYSIS")
print("Geographic Market Opportunity Analysis - Based on Actual Provider Data")
print("=" * 80)

# Provider type breakdown (REAL DATA)
alf_providers = df[df['provider_type'] == 'ALF']
hcbs_providers = df[df['provider_type'] == 'HCBS']

print(f"\n📊 REAL MARKET LANDSCAPE:")
print(f"ALF Providers: {len(alf_providers):,} facilities")
print(f"HCBS Providers: {len(hcbs_providers):,} agencies")
print(f"Total Providers: {len(df):,} across 10 states")

# Geographic analysis by ZIP code
print(f"\n🗺️  GEOGRAPHIC MARKET OPPORTUNITIES:")
print("(Areas with high provider density = easier market penetration)")

# Group by ZIP and analyze provider density
zip_analysis = df.groupby('zip').agg({
    'provider_type': 'count',
    'state': 'first'
}).reset_index()
zip_analysis.columns = ['zip', 'total_providers', 'state']

# Add ALF-specific analysis
alf_by_zip = alf_providers.groupby('zip').agg({
    'provider_type': 'count',
    'state': 'first'
}).reset_index()
alf_by_zip.columns = ['zip', 'alf_count', 'state']

# Add HCBS-specific analysis
hcbs_by_zip = hcbs_providers.groupby('zip').agg({
    'provider_type': 'count',
    'state': 'first'
}).reset_index()
hcbs_by_zip.columns = ['zip', 'hcbs_count', 'state']

# Merge all data
zip_analysis = zip_analysis.merge(alf_by_zip, on='zip', how='left', suffixes=('', '_alf'))
zip_analysis = zip_analysis.merge(hcbs_by_zip, on='zip', how='left', suffixes=('', '_hcbs'))
zip_analysis = zip_analysis.fillna(0)

# Calculate market opportunity scores
zip_analysis['alf_percentage'] = zip_analysis['alf_count'] / zip_analysis['total_providers'] * 100
zip_analysis['hcbs_percentage'] = zip_analysis['hcbs_count'] / zip_analysis['total_providers'] * 100

# Market opportunity score (higher = better for Addis Care)
zip_analysis['market_opportunity_score'] = (
    (zip_analysis['alf_count'] * 2) +  # ALF facilities are primary target
    (zip_analysis['hcbs_count'] * 1) +  # HCBS agencies are secondary target
    (zip_analysis['total_providers'] * 0.5)  # Bonus for high provider density
)

# Find high-opportunity areas for Addis Care
high_opportunity_areas = zip_analysis[
    (zip_analysis['total_providers'] >= 10) &  # Minimum market size
    ((zip_analysis['alf_count'] >= 5) | (zip_analysis['hcbs_count'] >= 20))  # Good provider mix
].sort_values('market_opportunity_score', ascending=False)

print(f"\n🏆 TOP 20 HIGH-OPPORTUNITY AREAS FOR ADDIS CARE:")
print("(Areas with high provider density - easier market penetration and higher impact potential)")

for _, row in high_opportunity_areas.head(20).iterrows():
    # Determine opportunity level based on provider density
    opportunity_level = "PREMIUM" if row['total_providers'] >= 200 else "HIGH" if row['total_providers'] >= 100 else "MEDIUM"
    
    print(f"ZIP {row['zip']} ({row['state']}): {row['alf_count']:.0f} ALFs, {row['hcbs_count']:.0f} HCBS ({row['total_providers']:.0f} total) - {opportunity_level} OPPORTUNITY")

# State-level analysis
print(f"\n🗺️  STATE-LEVEL MARKET OPPORTUNITIES:")

state_analysis = df.groupby('state').agg({
    'provider_type': 'count'
}).reset_index()
state_analysis.columns = ['state', 'total_providers']

# Add provider type breakdown by state
state_alf = alf_providers.groupby('state').agg({
    'provider_type': 'count'
}).reset_index()
state_alf.columns = ['state', 'alf_count']

state_hcbs = hcbs_providers.groupby('state').agg({
    'provider_type': 'count'
}).reset_index()
state_hcbs.columns = ['state', 'hcbs_count']

# Merge state data
state_analysis = state_analysis.merge(state_alf, on='state', how='left')
state_analysis = state_analysis.merge(state_hcbs, on='state', how='left')
state_analysis = state_analysis.fillna(0)

for _, row in state_analysis.iterrows():
    # Determine opportunity level based on total providers
    opportunity_level = "PREMIUM" if row['total_providers'] >= 10000 else "HIGH" if row['total_providers'] >= 5000 else "MEDIUM"
    print(f"{row['state']}: {row['alf_count']:.0f} ALFs, {row['hcbs_count']:.0f} HCBS ({row['total_providers']:.0f} total) - {opportunity_level} OPPORTUNITY")

# Addis Care value proposition analysis
print(f"\n💡 ADDIS CARE VALUE PROPOSITION FOR MEDICAID POLICY CHANGES:")

# Calculate potential impact for both provider types
total_alf_providers = len(alf_providers)
total_hcbs_providers = len(hcbs_providers)

print(f"Total ALF market: {total_alf_providers:,} facilities")
print(f"Total HCBS market: {total_hcbs_providers:,} agencies")
print(f"Combined market: {total_alf_providers + total_hcbs_providers:,} providers")

print(f"\n🎯 ADDIS CARE CAN HELP ALL PROVIDERS WITH MEDICAID POLICY CHANGES:")

# 1. Staff training and retention
print("1. STAFF TRAINING & RETENTION:")
print(f"   - {total_alf_providers:,} ALF facilities need faster staff training")
print(f"   - {total_hcbs_providers:,} HCBS agencies need staff support")
print(f"   - AI-driven insights can improve care quality across all facilities")

# 2. Documentation and compliance
print("\n2. DOCUMENTATION & COMPLIANCE:")
print(f"   - All {total_alf_providers:,} ALF facilities need accurate documentation")
print(f"   - All {total_hcbs_providers:,} HCBS agencies need compliance help")
print(f"   - Streamlined back-office operations for all {total_alf_providers + total_hcbs_providers:,} providers")

# 3. Family communication
print("\n3. FAMILY COMMUNICATION:")
print(f"   - Real-time family communication for {total_alf_providers:,} ALF facilities")
print(f"   - Family coordination for {total_hcbs_providers:,} HCBS agencies")
print(f"   - Improved transparency and trust building")

# 4. Care quality improvement
print("\n4. CARE QUALITY IMPROVEMENT:")
print(f"   - AI-driven insights for {total_alf_providers + total_hcbs_providers:,} providers")
print(f"   - Personalized care plans for residents")
print(f"   - Proactive care management")

# Market opportunity analysis
print(f"\n🎯 PRIORITY AREAS FOR ADDIS CARE DEPLOYMENT:")
print("(Based on provider density and market opportunity scores)")

# Premium opportunity areas (top 10% by market opportunity score)
premium_threshold = high_opportunity_areas['market_opportunity_score'].quantile(0.9)
premium_areas = high_opportunity_areas[high_opportunity_areas['market_opportunity_score'] >= premium_threshold]

print(f"PREMIUM OPPORTUNITY AREAS ({len(premium_areas)} ZIP codes):")
print("   - Highest provider density")
print("   - Easiest market penetration")
print("   - Highest potential impact")

# High opportunity areas (top 25% by market opportunity score)
high_threshold = high_opportunity_areas['market_opportunity_score'].quantile(0.75)
high_areas = high_opportunity_areas[
    (high_opportunity_areas['market_opportunity_score'] >= high_threshold) &
    (high_opportunity_areas['market_opportunity_score'] < premium_threshold)
]

print(f"HIGH OPPORTUNITY AREAS ({len(high_areas)} ZIP codes):")
print("   - Strong provider density")
print("   - Good market potential")
print("   - Strong opportunity for Addis Care")

# Market expansion opportunities
print(f"\n📈 MARKET EXPANSION OPPORTUNITIES:")
print("Top 5 states by total provider count:")

for _, row in state_analysis.nlargest(5, 'total_providers').iterrows():
    print(f"   {row['state']}: {row['alf_count']:.0f} ALFs, {row['hcbs_count']:.0f} HCBS ({row['total_providers']:.0f} total)")

# Revenue projections based on real market size
print(f"\n💰 REVENUE PROJECTIONS BASED ON REAL MARKET SIZE:")
print("(Using $125 per resident pricing for both ALF and HCBS)")

# Facility size assumptions (clearly stated)
print("\n📋 CLEARLY STATED REVENUE ASSUMPTIONS:")

# ALF Facility Size Assumptions
alf_small_residents = 25
alf_medium_residents = 50
alf_large_residents = 100
alf_small_pct = 0.3
alf_medium_pct = 0.5
alf_large_pct = 0.2

# HCBS Agency Size Assumptions
hcbs_small_clients = 15
hcbs_medium_clients = 35
hcbs_large_clients = 75
hcbs_small_pct = 0.4
hcbs_medium_pct = 0.45
hcbs_large_pct = 0.15

print("ALF Facility Size Distribution:")
print(f"   - Small (25 residents): {alf_small_pct*100:.0f}% of facilities")
print(f"   - Medium (50 residents): {alf_medium_pct*100:.0f}% of facilities")
print(f"   - Large (100 residents): {alf_large_pct*100:.0f}% of facilities")

print("\nHCBS Agency Size Distribution:")
print(f"   - Small (15 clients): {hcbs_small_pct*100:.0f}% of agencies")
print(f"   - Medium (35 clients): {hcbs_medium_pct*100:.0f}% of agencies")
print(f"   - Large (75 clients): {hcbs_large_pct*100:.0f}% of agencies")

# Adoption rate assumptions
year1_adoption_rate = 0.005  # 0.5%
year2_adoption_rate = 0.02   # 2%
year3_adoption_rate = 0.10   # 10%

print(f"\nAdoption Rate Assumptions:")
print(f"   - Year 1: {year1_adoption_rate*100:.1f}% of providers")
print(f"   - Year 2: {year2_adoption_rate*100:.1f}% of providers")
print(f"   - Year 3: {year3_adoption_rate*100:.1f}% of providers")

# Calculate revenue projections
year1_alf_facilities = total_alf_providers * year1_adoption_rate
year1_hcbs_facilities = total_hcbs_providers * year1_adoption_rate

year1_alf_revenue = (
    (year1_alf_facilities * alf_small_pct * alf_small_residents * 125 * 12) +
    (year1_alf_facilities * alf_medium_pct * alf_medium_residents * 125 * 12) +
    (year1_alf_facilities * alf_large_pct * alf_large_residents * 125 * 12)
)

year1_hcbs_revenue = (
    (year1_hcbs_facilities * hcbs_small_pct * hcbs_small_clients * 125 * 12) +
    (year1_hcbs_facilities * hcbs_medium_pct * hcbs_medium_clients * 125 * 12) +
    (year1_hcbs_facilities * hcbs_large_pct * hcbs_large_clients * 125 * 12)
)

print(f"\n💰 PROJECTED REVENUE (Year 1 - {year1_adoption_rate*100:.1f}% adoption):")
print(f"   ALF Revenue: ${year1_alf_revenue:,.0f}")
print(f"   HCBS Revenue: ${year1_hcbs_revenue:,.0f}")
print(f"   Total Revenue: ${year1_alf_revenue + year1_hcbs_revenue:,.0f}")

# Year 2 projections
year2_alf_facilities = total_alf_providers * year2_adoption_rate
year2_hcbs_facilities = total_hcbs_providers * year2_adoption_rate

year2_alf_revenue = (
    (year2_alf_facilities * alf_small_pct * alf_small_residents * 125 * 12) +
    (year2_alf_facilities * alf_medium_pct * alf_medium_residents * 125 * 12) +
    (year2_alf_facilities * alf_large_pct * alf_large_residents * 125 * 12)
)

year2_hcbs_revenue = (
    (year2_hcbs_facilities * hcbs_small_pct * hcbs_small_clients * 125 * 12) +
    (year2_hcbs_facilities * hcbs_medium_pct * hcbs_medium_clients * 125 * 12) +
    (year2_hcbs_facilities * hcbs_large_pct * hcbs_large_clients * 125 * 12)
)

print(f"\n💰 PROJECTED REVENUE (Year 2 - {year2_adoption_rate*100:.1f}% adoption):")
print(f"   ALF Revenue: ${year2_alf_revenue:,.0f}")
print(f"   HCBS Revenue: ${year2_hcbs_revenue:,.0f}")
print(f"   Total Revenue: ${year2_alf_revenue + year2_hcbs_revenue:,.0f}")

# Total market potential
total_alf_revenue_potential = (
    (total_alf_providers * alf_small_pct * alf_small_residents * 125 * 12) +
    (total_alf_providers * alf_medium_pct * alf_medium_residents * 125 * 12) +
    (total_alf_providers * alf_large_pct * alf_large_residents * 125 * 12)
)

total_hcbs_revenue_potential = (
    (total_hcbs_providers * hcbs_small_pct * hcbs_small_clients * 125 * 12) +
    (total_hcbs_providers * hcbs_medium_pct * hcbs_medium_clients * 125 * 12) +
    (total_hcbs_providers * hcbs_large_pct * hcbs_large_clients * 125 * 12)
)

print(f"\n📊 TOTAL MARKET POTENTIAL:")
print(f"   ALF Market: ${total_alf_revenue_potential:,.0f} annual revenue potential")
print(f"   HCBS Market: ${total_hcbs_revenue_potential:,.0f} annual revenue potential")
print(f"   Combined Market: ${total_alf_revenue_potential + total_hcbs_revenue_potential:,.0f} annual revenue potential")

# Strategic recommendations
print(f"\n💡 STRATEGIC RECOMMENDATIONS FOR ADDIS CARE:")

print("1. IMMEDIATE DEPLOYMENT (0-3 months):")
print("   - Target premium opportunity ZIP codes first")
print("   - Focus on high-density provider areas")
print("   - Begin pilot programs in top 20 ZIP codes")
print("   - Demonstrate value proposition in both ALF and HCBS markets")

print("\n2. RAPID EXPANSION (3-6 months):")
print("   - Expand to high opportunity ZIP codes")
print("   - Scale programs in target markets")
print("   - Develop state partnerships")
print("   - Create provider network partnerships")

print("\n3. MARKET LEADERSHIP (6-12 months):")
print("   - Establish Addis Care as industry standard")
print("   - Develop specialized solutions for each provider type")
print("   - Create healthcare network partnerships")
print("   - Lead in AI-driven elder care technology")

print(f"\n✅ ANALYSIS COMPLETE - BASED ON REAL PROVIDER DATA")
print("Note: This analysis focuses on geographic opportunities and market potential.")
print("Medicaid policy impact is assumed to affect all providers equally.")
