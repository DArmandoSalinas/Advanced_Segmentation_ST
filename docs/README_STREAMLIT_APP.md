# APREU Advanced Segmentation - Streamlit POC

## Overview

This Streamlit application showcases three complementary segmentation strategies for APREU contacts, providing interactive analytics and insights for targeted marketing campaigns.

## 🎯 Three Segmentation Strategies

### Cluster 1: Socially Engaged Prospects
- **Goal**: Identify prospects with social media activity using historical data analysis
- **Segments**: 1A (High Engagement) and 1B (Low Engagement) with platform overlay tags
- **Key Features**: 
  - Multi-platform detection (12+ platforms)
  - Historical data parsing
  - Platform-specific targeting
  - Time-to-close analysis
  - Source journey visualization
  - Academic period analysis (seasonal trends)

### Cluster 2: Geography & Engagement Segmentation
- **Goal**: Segment by geography (Local/Domestic/International) and engagement level
- **Segments**: 2A-2F (6 segments: geography × engagement)
- **Key Features**:
  - Geographic classification (Local QRO, Domestic non-QRO, International)
  - State-level performance analysis
  - Engagement scoring per geo tier
  - Regional campaign insights

### Cluster 3: APREU Activities & Entry Channels
- **Goal**: Segment by promotional activities and entry channels
- **Segments**: 3A-3D (Digital/Event/Messaging/Niche)
- **Key Features**:
  - APREU activity tracking
  - Preparatoria cross-analysis
  - Conversion event analysis
  - Email engagement metrics
  - Activity journey visualization
  - Academic period analysis (seasonal trends)

## 📋 Prerequisites

- Python 3.8 or higher
- Contact data file: `contacts_campus_Qro_.csv` (optional - can upload your own!)

## 🚀 Installation

1. **Install dependencies:**
   ```bash
   pip install -r requirements_streamlit.txt
   ```

2. **Data Options:**
   
   **Option A: Use Default File**
   - Ensure `contacts_campus_Qro_.csv` is in the project directory
   - The file should contain HubSpot contact export data
   
   **Option B: Upload Your Own Data** (NEW! ⭐)
   - No file needed - upload CSV directly in the app
   - Export contacts from HubSpot as CSV
   - Upload through the app interface
   - See `FILE_UPLOAD_GUIDE.md` for details

## ▶️ Running the Application

### Option 1: Command Line
```bash
streamlit run streamlit_app.py
```

### Option 2: Using the startup script (Mac/Linux)
```bash
./START_STREAMLIT_APP.sh
```

### Option 3: Windows
```cmd
python -m streamlit run streamlit_app.py
```

The application will automatically open in your default web browser at `http://localhost:8501`

## 📊 Using the Application

### ⬆️ File Upload Feature (NEW!)

The app now supports uploading your own CSV files!

**How to use:**
1. In the sidebar, select "⬆️ Upload CSV"
2. Click the upload button
3. Choose your HubSpot contact export CSV
4. The app validates your data automatically
5. View data preview and any warnings
6. Start analyzing!

**Benefits:**
- ✅ No need to replace files manually
- ✅ Works with any HubSpot export
- ✅ Instant validation feedback
- ✅ Data preview before analysis
- ✅ More reproducible and shareable

**See `FILE_UPLOAD_GUIDE.md` for complete documentation**

### 🌎 Geographic Configuration (NEW!)

**Customize the app for YOUR region!**

Previously hardcoded for Mexico/Querétaro, now works for **any country and region**.

**Configure:**
1. Open sidebar → "🌎 Geographic Settings"
2. Enter your home country (e.g., "United States", "Brazil", "Spain")
3. Add country aliases (e.g., "USA, US, United States")
4. Enter your local region (e.g., "California", "São Paulo", "Madrid")
5. Add region aliases (e.g., "CA, San Francisco, SF")
6. Click "Apply Settings"

**Result:** Cluster 2 analysis adapts to YOUR geography:
- 🏠 **Local**: Your specific city/state/region
- 🇺🇸 **Domestic**: Your country (but not local)
- 🌍 **International**: Outside your country

**Examples:**
- US University: Analyze California vs other states vs international
- Brazilian Company: Analyze São Paulo vs other regions vs LATAM
- Spanish Business: Analyze Madrid vs other communities vs EU

**See `GEOGRAPHIC_CONFIG_GUIDE.md` for detailed instructions and examples**

### Navigation
- Use the **sidebar** to switch between Overview and the three cluster analyses
- Each cluster has multiple tabs for different types of analysis:
  - Overview
  - Segment Analysis
  - Detailed Breakdowns
  - **Contact Lookup** with visual journey timelines (Cluster 1 & 3) 🆕

### 🗺️ Journey Visualizations (NEW!)

**Visual timelines showing contact journeys!**

