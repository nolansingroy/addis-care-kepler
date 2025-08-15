# **Addis Care: Medicaid Crisis Analysis**

## **🎯 Project Overview**

This repository contains comprehensive analysis of the Medicaid crisis impact on elder care providers, identifying high-risk areas and market opportunities for Addis Care's AI-driven solutions.

## **📊 Key Findings**

- **12 million people** at risk of losing Medicaid access
- **82,608 providers** across 10 states facing policy changes
- **1,861 high-risk ZIP codes** identified
- **$4.6B total market potential** for Addis Care solutions

## **📁 Repository Structure**

```
kelper/
├── README.md                           # This file - Project overview and key findings
├── requirements.txt                    # Python dependencies
├── app.py                             # Streamlit interactive dashboard
├── .gitignore                         # Git ignore rules
│
├── data/                              # Data files (not tracked in git)
│   ├── raw/                           # Original NPPES data sources
│   ├── processed/                     # Cleaned and geocoded provider data
│   └── enriched/                      # Enhanced data with additional features
│
├── scripts/                           # Analysis and processing scripts
│   ├── analysis/                      # Medicaid crisis analysis scripts
│   │   ├── addis_care_high_risk_analysis.py      # High-risk area identification
│   │   └── addis_care_real_data_analysis.py      # Real data market analysis
│   ├── providers_pipeline_google.py   # Provider data processing pipeline
│   ├── geocode_penalties.py           # Geocoding utilities
│   └── ...                           # Other processing scripts
│
├── analysis/                          # Analysis results and reports
│   └── medicaid_crisis/               # Medicaid crisis analysis documents
│       ├── ADDIS_CARE_MEDICAID_CRISIS_ANALYSIS.md    # Complete crisis analysis
│       └── ADDIS_CARE_HIGH_RISK_ANALYSIS.md          # Risk methodology
│
├── docs/                              # Documentation
│   ├── analysis/                      # Analysis documentation
│   │   ├── DATA_GUIDE_FOR_ADVISORS.md               # Guide for advisors
│   │   └── 12M_medicaid_loss_analysis.md            # 12M Medicaid loss impact
│   ├── ANALYSIS_GUIDE.md              # Step-by-step analysis instructions
│   ├── DATA_DICTIONARY.md             # Detailed data schema documentation
│   └── STREAMLIT_DEPLOYMENT.md        # Dashboard deployment guide
│
└── venv/                              # Virtual environment (not tracked)
```

## **🚨 Key Analysis Files**

### **Medicaid Crisis Analysis**
- `analysis/medicaid_crisis/ADDIS_CARE_MEDICAID_CRISIS_ANALYSIS.md` - Complete Medicaid crisis analysis
- `analysis/medicaid_crisis/ADDIS_CARE_HIGH_RISK_ANALYSIS.md` - High-risk area identification methodology
- `scripts/analysis/addis_care_high_risk_analysis.py` - High-risk area calculation script
- `scripts/analysis/addis_care_real_data_analysis.py` - Real data analysis script

### **Documentation**
- `docs/analysis/DATA_GUIDE_FOR_ADVISORS.md` - Data guide for advisors
- `docs/analysis/12M_medicaid_loss_analysis.md` - 12M Medicaid loss impact analysis

## **🏆 High-Risk Areas Identified**

### **CRITICAL RISK (374 ZIP codes)**
Top areas most vulnerable to Medicaid policy changes:

1. **ZIP 77036 (TX)**: 13 ALFs, 453 HCBS (466 total) - **CRITICAL RISK**
2. **ZIP 91411 (CA)**: 6 ALFs, 290 HCBS (296 total) - **CRITICAL RISK**
3. **ZIP 77407 (TX)**: 17 ALFs, 277 HCBS (294 total) - **CRITICAL RISK**
4. **ZIP 33186 (FL)**: 60 ALFs, 233 HCBS (293 total) - **CRITICAL RISK**
5. **ZIP 33330 (FL)**: 4 ALFs, 264 HCBS (268 total) - **CRITICAL RISK**

### **Risk Factors Identified**
- **HCBS-Dominant Areas** (>70% HCBS providers)
- **High Provider Density** (>100 total providers)
- **ALF-Heavy Areas** (>50% ALF providers)

## **📈 Revenue Projections**

