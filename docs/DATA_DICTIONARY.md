# Data Dictionary

## Healthcare Provider Dataset Schema

This document provides detailed descriptions of all columns in the healthcare provider dataset.

## Core Provider Information

### `npi` (National Provider Identifier)
- **Type**: String
- **Description**: Unique 10-digit identifier assigned to healthcare providers by CMS
- **Example**: "1023011079"
- **Source**: CMS NPPES

### `entity_type`
- **Type**: String
- **Description**: Type of healthcare entity
- **Values**: 
  - "1" = Individual provider
  - "2" = Organization
- **Example**: "2"

### `provider_type`
- **Type**: String
- **Description**: Classification of provider based on taxonomy codes
- **Values**:
  - "HCBS" = Home and Community-Based Services
  - "ALF" = Assisted Living Facilities
- **Example**: "HCBS"

### `provider_tags`
- **Type**: String
- **Description**: Additional provider classifications and tags
- **Example**: "Home Health, Personal Care"

### `org_or_person_name`
- **Type**: String
- **Description**: Legal business name for organizations or full name for individuals
- **Example**: "ADVANTAGE HOME HEALTH CARE, INC."

## Contact Information

### `phone`
- **Type**: String
- **Description**: Provider's phone number
- **Format**: (XXX) XXX-XXXX
- **Example**: "(555) 123-4567"

## Address Information

### `address`
- **Type**: String
- **Description**: Primary address line
- **Example**: "123 MAIN ST"

### `address2`
- **Type**: String
- **Description**: Secondary address line (suite, unit, etc.)
- **Example**: "SUITE 100"

### `city`
- **Type**: String
- **Description**: City name
- **Example**: "CHICAGO"

### `state`
- **Type**: String
- **Description**: Two-letter state abbreviation
- **Example**: "IL"

### `zip`
- **Type**: String
- **Description**: ZIP code
- **Format**: 5-digit or 9-digit
- **Example**: "60601"

### `address_full`
- **Type**: String
- **Description**: Complete formatted address for geocoding
- **Example**: "123 MAIN ST, CHICAGO, IL 60601"

## Geographic Coordinates

### `lat`
- **Type**: Float
- **Description**: Latitude coordinate (decimal degrees)
- **Range**: -90 to 90
- **Example**: 41.8781

### `lon`
- **Type**: Float
- **Description**: Longitude coordinate (decimal degrees)
- **Range**: -180 to 180
- **Example**: -87.6298

### `geocode_status`
- **Type**: String
- **Description**: Status of geocoding process
- **Values**:
  - "OK" = Successfully geocoded
  - "ZERO_RESULTS" = No results found
  - "OVER_QUERY_LIMIT" = API limit exceeded
  - "REQUEST_DENIED" = Request denied
  - "INVALID_REQUEST" = Invalid address
- **Example**: "OK"

### `place_id`
- **Type**: String
- **Description**: Google Maps place identifier
- **Format**: ChIJ... (unique identifier)
- **Example**: "ChIJ7cv00DwsDogRAMDACa2m4K8"

## Healthcare Classification

### `taxonomy_primary`
- **Type**: String
- **Description**: Primary healthcare provider taxonomy code
- **Format**: 10-character alphanumeric code
- **Examples**:
  - "251E00000X" = Home Health
  - "3747P1801X" = Personal Care
  - "310400000X" = Assisted Living
- **Source**: CMS NPPES

### `taxonomy_all`
- **Type**: String
- **Description**: All taxonomy codes associated with the provider
- **Format**: Comma-separated list
- **Example**: "251E00000X, 3747P1801X"

## Data Quality Notes

### Geocoding Accuracy
- **Success Rate**: 100% of providers successfully geocoded
- **Precision**: High-precision coordinates with place_id validation
- **Caching**: Results cached to avoid duplicate API calls

### Provider Classification
- **HCBS Providers**: Home health, personal care, community-based services
- **ALF Providers**: Assisted living facilities, residential care
- **Classification Method**: Based on taxonomy code analysis

### Data Completeness
- **Required Fields**: All providers have NPI, name, and address
- **Optional Fields**: Some providers may have missing phone or secondary address
- **Geographic Coverage**: 10 states with comprehensive provider coverage

## State Coverage

| State | Provider Count | Coverage Type |
|-------|---------------|---------------|
| CA | 14,088 | Home Health, Assisted Living |
| TX | 19,958 | Home Health, Assisted Living |
| FL | 21,977 | Home Health, Assisted Living |
| IL | 4,194 | Home Health, Assisted Living |
| MN | 5,432 | Home Health, Assisted Living |
| WA | 1,337 | Home Health, Assisted Living |
| OR | 1,141 | Home Health, Assisted Living |
| AZ | 4,046 | Home Health, Assisted Living |
| MD | 4,608 | Home Health, Assisted Living |
| VA | 5,827 | Home Health, Assisted Living |

## Usage Guidelines

### For Analysis
- Use `lat` and `lon` for geographic analysis
- Filter by `provider_type` for specific service types
- Group by `state` or `zip` for regional analysis
- Use `taxonomy_primary` for specialty analysis

### For Visualization
- Map points using `lat` and `lon` coordinates
- Color by `provider_type` for service type visualization
- Size by provider density for concentration analysis
- Filter by `state` for regional views

### For Business Intelligence
- Analyze provider density by geographic area
- Identify underserved regions
- Assess network adequacy
- Evaluate market competition
