# **Addis Care: Medicaid Crisis Analysis**

## **🏥 Healthcare Provider Network Analysis & Medicaid Crisis Assessment**

This repository contains a comprehensive analysis of healthcare provider networks across 10 states, focusing on the Medicaid crisis and opportunities for Addis Care's AI-driven elder care solutions.

## **📊 Key Findings**

### **Market Opportunity**
- **82,608 total providers** across 10 states (MN, CA, OR, WA, TX, AZ, IL, MD, VA, FL)
- **66,013 HCBS providers** (Medicaid-oriented home health services)
- **16,595 ALF providers** (Assisted Living Facilities)
- **1,861 high-risk ZIP codes** identified for Addis Care deployment
- **$4.6B total market potential** for AI-driven elder care solutions

### **Medicaid Crisis Impact**
- **12 million people** at risk of losing Medicaid access
- **HCBS providers** heavily dependent on Medicaid funding
- **Geographic gaps** in provider coverage identified
- **Critical need** for alternative care solutions

## **🚀 Quick Start**

### **🎯 One-Command Setup (Recommended)**
```bash
# Option A: Using the shell script (Unix/Mac/Linux)
curl -sSL https://raw.githubusercontent.com/nolansingroy/addis-care-kepler/main/start.sh | bash

# Option B: Windows users - download and run start.bat
# Or manually:
git clone https://github.com/nolansingroy/addis-care-kepler.git
cd addis-care-kepler
python run.py
```
**What this does:**
- ✅ Downloads the full dataset (~1.1GB) from Google Drive
- ✅ Extracts and organizes all data files
- ✅ Installs Python dependencies
- ✅ Launches Streamlit application
- ✅ Opens your browser automatically
- ✅ Handles errors gracefully with fallback options

### **🔧 Full Automated Setup**
```bash
# Clone the repository
git clone https://github.com/nolansingroy/addis-care-kepler.git
cd addis-care-kepler

# Run comprehensive setup with options
python3 setup.py
```
**What this does:**
- ✅ Checks Python version compatibility
- ✅ Creates all necessary directories
- ✅ Downloads full dataset with progress tracking
- ✅ Extracts files with progress indicators
- ✅ Installs dependencies with error handling
- ✅ Launches Streamlit and opens browser
- ✅ Provides fallback to subset data if download fails

### **⚡ Quick Launch (If data already exists)**
```bash
# If you already have the data files
git clone https://github.com/nolansingroy/addis-care-kepler.git
cd addis-care-kepler
pip install -r requirements.txt
streamlit run streamlit_app.py
```

### **📥 Manual Data Download**
If you prefer to download manually:

