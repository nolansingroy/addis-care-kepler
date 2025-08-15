#!/usr/bin/env python3
"""
Practical Medicare/Medicaid enrichment using publicly available data sources.
This version provides a framework for enriching provider data with Medicare/Medicaid information.
"""

import pandas as pd
import os
from typing import Dict, Set
from tqdm import tqdm

# Configuration
INPUT_FILE = "data/processed/providers_geocoded_tmp.csv"
OUTPUT_FILE = "data/enriched/providers_enriched_medicare_medicaid.csv"

def create_medicare_medicaid_template():
    """Create a template file for manual Medicare/Medicaid data entry."""
    print("📋 Creating Medicare/Medicaid data template...")
    
    # Load provider data
    df = pd.read_csv(INPUT_FILE)
    
    # Create template with NPIs and states
    template = df[['npi', 'org_or_person_name', 'state']].copy()
    template['medicare_enrolled'] = False
    template['medicare_enrollment_date'] = ''
    template['medicare_specialty'] = ''
    template['ma_participating'] = False
    template['ma_plan_count'] = 0
    template['ma_plans'] = ''
    template['medicaid_enrolled'] = False
    template['medicaid_enrollment_date'] = ''
    template['medicaid_provider_type'] = ''
    template['medicaid_managed_care_participating'] = False
    
    # Save template
    template_file = "medicare_medicaid_template.csv"
    template.to_csv(template_file, index=False)
    print(f"   ✅ Created template: {template_file}")
    print(f"   📝 Instructions:")
    print(f"      1. Open {template_file} in Excel/Google Sheets")
    print(f"      2. Research each provider's Medicare/Medicaid status")
    print(f"      3. Update the boolean columns (True/False)")
    print(f"      4. Add enrollment dates and other details")
    print(f"      5. Save as 'medicare_medicaid_data.csv'")
    print(f"      6. Run this script again to merge the data")
    
    return template_file

def load_manual_medicare_medicaid_data() -> pd.DataFrame:
    """Load manually collected Medicare/Medicaid data."""
    data_file = "medicare_medicaid_data.csv"
    
    if not os.path.exists(data_file):
        print(f"⚠️  {data_file} not found. Creating template...")
        create_medicare_medicaid_template()
        return None
    
    print(f"📖 Loading manual Medicare/Medicaid data from {data_file}...")
    try:
        df = pd.read_csv(data_file)
        print(f"   Loaded {len(df):,} provider records")
        return df
    except Exception as e:
        print(f"   ❌ Error loading data: {e}")
        return None

