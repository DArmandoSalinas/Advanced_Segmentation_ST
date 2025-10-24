"""
APREU Advanced Segmentation - Interactive POC
A comprehensive Streamlit application showcasing three distinct segmentation strategies.
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path

# Page configuration
st.set_page_config(
    page_title="APREU Advanced Segmentation POC",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Memory optimization
import gc
import os
os.environ['PYARROW_IGNORE_TIMEZONE'] = '1'

# Custom CSS for better UI
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        padding: 1rem 0;
    }
    .sub-header {
        font-size: 1.5rem;
        color: #555;
        text-align: center;
        padding-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1.5rem;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 2rem;
    }
    .stTabs [data-baseweb="tab"] {
        height: 3rem;
        font-size: 1.1rem;
    }
</style>
""", unsafe_allow_html=True)

# Import cluster-specific modules
from cluster1_analysis import render_cluster1
from cluster2_analysis import render_cluster2
from cluster3_analysis import render_cluster3
from utils import load_data, display_metrics, create_segment_pie_chart, validate_data, apply_global_filters
from geo_config import render_geo_config_ui, get_geo_config

def main():
    """Main application entry point"""
    
    # Header
    st.markdown('<h1 class="main-header">🎯 APREU Advanced Segmentation</h1>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Proof of Concept - Interactive Segmentation Analytics</p>', unsafe_allow_html=True)
    
    # Sidebar navigation
    with st.sidebar:
        # Display logo
        from pathlib import Path
        from PIL import Image
        
        logo_path = Path("app/assets/corchetes-blanco.webp")
        if logo_path.exists():
            try:
                logo_img = Image.open(logo_path)
                st.image(logo_img, use_container_width=True)
            except Exception as e:
                st.error(f"Error loading logo: {e}")
                st.markdown("### 🎯 APREU")
        else:
            st.markdown("### 🎯 APREU")
        st.markdown("---")
        
        st.markdown("### 📁 Data Source")
        
        # File upload option
        data_source = st.radio(
            "Choose data source:",
            ["📂 Use Default File", "⬆️ Upload CSV"],
            index=0
        )
        
        uploaded_file = None
        data = None
        
        if data_source == "⬆️ Upload CSV":
            st.markdown("**Upload HubSpot Contact Export:**")
            uploaded_file = st.file_uploader(
                "Choose a CSV file",
                type=['csv'],
                help="Upload your HubSpot contacts export CSV file"
            )
            
            if uploaded_file is not None:
                try:
                    # Load and validate data
                    data = load_data(uploaded_file)
                    validation = validate_data(data)
                    
                    if validation['is_valid']:
                        st.success(f"✅ Loaded {len(data):,} contacts")
                        
                        # Show data preview
                        with st.expander("📋 Data Preview"):
                            st.write(f"**Columns:** {len(data.columns)}")
                            st.write(f"**Rows:** {len(data):,}")
                            st.dataframe(data.head(3), use_container_width=True)
                        
                        # Show warnings if any
                        if validation['warnings']:
                            with st.expander("⚠️ Warnings", expanded=False):
                                for warning in validation['warnings']:
                                    st.warning(warning)
                    else:
                        st.error(f"❌ Invalid data: Missing required columns: {', '.join(validation['missing_basic'])}")
                        data = None
                        
                except Exception as e:
                    st.error(f"❌ Error loading file: {e}")
                    data = None
            else:
                st.info("👆 Please upload a CSV file to begin analysis")
        else:
            # Use default file
            try:
                data = load_data()
                st.success(f"✅ Loaded {len(data):,} contacts")
                
                with st.expander("ℹ️ Using Default Data"):
                    st.write("**File:** data/raw/contacts_campus_Qro_.csv")
                    st.write(f"**Columns:** {len(data.columns)}")
                    st.write(f"**Rows:** {len(data):,}")
            except Exception as e:
                st.error(f"❌ Error loading default file: {e}")
                st.info("💡 Try uploading your own CSV file instead")
                data = None
        
        st.markdown("---")
        
        # Global Filters Section
        st.markdown("### 🎛️ Global Filters")
        
        with st.expander("📅 Academic Period Filter", expanded=False):
            if data is not None:
                # Look for periodo de ingreso field
                periodo_fields = [
                    'Periodo de ingreso a licenciatura (MQL)', 
                    'Periodo de ingreso',
                    'periodo_de_ingreso',
                    'PERIODO DE INGRESO'
                ]
                
                periodo_col = None
                for field in periodo_fields:
                    if field in data.columns:
                        periodo_col = field
                        break
                
                if periodo_col:
                    # Convert periodo codes to readable format
                    # Based on YYYYMM format where MM codes are:
                    # 05 = Special, 10 = Spring, 35 = Summer, 60 = Fall, 75 = Winter/Special
                    def convert_periodo(val):
                        try:
                            if pd.isna(val):
                                return "Unknown"
                            periodo_str = str(int(float(val))).strip()
                            if len(periodo_str) != 6:
                                return "Unknown"
                            year = periodo_str[:4]
                            period_code = int(periodo_str[4:])
                            
                            # Map period codes to semester names (from notebooks)
                            period_map = {
                                5: "Special",
                                10: "Spring", 
                                35: "Summer",
                                60: "Fall",
                                75: "Winter/Special"
                            }
                            
                            semester = period_map.get(period_code, f"Unknown({period_code})")
                            return f"{year} {semester}"
                        except:
                            return "Unknown"
                    
                    import pandas as pd
                    from utils import hist_latest
                    
                    # Get latest periodo values
                    periodo_latest = data[periodo_col].apply(hist_latest)
                    periodo_readable = periodo_latest.apply(convert_periodo)
                    available_periodos = sorted([p for p in periodo_readable.unique() if p != "Unknown"])
                    
                    if available_periodos:
                        selected_periodos = st.multiselect(
                            "Select Admission Period(s):",
                            options=available_periodos,
                            default=[],
                            help="Filter contacts by their admission period (leave empty for all)"
                        )
                        
                        st.session_state['filter_periodos'] = selected_periodos
                    else:
                        st.info("No valid periodo de ingreso data found")
                else:
                    st.info("📅 Periodo de ingreso field not found in dataset")
            else:
                st.info("Load data to see periodo filter")
        
        with st.expander("💼 Closure Status Filter", expanded=False):
            closure_status = st.radio(
                "Closure Status:",
                ["All Contacts", "Closed Only", "Open Only"],
                index=0,
                help="Filter by deal closure status"
            )
            
            # Store in session state
            st.session_state['filter_closure_status'] = closure_status
        
        with st.expander("🔄 Lifecycle Filters", expanded=False):
            if data is not None:
                from utils import hist_latest
                import pandas as pd
                
                lifecycle_col = 'Lifecycle Stage' if 'Lifecycle Stage' in data.columns else 'lifecycle_stage'
                if lifecycle_col in data.columns:
                    # Get LATEST lifecycle stage values only
                    lifecycle_latest = data[lifecycle_col].apply(hist_latest)
                    available_stages = sorted([str(x) for x in lifecycle_latest.dropna().unique() if str(x).lower() not in ['other', 'subscriber', 'nan', 'none', '']])
                    
                    if available_stages:
                        selected_stages = st.multiselect(
                            "Select Lifecycle Stages (leave empty for all):",
                            options=available_stages,
                            default=[],
                            help="Filter to specific lifecycle stages (uses LATEST value only)"
                        )
                        
                        st.session_state['filter_lifecycle_stages'] = selected_stages
                    else:
                        st.info("No valid lifecycle stages found")
                else:
                    st.info("Lifecycle stage data not available")
        
        # Reset filters button
        if st.button("🔄 Reset All Filters", use_container_width=True):
            for key in list(st.session_state.keys()):
                if key.startswith('filter_'):
                    del st.session_state[key]
            st.rerun()
        
        # Show active filters count
        active_filters = sum(1 for k in st.session_state.keys() if k.startswith('filter_'))
        if active_filters > 0:
            st.info(f"✅ {active_filters} filter(s) active")
        
        st.markdown("---")
        
        # Geographic configuration (for Cluster 2)
        render_geo_config_ui()
        
        st.markdown("---")
        st.markdown("### 📊 Navigation")
        
        cluster_choice = st.radio(
            "Select Segmentation Strategy:",
            ["🏠 Overview", "📱 Cluster 1: Social Engagement", "🌍 Cluster 2: Geography & Engagement", 
             "🎪 Cluster 3: APREU Activities"],
            index=0,
            disabled=(data is None)
        )
        
        st.markdown("---")
        st.markdown("### 📖 Quick Reference")
        
        with st.expander("🎯 Which Cluster Should I Use?"):
            st.markdown("""
            **📱 Cluster 1: Social Media Strategy**
            - *When:* Optimizing social media campaigns
            - *For:* Platform budget allocation
            - *Answers:* Which platforms convert best?
            
            **🌍 Cluster 2: Regional Campaigns**
            - *When:* Planning geographic outreach
            - *For:* Regional marketing strategy
            - *Answers:* Which regions perform best?
            
            **🎪 Cluster 3: Event Planning**
            - *When:* Optimizing promotional activities
            - *For:* APREU event ROI analysis
            - *Answers:* Which events drive conversions?
            
            ---
            
            **💡 Pro Tip:** Use multiple clusters together!
            - Cluster 1 + 2 = Social strategy by region
            - Cluster 2 + 3 = Event planning by geography
            - All 3 = Comprehensive marketing strategy
            """)
        
        st.markdown("---")
        st.markdown("### ℹ️ About")
        st.info("""
        **Advanced Segmentation POC**
        
        This application showcases three complementary segmentation approaches:
        
        - **Cluster 1**: Social media activity & platform engagement
        - **Cluster 2**: Geographic distribution & engagement levels  
        - **Cluster 3**: Promotional activities & entry channels
        
        **Global Filters Available:**
        - 📅 Academic Period (Periodo de Ingreso)
        - 🔄 Lifecycle Stage (latest value)
        - 💼 Closure Status (Open/Closed/All)
        
        Each cluster also has specific filters for deeper analysis.
        
        **Data Pipeline:**
        1. Total Contacts → 2. APREU Contacts → 3. Remove "other"/"subscriber" → 4. Working Contacts
        """)
        
        # Download template
        st.markdown("---")
        st.markdown("### 📥 Need Help?")
        
        with st.expander("Required Data Format"):
            st.markdown("""
            **Your CSV should include:**
            
            **Basic Fields:**
            - Record ID (contact identifier)
            - Propiedad del contacto (to filter for APREU)
            
            **For Global Filters:**
            - Periodo de ingreso (admission period - format: YYYYMM, e.g., 202460 = 2024 Fall)
            - Lifecycle Stage (will use latest value, will remove "other" and "subscriber")
            - Close Date (for closure status filter)
            
            **For Cluster 1 (Social):**
            - Original Source
            - Broadcast/LinkedIn/Twitter/Facebook Clicks
            - Number of Sessions, Pageviews, Form Submissions
            
            **For Cluster 2 (Geography):**
            - IP Country, IP State/Region
            - Preparatoria location fields
            - Number of Sessions, Pageviews, Form Submissions
            
            **For Cluster 3 (APREU):**
            - Actividades de promoción APREU
            - First/Recent Conversion
            - Preparatoria information
            
            **Note:** Fields with historical values (delimiter: //) will use the latest value for filtering.
            
            **Periodo Codes:** 05=Special, 10=Spring, 35=Summer, 60=Fall, 75=Winter/Special
            """)
        
        if st.button("📄 View Sample Data Structure", use_container_width=True):
            if data is not None:
                st.info("Sample columns from loaded data:")
                st.code('\n'.join(data.columns[:20].tolist()))
            else:
                st.info("Load data first to see column structure")
    
    # Main content area
    if data is None:
        st.warning("⚠️ No data loaded. Please upload a CSV file or ensure the default file exists.")
        st.markdown("---")
        st.markdown("### 🚀 Getting Started")
        st.markdown("""
        **Option 1: Use Default File**
        - Ensure `contacts_campus_Qro_.csv` is in the `data/raw/` directory
        - Select "📂 Use Default File" in the sidebar
        
        **Option 2: Upload Your Own Data**
        - Export contacts from HubSpot as CSV
        - Select "⬆️ Upload CSV" in the sidebar
        - Click the upload button and select your file
        
        **Need Help?**
        - Check the "Required Data Format" section in the sidebar
        - View sample data structure using the button in the sidebar
        """)
    else:
        # Apply global filters
        filtered_data, filters_applied = apply_global_filters(data)
        
        # Show filter status
        if len(filters_applied) > 0:
            with st.expander(f"🔍 Active Filters ({len(filters_applied)})", expanded=False):
                st.markdown("**Applied filters:**")
                for f in filters_applied:
                    st.markdown(f"- {f}")
                st.markdown(f"**Result:** {len(filtered_data):,} of {len(data):,} contacts ({len(filtered_data)/len(data)*100:.1f}%)")
        
        # Route to appropriate cluster with filtered data
        if cluster_choice == "🏠 Overview":
            render_overview(filtered_data)
        elif cluster_choice == "📱 Cluster 1: Social Engagement":
            render_cluster1(filtered_data)
        elif cluster_choice == "🌍 Cluster 2: Geography & Engagement":
            render_cluster2(filtered_data)
        elif cluster_choice == "🎪 Cluster 3: APREU Activities":
            render_cluster3(filtered_data)

