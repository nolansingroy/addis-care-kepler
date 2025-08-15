#!/usr/bin/env python3
"""
Addis Care Kepler - Automated Setup Script
Downloads large dataset from Google Drive and runs Streamlit application
"""

import os
import sys
import subprocess
import zipfile
import requests
import time
from pathlib import Path
import webbrowser
import threading

# Configuration
GOOGLE_DRIVE_URL = "https://drive.google.com/uc?export=download&id=1s7Pzx9wbf45ZxwiFFgU9m3xsL0W4Wpdh"
ZIP_FILENAME = "large_data_files.zip"
DATA_DIR = "data"
REQUIREMENTS_FILE = "requirements.txt"

def print_banner():
    """Print setup banner"""
    print("=" * 70)
    print("🏥 Addis Care: Medicaid Crisis Analysis - Automated Setup")
    print("=" * 70)
    print("This script will automatically:")
    print("1. ✅ Check Python version and dependencies")
    print("2. 📁 Create necessary directories")
    print("3. 📥 Download the full dataset (~1.1GB) from Google Drive")
    print("4. 📦 Extract and organize data files")
    print("5. 🚀 Launch the Streamlit application")
    print("6. 🌐 Open your browser to the dashboard")
    print("=" * 70)

def check_python_version():
    """Check if Python version is compatible"""
    if sys.version_info < (3, 8):
        print("❌ Error: Python 3.8 or higher is required")
        print(f"Current version: {sys.version}")
        sys.exit(1)
    print(f"✅ Python version: {sys.version.split()[0]}")

