#!/usr/bin/env python3
"""
Enrich geocoded provider data with Medicare/Medicaid enrollment information.
Cross-references with CMS data sources to add enrollment status and network information.
"""

import pandas as pd
import requests
import os
import time
from typing import Dict, List, Optional
import json
from tqdm import tqdm

# Configuration
INPUT_FILE = "providers_geocoded_tmp.csv"
OUTPUT_FILE = "providers_enriched_medicare_medicaid.csv"
CACHE_FILE = "medicare_medicaid_cache.json"

# CMS Data Sources
CMS_PROVIDER_ENROLLMENT_API = "https://data.cms.gov/provider-data/api/1/datastore/query/medicare-provider-enrollment"
CMS_PLAN_NET_API = "https://data.cms.gov/provider-data/api/1/datastore/query/plan-net"
CMS_MEDICAID_PROVIDERS_API = "https://data.medicaid.gov/api/1/datastore/query/medicaid-providers"

def load_cache():
    """Load cached Medicare/Medicaid data."""
    if os.path.exists(CACHE_FILE):
        with open(CACHE_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_cache(cache):
    """Save Medicare/Medicaid data to cache."""
    with open(CACHE_FILE, 'w') as f:
        json.dump(cache, f, indent=2)

def query_cms_api(api_url: str, params: Dict) -> Optional[List[Dict]]:
    """Query CMS API with rate limiting."""
    try:
        response = requests.get(api_url, params=params, timeout=30)
        response.raise_for_status()
        data = response.json()
        return data.get('results', [])
    except Exception as e:
        print(f"API query failed: {e}")
        return None

def get_medicare_enrollment(npi: str, cache: Dict) -> Dict:
    """Get Medicare enrollment status for an NPI."""
    if npi in cache.get('medicare', {}):
        return cache['medicare'][npi]
    
    # Query CMS Provider Enrollment API
    params = {
        'filter': f'npi={npi}',
        'limit': 1
    }
    
    results = query_cms_api(CMS_PROVIDER_ENROLLMENT_API, params)
    
    enrollment_data = {
        'medicare_enrolled': False,
        'medicare_enrollment_date': None,
        'medicare_specialty': None,
        'medicare_practice_location': None
    }
    
    if results:
        provider = results[0]
        enrollment_data.update({
            'medicare_enrolled': True,
            'medicare_enrollment_date': provider.get('enrollment_date'),
            'medicare_specialty': provider.get('primary_specialty'),
            'medicare_practice_location': provider.get('practice_location')
        })
    
    # Cache the result
    if 'medicare' not in cache:
        cache['medicare'] = {}
    cache['medicare'][npi] = enrollment_data
    
    return enrollment_data

def get_medicare_advantage_plans(npi: str, cache: Dict) -> Dict:
    """Get Medicare Advantage plan participation for an NPI."""
    if npi in cache.get('ma_plans', {}):
        return cache['ma_plans'][npi]
    
    # Query CMS Plan-Net API
    params = {
        'filter': f'npi={npi}',
        'limit': 100
    }
    
    results = query_cms_api(CMS_PLAN_NET_API, params)
    
    ma_data = {
        'ma_participating': False,
        'ma_plans': [],
        'ma_plan_count': 0
    }
    
    if results:
        plans = []
        for plan in results:
            plan_info = {
                'plan_id': plan.get('plan_id'),
                'plan_name': plan.get('plan_name'),
                'plan_type': plan.get('plan_type'),
                'state': plan.get('state')
            }
            plans.append(plan_info)
        
        ma_data.update({
            'ma_participating': True,
            'ma_plans': plans,
            'ma_plan_count': len(plans)
        })
    
    # Cache the result
    if 'ma_plans' not in cache:
        cache['ma_plans'] = {}
    cache['ma_plans'][npi] = ma_data
    
    return ma_data

def get_medicaid_enrollment(npi: str, state: str, cache: Dict) -> Dict:
    """Get Medicaid enrollment status for an NPI in a specific state."""
    cache_key = f"{npi}_{state}"
    if cache_key in cache.get('medicaid', {}):
        return cache['medicaid'][cache_key]
    
    # Query Medicaid.gov API (state-specific)
    params = {
        'filter': f'npi={npi} AND state={state}',
        'limit': 1
    }
    
    results = query_cms_api(CMS_MEDICAID_PROVIDERS_API, params)
    
    medicaid_data = {
        'medicaid_enrolled': False,
        'medicaid_enrollment_date': None,
        'medicaid_provider_type': None,
        'medicaid_managed_care_participating': False
    }
    
    if results:
        provider = results[0]
        medicaid_data.update({
            'medicaid_enrolled': True,
            'medicaid_enrollment_date': provider.get('enrollment_date'),
            'medicaid_provider_type': provider.get('provider_type'),
            'medicaid_managed_care_participating': provider.get('managed_care_participating', False)
        })
    
    # Cache the result
    if 'medicaid' not in cache:
        cache['medicaid'] = {}
    cache['medicaid'][cache_key] = medicaid_data
    
    return medicaid_data

def enrich_providers(input_file: str, output_file: str):
    """Main function to enrich provider data with Medicare/Medicaid information."""
    print("🏥 Starting Medicare/Medicaid enrichment...")
    
    # Load existing data
    print(f"📖 Loading provider data from {input_file}...")
    df = pd.read_csv(input_file)
    print(f"   Loaded {len(df):,} providers")
    
    # Load cache
    cache = load_cache()
    print(f"   Loaded {len(cache.get('medicare', {})):,} cached Medicare records")
    print(f"   Loaded {len(cache.get('ma_plans', {})):,} cached MA plan records")
    print(f"   Loaded {len(cache.get('medicaid', {})):,} cached Medicaid records")
    
    # Initialize new columns
    new_columns = [
        'medicare_enrolled', 'medicare_enrollment_date', 'medicare_specialty',
        'ma_participating', 'ma_plan_count', 'ma_plans',
        'medicaid_enrolled', 'medicaid_enrollment_date', 'medicaid_provider_type',
        'medicaid_managed_care_participating'
    ]
    
    for col in new_columns:
        df[col] = None
    
    # Process each provider
    print("🔍 Enriching provider data...")
    for idx, row in tqdm(df.iterrows(), total=len(df), desc="Processing providers"):
        npi = str(row['npi'])
        state = row['state']
        
        # Get Medicare enrollment
        medicare_data = get_medicare_enrollment(npi, cache)
        df.at[idx, 'medicare_enrolled'] = medicare_data['medicare_enrolled']
        df.at[idx, 'medicare_enrollment_date'] = medicare_data['medicare_enrollment_date']
        df.at[idx, 'medicare_specialty'] = medicare_data['medicare_specialty']
        
        # Get Medicare Advantage plans
        ma_data = get_medicare_advantage_plans(npi, cache)
        df.at[idx, 'ma_participating'] = ma_data['ma_participating']
        df.at[idx, 'ma_plan_count'] = ma_data['ma_plan_count']
        df.at[idx, 'ma_plans'] = json.dumps(ma_data['ma_plans']) if ma_data['ma_plans'] else None
        
        # Get Medicaid enrollment
        medicaid_data = get_medicaid_enrollment(npi, state, cache)
        df.at[idx, 'medicaid_enrolled'] = medicaid_data['medicaid_enrolled']
        df.at[idx, 'medicaid_enrollment_date'] = medicaid_data['medicaid_enrollment_date']
        df.at[idx, 'medicaid_provider_type'] = medicaid_data['medicaid_provider_type']
        df.at[idx, 'medicaid_managed_care_participating'] = medicaid_data['medicaid_managed_care_participating']
        
        # Save cache periodically
        if (idx + 1) % 100 == 0:
            save_cache(cache)
            print(f"   Processed {idx + 1:,} providers, cache saved")
        
        # Rate limiting
        time.sleep(0.1)  # 10 requests per second
    
    # Save final cache
    save_cache(cache)
    
    # Save enriched data
    print(f"💾 Saving enriched data to {output_file}...")
    df.to_csv(output_file, index=False)
    
    # Print summary
    print("\n📊 Enrichment Summary:")
    print(f"   Total providers: {len(df):,}")
    print(f"   Medicare enrolled: {df['medicare_enrolled'].sum():,}")
    print(f"   MA participating: {df['ma_participating'].sum():,}")
    print(f"   Medicaid enrolled: {df['medicaid_enrolled'].sum():,}")
    print(f"   Both Medicare & Medicaid: {((df['medicare_enrolled'] == True) & (df['medicaid_enrolled'] == True)).sum():,}")
    
    print(f"\n✅ Enrichment complete! Output: {output_file}")

if __name__ == "__main__":
    enrich_providers(INPUT_FILE, OUTPUT_FILE)
