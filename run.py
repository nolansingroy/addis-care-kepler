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

def install_dependencies():
    """Install Python dependencies with proper error handling"""
    print("📦 Installing Python dependencies...")
    
    try:
        # Check if requirements.txt exists
        if not os.path.exists("requirements.txt"):
            print("❌ requirements.txt not found")
            return False
        
        # Try to install with --user flag first
        try:
            result = subprocess.run(
                [sys.executable, "-m", "pip", "install", "--user", "-r", "requirements.txt"],
                capture_output=False,  # Show output
                text=True
            )
            if result.returncode == 0:
                print("✅ Dependencies installed successfully")
                return True
        except:
            pass
        
        # If that fails, try with --break-system-packages
        try:
            result = subprocess.run(
                [sys.executable, "-m", "pip", "install", "--break-system-packages", "-r", "requirements.txt"],
                capture_output=False,  # Show output
                text=True
            )
            if result.returncode == 0:
                print("✅ Dependencies installed successfully")
                return True
        except:
            pass
        
        # If both fail, suggest virtual environment
        print("❌ Could not install dependencies due to system restrictions")
        print("💡 Please create a virtual environment and try again:")
        print("   python3 -m venv venv")
        print("   source venv/bin/activate")
        print("   pip install -r requirements.txt")
        return False
            
    except Exception as e:
        print(f"❌ Error installing dependencies: {e}")
        return False

def check_streamlit():
    """Check if Streamlit is installed"""
    try:
        subprocess.run([sys.executable, "-c", "import streamlit"], 
                      check=True, capture_output=True)
        return True
    except:
        return False

def create_venv():
    """Create a virtual environment and install dependencies"""
    print("🐍 Creating virtual environment...")
    
    try:
        # Create virtual environment
        subprocess.run([sys.executable, "-m", "venv", "venv"], check=True)
        print("✅ Virtual environment created")
        
        # Determine the correct pip path
        if os.name == 'nt':  # Windows
            pip_path = "venv/Scripts/pip"
        else:  # Unix/Linux/macOS
            pip_path = "venv/bin/pip"
        
        # Install dependencies in virtual environment
        result = subprocess.run([pip_path, "install", "-r", "requirements.txt"], 
                              capture_output=False, text=True)
        
        if result.returncode == 0:
            print("✅ Dependencies installed in virtual environment")
            return True
        else:
            print("❌ Failed to install dependencies in virtual environment")
            return False
            
    except Exception as e:
        print(f"❌ Error creating virtual environment: {e}")
        return False

def get_venv_python():
    """Get the Python executable from virtual environment"""
    if os.name == 'nt':  # Windows
        return "venv/Scripts/python"
    else:  # Unix/Linux/macOS
        return "venv/bin/python"

def check_full_dataset():
    """Check if full dataset files exist"""
    full_dataset_files = [
        "data/processed/providers_geocoded_tmp.csv",
        "data/enriched/providers_medicare_medicaid_demo.csv"
    ]
    return all(os.path.exists(f) for f in full_dataset_files)

def check_subset_dataset():
    """Check if subset dataset files exist"""
    subset_dataset_files = [
        "data/processed/providers_geocoded_subset.csv",
        "data/enriched/providers_medicare_medicaid_subset.csv"
    ]
    return all(os.path.exists(f) for f in subset_dataset_files)

def download_full_dataset():
    """Download the full dataset from Google Drive"""
    print("📥 Downloading full dataset from Google Drive...")
    print("This will download ~1.1GB of data...")
    
    try:
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
        print("✅ Full dataset downloaded and extracted!")
        return True
    except Exception as e:
        print(f"❌ Download failed: {e}")
        return False

def main():
    """Quick start function"""
    print_banner()
    
    # Check if data exists
    if check_full_dataset():
        print("✅ Full dataset found - launching app...")
    elif check_subset_dataset():
        print("✅ Subset data found - launching app...")
    else:
        print("📥 No data found - downloading from Google Drive...")
        if not download_full_dataset():
            print("❌ Failed to download full dataset. Exiting.")
            sys.exit(1)
    
    # Check and install dependencies
    venv_created = False
    if not check_streamlit():
        print("📦 Streamlit not found - installing dependencies...")
        if not install_dependencies():
            print("🐍 Trying to create virtual environment...")
            if create_venv():
                venv_created = True
                print("✅ Using virtual environment")
            else:
                print("❌ Failed to install dependencies. Please run: pip install -r requirements.txt")
                sys.exit(1)
    else:
        print("✅ Dependencies already installed")
    
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
        # Use virtual environment Python if it was created
        python_exec = get_venv_python() if venv_created else sys.executable
        subprocess.run([python_exec, "-m", "streamlit", "run", "streamlit_app.py"])
    except KeyboardInterrupt:
        print("\n👋 Streamlit application stopped")
    except Exception as e:
        print(f"❌ Error running Streamlit: {e}")
        print("Please ensure Streamlit is installed: pip install streamlit")

if __name__ == "__main__":
    main()
