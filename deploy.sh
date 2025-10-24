#!/bin/bash

echo "🚀 Streamlit App Deployment Helper"
echo "=================================="
echo ""

# Check if git is initialized
if [ ! -d ".git" ]; then
    echo "📦 Initializing Git repository..."
    git init
    echo "✅ Git repository initialized"
    echo ""
fi

# Check if .streamlit config exists
if [ ! -f ".streamlit/config.toml" ]; then
    echo "⚙️  Creating Streamlit configuration..."
    mkdir -p .streamlit
    cat > .streamlit/config.toml << 'EOF'
[server]
port = 8501
headless = true
enableCORS = false
enableXsrfProtection = false

[browser]
gatherUsageStats = false

[theme]
primaryColor = "#1f77b4"
backgroundColor = "#ffffff"
secondaryBackgroundColor = "#f0f2f6"
textColor = "#262730"
EOF
    echo "✅ Streamlit configuration created"
    echo ""
fi

# Add all files to git
echo "📝 Adding files to Git..."
git add .
echo "✅ Files added to Git"
echo ""

# Commit changes
echo "💾 Committing changes..."
git commit -m "Streamlit app with offline analysis - ready for deployment"
echo "✅ Changes committed"
echo ""

echo "🎯 Next Steps:"
echo "=============="
echo ""
echo "Choose your deployment option:"
echo ""
echo "🔒 FOR PRIVATE REPOS (RECOMMENDED):"
echo "1. Create a PRIVATE GitHub repository:"
echo "   - Go to https://github.com/new"
echo "   - Name it something like 'streamlit-offline-analysis'"
echo "   - Make it PRIVATE ✅"
echo ""
echo "2. Connect your local repo to GitHub:"
echo "   git remote add origin https://github.com/YOURUSERNAME/YOURREPONAME.git"
echo "   git push -u origin main"
echo ""
echo "3. Deploy on Railway (best for private repos):"
echo "   - Go to https://railway.app"
echo "   - Click 'Start a New Project'"
echo "   - Connect your private GitHub repo"
echo "   - Railway auto-detects Streamlit"
echo "   - Click 'Deploy'"
echo ""
echo "4. Share with your team:"
echo "   - Get your private URL (like https://your-app-name.railway.app)"
echo "   - Send to teammates"
echo ""
echo "🌐 FOR PUBLIC REPOS:"
echo "1. Create a PUBLIC GitHub repository"
echo "2. Deploy on Streamlit Cloud:"
echo "   - Go to https://share.streamlit.io"
echo "   - Click 'New app'"
echo "   - Connect your GitHub repo"
echo "   - Main file: app/streamlit_app.py"
echo "   - Click 'Deploy'"
echo ""
echo "🎉 Your app will be live in minutes!"
echo ""
echo "📚 For detailed instructions:"
echo "   - Private repos: see PRIVATE_DEPLOYMENT_GUIDE.md"
echo "   - Public repos: see DEPLOYMENT_GUIDE.md"