def enrich_with_public_sources():
    """Enrich using publicly available Medicare/Medicaid data sources."""
    print("🔍 Enriching with public Medicare/Medicaid sources...")
    
    # Load provider data
    df = pd.read_csv(INPUT_FILE)
    print(f"   Loaded {len(df):,} providers")
    
    # Initialize Medicare/Medicaid columns
    medicare_cols = [
        'medicare_enrolled', 'medicare_enrollment_date', 'medicare_specialty',
        'ma_participating', 'ma_plan_count', 'ma_plans',
        'medicaid_enrolled', 'medicaid_enrollment_date', 'medicaid_provider_type',
        'medicaid_managed_care_participating'
    ]
    
    for col in medicare_cols:
        df[col] = None
    
    # Try to load any existing Medicare/Medicaid data files
    medicare_data_files = [
        "medicare_providers.csv",
        "medicare_enrollment.csv", 
        "ma_plans.csv",
        "medicaid_providers.csv"
    ]
    
    medicare_npis = set()
    ma_plan_counts = {}
    medicaid_by_state = {}
    
    for file in medicare_data_files:
        if os.path.exists(file):
            print(f"   📖 Found {file}, attempting to load...")
            try:
                temp_df = pd.read_csv(file, dtype=str)
                
                # Look for NPI column
                npi_col = None
                for col in temp_df.columns:
                    if 'npi' in col.lower():
                        npi_col = col
                        break
                
                if npi_col:
                    if 'medicare' in file.lower():
                        npis = set(temp_df[npi_col].dropna().astype(str))
                        medicare_npis.update(npis)
                        print(f"      Added {len(npis):,} Medicare NPIs")
                    elif 'ma' in file.lower() or 'plan' in file.lower():
                        plan_counts = temp_df[npi_col].value_counts().to_dict()
                        ma_plan_counts.update(plan_counts)
                        print(f"      Added {len(plan_counts):,} MA plan records")
                    elif 'medicaid' in file.lower():
                        # Look for state column
                        state_col = None
                        for col in temp_df.columns:
                            if 'state' in col.lower():
                                state_col = col
                                break
                        
                        if state_col:
                            for _, row in temp_df.iterrows():
                                npi = str(row[npi_col])
                                state = str(row[state_col]).upper()
                                if npi != 'nan' and state != 'NAN':
                                    if state not in medicaid_by_state:
                                        medicaid_by_state[state] = set()
                                    medicaid_by_state[state].add(npi)
                            print(f"      Added Medicaid data for {len(medicaid_by_state)} states")
                
            except Exception as e:
                print(f"      ❌ Error loading {file}: {e}")
    
    # Apply the data
    print("   🔍 Applying Medicare/Medicaid data...")
    medicare_count = 0
    ma_count = 0
    medicaid_count = 0
    
    for idx, row in tqdm(df.iterrows(), total=len(df), desc="Processing providers"):
        npi = str(row['npi'])
        state = str(row['state']).upper()
        
        # Check Medicare enrollment
        if npi in medicare_npis:
            df.at[idx, 'medicare_enrolled'] = True
            medicare_count += 1
        
        # Check Medicare Advantage participation
        if npi in ma_plan_counts:
            df.at[idx, 'ma_participating'] = True
            df.at[idx, 'ma_plan_count'] = ma_plan_counts[npi]
            ma_count += 1
        
        # Check Medicaid enrollment
        if state in medicaid_by_state and npi in medicaid_by_state[state]:
            df.at[idx, 'medicaid_enrolled'] = True
            medicaid_count += 1
    
    # Save enriched data
    print(f"💾 Saving enriched data to {OUTPUT_FILE}...")
    df.to_csv(OUTPUT_FILE, index=False)
    
    # Print summary
    print("\n📊 Enrichment Summary:")
    print(f"   Total providers: {len(df):,}")
    print(f"   Medicare enrolled: {medicare_count:,}")
    print(f"   MA participating: {ma_count:,}")
    print(f"   Medicaid enrolled: {medicaid_count:,}")
    print(f"   Both Medicare & Medicaid: {((df['medicare_enrolled'] == True) & (df['medicaid_enrolled'] == True)).sum():,}")
    
    # Show sample
    print("\n📋 Sample enriched data:")
    sample_cols = ['npi', 'org_or_person_name', 'state', 'medicare_enrolled', 'ma_participating', 'medicaid_enrolled']
    print(df[sample_cols].head(10).to_string(index=False))
    
    print(f"\n✅ Enrichment complete! Output: {OUTPUT_FILE}")
    
    # Provide next steps
    print("\n📋 Next Steps for Complete Medicare/Medicaid Data:")
    print("   1. Download Medicare Provider Enrollment data from:")
    print("      https://data.cms.gov/provider-data/dataset/medicare-provider-enrollment")
    print("   2. Download Medicare Advantage Plan-Net data from:")
    print("      https://data.cms.gov/provider-data/dataset/plan-net")
    print("   3. Download state Medicaid provider directories from:")
    print("      https://www.medicaid.gov/state-resource-center/medicaid-state-technical-assistance/state-medicaid-directories.html")
    print("   4. Place downloaded files in this directory and run this script again")
    print("   5. Or use the template approach: run create_medicare_medicaid_template()")

def main():
    """Main function."""
    print("🏥 Medicare/Medicaid Enrichment Tool")
    print("=" * 50)
    
    # Check if manual data exists
    manual_data = load_manual_medicare_medicaid_data()
    
    if manual_data is not None:
        print("✅ Found manual Medicare/Medicaid data!")
        # Merge manual data with geocoded data
        df_geocoded = pd.read_csv(INPUT_FILE)
        df_enriched = df_geocoded.merge(manual_data, on='npi', how='left', suffixes=('', '_medicare'))
        
        # Save merged data
        df_enriched.to_csv(OUTPUT_FILE, index=False)
        print(f"✅ Merged data saved to {OUTPUT_FILE}")
        
        # Print summary
        print("\n📊 Manual Data Summary:")
        print(f"   Total providers: {len(df_enriched):,}")
        print(f"   Medicare enrolled: {df_enriched['medicare_enrolled'].sum():,}")
        print(f"   MA participating: {df_enriched['ma_participating'].sum():,}")
        print(f"   Medicaid enrolled: {df_enriched['medicaid_enrolled'].sum():,}")
    else:
        print("📋 No manual data found. Using public sources...")
        enrich_with_public_sources()

if __name__ == "__main__":
    main()
