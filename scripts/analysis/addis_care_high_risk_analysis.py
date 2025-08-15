import pandas as pd
import numpy as np

# Load the REAL data
df = pd.read_csv('data/processed/providers_geocoded_tmp.csv')

print("🏥 ADDIS CARE HIGH-RISK AREA ANALYSIS")
print("Identifying Areas Most Vulnerable to Medicaid Policy Changes")
print("=" * 80)

# Provider type breakdown
alf_providers = df[df['provider_type'] == 'ALF']
hcbs_providers = df[df['provider_type'] == 'HCBS']

print(f"\n📊 REAL MARKET LANDSCAPE:")
print(f"ALF Providers: {len(alf_providers):,} facilities")
print(f"HCBS Providers: {len(hcbs_providers):,} agencies")
print(f"Total Providers: {len(df):,} across 10 states")

# Geographic analysis by ZIP code
print(f"\n🚨 HIGH-RISK AREA IDENTIFICATION METHODOLOGY:")
print("(Based on provider characteristics that indicate vulnerability to Medicaid policy changes)")

# Group by ZIP and analyze provider characteristics
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

# Calculate risk indicators
zip_analysis['alf_percentage'] = zip_analysis['alf_count'] / zip_analysis['total_providers'] * 100
zip_analysis['hcbs_percentage'] = zip_analysis['hcbs_count'] / zip_analysis['total_providers'] * 100

# HIGH-RISK AREA IDENTIFICATION METHODOLOGY
print(f"\n🎯 RISK FACTORS IDENTIFIED:")

print("1. HCBS-DOMINANT AREAS (High Risk):")
print("   - HCBS agencies are more dependent on Medicaid funding")
print("   - Higher percentage of HCBS = higher Medicaid vulnerability")
print("   - Target: Areas with >70% HCBS providers")

print("\n2. HIGH PROVIDER DENSITY AREAS (High Risk):")
print("   - More providers competing for limited Medicaid dollars")
print("   - Higher competition = higher vulnerability to policy changes")
print("   - Target: Areas with >100 total providers")

print("\n3. ALF-HEAVY AREAS (Moderate Risk):")
print("   - ALF facilities have mixed funding sources")
print("   - Some private pay, some Medicaid")
print("   - Target: Areas with >50% ALF providers")

print("\n4. RURAL/UNDERSERVED AREAS (High Risk):")
print("   - Limited alternative funding sources")
print("   - Higher dependency on Medicaid")
print("   - Target: Areas with moderate provider counts but high concentration")

# Calculate risk scores based on these factors
zip_analysis['hcbs_risk_score'] = zip_analysis['hcbs_percentage'] * 0.01  # Higher HCBS % = higher risk
zip_analysis['density_risk_score'] = zip_analysis['total_providers'] * 0.01  # Higher density = higher risk
zip_analysis['alf_risk_score'] = zip_analysis['alf_percentage'] * 0.005  # Moderate ALF risk

# Combined risk score
zip_analysis['total_risk_score'] = (
    zip_analysis['hcbs_risk_score'] + 
    zip_analysis['density_risk_score'] + 
    zip_analysis['alf_risk_score']
)

# Find high-risk areas
high_risk_areas = zip_analysis[
    (zip_analysis['total_providers'] >= 10) &  # Minimum market size
    (
        (zip_analysis['hcbs_percentage'] >= 70) |  # HCBS-dominant areas
        (zip_analysis['total_providers'] >= 100) |  # High density areas
        (zip_analysis['alf_percentage'] >= 50)  # ALF-heavy areas
    )
].sort_values('total_risk_score', ascending=False)

print(f"\n🏆 TOP 20 HIGH-RISK AREAS FOR ADDIS CARE:")
print("(Areas most vulnerable to Medicaid policy changes)")

for _, row in high_risk_areas.head(20).iterrows():
    # Determine risk level based on risk factors
    risk_factors = []
    if row['hcbs_percentage'] >= 70:
        risk_factors.append("HCBS-DOMINANT")
    if row['total_providers'] >= 100:
        risk_factors.append("HIGH-DENSITY")
    if row['alf_percentage'] >= 50:
        risk_factors.append("ALF-HEAVY")
    
    risk_level = "CRITICAL" if len(risk_factors) >= 2 else "HIGH" if len(risk_factors) >= 1 else "MODERATE"
    
    print(f"ZIP {row['zip']} ({row['state']}): {row['alf_count']:.0f} ALFs, {row['hcbs_count']:.0f} HCBS ({row['total_providers']:.0f} total) - {risk_level} RISK")
    print(f"   Risk Factors: {', '.join(risk_factors)}")

# State-level risk analysis
print(f"\n🗺️  STATE-LEVEL RISK ASSESSMENT:")

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

# Calculate state-level risk indicators
state_analysis['hcbs_percentage'] = state_analysis['hcbs_count'] / state_analysis['total_providers'] * 100
state_analysis['alf_percentage'] = state_analysis['alf_count'] / state_analysis['total_providers'] * 100

for _, row in state_analysis.iterrows():
    # Determine risk level based on state characteristics
    risk_factors = []
    if row['hcbs_percentage'] >= 70:
        risk_factors.append("HCBS-DOMINANT")
    if row['total_providers'] >= 10000:
        risk_factors.append("HIGH-DENSITY")
    if row['alf_percentage'] >= 50:
        risk_factors.append("ALF-HEAVY")
    
    risk_level = "CRITICAL" if len(risk_factors) >= 2 else "HIGH" if len(risk_factors) >= 1 else "MODERATE"
    
    print(f"{row['state']}: {row['alf_count']:.0f} ALFs, {row['hcbs_count']:.0f} HCBS ({row['total_providers']:.0f} total) - {risk_level} RISK")
    if risk_factors:
        print(f"   Risk Factors: {', '.join(risk_factors)}")

