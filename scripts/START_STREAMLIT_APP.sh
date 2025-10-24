#!/bin/bash

# APREU Advanced Segmentation - Streamlit App Launcher
# This script starts the Streamlit application

echo "================================================"
echo "APREU Advanced Segmentation - Streamlit POC"
echo "================================================"
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Error: Python 3 is not installed."
    echo "Please install Python 3.8 or higher."
    exit 1
fi

# Check Python version
PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
echo "✓ Python version: $PYTHON_VERSION"

# Check if streamlit is installed
if ! python3 -c "import streamlit" &> /dev/null; then
    echo ""
    echo "⚠️  Streamlit not found. Installing dependencies..."
    pip3 install -r requirements_streamlit.txt
fi

# Check if data file exists (optional now with upload feature)
if [ ! -f "data/raw/contacts_campus_Qro_.csv" ]; then
    echo ""
    echo "⚠️  Default data file not found at data/raw/contacts_campus_Qro_.csv"
    echo "You can still use the app by uploading your own CSV file."
    echo ""
else
    echo "✓ Data file found"
fi

echo ""
echo "🚀 Starting Streamlit application..."
echo "The app will open in your browser at http://localhost:8501"
echo ""
echo "Press Ctrl+C to stop the application"
echo "================================================"
echo ""

# Start Streamlit from project root
cd "$(dirname "$0")/.." && python3 -m streamlit run app/streamlit_app.py

