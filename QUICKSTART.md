# Quick Start Guide

## Installation (2 minutes)

1. **Open Terminal** and navigate to this directory:
```bash
cd /Users/diegosalinas/Documents/SettingUp
```

2. **Install dependencies** (one-time setup):
```bash
pip3 install -r requirements_streamlit.txt
```

> **Note for macOS users**: Use `python3` and `pip3` commands instead of `python` and `pip`.

## Running the App (30 seconds)

**Option 1: Using the startup script**
```bash
./scripts/START_STREAMLIT_APP.sh
```

**Option 2: Direct command**
```bash
streamlit run app/streamlit_app.py
```

Your browser will automatically open to `http://localhost:8501`

## First Steps

### 1. Load Your Data

**Option A: Upload CSV**
- In the sidebar, select "⬆️ Upload CSV"
- Click the upload button
- Choose your HubSpot contact export CSV
- Wait for validation and processing

**Option B: Use Default File**
- Ensure `contacts_campus_Qro_.csv` is in `data/raw/` directory
- Select "📂 Use Default File" in sidebar
- Data loads automatically

### 2. Explore the Analysis Tabs

**📊 Overview**
- Executive summary of key metrics
- Segment distribution and performance

**🎯 Segment Analysis**
- Deep-dive into segment characteristics
- Cross-tabulations and comparisons

**🏷️ Platform/Geography/Activity Analysis**
- Cluster-specific detailed breakdowns
- Performance by category

**💰 Business Outcomes**
- Conversion metrics
- Close rates and revenue potential

**⚡ Fast/Slow Closers**
- Time-to-close analysis
- Identify patterns in conversion speed

**📅 Academic Period** (C1 & C3)
- Seasonal trends
- Enrollment cycle insights

**🔍 Contact Lookup**
- Individual contact deep-dive
- Journey visualizations

### 3. Try These Common Tasks

**Analyze social media performance:**
1. Select "Cluster 1" from the sidebar
2. Navigate to "🏷️ Platform Analysis" tab
3. View platform-specific metrics
4. Check "Fast/Slow Closers" for conversion patterns

**Explore geographic segments:**
1. Select "Cluster 2" from the sidebar
2. Configure your domestic region in sidebar settings
3. View "🗺️ Geography Analysis" tab
4. Analyze performance by state/country

**Track APREU activities:**
1. Select "Cluster 3" from the sidebar
2. Navigate to "🎪 Activity Analysis" tab
3. View entry channel performance
4. Check "📧 Email & Conversion" for engagement metrics

**Look up individual contacts:**
1. Select any cluster from sidebar
2. Navigate to "🔍 Contact Lookup" tab
3. Enter contact ID or email
4. View complete profile and journey visualization

## Stopping the App

Press `Ctrl+C` in the terminal where Streamlit is running.

## Tips

- **Filters persist** across page refreshes - use "All" to reset
- **Charts are interactive** - hover for details, zoom, pan
- **Tables support sorting** - click column headers
- **Downloads include metadata** - check the first sheet in Excel exports
- **Schema is flexible** - app adapts to your column names

## Sample Workflow

```
Load Data (Upload or Default)
    ↓
Select Cluster Strategy
    ↓
Explore Analysis Tabs
    ↓
Configure Filters (if needed)
    ↓
View Insights & Visualizations
    ↓
Look Up Individual Contacts
    ↓
Export or Take Action
```

## Troubleshooting

**App won't start:**
```bash
# Make sure you're in the right directory
pwd
# Should show: /Users/diegosalinas/Documents/SettingUp

# Try reinstalling dependencies
pip3 install -r requirements_streamlit.txt --upgrade

# Test the installation
python3 scripts/test_installation.py
```

**Data not loading:**
- Check CSV is not empty
- Verify it's a valid CSV (comma-separated)
- Ensure encoding is UTF-8
- For default file: ensure it's in `data/raw/` directory

**Logo not displaying:**
- Check that `app/assets/corchetes-blanco.webp` exists
- App will still work without it

**Import errors:**
- Make sure you're running from project root
- Use the full path: `streamlit run app/streamlit_app.py`

**Metrics show N/A or missing:**
- Check required columns exist in your CSV
- See `docs/technical/COLUMN_REFERENCE.md` for column name variations
- Use "ℹ️ About This Analysis" expanders for requirements

## Need Help?

- **📖 Full docs**: See `README.md`
- **🚀 Quick guides**: Check `docs/guides/` directory
- **🔧 Technical info**: See `docs/technical/` directory
- **💡 Feature docs**: Check `docs/features/` directory

## Key Documentation Files

- `docs/guides/FILE_UPLOAD_GUIDE.md` - CSV upload instructions
- `docs/guides/GEOGRAPHIC_CONFIG_GUIDE.md` - Configure regions
- `docs/features/ACADEMIC_PERIOD_FEATURE.md` - Seasonal analysis
- `docs/technical/COLUMN_REFERENCE.md` - Data requirements

---

**Ready to analyze? Run:** `./scripts/START_STREAMLIT_APP.sh` or `streamlit run app/streamlit_app.py`

