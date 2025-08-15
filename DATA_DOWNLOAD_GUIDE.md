# **Data Download Guide**

## **📁 Large Data Files**

Due to GitHub's file size limits, the following large NPPES data files are not included in this repository:

### **Missing Files:**
1. **`npidata_pfile_20050523-20250810.csv`** (10.4 GB) - Main NPPES provider data
2. **`endpoint_pfile_20050523-20250810.csv`** (114 MB) - Provider endpoint data  
3. **`pl_pfile_20050523-20250810.csv`** (97 MB) - Provider location data

## **🔗 Download Options**

### **Option 1: Official NPPES Data Source**
Download directly from CMS:
- **URL**: https://download.cms.gov/nppes/NPPES_Data_Dissemination_August_2025.zip
- **Size**: ~11 GB total
- **Format**: ZIP file containing all NPPES data

### **Option 2: Cloud Storage (Recommended)**
We recommend hosting these files on cloud storage:

#### **Google Drive**
- Upload files to Google Drive
- Share with "Anyone with link can view"
- Download using wget or curl

#### **AWS S3 / Google Cloud Storage**
- Upload to cloud storage bucket
- Generate public download URLs
- Include in documentation

#### **Dropbox / OneDrive**
- Upload to cloud storage
- Generate shareable links
- Document download instructions

## **📥 Download Instructions**

### **For Local Development:**
```bash
# Create data directory
mkdir -p data/raw/NPPES_Data_Dissemination_August_2025

# Download from cloud storage (replace URL with actual link)
wget -O data/raw/NPPES_Data_Dissemination_August_2025/npidata_pfile_20050523-20250810.csv "CLOUD_STORAGE_URL"
wget -O data/raw/NPPES_Data_Dissemination_August_2025/endpoint_pfile_20050523-20250810.csv "CLOUD_STORAGE_URL"
wget -O data/raw/NPPES_Data_Dissemination_August_2025/pl_pfile_20050523-20250810.csv "CLOUD_STORAGE_URL"
```

### **For Streamlit Cloud Deployment:**
The app will work with sample data if these files are not available.

## **🗂️ File Structure After Download**

```
data/
├── raw/
│   └── NPPES_Data_Dissemination_August_2025/
│       ├── npidata_pfile_20050523-20250810.csv          # Main provider data (10.4 GB)
│       ├── endpoint_pfile_20050523-20250810.csv         # Provider endpoints (114 MB)
│       ├── pl_pfile_20050523-20250810.csv               # Provider locations (97 MB)
│       ├── NPPES_Data_Dissemination_CodeValues.pdf      # Code documentation
│       └── NPPES_Data_Dissemination_Readme.pdf          # Data documentation
├── processed/
│   └── providers_geocoded_tmp.csv                       # Processed data (included)
└── enriched/
    └── providers_medicare_medicaid_demo.csv             # Enriched data (included)
```

## **⚡ Quick Start**

### **Option A: Use Processed Data (Recommended)**
The repository includes processed data files that are ready to use:
- `data/processed/providers_geocoded_tmp.csv` - 82,609 geocoded providers
- `data/enriched/providers_medicare_medicaid_demo.csv` - Enriched with demo data

### **Option B: Download Raw Data**
If you need to reprocess the raw data:
1. Download the large files from cloud storage
2. Place them in `data/raw/NPPES_Data_Dissemination_August_2025/`
3. Run the processing scripts

## **🔧 Processing Scripts**

Once you have the raw data, you can run:

```bash
# Process NPPES data
python scripts/providers_pipeline_google.py --nppes data/raw/NPPES_Data_Dissemination_August_2025/npidata_pfile_20050523-20250810.csv --states "MN,CA,OR,WA,TX,AZ,IL,MD,VA,FL" --step all --out data/processed/providers_geocoded_tmp.csv

# Create Medicare/Medicaid demo data
python scripts/create_medicare_medicaid_demo.py
```

## **📊 Data Summary**

### **Included Files:**
- ✅ **Processed data**: 82,609 geocoded providers
- ✅ **Enriched data**: Medicare/Medicaid demo data
- ✅ **Documentation**: Code values and readme files

### **Missing Files (Need Download):**
- ❌ **Raw NPPES data**: 10.4 GB main file
- ❌ **Endpoint data**: 114 MB provider endpoints
- ❌ **Location data**: 97 MB provider locations

## **🚀 Deployment Note**

For **Streamlit Cloud deployment**, the app will work with the included processed data files. The large raw files are only needed if you want to reprocess the data from scratch.

---

**The repository is ready for deployment with the included processed data files!**