def create_directories():
    """Create necessary directories"""
    directories = [
        "data/raw",
        "data/processed", 
        "data/enriched"
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        print(f"✅ Created directory: {directory}")

def download_file(url, filename):
    """Download file from Google Drive with progress bar"""
    print(f"📥 Downloading {filename} from Google Drive...")
    print("This may take 5-10 minutes depending on your internet connection...")
    
    try:
        response = requests.get(url, stream=True)
        response.raise_for_status()
        
        total_size = int(response.headers.get('content-length', 0))
        downloaded = 0
        start_time = time.time()
        
        with open(filename, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
                    downloaded += len(chunk)
                    if total_size > 0:
                        percent = (downloaded / total_size) * 100
                        elapsed = time.time() - start_time
                        if elapsed > 0:
                            speed = downloaded / (1024 * 1024 * elapsed)  # MB/s
                            eta = (total_size - downloaded) / (1024 * 1024 * speed) if speed > 0 else 0
                            print(f"\r📥 Download: {percent:.1f}% | Speed: {speed:.1f} MB/s | ETA: {eta:.0f}s", end='', flush=True)
        
        print(f"\n✅ Downloaded {filename} ({downloaded / 1024 / 1024:.1f} MB)")
        return True
        
    except Exception as e:
        print(f"\n❌ Error downloading file: {e}")
        return False

def extract_zip(zip_filename, extract_to):
    """Extract zip file with progress"""
    print(f"📦 Extracting {zip_filename}...")
    
    try:
        with zipfile.ZipFile(zip_filename, 'r') as zip_ref:
            file_list = zip_ref.namelist()
            total_files = len(file_list)
            
            for i, file in enumerate(file_list, 1):
                zip_ref.extract(file, extract_to)
                if i % 10 == 0 or i == total_files:  # Show progress every 10 files
                    print(f"\r📦 Extracting: {i}/{total_files} files", end='', flush=True)
        
        print(f"\n✅ Extracted {total_files} files to {extract_to}")
        return True
    except Exception as e:
        print(f"❌ Error extracting file: {e}")
        return False

def install_dependencies():
    """Install Python dependencies"""
    print("📦 Installing Python dependencies...")
    
    try:
        # Check if requirements.txt exists
        if not os.path.exists(REQUIREMENTS_FILE):
            print(f"❌ {REQUIREMENTS_FILE} not found")
            return False
            
        result = subprocess.run(
            [sys.executable, "-m", "pip", "install", "-r", REQUIREMENTS_FILE],
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            print("✅ Dependencies installed successfully")
            return True
        else:
            print(f"❌ Error installing dependencies: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Error installing dependencies: {e}")
        return False

def check_data_files():
    """Check if required data files exist"""
    required_files = [
        "data/processed/providers_geocoded_tmp.csv",
        "data/enriched/providers_medicare_medicaid_demo.csv"
    ]
    
    # Also check for subset files as fallback
    subset_files = [
        "data/processed/providers_geocoded_subset.csv",
        "data/enriched/providers_medicare_medicaid_subset.csv"
    ]
    
    missing_files = []
    for file_path in required_files:
        if not os.path.exists(file_path):
            missing_files.append(file_path)
    
    if missing_files:
        print("⚠️ Some data files are missing:")
        for file_path in missing_files:
            print(f"   - {file_path}")
        
        # Check if we have subset files
        subset_available = all(os.path.exists(f) for f in subset_files)
        if subset_available:
            print("✅ Subset data files are available as fallback")
            return "subset"
        return False
    
    print("✅ All required data files found")
    return "full"

def open_browser():
    """Open browser to Streamlit app after a delay"""
    time.sleep(3)  # Wait for Streamlit to start
    try:
        webbrowser.open("http://localhost:8501")
        print("🌐 Opened browser to http://localhost:8501")
    except:
        print("🌐 Please open your browser to http://localhost:8501")

def run_streamlit():
    """Run the Streamlit application"""
    print("🚀 Launching Streamlit application...")
    print("The app will open in your browser at http://localhost:8501")
    print("Press Ctrl+C to stop the application")
    print("-" * 70)
    
    # Start browser opening in background
    browser_thread = threading.Thread(target=open_browser)
    browser_thread.daemon = True
    browser_thread.start()
    
    try:
        subprocess.run([sys.executable, "-m", "streamlit", "run", "streamlit_app.py"])
    except KeyboardInterrupt:
        print("\n👋 Streamlit application stopped")
    except Exception as e:
        print(f"❌ Error running Streamlit: {e}")

def main():
    """Main setup function"""
    print_banner()
    
    # Step 1: Check Python version
    check_python_version()
    
    # Step 2: Create directories
    create_directories()
    
    # Step 3: Check if data already exists
    data_status = check_data_files()
    
    if data_status == "full":
        print("✅ Full dataset already exists, skipping download")
    elif data_status == "subset":
        print("📊 Subset data available - downloading full dataset for complete analysis...")
        choice = input("Download full dataset (~1.1GB)? (y/n): ")
        if choice.lower() != 'y':
            print("✅ Using subset data for analysis")
        else:
            # Download full dataset
            if not download_file(GOOGLE_DRIVE_URL, ZIP_FILENAME):
                print("❌ Failed to download data. Using subset data.")
            else:
                # Extract data
                if not extract_zip(ZIP_FILENAME, DATA_DIR):
                    print("❌ Failed to extract data. Using subset data.")
                else:
                    # Clean up zip file
                    try:
                        os.remove(ZIP_FILENAME)
                        print(f"✅ Cleaned up {ZIP_FILENAME}")
                    except:
                        pass
    else:
        # No data found - download required
        print("📥 No data found - downloading full dataset...")
        if not download_file(GOOGLE_DRIVE_URL, ZIP_FILENAME):
            print("❌ Failed to download data. Please check your internet connection.")
            print("You can manually download from: https://drive.google.com/file/d/1s7Pzx9wbf45ZxwiFFgU9m3xsL0W4Wpdh/view?usp=sharing")
            sys.exit(1)
        else:
            # Extract data
            if not extract_zip(ZIP_FILENAME, DATA_DIR):
                print("❌ Failed to extract data.")
                sys.exit(1)
            
            # Clean up zip file
            try:
                os.remove(ZIP_FILENAME)
                print(f"✅ Cleaned up {ZIP_FILENAME}")
            except:
                pass
    
    # Step 4: Install dependencies
    if not install_dependencies():
        print("❌ Failed to install dependencies.")
        sys.exit(1)
    
    # Step 5: Run Streamlit
    run_streamlit()

if __name__ == "__main__":
    main()
