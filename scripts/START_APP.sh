#!/bin/bash
# Quick start script for HubSpot Segmentation Explorer

echo "🚀 Starting HubSpot Segmentation Explorer..."
echo ""

cd "$(dirname "$0")"

# Check if streamlit is installed
if ! command -v streamlit &> /dev/null
then
    echo "❌ Streamlit not found. Installing dependencies..."
    pip3 install -r requirements.txt
    echo ""
fi

echo "📊 Launching app..."
echo "   Your browser will open automatically."
echo "   Press Ctrl+C to stop the app."
echo ""

streamlit run app/app.py

