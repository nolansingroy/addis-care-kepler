"""
Merge COPD CSV (county-level) to US Counties GeoJSON by FIPS and
export a merged GeoJSON + an optional simplified version + centroid CSV.

Inputs:
  - counties GeoJSON: geojson-counties-fips.json (Plotly dataset)
  - COPD CSV: County_COPD_prevalence.csv  (must contain 'LocationID' and 'Percent_COPD')

Usage:
  python merge_copd_to_counties.py \
    --csv County_COPD_prevalence.csv \
    --geojson geojson-counties-fips.json \
    --out-geo merged_copd.geojson \
    --out-geo-simplified merged_copd_simplified.geojson \
    --out-centroids copd_county_centroids.csv \
    --simplify-tolerance 100
"""

import argparse
import pandas as pd
import geopandas as gpd
from shapely.geometry import Point
import json
import sys

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--csv", required=True, help="Path to COPD prevalence CSV")
    ap.add_argument("--geojson", required=True, help="Path to counties GeoJSON (Plotly fips)")
    ap.add_argument("--out-geo", default="merged_copd.geojson", help="Output merged GeoJSON")
    ap.add_argument("--out-geo-simplified", default="", help="(Optional) Output simplified GeoJSON")
    ap.add_argument("--out-centroids", default="copd_county_centroids.csv", help="Output county centroid CSV")
    ap.add_argument("--simplify-tolerance", type=float, default=100.0,
                    help="Simplify tolerance in meters (Web Mercator). Increase to shrink size more.")
    args = ap.parse_args()

    # --- Load COPD CSV ---
    # Expecting columns: LocationID (FIPS), Percent_COPD, StateDesc, County, etc.
    copd = pd.read_csv(args.csv, dtype={"LocationID": "string"})
    if "LocationID" not in copd.columns:
        sys.exit("CSV must include a 'LocationID' column (county FIPS).")

    # pad to 5-digit FIPS
    copd["FIPS"] = copd["LocationID"].str.zfill(5)

    # keep useful columns
    keep_map = {
        "FIPS": "FIPS",
        "Percent_COPD": "Percent_COPD",
        "StateDesc": "State",
        "County": "County",
        "95% Confidence Interval": "CI_95",
        "Quartile": "Quartile",
    }
    missing = [c for c in keep_map if c not in copd.columns]
    for m in missing:
        # make optional columns safe
        if m != "FIPS":
            copd[m] = pd.NA
    copd = copd[list(keep_map.keys())].rename(columns=keep_map)

    # ensure numeric
    copd["Percent_COPD"] = pd.to_numeric(copd["Percent_COPD"], errors="coerce")

    # --- Load GeoJSON (counties) ---
    gdf = gpd.read_file(args.geojson)

    # Plotly file usually has an 'id' with the 5-digit FIPS. If not, build it.
    if "id" in gdf.columns:
        gdf["FIPS"] = gdf["id"].astype(str).str.zfill(5)
    elif "GEO_ID" in gdf.columns:
        # last 5 chars of GEO_ID like '0500000US01001'
        gdf["FIPS"] = gdf["GEO_ID"].astype(str).str[-5:].str.zfill(5)
    else:
        # last resort: try properties->COUNTY + STATE combo (unlikely needed)
        raise SystemExit("Could not find FIPS in GeoJSON. Expected 'id' or 'GEO_ID'.")

    # --- Merge COPD attributes onto polygons ---
    merged = gdf.merge(copd, on="FIPS", how="left")

    # --- Export merged GeoJSON (full geometry) ---
    merged.to_file(args.out_geo, driver="GeoJSON")
    print(f"✓ Wrote merged polygons: {args.out_geo}  (rows: {len(merged)})")

    # --- Optional: simplify to shrink file size ---
    if args.out_geo_simplified:
        # Project to Web Mercator for meter-based tolerance, then simplify, then back to WGS84
        wm = merged.to_crs(3857)
        wm["geometry"] = wm.geometry.simplify(tolerance=args.simplify_tolerance, preserve_topology=True)
        simplified = wm.to_crs(4326)

        # Drop any empty geometries after simplify
        simplified = simplified[~simplified.geometry.is_empty]
        simplified.to_file(args.out_geo_simplified, driver="GeoJSON")
        print(f"✓ Wrote simplified polygons: {args.out_geo_simplified} "
              f"(tolerance={args.simplify_tolerance}m, rows: {len(simplified)})")

    # --- Also export county centroids as points (small, fast for Kepler) ---
    cent = merged.copy()
    # use representative_point to keep centroid within polygon
    cent["geometry"] = cent.representative_point()
    cent = cent.set_geometry("geometry")
    cent_points = pd.DataFrame({
        "FIPS": cent["FIPS"],
        "County": cent["County"],
        "State": cent["State"],
        "Percent_COPD": cent["Percent_COPD"],
        "CI_95": cent["CI_95"],
        "Quartile": cent["Quartile"],
        "Longitude": cent.geometry.x.round(6),
        "Latitude": cent.geometry.y.round(6),
    })
    cent_points.to_csv(args.out_centroids, index=False)
    print(f"✓ Wrote county centroids CSV: {args.out_centroids}  (rows: {len(cent_points)})")

if __name__ == "__main__":
    main()