**Cluster 1 - Source Journey:**
- See how contacts arrived through different traffic sources
- Visual flow: Original Source → Touch 1 → Touch 2 → etc.
- Track multi-touch attribution

**Cluster 3 - APREU Journey:**
- Two-row timeline: Activities + Conversions
- See which events led to conversions
- Understand journey progression

**How to use:**
1. Go to Contact Lookup tab (Cluster 1 or 3)
2. Enter any Contact ID
3. Scroll to journey visualization
4. See the complete visual timeline!

**See `JOURNEY_VISUALIZATIONS.md` for detailed documentation**
  - Contact Lookup

### Key Features

#### 1. Interactive Filters
- Select specific segments to analyze
- Filter by date ranges, engagement levels, or geography

#### 2. Visual Analytics
- Interactive charts and graphs using Plotly
- Hover over data points for detailed information
- Zoom, pan, and export visualizations

#### 3. Contact Lookup
- Search for individual contacts by ID
- View complete profile with all metrics
- See segment assignment and recommendations

#### 4. Performance Metrics
- Close rates by segment
- Time-to-close analysis
- Engagement score distributions
- Platform/geography/activity performance

### Tips for Best Experience
- Start with the **Overview** tab to understand each cluster
- Use **full-screen mode** for better visualization (click expand icon on charts)
- **Hover over metrics** to see detailed tooltips
- Use the **contact lookup** feature to validate segment assignments

## 📁 File Structure

```
SettingUp/
├── streamlit_app.py           # Main application entry point
├── utils.py                    # Shared utility functions
├── cluster1_analysis.py        # Cluster 1: Social Engagement
├── cluster2_analysis.py        # Cluster 2: Geography & Engagement  
├── cluster3_analysis.py        # Cluster 3: APREU Activities
├── requirements_streamlit.txt  # Python dependencies
├── contacts_campus_Qro_.csv    # Contact data (required)
└── README_STREAMLIT_APP.md     # This file
```

## 🔧 Troubleshooting

### Application won't start
- **Check Python version**: `python --version` (should be 3.8+)
- **Reinstall dependencies**: `pip install -r requirements_streamlit.txt --force-reinstall`
- **Check file paths**: Ensure `contacts_campus_Qro_.csv` exists

### Data not loading
- Verify the CSV file name matches exactly: `contacts_campus_Qro_.csv`
- Check file is not empty: `wc -l contacts_campus_Qro_.csv`
- Ensure CSV is properly formatted (UTF-8 encoding)

### Slow performance
- The first load caches data for faster subsequent access
- Large datasets may take 30-60 seconds to process initially
- Consider filtering data if working with >100K contacts

### Port already in use
If port 8501 is busy:
```bash
streamlit run streamlit_app.py --server.port 8502
```

## 💡 Key Insights per Cluster

### Cluster 1 Insights
- **1A segments** show higher close rates (typically 5-10% higher than 1B)
- **Platform tags** enable targeted retargeting campaigns
- **Google_Ads** and **Organic_Social** often have highest volume
- Fast-track 1A contacts for immediate follow-up

### Cluster 2 Insights
- **Local (2E/2F)** contacts typically close faster than international
- **Domestic (2A/2B)** segments benefit from state-specific campaigns
- **International (2C/2D)** require different nurture approaches
- State-level performance varies significantly

### Cluster 3 Insights
- **Event-first (3B)** contacts convert best with 48h follow-up
- **Digital-first (3A)** largest volume but requires longer nurture
- **Messaging-first (3C)** expects fast, personalized response
- **Preparatoria partnerships** impact varies by school and activity

## 📈 Export and Reporting

While the Streamlit app focuses on interactive exploration, you can still generate the full Excel reports using the original Jupyter notebooks:

- `Cluster1.ipynb` → `segments_cluster1_overlay_summary.xlsx` (25+ worksheets)
- `Cluster2.ipynb` → `cluster2_summary.xlsx` (27+ worksheets)
- `Cluster3.ipynb` → `segments_cluster3_summary.xlsx` (32+ worksheets)

## 🆘 Support

For questions or issues:
1. Review this README thoroughly
2. Check the original notebook documentation
3. Verify data quality and file formats
4. Contact the development team with specific error messages

## 🎓 Learning Resources

To understand the underlying analysis:
- Review `COMPLETE_SUMMARY.md` for overall strategy
- Read individual `README_Cluster*.md` files for detailed methodology
- Check `COLUMN_REFERENCE.md` for data field definitions
- See `IMPLEMENTATION_STATUS.md` for technical details

## 📝 Notes

- This is a **Proof of Concept** for demonstration purposes
- Performance may vary with different data sizes
- Cache is cleared when the app restarts
- Filters apply to visualizations but not cached data processing

---

**Version**: 1.0.0  
**Last Updated**: October 2025  
**Built with**: Streamlit, Pandas, Plotly, Scikit-learn

