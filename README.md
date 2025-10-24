# APREU Advanced Segmentation - POC

A comprehensive Streamlit application showcasing three complementary segmentation strategies for APREU contacts, providing interactive analytics and insights for targeted marketing campaigns.

![Version](https://img.shields.io/badge/version-2.0.0-blue)
![Python](https://img.shields.io/badge/python-3.8%2B-brightgreen)
![Streamlit](https://img.shields.io/badge/streamlit-1.31%2B-red)

---

## 🎯 Overview

This application provides **dynamic, real-time analysis** of HubSpot contact data through three distinct segmentation approaches. All analysis is performed live on user-provided data - no static exports or pre-computed results.

### 🔑 Key Features

- ✅ **Upload Your Own Data**: CSV upload with automatic validation
- ✅ **Dynamic Analysis**: All metrics computed in real-time
- ✅ **Three Segmentation Strategies**: Social, Geographic, and Activity-based
- ✅ **Interactive Visualizations**: Plotly charts with drill-down capabilities
- ✅ **Journey Visualizations**: Visual timelines for source and activity journeys
- ✅ **Academic Period Analysis**: Seasonal trends and enrollment cycle insights
- ✅ **Geographic Configuration**: Customizable domestic/local region definitions
- ✅ **Contact Lookup**: Individual contact deep-dive analysis

---

## 📁 Project Structure

```
SettingUp/
├── app/                              # Streamlit Application
│   ├── streamlit_app.py             # Main application entry point
│   ├── utils.py                     # Shared utility functions
│   ├── geo_config.py                # Geographic configuration
│   ├── cluster1_analysis.py         # Social Engagement analysis
│   ├── cluster2_analysis.py         # Geography & Engagement analysis
│   ├── cluster3_analysis.py         # APREU Activities analysis
│   └── assets/
│       └── corchetes-blanco.webp    # Logo/branding assets
│
├── notebooks/                        # Jupyter Notebooks (Original Analysis)
│   ├── Cluster1.ipynb               # Social engagement development
│   ├── Cluster2.ipynb               # Geography segmentation development
│   ├── Cluster3.ipynb               # APREU activities development
│   └── sacar_historicos_PLANTILLA.ipynb  # Historical data extraction template
│
├── data/                             # Data Files
│   ├── raw/                         # Original data files
│   │   ├── contacts_campus_Qro_.csv          # Main contact data (gitignored)
│   │   └── propiedades_contactos_negocios.csv # Additional properties (gitignored)
│   └── processed/                   # Analysis outputs (gitignored)
│       ├── cluster2_rows.csv
│       ├── cluster3_contacts.csv
│       ├── segments_cluster1_overlay.csv
│       └── *.xlsx (summary files)
│
├── docs/                             # Documentation
│   ├── README.md                    # This file
│   ├── QUICKSTART.md                # Quick start guide
│   ├── guides/                      # User Guides
│   │   ├── FILE_UPLOAD_GUIDE.md
│   │   ├── GEOGRAPHIC_CONFIG_GUIDE.md
│   │   ├── JOURNEY_VISUALIZATIONS.md
│   │   └── STREAMLIT_APP_GUIDE.md
│   ├── features/                    # Feature Documentation
│   │   ├── ACADEMIC_PERIOD_FEATURE.md
│   │   ├── ENRICHMENT_SUMMARY.md
│   │   ├── NEW_FEATURES_ADDED.md
│   │   └── UI_DESCRIPTIONS_GUIDE.md
│   ├── technical/                   # Technical Documentation
│   │   ├── COLUMN_REFERENCE.md
│   │   ├── IMPLEMENTATION_STATUS.md
│   │   ├── FIXES_APPLIED.md
│   │   └── MISSING_FEATURES_ANALYSIS.md
│   └── notebooks/                   # Notebook-specific Docs
│       ├── README_Cluster1.md
│       ├── README_Cluster2.md
│       ├── README_Cluster3.md
│       ├── README_sacar_historicos_PLANTILLA.md
│       └── COMPLETE_SUMMARY.md
│
├── exports/                          # Notebook Exports (gitignored)
│   ├── Cluster1.html
│   ├── Cluster1.pdf
│   ├── Cluster2.html
│   ├── Cluster2.pdf
│   ├── Cluster3.html
│   └── Cluster3.pdf
│
├── scripts/                          # Utility Scripts
│   ├── START_STREAMLIT_APP.sh       # Launch script for the app
│   ├── START_APP.sh                 # Alternative launcher
│   └── test_installation.py         # Dependency checker
│
├── requirements.txt                  # Notebook dependencies
├── requirements_streamlit.txt        # Streamlit app dependencies
├── .gitignore                       # Git ignore rules
└── README.md                        # Main documentation (you are here)
```

---

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- pip (Python package installer)
- (Optional) Contact data CSV file

### Installation

1. **Install dependencies:**
```bash
pip install -r requirements_streamlit.txt
```

2. **Place your data (optional):**
   - Copy your HubSpot export to `data/raw/contacts_campus_Qro_.csv`
   - Or use the upload feature in the app

3. **Run the application:**
```bash
# Option 1: Using the script
./scripts/START_STREAMLIT_APP.sh

# Option 2: Direct command
streamlit run app/streamlit_app.py

# Option 3: From project root
cd /path/to/SettingUp
python3 -m streamlit run app/streamlit_app.py
```

4. **Open your browser** to `http://localhost:8501`

---

## 🎯 Three Segmentation Strategies

### 📱 Cluster 1: Socially Engaged Prospects

**Goal**: Identify prospects with social media activity using historical data analysis

**Segments**: 
- 1A: High Engagement Socially Active
- 1B: Low Engagement Socially Active

**Key Features**:
- Multi-platform detection (12+ platforms)
- Historical data parsing
- Platform-specific targeting
- Time-to-close analysis
- Source journey visualization
- Academic period analysis (seasonal trends)
- Fast/Slow closers analysis
- Traffic source performance

**Best For**: Social media budget allocation, platform-specific campaigns

---

### 🌍 Cluster 2: Geography & Engagement Segmentation

**Goal**: Segment by geography (Local/Domestic/International) and engagement level

**Segments**:
- 2A: Domestic High Engagement
- 2B: Domestic Low Engagement
- 2C: International High Engagement
- 2D: International Low Engagement
- 2E: Local High Engagement
- 2F: Local Low Engagement

**Key Features**:
- Geographic classification (configurable)
- State-level performance analysis
- Engagement scoring per geo tier
- Regional campaign insights
- Fast/Slow closers by geography
- Lifecycle stage deep-dive

**Best For**: Regional marketing strategy, geographic outreach planning

---

### 🎪 Cluster 3: APREU Activities & Entry Channels

**Goal**: Segment by promotional activities and entry channels

**Segments**:
- 3A: Digital-first converters
- 3B: Event-first converters
- 3C: Messaging-first converters
- 3D: Niche/Low-volume converters

**Key Features**:
- APREU activity tracking
- Preparatoria cross-analysis
- Conversion event analysis
- Email engagement metrics
- Activity journey visualization
- Academic period analysis (seasonal trends)
- Fast/Slow closers by activity
- Conversion timeline analysis

**Best For**: Event ROI analysis, activity optimization, promotional planning

---

## 📊 Application Features

### Data Upload & Validation
- **CSV Upload**: Upload HubSpot exports directly
- **Auto-validation**: Checks for required columns
- **Data Preview**: See sample data before analysis
- **Error Handling**: Clear messages for data issues

### Interactive Analysis
- **Real-time Computation**: All metrics calculated on-demand
- **Filtering**: Dynamic filters for each cluster
- **Drill-down**: Click charts to explore details
- **Cross-tabulations**: Segment vs Platform/Geography/Activity

### Visualizations
- **Plotly Charts**: Interactive bar, pie, line, and scatter plots
- **Heatmaps**: Cross-tabulation visualizations
- **Journey Maps**: Visual timelines for contact paths
- **Distribution Charts**: Engagement, time-to-close, activity patterns

### Insights & Recommendations
- **Automatic Insights**: Key findings generated per analysis
- **Performance Metrics**: Conversion rates, engagement scores, close rates
- **Comparative Analysis**: Best/worst performing segments
- **Trend Analysis**: Seasonal patterns, volume trends

### Contact Lookup
- **Individual Search**: Look up any contact by ID or email
- **Deep Dive**: Complete profile with all metrics
- **Journey Visualization**: Visual path through touchpoints
- **Segment Assignment**: See which segments contact belongs to

---

## 📖 Documentation

### User Guides
- **[Quick Start Guide](docs/QUICKSTART.md)**: Get started in 5 minutes
- **[File Upload Guide](docs/guides/FILE_UPLOAD_GUIDE.md)**: CSV upload instructions
- **[Geographic Config](docs/guides/GEOGRAPHIC_CONFIG_GUIDE.md)**: Customize regions
- **[Journey Visualizations](docs/guides/JOURNEY_VISUALIZATIONS.md)**: Understanding journey maps

### Feature Documentation
- **[Academic Period Analysis](docs/features/ACADEMIC_PERIOD_FEATURE.md)**: Seasonal insights
- **[Enrichment Summary](docs/features/ENRICHMENT_SUMMARY.md)**: Latest features added
- **[UI Descriptions](docs/features/UI_DESCRIPTIONS_GUIDE.md)**: Interface guide

### Technical Documentation
- **[Column Reference](docs/technical/COLUMN_REFERENCE.md)**: Data field definitions
- **[Implementation Status](docs/technical/IMPLEMENTATION_STATUS.md)**: Development progress
- **[Fixes Applied](docs/technical/FIXES_APPLIED.md)**: Bug fixes and improvements

---

## 🔧 Configuration

### Geographic Configuration

Customize your domestic and local regions:

1. In the sidebar, click "⚙️ Geographic Configuration"
2. Select your home country (e.g., "Mexico")
3. Select your local region (e.g., "Querétaro")
4. Click "Apply Configuration"

The Cluster 2 analysis will update to reflect your settings.

### Data Requirements

**Minimum Required Columns**:
- Contact ID or Email
- Create Date
- Lifecycle Stage (recommended)
- Any historical data fields (for full analysis)

**Recommended Columns**:
- Close Date (for conversion analysis)
- Traffic sources (for Cluster 1)
- State/Country (for Cluster 2)
- APREU activities (for Cluster 3)
- Engagement metrics (sessions, pageviews, forms)

---

## 🛠️ Development

### Running from Source

```bash
# Navigate to project root
cd /path/to/SettingUp

# Install dependencies
pip install -r requirements_streamlit.txt

# Run the app
streamlit run app/streamlit_app.py
```

### Testing

```bash
# Test dependencies
python3 scripts/test_installation.py

# Run the app in debug mode
streamlit run app/streamlit_app.py --logger.level=debug
```

### Notebooks

The original analysis notebooks are in the `notebooks/` directory:

```bash
# Launch Jupyter
jupyter notebook notebooks/

# Or open specific notebook
jupyter notebook notebooks/Cluster1.ipynb
```

---

## 📦 Dependencies

### Core Libraries
- `streamlit>=1.31.0` - Web application framework
- `pandas>=2.0.0` - Data manipulation
- `numpy>=1.24.0` - Numerical computing
- `plotly>=5.18.0` - Interactive visualizations

### Additional Libraries
- `scikit-learn>=1.3.0` - Machine learning (KMeans)
- `openpyxl>=3.1.0` - Excel file handling
- `matplotlib>=3.7.0` - Journey visualizations
- `pillow>=10.0.0` - Image handling (logo)

See `requirements_streamlit.txt` for complete list.

---

## 🤝 Contributing

This is a POC application. For improvements:

1. **Report Issues**: Document any bugs or unexpected behavior
2. **Suggest Features**: Share ideas for new analyses or visualizations
3. **Enhance Docs**: Update documentation as needed
4. **Test Data**: Validate with different data sources

---

## 📝 License

Internal use for APREU Advanced Segmentation project.

---

## 📞 Support

For questions or issues:

1. Check the `docs/` directory for detailed guides
2. Review the technical documentation in `docs/technical/`
3. Examine the original notebooks in `notebooks/`
4. Check the feature documentation in `docs/features/`

---

## 🎓 Academic Period Analysis

Track enrollment cycles and seasonal trends:
- Contact volume by semester
- Performance metrics over time
- Platform/Activity effectiveness by period
- Close rate trends
- Lifecycle stage evolution

Available in Cluster 1 and Cluster 3.

---

## 🗺️ Journey Visualizations

Visual timelines showing:
- **Source Journey** (Cluster 1): Traffic sources over time
- **APREU Journey** (Cluster 3): Activities and conversions

Available in Contact Lookup for Cluster 1 and 3.

---

## ⚡ Fast/Slow Closers Analysis

Identify patterns in conversion speed:
- Fast closers (<30 days)
- Medium closers (30-90 days)
- Slow closers (>90 days)

Cross-tabulated with segments, platforms, geography, and activities.

Available in all three clusters.

---

**Version**: 2.0.0  
**Last Updated**: October 2025  
**Status**: Production Ready ✅