### **Market Potential**
- **Total Market**: $4.6B annual revenue potential
- **Year 1**: $22.9M (0.5% adoption)
- **Year 2**: $91.5M (2.0% adoption)
- **Year 3**: $457.5M (10.0% adoption)

### **Pricing Model**
- **$125 per resident/client per month** for both ALF and HCBS
- **Same pricing model** for both provider types

## **💡 Addis Care Value Proposition**

**For Both ALF and HCBS Providers:**

1. **Staff Training & Retention**: AI-driven training for 82,608 facilities
2. **Documentation & Compliance**: Streamlined operations for all facilities
3. **Family Communication**: Real-time communication and coordination
4. **Care Quality Improvement**: AI-driven insights and personalized care plans

## **🚀 Quick Start**

### **Setup Environment**
```bash
# Clone the repository
git clone <repository-url>
cd kelper

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### **Run Analysis**
```bash
# Run high-risk area analysis
python scripts/analysis/addis_care_high_risk_analysis.py

# Run real data analysis
python scripts/analysis/addis_care_real_data_analysis.py
```

### **Launch Dashboard**
```bash
# Start Streamlit app
streamlit run app.py
```

## **📋 Data Sources**

- **NPPES Database**: Provider information and geographic data
- **Real Provider Data**: 82,608 providers across 10 states
- **Geographic Analysis**: ZIP code level provider distribution

## **⚠️ Important Disclaimers**

- **No real Medicare/Medicaid enrollment data** available in current dataset
- **Risk assessment based on provider characteristics** and industry knowledge
- **Revenue projections based on clearly stated assumptions**
- **Analysis focuses on geographic opportunities and market density**

## **🎯 Strategic Recommendations**

### **Phase 1 (0-3 months)**: Critical risk ZIP codes
### **Phase 2 (3-6 months)**: High risk areas + HCBS market entry
### **Phase 3 (6-12 months)**: Market leadership and industry standard

## **📊 Business Intelligence & Sample Questions**

### **Strategic Planning Questions**
- "Which states have the highest HCBS provider density?"
- "Are there geographic gaps in assisted living coverage?"
- "Which markets are underserved for home health services?"
- "What's the provider-to-population ratio by region?"

### **Medicaid Crisis Analysis**
- "Which areas have the highest Medicaid vulnerability?"
- "Are there Medicaid coverage gaps in specific regions?"
- "How many providers are in high-risk ZIP codes?"
- "Which states have the most critical risk areas?"

### **Competitive Intelligence**
- "Who are the major providers in each state?"
- "Which areas have the most provider competition?"
- "What's the market concentration by provider type?"
- "Are there opportunities for new market entry?"

### **Operational Analysis**
- "How far do patients travel to access providers?"
- "Which areas need more provider recruitment?"
- "What's the optimal provider network configuration?"
- "How does provider distribution affect access?"

## **🤖 Interactive Analysis**

### **Streamlit Dashboard Features**
- 📊 **Interactive Dashboard**: Key metrics, charts, and real-time data
- 🗺️ **Interactive Map**: All 82,608 providers with color-coded locations
- 🤖 **AI Agent**: Natural language queries about the data
- 📈 **Geographic Analysis**: Density heatmaps and ZIP code analysis
- 🔍 **Data Explorer**: Filter, search, and export provider data

### **AI Agent Capabilities**
Ask questions in plain English:
- "How many providers are in California?"
- "Which state has the most providers?"
- "Show me geographic density analysis"
- "What are the provider types?"
- "Show me high-risk areas for Medicaid policy changes"

## **📈 Key Insights Available**

### **Coverage Analysis**
- **Provider Density**: High vs low concentration areas
- **Geographic Gaps**: Underserved regions
- **State Comparisons**: Provider distribution patterns
- **Urban vs Rural**: Access disparities

### **Network Quality**
- **Provider Types**: HCBS vs ALF distribution
- **Specialty Mix**: Taxonomy code analysis
- **Organization vs Individual**: Entity type patterns
- **Geographic Spread**: Coverage breadth

### **Market Intelligence**
- **Competition Analysis**: Provider density by market
- **Expansion Opportunities**: Underserved areas
- **Network Adequacy**: Sufficient provider coverage
- **Risk Assessment**: Coverage gap identification


For questions about this analysis or Addis Care's solutions, please refer to the documentation in the `docs/` directory.

---

*This analysis is based on real provider data from NPPES database. Medicare/Medicaid enrollment status is not available in the current dataset.*
