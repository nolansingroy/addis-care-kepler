#!/bin/bash

# Addis Care Kepler - One-Command Startup Script
# This script clones the repository and runs the application automatically

echo "🏥 Addis Care: Medicaid Crisis Analysis"
echo "======================================"
echo "🚀 One-Command Setup & Launch"
echo "======================================"

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Error: Python 3 is not installed"
    echo "Please install Python 3.8 or higher and try again"
    exit 1
fi

# Check if git is installed
if ! command -v git &> /dev/null; then
    echo "❌ Error: Git is not installed"
    echo "Please install Git and try again"
    exit 1
fi

# Clone repository if it doesn't exist
if [ ! -d "addis-care-kepler" ]; then
    echo "📥 Cloning repository..."
    git clone https://github.com/nolansingroy/addis-care-kepler.git
    if [ $? -ne 0 ]; then
        echo "❌ Failed to clone repository"
        exit 1
    fi
fi

# Change to repository directory
cd addis-care-kepler

# Run the Python setup script
echo "🚀 Starting automated setup..."
python3 run.py

echo "✅ Setup complete!"
