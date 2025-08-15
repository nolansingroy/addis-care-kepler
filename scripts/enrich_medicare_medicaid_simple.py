#!/usr/bin/env python3
"""
Simpler Medicare/Medicaid enrichment using downloadable CMS data files.
This version downloads and processes CMS provider enrollment files locally.
"""

import pandas as pd
import requests
import os
import zipfile
from typing import Dict, Set
import time
from tqdm import tqdm

# Configuration
INPUT_FILE = "providers_geocoded_tmp.csv"
OUTPUT_FILE = "providers_enriched_medicare_medicaid.csv"

# CMS Data Sources (downloadable files)
CMS_MEDICARE_PROVIDERS_URL = "https://data.cms.gov/provider-data/sites/default/files/resources/medicare-provider-enrollment.csv"
CMS_PLAN_NET_URL = "https://data.cms.gov/provider-data/sites/default/files/resources/plan-net.csv"
CMS_MEDICAID_PROVIDERS_URL = "https://data.medicaid.gov/sites/default/files/resources/medicaid-providers.csv"

def download_cms_data():
    """Download CMS data files if they don't exist."""
    files_to_download = [
        ("medicare_providers.csv", CMS_MEDICARE_PROVIDERS_URL),
        ("plan_net.csv", CMS_PLAN_NET_URL),
        ("medicaid_providers.csv", CMS_MEDICAID_PROVIDERS_URL)
    ]
    
    for filename, url in files_to_download:
        if not os.path.exists(filename):
            print(f"📥 Downloading {filename}...")
            try:
                response = requests.get(url, stream=True)
                response.raise_for_status()
                
                with open(filename, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        f.write(chunk)
                print(f"   ✅ Downloaded {filename}")
            except Exception as e:
                print(f"   ❌ Failed to download {filename}: {e}")
                print(f"   You may need to download manually from: {url}")
        else:
            print(f"   ✅ {filename} already exists")

def load_medicare_providers() -> Set[str]:
    """Load Medicare enrolled NPIs."""
    if not os.path.exists("medicare_providers.csv"):
        print("⚠️  Medicare providers file not found. Skipping Medicare enrichment.")
        return set()
    
    print("📖 Loading Medicare provider data...")
    try:
        # Try different column names that might exist
        df = pd.read_csv("medicare_providers.csv", dtype=str)
        
        # Look for NPI column
        npi_col = None
        for col in df.columns:
            if 'npi' in col.lower():
                npi_col = col
                break
        
        if npi_col:
            npis = set(df[npi_col].dropna().astype(str))
            print(f"   Loaded {len(npis):,} Medicare enrolled NPIs")
            return npis
        else:
            print("   ❌ No NPI column found in Medicare data")
            return set()
    except Exception as e:
        print(f"   ❌ Error loading Medicare data: {e}")
        return set()

def load_medicare_advantage_plans() -> Dict[str, int]:
    """Load Medicare Advantage plan participation counts."""
    if not os.path.exists("plan_net.csv"):
        print("⚠️  Plan-Net file not found. Skipping MA plan enrichment.")
        return {}
    
    print("📖 Loading Medicare Advantage plan data...")
    try:
        df = pd.read_csv("plan_net.csv", dtype=str)
        
        # Look for NPI column
        npi_col = None
        for col in df.columns:
            if 'npi' in col.lower():
                npi_col = col
                break
        
        if npi_col:
            # Count plans per NPI
            plan_counts = df[npi_col].value_counts().to_dict()
            print(f"   Loaded MA plan data for {len(plan_counts):,} NPIs")
            return plan_counts
        else:
            print("   ❌ No NPI column found in Plan-Net data")
            return {}
    except Exception as e:
        print(f"   ❌ Error loading Plan-Net data: {e}")
        return {}

def load_medicaid_providers() -> Dict[str, Set[str]]:
    """Load Medicaid enrolled NPIs by state."""
    if not os.path.exists("medicaid_providers.csv"):
        print("⚠️  Medicaid providers file not found. Skipping Medicaid enrichment.")
        return {}
    
    print("📖 Loading Medicaid provider data...")
    try:
        df = pd.read_csv("medicaid_providers.csv", dtype=str)
        
        # Look for NPI and state columns
        npi_col = None
        state_col = None
        
        for col in df.columns:
            if 'npi' in col.lower():
                npi_col = col
            elif 'state' in col.lower():
                state_col = col
        
        if npi_col and state_col:
            # Group NPIs by state
            medicaid_by_state = {}
            for _, row in df.iterrows():
                npi = str(row[npi_col])
                state = str(row[state_col]).upper()
                if npi != 'nan' and state != 'NAN':
                    if state not in medicaid_by_state:
                        medicaid_by_state[state] = set()
                    medicaid_by_state[state].add(npi)
            
            print(f"   Loaded Medicaid data for {len(medicaid_by_state)} states")
            return medicaid_by_state
        else:
            print("   ❌ NPI or state column not found in Medicaid data")
            return {}
    except Exception as e:
        print(f"   ❌ Error loading Medicaid data: {e}")
        return {}

def enrich_providers_simple():
    """Main function to enrich provider data with Medicare/Medicaid information."""
    print("🏥 Starting Medicare/Medicaid enrichment (simple version)...")
    
    # Download CMS data
    download_cms_data()
    
    # Load existing provider data
    print(f"📖 Loading provider data from {INPUT_FILE}...")
    df = pd.read_csv(INPUT_FILE)
    print(f"   Loaded {len(df):,} providers")
    
    # Load CMS data
    medicare_npis = load_medicare_providers()
    ma_plan_counts = load_medicare_advantage_plans()
    medicaid_by_state = load_medicaid_providers()
    
    # Initialize new columns
    df['medicare_enrolled'] = False
    df['ma_participating'] = False
    df['ma_plan_count'] = 0
    df['medicaid_enrolled'] = False
    
    # Enrich data
    print("🔍 Enriching provider data...")
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
    
    # Show sample of enriched data
    print("\n📋 Sample enriched data:")
    sample_cols = ['npi', 'org_or_person_name', 'state', 'medicare_enrolled', 'ma_participating', 'medicaid_enrolled']
    print(df[sample_cols].head(10).to_string(index=False))
    
    print(f"\n✅ Enrichment complete! Output: {OUTPUT_FILE}")

if __name__ == "__main__":
    enrich_providers_simple()
