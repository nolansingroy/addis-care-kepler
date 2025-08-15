# 🚀 Addis Care Kepler - Automation Guide

## **Overview**

This guide explains the automated setup and deployment options for the Addis Care Medicaid Crisis Analysis project. The automation handles downloading the large dataset (~1.1GB), setting up dependencies, and launching the Streamlit application.

## **🔄 Automation Features**

### **What Gets Automated:**
- ✅ **Data Download**: Automatic download of 1.1GB dataset from Google Drive
- ✅ **File Extraction**: Automatic extraction and organization of data files
- ✅ **Dependency Installation**: Automatic installation of Python packages
- ✅ **Application Launch**: Automatic startup of Streamlit dashboard
- ✅ **Browser Opening**: Automatic browser launch to the application
- ✅ **Error Handling**: Graceful fallback to subset data if download fails
- ✅ **Progress Tracking**: Real-time progress indicators for downloads and extraction

### **Cross-Platform Support:**
- 🐧 **Linux/macOS**: Shell script (`start.sh`)
- 🪟 **Windows**: Batch file (`start.bat`)
- 🐍 **Python**: Cross-platform Python scripts (`run.py`, `setup.py`)

## **🎯 Quick Start Options**

### **1. One-Command Setup (Recommended)**

#### **For Unix/Linux/macOS:**
```bash
curl -sSL https://raw.githubusercontent.com/nolansingroy/addis-care-kepler/main/start.sh | bash
```

#### **For Windows:**
```cmd
# Download start.bat and run it, or:
git clone https://github.com/nolansingroy/addis-care-kepler.git
cd addis-care-kepler
python run.py
```

### **2. Manual Setup with Automation**
```bash
git clone https://github.com/nolansingroy/addis-care-kepler.git
cd addis-care-kepler
python3 setup.py
```

### **3. Quick Launch (If data exists)**
```bash
git clone https://github.com/nolansingroy/addis-care-kepler.git
cd addis-care-kepler
pip install -r requirements.txt
streamlit run streamlit_app.py
```

## **📁 Script Details**

### **`start.sh` (Unix/Linux/macOS)**
- **Purpose**: One-command setup for Unix-like systems
- **Features**:
  - Checks for Python and Git installation
  - Clones repository if not present
  - Runs the Python automation script
- **Usage**: `curl -sSL [url] | bash` or `./start.sh`

### **`start.bat` (Windows)**
- **Purpose**: One-command setup for Windows systems
- **Features**:
  - Checks for Python and Git installation
  - Clones repository if not present
  - Runs the Python automation script
- **Usage**: Download and double-click, or run from command prompt

### **`run.py` (Cross-platform)**
- **Purpose**: Quick setup and launch
- **Features**:
  - Downloads data if missing
  - Installs dependencies
  - Launches Streamlit with browser opening
- **Usage**: `python run.py`

### **`setup.py` (Cross-platform)**
- **Purpose**: Comprehensive setup with options
- **Features**:
  - Full progress tracking
  - Error handling and fallbacks
  - User prompts for data download
  - Detailed status reporting
- **Usage**: `python3 setup.py`

## **📊 Data Management**

### **Automatic Data Handling:**
1. **Check Existing Data**: Scripts check for existing data files
2. **Download if Missing**: Automatically download from Google Drive if needed
3. **Extract and Organize**: Place files in correct directories
4. **Fallback Options**: Use subset data if full download fails
5. **Cleanup**: Remove temporary zip files after extraction

### **Data Files Structure:**
```
data/
├── processed/
│   ├── providers_geocoded_subset.csv    # 10,326 providers (included)
│   └── providers_geocoded_tmp.csv       # 82,608 providers (downloaded)
└── enriched/
    ├── providers_medicare_medicaid_subset.csv  # Enriched subset (included)
    └── providers_medicare_medicaid_demo.csv    # Full enriched data (downloaded)
```

## **🔧 Technical Requirements**

### **Prerequisites:**
- **Python 3.8+**: Required for all automation scripts
- **Git**: Required for repository cloning
- **Internet Connection**: Required for data download (~1.1GB)

### **Dependencies (Auto-installed):**
- `streamlit>=1.28.0` - Web application framework
- `pandas>=2.0.0` - Data manipulation
- `plotly>=5.15.0` - Interactive visualizations
- `folium>=0.14.0` - Interactive maps
- `numpy>=1.24.0` - Numerical computing
- `requests>=2.25.0` - HTTP requests for downloads

## **🚨 Troubleshooting**

### **Common Issues:**

#### **Download Fails:**
- **Cause**: Network issues or Google Drive restrictions
- **Solution**: Scripts automatically fall back to subset data
- **Manual Fix**: Download manually from Google Drive link

#### **Python Not Found:**
- **Cause**: Python not installed or not in PATH
- **Solution**: Install Python 3.8+ and ensure it's in PATH
- **Check**: Run `python --version` or `python3 --version`

#### **Git Not Found:**
- **Cause**: Git not installed or not in PATH
- **Solution**: Install Git and ensure it's in PATH
- **Check**: Run `git --version`

#### **Dependencies Fail:**
- **Cause**: Network issues or package conflicts
- **Solution**: Scripts show detailed error messages
- **Manual Fix**: Run `pip install -r requirements.txt` manually

### **Error Messages:**
- `❌ Error: Python 3.8 or higher is required` → Install/update Python
- `❌ Error: Git is not installed` → Install Git
- `❌ Failed to download data` → Check internet connection
- `❌ Error installing dependencies` → Check pip and network

## **🎯 Best Practices**

### **For Users:**
1. **Use One-Command Setup**: Simplest option for most users
2. **Check Prerequisites**: Ensure Python and Git are installed
3. **Stable Internet**: Download requires ~1.1GB of data
4. **Patience**: Download may take 5-10 minutes depending on connection

### **For Developers:**
1. **Test Automation**: Run scripts on clean environments
2. **Handle Errors**: Scripts include comprehensive error handling
3. **Update URLs**: Keep Google Drive links current
4. **Cross-Platform**: Test on multiple operating systems

## **📞 Support**

### **Getting Help:**
- **Repository Issues**: [GitHub Issues](https://github.com/nolansingroy/addis-care-kepler/issues)
- **Documentation**: Check `/docs/` folder for detailed guides
- **Data Questions**: See `DATA_DICTIONARY.md` for schema details

### **Manual Override:**
If automation fails, you can always:
1. Clone repository manually: `git clone [url]`
2. Download data manually from Google Drive
3. Install dependencies: `pip install -r requirements.txt`
4. Run application: `streamlit run streamlit_app.py`

---

**Addis Care: Automated Solutions for the Medicaid Crisis** 🏥
