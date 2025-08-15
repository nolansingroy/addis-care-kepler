# providers_pipeline_google.py
import os, re, time, csv, math, glob, argparse, json, random
import pandas as pd
import requests
from tqdm import tqdm
from dotenv import load_dotenv
from concurrent.futures import ThreadPoolExecutor, as_completed
from collections import deque
import threading

# ---------------- CONFIG ----------------
HCBS_TAX = {"253Z00000X","3747P1801X","376J00000X","251E00000X"}   # home-care / HCBS
ALF_TAX  = {"310400000X","3104A0625X","3104A0630X"}                 # assisted living
CHUNK = 100_000
GEOCODE_CACHE = "geocode_cache.csv"     # addr_key -> lat,lon,place_id,status
GEOIDS_CACHE  = "geoids_cache.csv"      # lat,lon -> county_geoid,tract_geoid
GOOGLE_URL = "https://maps.googleapis.com/maps/api/geocode/json"
CENSUS_COORDS_URL = "https://geocoding.geo.census.gov/geocoder/geographies/coordinates"
CENSUS_BATCH_URL = "https://geocoding.geo.census.gov/geocoder/geographies/addressbatch"
CACHE_FIELDS = ["qkey","query","lat","lon","status","place_id"]
# ---------------------------------------

def pick(df,*cands):
    for c in cands:
        if c in df.columns: return c
    return None

def zip5(z):
    z = str(z or "")
    m = re.match(r"(\d{5})", z)
    return m.group(1) if m else z

def normalize_address_key(s: str) -> str:
    # stable key for cache/dedupe: trim, collapse spaces, uppercase
    s = (s or "").strip()
    s = re.sub(r"\s+", " ", s)
    return s.upper()

class RateLimiter:
    def __init__(self, qps:int):
        self.qps = max(1, qps)
        self.buf = deque()
        self.lock = threading.Lock()
    def acquire(self):
        with self.lock:
            now = time.time()
            while self.buf and now - self.buf[0] > 1.0:
                self.buf.popleft()
            if len(self.buf) >= self.qps:
                sleep_for = 1.0 - (now - self.buf[0])
                if sleep_for > 0:
                    time.sleep(sleep_for)
                # purge again
                now = time.time()
                while self.buf and now - self.buf[0] > 1.0:
                    self.buf.popleft()
            self.buf.append(time.time())

def make_session():
    s = requests.Session()
    a = requests.adapters.HTTPAdapter(pool_connections=200, pool_maxsize=200)
    s.mount("https://", a)
    return s

def load_cache(path, keys):
    if not os.path.exists(path): return {}
    out = {}
    with open(path, newline="", encoding="utf-8") as f:
        r = csv.DictReader(f)
        for row in r:
            out[tuple(row[k] for k in keys)] = row
    return out

def save_cache_safe(path, dct):
    tmp = path + ".tmp"
    with open(tmp, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=CACHE_FIELDS)
        w.writeheader()
        for (qkey,), row in dct.items():
            w.writerow({
                "qkey": qkey,
                "query": row.get("query",""),
                "lat": row.get("lat",""),
                "lon": row.get("lon",""),
                "status": row.get("status",""),
                "place_id": row.get("place_id",""),
            })
    os.replace(tmp, path)