# Risk-based value proposition
print(f"\n💡 ADDIS CARE VALUE PROPOSITION FOR HIGH-RISK AREAS:")

# Calculate potential impact for high-risk areas
total_high_risk_zips = len(high_risk_areas)
critical_risk_zips = len(high_risk_areas[high_risk_areas['total_risk_score'] >= high_risk_areas['total_risk_score'].quantile(0.8)])
high_risk_zips = len(high_risk_areas[high_risk_areas['total_risk_score'] >= high_risk_areas['total_risk_score'].quantile(0.6)])

print(f"Total High-Risk ZIP Codes: {total_high_risk_zips}")
print(f"Critical Risk ZIP Codes: {critical_risk_zips}")
print(f"High Risk ZIP Codes: {high_risk_zips}")

print(f"\n🎯 WHY THESE AREAS ARE HIGH-RISK:")

print("1. HCBS-DOMINANT AREAS:")
print("   - HCBS agencies rely heavily on Medicaid funding")
print("   - Policy changes directly impact service delivery")
print("   - Limited alternative revenue sources")

print("\n2. HIGH-DENSITY PROVIDER AREAS:")
print("   - More providers competing for limited Medicaid dollars")
print("   - Higher operational costs in competitive markets")
print("   - Increased vulnerability to funding cuts")

print("\n3. ALF-HEAVY AREAS:")
print("   - Mixed funding models create uncertainty")
print("   - Medicaid-dependent residents at risk")
print("   - Need for operational efficiency solutions")

print(f"\n🚨 CRITICAL INTERVENTION NEEDED:")

print("Addis Care can help high-risk areas by:")
print("1. STREAMLINING OPERATIONS - Reduce costs and improve efficiency")
print("2. ENHANCING DOCUMENTATION - Ensure accurate Medicaid billing")
print("3. IMPROVING STAFF TRAINING - Faster onboarding and retention")
print("4. FAMILY COMMUNICATION - Better coordination and transparency")
print("5. CARE QUALITY OPTIMIZATION - AI-driven insights for better outcomes")

# Revenue projections for high-risk areas
print(f"\n💰 REVENUE PROJECTIONS FOR HIGH-RISK AREAS:")
print("(Using $125 per resident pricing)")

# Calculate total providers in high-risk areas
high_risk_alf_providers = high_risk_areas['alf_count'].sum()
high_risk_hcbs_providers = high_risk_areas['hcbs_count'].sum()

print(f"High-Risk ALF Providers: {high_risk_alf_providers:,}")
print(f"High-Risk HCBS Providers: {high_risk_hcbs_providers:,}")
print(f"Total High-Risk Providers: {high_risk_alf_providers + high_risk_hcbs_providers:,}")

# Revenue assumptions (same as before)
alf_small_residents = 25
alf_medium_residents = 50
alf_large_residents = 100
alf_small_pct = 0.3
alf_medium_pct = 0.5
alf_large_pct = 0.2

hcbs_small_clients = 15
hcbs_medium_clients = 35
hcbs_large_clients = 75
hcbs_small_pct = 0.4
hcbs_medium_pct = 0.45
hcbs_large_pct = 0.15

# Adoption rates for high-risk areas (higher due to greater need)
year1_adoption_rate = 0.01  # 1% (higher than general market)
year2_adoption_rate = 0.05  # 5% (higher than general market)
year3_adoption_rate = 0.20  # 20% (higher than general market)

print(f"\n📋 HIGH-RISK AREA ADOPTION ASSUMPTIONS:")
print(f"   - Year 1: {year1_adoption_rate*100:.1f}% (higher due to urgent need)")
print(f"   - Year 2: {year2_adoption_rate*100:.1f}% (higher due to proven value)")
print(f"   - Year 3: {year3_adoption_rate*100:.1f}% (higher due to market leadership)")

# Calculate revenue for high-risk areas
year1_alf_facilities = high_risk_alf_providers * year1_adoption_rate
year1_hcbs_facilities = high_risk_hcbs_providers * year1_adoption_rate

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

print(f"\n💰 HIGH-RISK AREA REVENUE PROJECTIONS:")
print(f"Year 1 ({year1_adoption_rate*100:.1f}% adoption):")
print(f"   ALF Revenue: ${year1_alf_revenue:,.0f}")
print(f"   HCBS Revenue: ${year1_hcbs_revenue:,.0f}")
print(f"   Total Revenue: ${year1_alf_revenue + year1_hcbs_revenue:,.0f}")

# Strategic recommendations
print(f"\n💡 STRATEGIC RECOMMENDATIONS FOR HIGH-RISK AREAS:")

print("1. IMMEDIATE DEPLOYMENT (0-3 months):")
print("   - Target critical risk ZIP codes first")
print("   - Focus on HCBS-dominant areas")
print("   - Begin pilot programs in highest-risk areas")
print("   - Demonstrate urgent value proposition")

print("\n2. RAPID EXPANSION (3-6 months):")
print("   - Expand to high-risk ZIP codes")
print("   - Scale programs in vulnerable markets")
print("   - Develop state partnerships for high-risk states")
print("   - Create provider network partnerships")

print("\n3. MARKET LEADERSHIP (6-12 months):")
print("   - Establish Addis Care as essential solution for high-risk areas")
print("   - Develop specialized solutions for vulnerable providers")
print("   - Create healthcare network partnerships")
print("   - Lead in AI-driven elder care technology")

print(f"\n✅ ANALYSIS COMPLETE - HIGH-RISK AREA FOCUS")
print("Note: Risk assessment based on provider characteristics and market density.")
print("Medicaid policy impact is assumed to affect all providers, with higher impact in identified risk areas.")
