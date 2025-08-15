#!/usr/bin/env python3
"""
Addis Care Kepler - Quick Start Script
One-liner to download data and run Streamlit app
"""

import os
import sys
import subprocess
import time
import webbrowser
import threading

def print_banner():
    """Print quick start banner"""
    print("🏥 Addis Care: Medicaid Crisis Analysis")
    print("=" * 50)
    print("🚀 Quick Start - One Command Setup")
    print("=" * 50)

def open_browser():
    """Open browser to Streamlit app after a delay"""
    time.sleep(3)  # Wait for Streamlit to start
    try:
        webbrowser.open("http://localhost:8501")
        print("🌐 Opened browser to http://localhost:8501")
    except:
        print("🌐 Please open your browser to http://localhost:8501")

def main():
    """Quick start function"""
    print_banner()
    
    # Check if data exists
    if os.path.exists("data/processed/providers_geocoded_tmp.csv"):
        print("✅ Full dataset found - launching app...")
    elif os.path.exists("data/processed/providers_geocoded_subset.csv"):
        print("✅ Subset data found - launching app...")
    else:
        print("📥 No data found - downloading from Google Drive...")
        print("This will download ~1.1GB of data...")
        
        # Download and extract
        try:
            print("📥 Downloading large dataset...")
            # Download
            subprocess.run([
                sys.executable, "-c", 
                "import requests; import zipfile; import os; "
                "print('Downloading from Google Drive...'); "
                "r=requests.get('https://drive.google.com/uc?export=download&id=1s7Pzx9wbf45ZxwiFFgU9m3xsL0W4Wpdh'); "
                "open('large_data_files.zip','wb').write(r.content); "
                "print('Extracting files...'); "
                "zipfile.ZipFile('large_data_files.zip').extractall('data'); "
                "os.remove('large_data_files.zip'); "
                "print('✅ Data ready!')"
            ], check=True)
            print("✅ Data downloaded and extracted!")
        except Exception as e:
            print(f"⚠️ Download failed: {e}")
            print("⚠️ Using subset data only (if available)")
    
    # Install dependencies if needed
    print("📦 Checking dependencies...")
    try:
        subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], 
                      check=True, capture_output=True)
        print("✅ Dependencies ready")
    except:
        print("⚠️ Some dependencies may be missing")
    
    # Start browser opening in background
    browser_thread = threading.Thread(target=open_browser)
    browser_thread.daemon = True
    browser_thread.start()
    
    # Run Streamlit
    print("🚀 Launching Streamlit app...")
    print("The app will open in your browser at http://localhost:8501")
    print("Press Ctrl+C to stop the application")
    print("-" * 50)
    
    try:
        subprocess.run([sys.executable, "-m", "streamlit", "run", "streamlit_app.py"])
    except KeyboardInterrupt:
        print("\n👋 Streamlit application stopped")

if __name__ == "__main__":
    main()