def save_cache(path, dct, fieldnames):
    tmp = path + ".tmp"
    with open(tmp, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        for _, row in dct.items():
            w.writerow(row)
    os.replace(tmp, path)

# ---------- STEP 1: FILTER NPPES ----------
def filter_nppes(nppes_csv, out_filtered_csv, states=None):
    print(f"🔍 Starting NPPES filtering...")
    print(f"   Input file: {nppes_csv}")
    print(f"   States filter: {states if states else 'ALL'}")
    
    # First, count total rows for progress tracking
    print(f"   Counting total rows...")
    total_file_rows = sum(1 for _ in pd.read_csv(nppes_csv, dtype=str, chunksize=CHUNK, low_memory=False))
    total_file_rows *= CHUNK  # Approximate total
    print(f"   Estimated total rows: {total_file_rows:,}")
    
    first = True
    kept = []
    chunk_count = 0
    total_rows = 0
    start_time = time.time()
    
    for chunk in pd.read_csv(nppes_csv, dtype=str, chunksize=CHUNK, low_memory=False):
        chunk_count += 1
        total_rows += len(chunk)
        
        # Calculate progress and ETA
        progress = (total_rows / total_file_rows) * 100
        elapsed = time.time() - start_time
        if progress > 0:
            eta_seconds = (elapsed / progress) * (100 - progress)
            eta_minutes = eta_seconds / 60
            eta_str = f"{eta_minutes:.1f} min" if eta_minutes < 60 else f"{eta_minutes/60:.1f} hours"
        else:
            eta_str = "calculating..."
        
        print(f"   Processing chunk {chunk_count} ({len(chunk):,} rows, total: {total_rows:,}) - {progress:.1f}% complete, ETA: {eta_str}")
        if first:
            TAX = [c for c in chunk.columns if "Healthcare Provider Taxonomy Code_" in c]
            SW  = [c for c in chunk.columns if "Healthcare Provider Primary Taxonomy Switch_" in c]
            ENT = pick(chunk,"Entity Type Code","Entity Type")
            ORG = pick(chunk,"Provider Organization Name (Legal Business Name)","Organization Name")
            LAST= pick(chunk,"Provider Last Name (Legal Name)","Last Name")
            FIRST=pick(chunk,"Provider First Name","First Name")
            ADD1= pick(chunk,"Provider First Line Business Practice Location Address","Practice Address Line 1")
            ADD2= pick(chunk,"Provider Second Line Business Practice Location Address","Practice Address Line 2")
            CITY= pick(chunk,"Provider Business Practice Location Address City Name","Practice City")
            STATE=pick(chunk,"Provider Business Practice Location Address State Name","Practice State")
            ZIP = pick(chunk,"Provider Business Practice Location Address Postal Code","Practice Postal Code")
            PHONE=pick(chunk,"Provider Business Practice Location Address Telephone Number","Practice Phone")
            NPI = "NPI"
            
            # Debug: print found columns
            print(f"   Found columns:")
            print(f"     TAX: {len(TAX)} taxonomy columns")
            print(f"     SW: {len(SW)} switch columns")
            print(f"     ENT: {ENT}")
            print(f"     ORG: {ORG}")
            print(f"     ADD1: {ADD1}")
            print(f"     ADD2: {ADD2}")
            print(f"     CITY: {CITY}")
            print(f"     STATE: {STATE}")
            print(f"     ZIP: {ZIP}")
            print(f"     PHONE: {PHONE}")
            print(f"     NPI: {NPI}")
            
            first = False

        # optional state filter
        if states:
            chunk[STATE] = chunk[STATE].str.upper().str.strip()
            before_filter = len(chunk)
            chunk = chunk[chunk[STATE].isin(states)]
            after_filter = len(chunk)
            if chunk.empty: 
                print(f"     → No matching states in chunk {chunk_count}")
                continue
            print(f"     → State filter: {before_filter:,} → {after_filter:,} rows")

        # taxonomy filter (HCBS or ALF anywhere)
        hit_hcbs = pd.Series(False, index=chunk.index)
        hit_alf  = pd.Series(False,  index=chunk.index)
        for c in TAX:
            vals = chunk[c].fillna("")
            hit_hcbs |= vals.isin(HCBS_TAX)
            hit_alf  |= vals.isin(ALF_TAX)
        hit_any = hit_hcbs | hit_alf
        before_tax = len(chunk)
        chunk = chunk[hit_any]
        after_tax = len(chunk)
        if chunk.empty: 
            print(f"     → No matching taxonomies in chunk {chunk_count}")
            continue
        print(f"     → Taxonomy filter: {before_tax:,} → {after_tax:,} rows (HCBS: {hit_hcbs.sum():,}, ALF: {hit_alf.sum():,})")

        # choose primary among matched (prefer primary switch=Y)
        def choose_primary(row):
            best=None
            for i,tcol in enumerate(TAX):
                code=str(row.get(tcol,"") or "")
                if code in HCBS_TAX or code in ALF_TAX:
                    sw = str(row.get(SW[i], "") if i < len(SW) else "")
                    if sw=="Y": return code
                    best = best or code
            return best

        def provider_type(code):
            if code in ALF_TAX:  return "ALF"
            if code in HCBS_TAX: return "HCBS"
            return "HCBS"

        chunk["taxonomy_primary"] = chunk.apply(choose_primary, axis=1)
        chunk = chunk[chunk["taxonomy_primary"].notna()]

        # tag dual matches
        chunk["provider_tags"] = [
            ";".join([t for t,cond in [("HCBS", h),("ALF", a)] if cond])
            for h,a in zip(hit_hcbs.loc[chunk.index], hit_alf.loc[chunk.index])
        ]
        chunk["provider_type"] = chunk["taxonomy_primary"].apply(provider_type)

        # collect all taxonomies
        TAX_ALL = chunk[[c for c in TAX]].copy()
        chunk["taxonomy_all"] = TAX_ALL.apply(
            lambda s: ";".join(sorted(set(x for x in s if isinstance(x,str) and x.strip()))), axis=1)

        def name_of(r):
            if str(r.get(ENT,"2"))=="2" and ORG:
                return str(r.get(ORG) or "").strip()
            first = str(r.get(FIRST) or "")
            last = str(r.get(LAST) or "")
            return (" ".join([first, last])).strip()

        out = pd.DataFrame({
            "npi": chunk[NPI].astype(str),
            "entity_type": chunk[ENT].astype(str),
            "provider_type": chunk["provider_type"],
            "provider_tags": chunk["provider_tags"],
            "org_or_person_name": chunk.apply(name_of, axis=1),
            "address": chunk[ADD1].fillna("").astype(str).str.strip(),
            "address2": chunk[ADD2].fillna("").astype(str).str.strip(),
            "city": chunk[CITY].fillna("").astype(str).str.title().str.strip(),
            "state": chunk[STATE].astype(str),
            "zip": chunk[ZIP].apply(zip5),
            "phone": chunk[PHONE].fillna("").astype(str),
            "taxonomy_primary": chunk["taxonomy_primary"],
            "taxonomy_all": chunk["taxonomy_all"]
        })

        # de-dupe by NPI+address
        out["address_full"] = out.apply(
            lambda r: (r["address"] + (" " + r["address2"] if r["address2"] else "") +
                       f", {r['city']}, {r['state']} {r['zip']}").strip(), axis=1)
        out = out.drop_duplicates(subset=["npi","address_full"]).drop(columns=["address_full"])
        kept.append(out)
        print(f"     → Chunk {chunk_count} complete: {len(out):,} providers kept")

    filtered = pd.concat(kept, ignore_index=True) if kept else pd.DataFrame(columns=[
        "npi","entity_type","provider_type","provider_tags","org_or_person_name",
        "address","address2","city","state","zip","phone","taxonomy_primary","taxonomy_all"
    ])
    filtered.to_csv(out_filtered_csv, index=False)
    print(f"✅ [filter] Complete! Wrote {out_filtered_csv}")
    print(f"   Total rows processed: {total_rows:,}")
    print(f"   Providers found: {len(filtered):,}")
    print(f"   Breakdown by type:")
    if len(filtered) > 0:
        print(f"     HCBS: {len(filtered[filtered['provider_type'] == 'HCBS']):,}")
        print(f"     ALF:  {len(filtered[filtered['provider_type'] == 'ALF']):,}")
        print(f"     Dual: {len(filtered[filtered['provider_tags'].str.contains(';')]):,}")

# ---------- STEP 2: GEOCODE (Google) ----------
def geocode_google_one(session, addr_full, qkey, key):
    # Rate limit outside in the caller
    params = {"address": addr_full, "key": key, "components": "country:US"}
    backoff = 0.25
    for _ in range(5):
        r = session.get(GOOGLE_URL, params=params, timeout=20)
        if r.status_code == 429:
            time.sleep(backoff); backoff *= 2; continue
        r.raise_for_status()
        j = r.json()
        st = j.get("status","")
        if st == "OK" and j.get("results"):
            res = j["results"][0]
            loc = res["geometry"]["location"]
            return qkey, addr_full, str(loc["lat"]), str(loc["lng"]), "OK", res.get("place_id","")
        # Accept other terminal states (ZERO_RESULTS, etc.)
        return qkey, addr_full, "", "", st, ""
    return qkey, addr_full, "", "", "OVER_QUERY_LIMIT", ""

def geocode_file_google(df, out_csv, google_key, cache, save_every=2000, qps=10, workers=10):
    # Map addr_key -> first matching full address to send to Google
    first_full = df.drop_duplicates("addr_key")[["addr_key","address_full"]].set_index("addr_key")["address_full"].to_dict()

    todo = [(k, first_full[k]) for k in df["addr_key"].unique() if (k,) not in cache]
    print(f"Unique addresses: {len(first_full):,}; to geocode: {len(todo):,}; cached: {len(cache):,}")

    session = make_session()
    limiter = RateLimiter(qps)
    done = 0

    def task(k, query):
        limiter.acquire()
        return geocode_google_one(session, query, k, google_key)

    results = []
    if todo:
        with ThreadPoolExecutor(max_workers=workers) as ex:
            futs = [ex.submit(task, k, q) for (k,q) in todo]
            for fut in as_completed(futs):
                qkey, query, lat, lon, status, pid = fut.result()
                cache[(qkey,)] = {"qkey": qkey, "query": query, "lat": lat, "lon": lon,
                                  "status": status, "place_id": pid}
                done += 1
                if done % save_every == 0:
                    save_cache_safe(GEOCODE_CACHE, cache)
                if done % 1000 == 0:
                    print(f"  Geocoded {done:,}/{len(todo):,}")
        save_cache_safe(GEOCODE_CACHE, cache)

    # Rehydrate onto df from cache
    def pick_row(k):
        r = cache.get((k,), {})
        return pd.Series([r.get("lat",""), r.get("lon",""), r.get("status",""), r.get("place_id","")])

    df[["lat","lon","geocode_status","place_id"]] = df["addr_key"].apply(pick_row)
    df = df[(df["lat"]!="") & (df["lon"]!="")]
    df.drop(columns=["addr_key"], inplace=True)
    df.to_csv(out_csv, index=False)
    print(f"✅ [geocode/google] wrote {out_csv} rows={len(df):,}")

# ---------- STEP 2B: GEOCODE (Census Batch) ----------
def census_batch_file(df_chunk, path):
    tmp = df_chunk.copy()
    tmp.insert(0, "id", range(1, len(tmp)+1))
    street = (tmp["address"].astype(str) + " " + tmp["address2"].astype(str)).str.strip()
    out = pd.DataFrame({
        "id": tmp["id"],
        "street": street,
        "city": tmp["city"],
        "state": tmp["state"],
        "zip": tmp["zip"].str[:5]
    })
    out.to_csv(path, index=False, header=False)

def call_census_batch(file_path):
    with open(file_path, "rb") as f:
        files = {"addressFile": f}
        data = {"benchmark":"Public_AR_Current","vintage":"Current_Current"}
        r = requests.post(CENSUS_BATCH_URL, files=files, data=data, timeout=300)
    r.raise_for_status()
    return r.text  # CSV string

def parse_census_batch(csv_text):
    # Columns: id, street, city, state, zip, match, matchtype, matched_addr, lon, lat, ... + JSON of geographies
    rows = []
    for row in csv.reader(csv_text.splitlines()):
        if len(row) < 9: continue
        (rid, *_rest) = row
        lat = row[8]; lon = row[7]  # Census returns lon,lat at 7,8
        # The last column has geogs JSON; parse GEOIDs if present
        county_geoid = tract_geoid = ""
        if len(row) > 9 and row[-1]:
            try:
                j = json.loads(row[-1])
                geos = j.get("geographies", {})
                if "Counties" in geos and geos["Counties"]:
                    county_geoid = geos["Counties"][0].get("GEOID","")
                if "Census Tracts" in geos and geos["Census Tracts"]:
                    tract_geoid = geos["Census Tracts"][0].get("GEOID","")
            except Exception:
                pass
        rows.append((int(rid), lat, lon, county_geoid, tract_geoid))
    return pd.DataFrame(rows, columns=["id","lat","lon","county_geoid","tract_geoid"])

def geocode_file_census_batch(df, out_csv, cache, save_every=2000, batch_size=10000):
    df = df.reset_index(drop=True)
    df["addr_key"] = df["address_full"].map(normalize_address_key)
    # NOTE: you can still use the cache keyed by addr_key if you want
    parts = []
    for start in range(0, len(df), batch_size):
        sub = df.iloc[start:start+batch_size].copy()
        tmp_path = f"_census_batch_{start}.csv"
        census_batch_file(sub, tmp_path)
        txt = call_census_batch(tmp_path)
        os.remove(tmp_path)
        res = parse_census_batch(txt)
        sub = sub.reset_index(drop=True)
        res = res.set_index("id")
        sub = sub.join(res, on=None)  # id matches order in file
        parts.append(sub)
    out = pd.concat(parts, ignore_index=True)
    out.to_csv(out_csv, index=False)
    print(f"✅ [geocode/census] wrote {out_csv} rows={len(out):,}")

def geocode_file(in_csv, out_csv, google_key, cache_path=GEOCODE_CACHE, throttle=0.08, max_retries=4, 
                engine="google", qps=10, workers=10, save_every=2000, batch_size=10000):
    print(f"🌍 Starting {engine} geocoding...")
    print(f"   Input file: {in_csv}")
    print(f"   Cache file: {cache_path}")
    
    df = pd.read_csv(in_csv, dtype=str).fillna("")
    print(f"   Loaded {len(df):,} providers to geocode")
    
    df["address_full"] = (df["address"] + (" " + df["address2"]).where(df["address2"]!="", "") +
                          ", " + df["city"] + ", " + df["state"] + " " + df["zip"]).str.strip()
    
    df["addr_key"] = df["address_full"].map(normalize_address_key)
    
    # Try to load cache with new format first, fall back to old format
    try:
        cache = load_cache(cache_path, ["qkey"])
        print(f"   Loaded {len(cache):,} cached addresses (new format)")
    except KeyError:
        # Old format cache - convert to new format
        print(f"   Converting old cache format...")
        old_cache = load_cache(cache_path, ["q"])
        cache = {}
        for k, v in old_cache.items():
            addr = k[0]  # old key was (address,)
            addr_key = normalize_address_key(addr)
            cache[(addr_key,)] = {
                "qkey": addr_key,
                "query": addr,
                "lat": str(v.get("lat", "")),
                "lon": str(v.get("lon") or v.get("lng") or ""),
                "status": v.get("status", "CACHED"),
                "place_id": v.get("place_id", "")
            }
        print(f"   Converted {len(cache):,} cached addresses")
    
    # normalise cache row values
    for k,v in list(cache.items()):
        # ensure lat/lon are strings in cache
        cache[k]["lat"] = str(cache[k]["lat"])
        cache[k]["lon"] = str(cache[k].get("lon") or cache[k].get("lng") or "")
        cache[k]["status"] = cache[k].get("status","CACHED")
        cache[k]["place_id"] = cache[k].get("place_id","")
        # Remove any 'lng' key to avoid conflicts
        if "lng" in cache[k]:
            del cache[k]["lng"]
    
    if engine == "google":
        if not google_key:
            raise SystemExit("Missing GOOGLE_MAPS_API_KEY env var")
        print(f"   QPS: {qps}, Workers: {workers}")
        geocode_file_google(df, out_csv, google_key, cache, save_every, qps, workers)
    else:
        print(f"   Batch size: {batch_size}")
        geocode_file_census_batch(df, out_csv, cache, save_every, batch_size)

# ---------- STEP 3: GEOIDs from Census (coords->geographies) ----------
def coords_to_geoids(lat, lon):
    params = {
        "x": lon, "y": lat,
        "benchmark": "Public_AR_Current",
        "vintage": "Current_Current",
        "format": "json"
    }
    r = requests.get(CENSUS_COORDS_URL, params=params, timeout=20)
    j = r.json()
    county_geoid = tract_geoid = ""
    try:
        geos = j["result"]["geographies"]
        if "Counties" in geos and geos["Counties"]:
            county_geoid = geos["Counties"][0]["GEOID"]
        if "Census Tracts" in geos and geos["Census Tracts"]:
            tract_geoid = geos["Census Tracts"][0]["GEOID"]
        elif "Census Blocks" in geos and geos["Census Blocks"]:
            tract_geoid = geos["Census Blocks"][0]["TRACT"]
    except Exception:
        pass
    return county_geoid, tract_geoid

def add_geoids(in_csv, out_csv, cache_path=GEOIDS_CACHE):
    print(f"🏛️ Starting GEOID tagging...")
    print(f"   Input file: {in_csv}")
    print(f"   Cache file: {cache_path}")
    
    df = pd.read_csv(in_csv, dtype=str)
    df["lat"] = pd.to_numeric(df["lat"], errors="coerce")
    df["lon"] = pd.to_numeric(df["lon"], errors="coerce")
    df = df.dropna(subset=["lat","lon"])
    print(f"   Loaded {len(df):,} geocoded providers")

    cache = load_cache(cache_path, ["lat","lon"])
    print(f"   Loaded {len(cache):,} cached coordinate lookups")
    
    county_ids, tract_ids = [], []
    start_time = time.time()
    for i, (la, lo) in enumerate(tqdm(zip(df["lat"], df["lon"]), total=len(df), desc="Tagging GEOIDs")):
        if i % 1000 == 0 and i > 0:
            progress = (i / len(df)) * 100
            elapsed = time.time() - start_time
            if progress > 0:
                eta_seconds = (elapsed / progress) * (100 - progress)
                eta_minutes = eta_seconds / 60
                eta_str = f"{eta_minutes:.1f} min" if eta_minutes < 60 else f"{eta_minutes/60:.1f} hours"
            else:
                eta_str = "calculating..."
            print(f"     Progress: {i:,}/{len(df):,} ({progress:.1f}%) - ETA: {eta_str}")
        key = (f"{la:.6f}", f"{lo:.6f}")
        if key in cache:
            county_geoid = cache[key]["county_geoid"]
            tract_geoid  = cache[key]["tract_geoid"]
        else:
            county_geoid, tract_geoid = coords_to_geoids(la, lo)
            cache[key] = {"lat": key[0], "lon": key[1],
                          "county_geoid": county_geoid, "tract_geoid": tract_geoid}
            if len(cache) % 200 == 0:
                save_cache(cache_path, cache, ["lat","lon","county_geoid","tract_geoid"])
            time.sleep(0.05)
        county_ids.append(county_geoid)
        tract_ids.append(tract_geoid)

    df["county_geoid"] = county_ids
    df["tract_geoid"] = tract_ids
    df.to_csv(out_csv, index=False)
    save_cache(cache_path, cache, ["lat","lon","county_geoid","tract_geoid"])
    print(f"[geoids] wrote {out_csv} rows={len(df)}")

# ---------- STEP 4: EXPORT (final column order) ----------
def export_final(in_csv, out_csv):
    df = pd.read_csv(in_csv, dtype=str).fillna("")
    cols = [
        "npi","entity_type","provider_type","provider_tags",
        "org_or_person_name","address","address2","city","state","zip","phone",
        "taxonomy_primary","taxonomy_all",
        "lat","lon","county_geoid","tract_geoid"
    ]
    # keep any missing columns gracefully
    cols = [c for c in cols if c in df.columns]
    df[cols].to_csv(out_csv, index=False)
    print(f"[export] wrote {out_csv} rows={len(df)}")

# ---------- CLI ----------
def main():
    load_dotenv()
    ap = argparse.ArgumentParser(description="NPPES → (HCBS+ALF) → Google/Census Geocode → GEOIDs → Kepler CSV")
    ap.add_argument("--nppes", required=True, help="Path to NPPES monthly CSV (unzipped)")
    ap.add_argument("--states", default="IL,WA,MN,CA,FL,AZ,NY,TX",
                    help='Comma list of 2-letter states or "ALL"')
    ap.add_argument("--step", choices=["filter","geocode","geoids","export","all"], required=True)
    ap.add_argument("--in", dest="in_csv", help="Input CSV for geocode/geoids/export steps")
    ap.add_argument("--out-filtered", default="providers_filtered.csv")
    ap.add_argument("--out-geocoded", default="providers_geocoded_tmp.csv")
    ap.add_argument("--out-geoids", default="providers_with_geoids_tmp.csv")
    ap.add_argument("--out", default="providers_8states_geocoded.csv")
    ap.add_argument("--throttle", type=float, default=0.08, help="Seconds between Google calls")
    ap.add_argument("--retries", type=int, default=4, help="Max retries for Google OVER_QUERY_LIMIT")
    
    # New geocoding options
    ap.add_argument("--engine", choices=["google","census"], default="google", help="Geocoding engine")
    ap.add_argument("--qps", type=int, default=10, help="Queries per second for Google API")
    ap.add_argument("--workers", type=int, default=10, help="Number of worker threads")
    ap.add_argument("--save-every", type=int, default=2000, help="Save cache every N geocodes")
    ap.add_argument("--batch-size", type=int, default=10000, help="Census batch file size")
    
    args = ap.parse_args()

    states = None if args.states.upper()=="ALL" else {s.strip().upper() for s in args.states.split(",") if s.strip()}

    if args.step in ("filter","all"):
        filter_nppes(args.nppes, args.out_filtered, states=states)

    if args.step in ("geocode","all"):
        google_key = os.getenv("GOOGLE_MAPS_API_KEY")
        in_csv = args.in_csv or args.out_filtered
        geocode_file(in_csv, args.out_geocoded, google_key, 
                    throttle=args.throttle, max_retries=args.retries,
                    engine=args.engine, qps=args.qps, workers=args.workers,
                    save_every=args.save_every, batch_size=args.batch_size)

    if args.step in ("geoids","all"):
        in_csv = args.in_csv or args.out_geocoded
        add_geoids(in_csv, args.out_geoids)

    if args.step in ("export","all"):
        in_csv = args.in_csv or args.out_geoids
        export_final(in_csv, args.out)

if __name__ == "__main__":
    main()