1. **Download from Google Drive:**
   - [Large Data Files (1.1GB)](https://drive.google.com/file/d/1s7Pzx9wbf45ZxwiFFgU9m3xsL0W4Wpdh/view?usp=sharing)
   - Contains all processed and enriched data files

2. **Extract and Setup:**
   ```bash
   # Download the zip file
   wget "https://drive.google.com/uc?export=download&id=1s7Pzx9wbf45ZxwiFFgU9m3xsL0W4Wpdh" -O large_data_files.zip
   
   # Extract to data folder
   unzip large_data_files.zip -d data/
   
   # Run the application
   streamlit run streamlit_app.py
   ```

3. **Alternative Download Method:**
   ```bash
   # Using curl
   curl -L "https://drive.google.com/uc?export=download&id=1s7Pzx9wbf45ZxwiFFgU9m3xsL0W4Wpdh" -o large_data_files.zip
   
   # Extract and run
   unzip large_data_files.zip -d data/
   streamlit run streamlit_app.py
   ```

## **📁 Repository Structure**

```
kelper/
├── README.md                           # This file - Project overview and key findings
├── requirements.txt                    # Python dependencies
├── streamlit_app.py                   # Streamlit interactive dashboard
├── DATA_DOWNLOAD_GUIDE.md             # Detailed data download instructions
│
├── data/                              # Data files
│   ├── processed/                     # Cleaned and geocoded provider data
│   │   ├── providers_geocoded_subset.csv    # 10,326 providers (included)
│   │   └── providers_geocoded_tmp.csv       # 82,608 providers (download from Drive)
│   └── enriched/                      # Enhanced data with additional features
│       └── providers_medicare_medicaid_subset.csv  # Enriched subset (included)
│
├── scripts/                           # Analysis and processing scripts
│   ├── analysis/                      # Medicaid crisis analysis scripts
│   │   ├── addis_care_high_risk_analysis.py      # High-risk area identification
│   │   └── addis_care_real_data_analysis.py      # Real data market analysis
│   ├── providers_pipeline_google.py   # Provider data processing pipeline
│   └── geocode_penalties.py           # Geocoding utilities
│
├── analysis/                          # Analysis results and reports
│   └── medicaid_crisis/               # Medicaid crisis analysis documents
│       ├── ADDIS_CARE_MEDICAID_CRISIS_ANALYSIS.md    # Complete crisis analysis
│       └── ADDIS_CARE_HIGH_RISK_ANALYSIS.md          # Risk methodology
│
├── docs/                              # Documentation
│   ├── ANALYSIS_GUIDE.md              # Step-by-step analysis instructions
│   ├── DATA_DICTIONARY.md             # Detailed data schema documentation
│   └── STREAMLIT_DEPLOYMENT.md        # Dashboard deployment guide
│
└── venv/                              # Virtual environment (not tracked)
```

## **🌐 Streamlit Application**

### **Interactive Dashboard Features:**
- **📊 Dashboard Overview** - Key metrics and visualizations
- **🗺️ Interactive Map** - Provider locations and clustering
- **📈 Geographic Analysis** - Density and distribution patterns
- **🤖 AI Agent** - Natural language queries about the data
- **🔍 Data Explorer** - Filter and search functionality
- **🚨 Medicaid Crisis Analysis** - Risk assessment and opportunities

### **Deploy to Streamlit Cloud:**
1. Fork this repository
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Connect your GitHub repository
4. Set main file to `streamlit_app.py`
5. Deploy!

## **📈 Business Intelligence & Sample Questions**

### **Operational Analysis**
- "Which ZIP codes have the highest provider density?"
- "Are there geographic gaps in provider coverage?"
- "How many providers are in high-risk ZIP codes?"
- "Which states have the most critical risk areas?"

### **Strategic Planning**
- "Which states have the highest HCBS provider density?"
- "Are there geographic gaps in assisted living coverage?"
- "Which markets are underserved for home health services?"
- "What's the provider density by region?"

### **Competitive Intelligence**
- "Who are the major providers in each state?"
- "Which areas have the most provider competition?"
- "What's the market concentration by provider type?"
- "Are there opportunities for new market entry?"

### **Medicaid Crisis Analysis**
- "Which areas have the highest Medicaid vulnerability?"
- "Are there Medicaid coverage gaps in specific regions?"
- "How many providers are in high-risk ZIP codes?"
- "Which states have the most critical risk areas?"

## **🔍 Interactive Analysis**

### **Data Explorer Features:**
- **Geographic filtering** by state, city, ZIP code
- **Provider type filtering** (HCBS, ALF)
- **Search functionality** by provider name
- **Coordinate-based filtering** for map analysis

### **AI Agent Capabilities:**
- **Provider count queries** by region and type
- **Geographic distribution analysis**
- **Medicare/Medicaid enrollment insights**
- **Market opportunity identification**
- **Risk area assessment**

## **📊 Key Insights Available**

### **Provider Network Analysis:**
- **82,608 total providers** across 10 states
- **Geographic distribution** patterns
- **Provider type concentration** by region
- **Service area coverage** gaps

### **Medicaid Crisis Impact:**
- **HCBS provider vulnerability** (66,013 providers)
- **Geographic risk assessment** by ZIP code
- **Service gap identification** in underserved areas
- **Market opportunity mapping** for Addis Care

### **Competitive Intelligence:**
- **Market concentration** analysis
- **Provider density** by region
- **Competitive hotspot** identification
- **Market entry opportunity** assessment

## **🚀 Deployment Options**

### **Local Development (Automated):**
```bash
# One-command setup and run
git clone https://github.com/nolansingroy/addis-care-kepler.git
cd addis-care-kepler
python run.py
```

### **Local Development (Manual):**
```bash
# Clone and setup manually
git clone https://github.com/nolansingroy/addis-care-kepler.git
cd addis-care-kepler
pip install -r requirements.txt

# Download full dataset (optional)
wget "https://drive.google.com/uc?export=download&id=1s7Pzx9wbf45ZxwiFFgU9m3xsL0W4Wpdh" -O large_data_files.zip
unzip large_data_files.zip -d data/

# Run application
streamlit run streamlit_app.py
```

### **Streamlit Cloud:**
- **Automatic deployment** from GitHub
- **Public URL** for sharing
- **Real-time updates** on code changes
- **No server management** required

### **Docker Deployment:**
```bash
# Build and run with Docker
docker build -t addis-care-kepler .
docker run -p 8501:8501 addis-care-kepler
```

## **📋 Data Sources**

### **Primary Data:**
- **NPPES (National Provider Identifier)** - CMS provider database
- **Google Maps Geocoding API** - Address to coordinate conversion
- **Census Geocoding API** - Alternative geocoding service

### **Enriched Data:**
- **Medicare/Medicaid enrollment** (simulated for demonstration)
- **Provider type classification** (HCBS, ALF)
- **Geographic clustering** analysis
- **Risk assessment** scoring

## **🔧 Technical Requirements**

### **Python Dependencies:**
- `streamlit>=1.28.0` - Web application framework
- `pandas>=2.0.0` - Data manipulation
- `plotly>=5.15.0` - Interactive visualizations
- `folium>=0.14.0` - Interactive maps
- `numpy>=1.24.0` - Numerical computing

### **API Requirements:**
- **Google Maps API Key** (for geocoding)
- **Census API** (alternative geocoding)

## **📞 Support & Contact**

For questions about the analysis, data, or deployment:
- **Repository Issues**: [GitHub Issues](https://github.com/nolansingroy/addis-care-kepler/issues)
- **Documentation**: See `/docs/` folder for detailed guides
- **Data Questions**: Check `DATA_DICTIONARY.md` for schema details

---

**Addis Care: AI-Driven Solutions for the Medicaid Crisis** 🏥
