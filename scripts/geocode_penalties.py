# geocode_penalties.py
import os, time, csv, math, requests, pandas as pd
from pathlib import Path

INPUT = "kepler_penalties_with_details.csv"      # or the enriched CSV you export
OUTPUT = "kepler_penalties_geocoded.csv"
CACHE  = "geocode_cache.csv"                     # simple on-disk cache to resume
API_KEY = "AIzaSyAYBOxHtJp5iuXGDq_z88EZZrUh7_XSll0"       # Google Maps API key

# Build a full address if you also have City/State in the file later:
# df['FullAddress'] = df['Address'] + ', ' + df['City/Town'] + ', ' + df['State'] + ' ' + df['ZIP Code'].astype(str)

def load_cache(path):
    if not Path(path).exists(): return {}
    with open(path, newline="") as f:
        return {row["q"]: (float(row["lat"]), float(row["lng"])) for row in csv.DictReader(f)}

def save_cache(cache, path):
    with open(path, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["q","lat","lng"])
        w.writeheader()
        for q,(lat,lng) in cache.items():
            if not (isinstance(lat,float) and isinstance(lng,float) and not math.isnan(lat) and not math.isnan(lng)):
                continue
            w.writerow({"q":q,"lat":lat,"lng":lng})

def geocode(q):
    url = "https://maps.googleapis.com/maps/api/geocode/json"
    r = requests.get(url, params={"address": q, "key": API_KEY}, timeout=20)
    r.raise_for_status()
    j = r.json()
    if j.get("status") == "OK" and j["results"]:
        g = j["results"][0]["geometry"]["location"]
        return g["lat"], g["lng"]
    return None, None

def main():
    print("🚀 Starting geocoding process...")
    
    if not API_KEY:
        raise SystemExit("Missing GOOGLE_MAPS_API_KEY. Put it in a .env or export it before running.")
    
    print(f"📖 Loading data from {INPUT}...")
    df = pd.read_csv(INPUT, dtype={"ZIP Code":"string"})
    print(f"   Loaded {len(df)} records")
    
    # Best quality if you later enrich with City/State:
    df["FullAddress"] = df["Address"].str.strip() + ", " + df["ZIP Code"].fillna("").astype(str).str.strip()

    print(f"💾 Loading cache from {CACHE}...")
    cache = load_cache(CACHE)
    print(f"   Found {len(cache)} cached addresses")

    lats, lngs = [], []
    total = len(df)
    cached_count = 0
    geocoded_count = 0
    
    print(f"🌍 Processing {total} addresses...")
    for i, addr in enumerate(df["FullAddress"], 1):
        if addr in cache:
            lat,lng = cache[addr]
            cached_count += 1
            print(f"   [{i}/{total}] Cached: {addr[:50]}...")
        else:
            print(f"   [{i}/{total}] Geocoding: {addr[:50]}...")
            lat,lng = geocode(addr)
            cache[addr] = (lat if lat is not None else float("nan"),
                           lng if lng is not None else float("nan"))
            geocoded_count += 1
            time.sleep(0.1)  # gentle rate limit
        lats.append(lat); lngs.append(lng)

    df["Latitude"]  = lats
    df["Longitude"] = lngs

    print(f"💾 Saving results to {OUTPUT}...")
    # keep your original fields + lat/lon
    df.to_csv(OUTPUT, index=False)
    save_cache(cache, CACHE)
    
    print(f"✅ Done! → {OUTPUT}")
    print(f"   Total processed: {total}")
    print(f"   From cache: {cached_count}")
    print(f"   Newly geocoded: {geocoded_count}")

if __name__ == "__main__":
    main()