def render_overview(data):
    """Render the overview dashboard"""
    
    st.markdown("## 📊 Executive Overview")
    st.markdown("---")
    
    if data is None:
        st.error("⚠️ Data not loaded. Please check the data file.")
        return
    
    # Calculate key metrics with clear pipeline
    from utils import hist_latest
    
    # 1. Total contacts
    total_contacts = len(data)
    
    # 2. APREU contacts
    propiedad_col = 'Propiedad del contacto' if 'Propiedad del contacto' in data.columns else 'propiedad_del_contacto'
    if propiedad_col in data.columns:
        data_with_propiedad = data.copy()
        data_with_propiedad[propiedad_col] = data_with_propiedad[propiedad_col].apply(hist_latest)
        apreu_contacts = data_with_propiedad[data_with_propiedad[propiedad_col] == 'APREU']
        apreu_count = len(apreu_contacts)
    else:
        apreu_contacts = data
        apreu_count = total_contacts
    
    # 3. Contacts after removing "other" and "subscriber"
    lifecycle_col = 'Lifecycle Stage' if 'Lifecycle Stage' in data.columns else 'lifecycle_stage'
    if lifecycle_col in apreu_contacts.columns:
        apreu_contacts_cleaned = apreu_contacts.copy()
        apreu_contacts_cleaned[lifecycle_col] = apreu_contacts_cleaned[lifecycle_col].apply(hist_latest)
        working_contacts = apreu_contacts_cleaned[~apreu_contacts_cleaned[lifecycle_col].str.lower().isin(['other', 'subscriber'])]
        working_count = len(working_contacts)
    else:
        working_contacts = apreu_contacts
        working_count = apreu_count
    
    # 4. Closed contacts (from working contacts)
    close_col = 'close_date' if 'close_date' in working_contacts.columns else 'Close Date'
    closed_count = working_contacts[close_col].notna().sum() if close_col in working_contacts.columns else 0
    close_rate = (closed_count / working_count * 100) if working_count > 0 else 0
    
    # Display metrics
    st.markdown("### 📊 Contact Pipeline")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Contacts", f"{total_contacts:,}", help="All contacts in the dataset")
    
    with col2:
        apreu_pct = (apreu_count / total_contacts * 100) if total_contacts > 0 else 0
        st.metric("APREU Contacts", f"{apreu_count:,}", delta=f"{apreu_pct:.1f}%", help="Contacts where Propiedad = APREU")
    
    with col3:
        removed = apreu_count - working_count
        st.metric("After Cleanup", f"{working_count:,}", delta=f"-{removed:,}", delta_color="off", help="APREU contacts after removing 'other' and 'subscriber' lifecycle stages")
    
    with col4:
        st.metric("Closed Deals", f"{closed_count:,}", delta=f"{close_rate:.1f}%", help="Closed contacts from working set")
    
    st.markdown("---")
    
    # Cluster Comparison Section
    st.markdown("### 🎯 Segmentation Strategies Comparison")
    
    tab1, tab2, tab3 = st.tabs(["📱 Cluster 1", "🌍 Cluster 2", "🎪 Cluster 3"])
    
    with tab1:
        st.markdown("""
        #### Cluster 1: Socially Engaged Prospects
        
        **Goal:** Identify and segment prospects with social media activity using advanced historical data analysis 
        and multi-platform detection.
        
        **Key Features:**
        - ✅ Comprehensive historical data analysis (ALL values, not just latest)
        - ✅ Multi-platform detection (12+ platforms: Instagram, TikTok, LinkedIn, Facebook, etc.)
        - ✅ Smart filtering for APREU contacts
        - ✅ Intelligent platform tagging using historical + click data
        - ✅ Advanced closure analysis with time-to-close buckets
        - ✅ Lifecycle integration tracking
        - ✅ Interactive filters (segment, platform, social clicks, engagement score)
        - ✅ Performance benchmarking with quartile analysis
        - ✅ CSV exports (full data, summary, platform breakdown)
        
        **Segments:**
        - **1A. High Engagement + Social Activity**: Active social users, higher close rate
        - **1B. Low Engagement + Social Activity**: Social presence but minimal interaction
        
        **Platform Overlays:** Combined engagement + platform tags (e.g., "1A + Google_Ads", "1B + Facebook")
        
        **Available Tabs:** Overview, Segment Analysis, Platform Analysis, Business Outcomes, Fast/Slow Closers, Academic Period, Performance Benchmarks, Contact Lookup
        """)
        
        col1, col2 = st.columns(2)
        with col1:
            st.info("**Primary Use Case:** Social media team optimization, platform budget allocation, retargeting campaigns")
        with col2:
            st.success("**Expected:** Engaged contacts split into 1A/1B with platform tags")
    
    with tab2:
        st.markdown("""
        #### Cluster 2: Geography & Engagement Segmentation
        
        **Goal:** Segment contacts by geography (Local/Domestic/International) and engagement level 
        into 6 actionable subclusters.
        
        **Key Features:**
        - ✅ Geographic classification (Local, Domestic, International) - Configurable!
        - ✅ Engagement scoring per geo tier with quantile thresholds (70th percentile)
        - ✅ Enhanced state normalization (32 Mexican states + CDMX variants)
        - ✅ State-level performance analysis and tier classification
        - ✅ Dynamic geo configuration (change home country & local region)
        - ✅ Time-to-close analysis by geography
        - ✅ Interactive filters (segment, geo tier, country, engagement level)
        - ✅ Performance benchmarking by geography and country
        - ✅ CSV exports (full data, summary, geography breakdown)
        
        **Segments:**
        - **2A**: Domestic (non-local), High Engagement
        - **2B**: Domestic (non-local), Low Engagement  
        - **2C**: International, High Engagement
        - **2D**: International, Low Engagement
        - **2E**: Local, High Engagement
        - **2F**: Local, Low Engagement
        
        **Available Tabs:** Overview, Segment Analysis, Geography Analysis, Business Outcomes, Fast/Slow Closers, Performance Benchmarks, Contact Lookup
        """)
        
        col1, col2 = st.columns(2)
        with col1:
            st.info("**Primary Use Case:** Regional marketing campaigns, international recruitment, local QRO engagement")
        with col2:
            st.success("**Expected Segments:** 6 core segments (2A-2F) + state-specific sub-segments for domestic")
    
    with tab3:
        st.markdown("""
        #### Cluster 3: Promotion-driven Converters (APREU Activities)
        
        **Goal:** Segment contacts by promotional activities and entry channels using comprehensive 
        historical APREU activity analysis.
        
        **Key Features:**
        - ✅ Comprehensive historical APREU activity parsing (ALL events attended)
        - ✅ Multi-activity detection (Open Day, Fogatada, TDLA, Gira Panamá, WhatsApp, etc.)
        - ✅ Smart entry channel classification (Digital/Event/Messaging/Niche)
        - ✅ Preparatoria cross-analysis per activity
        - ✅ Conversion event tracking (first + recent conversion)
        - ✅ Activity journey visualization per contact
        - ✅ Email engagement and conversion timeline analysis
        - ✅ Academic period analysis with seasonal trends
        
        **Segments:**
        - **3A. Digital-first**: Website, forms, online entries → automated sequences
        - **3B. Event-first**: Open Day, Fogatada, live events → 48h follow-up
        - **3C. Messaging-first**: WhatsApp, direct contact → personalized, fast response
        - **3D. Niche/Low-volume**: Specialty programs, small campaigns → ROI evaluation
        
        **Available Tabs:** Overview, Segment Analysis, Activity Analysis, Preparatoria Analysis, Email & Conversion, Fast/Slow Closers, Academic Period, Contact Lookup
        """)
        
        col1, col2 = st.columns(2)
        with col1:
            st.info("**Primary Use Case:** Event ROI analysis, APREU campaign optimization, preparatoria partnerships")
        with col2:
            st.success("**Expected Segments:** 4 entry channels (3A-3D) with activity and preparatoria insights")
    
    st.markdown("---")
    
    # Quick Start Guide
    st.markdown("### 🚀 Quick Start Guide")
    
    st.markdown("""
    **How to use this application:**
    
    1. **Select a cluster** from the sidebar navigation
    2. **Explore segment distributions** and performance metrics
    3. **Analyze detailed breakdowns** using interactive filters
    4. **Search individual contacts** using the contact lookup tool
    5. **Export data** for further analysis or campaign activation
    
    **Navigation Tips:**
    - Use the **sidebar** to switch between clusters
    - Each cluster has **multiple tabs** for different analyses
    - **Hover over charts** for detailed information
    - Use **filters** to drill down into specific segments
    - The **contact lookup** feature is available in each cluster
    """)
    
    st.markdown("---")
    
    # Data Quality Summary
    with st.expander("📋 Data Quality Summary", expanded=False):
        st.markdown("#### Data Coverage by Cluster")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("**Cluster 1: Social Engagement**")
            social_fields = ['Original Source', 'Latest Traffic Source', 'Broadcast Clicks', 
                           'LinkedIn Clicks', 'Twitter Clicks', 'Facebook Clicks']
            # Handle both original and lowercase column names
            coverage = 0
            for field in social_fields:
                if field in data.columns:
                    coverage += data[field].notna().sum()
                elif field.lower().replace(' ', '_') in data.columns:
                    coverage += data[field.lower().replace(' ', '_')].notna().sum()
            st.metric("Data Points Available", f"{coverage:,}")
        
        with col2:
            st.markdown("**Cluster 2: Geography**")
            geo_fields = ['IP Country', 'IP State/Region', 'País preparatoria BPM', 'Estado de preparatoria BPM']
            coverage = 0
            for field in geo_fields:
                if field in data.columns:
                    coverage += data[field].notna().sum()
                elif field.lower().replace(' ', '_').replace('/', '_') in data.columns:
                    coverage += data[field.lower().replace(' ', '_').replace('/', '_')].notna().sum()
            st.metric("Data Points Available", f"{coverage:,}")
        
        with col3:
            st.markdown("**Cluster 3: APREU Activities**")
            apreu_fields = ['Actividades de promoción APREU', 'First Conversion', 'Recent Conversion']
            coverage = 0
            for field in apreu_fields:
                if field in data.columns:
                    coverage += data[field].notna().sum()
                elif field.lower().replace(' ', '_') in data.columns:
                    coverage += data[field.lower().replace(' ', '_')].notna().sum()
            st.metric("Data Points Available", f"{coverage:,}")

if __name__ == "__main__":
    main()

