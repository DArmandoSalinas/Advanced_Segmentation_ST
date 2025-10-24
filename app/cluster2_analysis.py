"""
Cluster 2: Geography & Engagement Segmentation
Segments contacts by geography (Local/Domestic/International) and engagement level
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from utils import (
    hist_latest, normalize_text,
    create_segment_pie_chart, create_bar_chart, create_funnel_chart,
    calculate_close_rate, calculate_days_to_close, categorize_ttc,
    display_metrics, create_download_button, display_dataframe_with_style
)
from geo_config import get_geo_config, is_home_country, is_local_region, classify_geo_tier_dynamic, get_geo_display_names

# Mexican states and cities
MX_ALIASES = {"mexico", "mx", "mex", "cdmx", "mexico."}
QRO_TOKENS = {
    "queretaro", "queretaro de arteaga", "santiago de queretaro", "qro", "qro.",
    "queretaro, qro", "queretaro qro"
}

MEXICAN_STATES = {
    "aguascalientes", "baja california", "baja california sur", "campeche", "chiapas",
    "chihuahua", "coahuila", "colima", "durango", "guanajuato", "guerrero", "hidalgo",
    "jalisco", "michoacan", "morelos", "nayarit", "nuevo leon", "oaxaca", "puebla", 
    "queretaro", "quintana roo", "san luis potosi", "sinaloa", "sonora", "tabasco", 
    "tamaulipas", "tlaxcala", "veracruz", "yucatan", "zacatecas",
    "ags", "bc", "bcs", "camp", "chis", "chih", "coah", "col", "dgo", "gto", "gro", "hgo",
    "jal", "mich", "mor", "nay", "nl", "oax", "pue", "qro", "q.roo", "slp",
    "sin", "son", "tab", "tamps", "tlax", "ver", "yuc", "zac",
    "edo mex", "estado de mexico", "edo. mex.", "edomex", "mexico",
    "cdmx", "ciudad de mexico", "df", "distrito federal", "cuidad de mexico"
}

STATE_NORMALIZATION = {
    "aguascalientes": "Aguascalientes", "ags": "Aguascalientes",
    "baja california": "Baja California", "bc": "Baja California",
    "baja california sur": "Baja California Sur", "bcs": "Baja California Sur",
    "campeche": "Campeche", "camp": "Campeche",
    "chiapas": "Chiapas", "chis": "Chiapas",
    "chihuahua": "Chihuahua", "chih": "Chihuahua",
    "coahuila": "Coahuila", "coah": "Coahuila",
    "colima": "Colima", "col": "Colima",
    "durango": "Durango", "dgo": "Durango",
    "guanajuato": "Guanajuato", "gto": "Guanajuato",
    "guerrero": "Guerrero", "gro": "Guerrero",
    "hidalgo": "Hidalgo", "hgo": "Hidalgo",
    "jalisco": "Jalisco", "jal": "Jalisco",
    "estado de mexico": "Estado de Mexico", "edo mex": "Estado de Mexico",
    "edo. mex.": "Estado de Mexico", "edomex": "Estado de Mexico",
    "ciudad de mexico": "Ciudad de Mexico", "cdmx": "Ciudad de Mexico",
    "df": "Ciudad de Mexico", "distrito federal": "Ciudad de Mexico",
    "michoacan": "Michoacan", "mich": "Michoacan",
    "morelos": "Morelos", "mor": "Morelos",
    "nayarit": "Nayarit", "nay": "Nayarit",
    "nuevo leon": "Nuevo Leon", "nl": "Nuevo Leon",
    "oaxaca": "Oaxaca", "oax": "Oaxaca",
    "puebla": "Puebla", "pue": "Puebla",
    "queretaro": "Queretaro", "qro": "Queretaro",
    "quintana roo": "Quintana Roo", "q.roo": "Quintana Roo",
    "san luis potosi": "San Luis Potosi", "slp": "San Luis Potosi",
    "sinaloa": "Sinaloa", "sin": "Sinaloa",
    "sonora": "Sonora", "son": "Sonora",
    "tabasco": "Tabasco", "tab": "Tabasco",
    "tamaulipas": "Tamaulipas", "tamps": "Tamaulipas",
    "tlaxcala": "Tlaxcala", "tlax": "Tlaxcala",
    "veracruz": "Veracruz", "ver": "Veracruz",
    "yucatan": "Yucatan", "yuc": "Yucatan",
    "zacatecas": "Zacatecas", "zac": "Zacatecas",
    "mexico": "Estado de Mexico",
}

@st.cache_data
def process_cluster2_data(_data, geo_config=None, cache_key=None):
    """Process data for Cluster 2 analysis with dynamic geo configuration
    
    Args:
        _data: Input dataframe (underscore prevents caching on this param)
        geo_config: Geographic configuration dict
        cache_key: String to bust cache when filters change (NO underscore = used for cache hashing)
    """
    
    df = _data.copy()
    
    # Get geo config (use provided or get from session state)
    if geo_config is None:
        geo_config = get_geo_config()
    
    # Column mapping
    column_map = {
        'Record ID': 'contact_id',
        'Number of Sessions': 'num_sessions',
        'Number of Pageviews': 'num_pageviews',
        'Number of Form Submissions': 'forms_submitted',
        'IP Country': 'ip_country',
        'IP State/Region': 'ip_state_region',
        'Ciudad preparatoria BPM': 'prep_city_bpm',
        'Preparatoria BPM': 'prep_school_bpm',
        'Estado de preparatoria BPM': 'prep_state_bpm',
        'Estado de procedencia': 'estado_de_procedencia',
        'País preparatoria BPM': 'prep_country_bpm',
        'Likelihood to close': 'likelihood_to_close',
        'Create Date': 'create_date',
        'Close Date': 'close_date',
        'Lifecycle Stage': 'lifecycle_stage',
        'Propiedad del contacto': 'propiedad_del_contacto',
        'Original Source': 'original_source',
        'Latest Traffic Source': 'latest_source',
        'Last Referring Site': 'last_referrer',
        'Periodo de ingreso a licenciatura (MQL)': 'periodo_de_ingreso',
        'Periodo de ingreso': 'periodo_de_ingreso',
        'PERIODO DE INGRESO': 'periodo_de_ingreso'
    }
    
    df = df.rename(columns=column_map)
    
    # Apply hist_latest
    for col in df.columns:
        if col in ['num_sessions', 'num_pageviews', 'forms_submitted', 'likelihood_to_close']:
            df[col] = pd.to_numeric(df[col].apply(hist_latest), errors='coerce').fillna(0)
        elif col not in ['create_date', 'close_date']:
            df[col] = df[col].apply(hist_latest)
    
    # Filter for APREU contacts
    if 'propiedad_del_contacto' in df.columns:
        df = df[df['propiedad_del_contacto'].str.upper() == 'APREU'].copy()
    
    # Filter out "Other" and "subscriber" lifecycle stages
    if 'lifecycle_stage' in df.columns:
        df = df[~df['lifecycle_stage'].str.lower().isin(['other', 'subscriber'])].copy()
    
    # Normalize geography columns
    geo_cols = ['ip_country', 'ip_state_region', 'prep_city_bpm', 'prep_school_bpm',
                'prep_state_bpm', 'prep_country_bpm', 'estado_de_procedencia']
    
    for col in geo_cols:
        if col in df.columns:
            df[col] = df[col].apply(normalize_text)
    
    # Normalize state names
    for col in ['ip_state_region', 'prep_state_bpm', 'estado_de_procedencia']:
        if col in df.columns:
            df[col] = df[col].map(STATE_NORMALIZATION).fillna(df[col])
    
    # Consolidate geography fields
    def coalesce_non_unknown(series_list):
        cleaned = [s.replace({"unknown": np.nan}) if isinstance(s, pd.Series) else s 
                  for s in series_list]
        if cleaned:
            out = pd.concat(cleaned, axis=1).bfill(axis=1).iloc[:, 0]
            return out.fillna("unknown")
        return pd.Series("unknown", index=df.index)
    
    country_series = [df.get(col, pd.Series("unknown", index=df.index)) 
                     for col in ['prep_country_bpm', 'ip_country']]
    df['country_any'] = coalesce_non_unknown(country_series)
    
    state_series = [df.get(col, pd.Series("unknown", index=df.index)) 
                   for col in ['prep_state_bpm', 'estado_de_procedencia', 'ip_state_region']]
    df['state_any'] = coalesce_non_unknown(state_series)
    
    city_series = [df.get(col, pd.Series("unknown", index=df.index)) 
                  for col in ['prep_city_bpm']]
    df['city_any'] = coalesce_non_unknown(city_series)
    
    # Classify geo tier using dynamic configuration
    df['geo_tier'] = df.apply(lambda row: classify_geo_tier_dynamic(row, geo_config), axis=1)
    
    # Rescue contacts with domestic indicators but no country
    rescued_mask = (df['country_any'] == 'unknown') & (df['geo_tier'].isin(['local', 'domestic_non_local']))
    df.loc[rescued_mask, 'country_any'] = geo_config['home_country'].lower()
    
    # Engagement features
    df['log_sessions'] = np.log1p(df.get('num_sessions', 0))
    df['log_pageviews'] = np.log1p(df.get('num_pageviews', 0))
    df['log_forms'] = np.log1p(df.get('forms_submitted', 0))
    df['engagement_score'] = df['log_sessions'] + df['log_pageviews'] + df['log_forms']
    
    # Mark high/low per geo tier using quantile threshold
    HIGH_ENG_Q = 0.70
    df['is_high_engager'] = False
    for tier, grp in df.groupby('geo_tier'):
        if len(grp) > 0:
            thr = grp['engagement_score'].quantile(HIGH_ENG_Q)
            df.loc[grp.index, 'is_high_engager'] = grp['engagement_score'] >= thr
    
    # Assign 2A-2F segments
    def assign_c2(row):
        tier = row['geo_tier']
        hi = bool(row['is_high_engager'])
        if tier == 'domestic_non_local':
            return '2A' if hi else '2B'
        if tier == 'international':
            return '2C' if hi else '2D'
        if tier == 'local':
            return '2E' if hi else '2F'
        return '2Z'
    
    df['segment_c2'] = df.apply(assign_c2, axis=1)
    
    # Dynamic action map based on geo config
    local_name = geo_config['local_region']
    country_name = geo_config['home_country']
    
    ACTION_MAP = {
        '2A': f'Digital engagement + virtual events ({country_name} non-{local_name})',
        '2B': f'WhatsApp/email pushes ({country_name} non-{local_name})',
        '2C': 'Webinars + virtual Q&A (International)',
        '2D': 'Awareness campaigns (International)',
        '2E': f'In-person events + local engagement (Local {local_name})',
        '2F': f'Local nurture + WhatsApp (Local {local_name})',
        '2Z': 'Investigate missing geography'
    }
    df['segment_c2_action'] = df['segment_c2'].map(ACTION_MAP)
    
    # Calculate days to close
    if 'create_date' in df.columns and 'close_date' in df.columns:
        df['days_to_close'] = df.apply(
            lambda row: calculate_days_to_close(row['create_date'], row['close_date']),
            axis=1
        )
        df['ttc_bucket'] = df['days_to_close'].apply(categorize_ttc)
    
    # Convert academic period codes to readable formats (YYYYMM -> "Year Semester")
    def convert_academic_period(period_code):
        """Convert YYYYMM period codes to readable format"""
        if pd.isna(period_code) or period_code == "" or period_code == "unknown":
            return "Unknown"
        
        try:
            period_str = str(period_code).strip()
            if len(period_str) != 6:
                return f"Invalid: {period_code}"
            
            year = int(period_str[:4])
            period = int(period_str[4:])
            
            # Map period codes to semester names
            period_map = {
                5: "Special",
                10: "Spring", 
                35: "Summer",
                60: "Fall",
                75: "Winter/Special"
            }
            
            semester = period_map.get(period, f"Unknown({period})")
            return f"{year} {semester}"
            
        except (ValueError, IndexError):
            return f"Invalid: {period_code}"
    
    # Apply period conversion
    if 'periodo_de_ingreso' in df.columns:
        df['periodo_ingreso'] = df['periodo_de_ingreso'].apply(convert_academic_period)
        # Drop the old column to avoid confusion
        df = df.drop(columns=['periodo_de_ingreso'])
    
    # Normalize likelihood
    if 'likelihood_to_close' in df.columns:
        s = df['likelihood_to_close']
        s = np.where(s > 1, s / 100.0, s)
        df['likelihood_pct'] = pd.Series(s, index=df.index).clip(0, 1) * 100
    
    return df

def create_cluster2_xlsx_export(cohort):
    """Create comprehensive XLSX workbook with 20+ analysis sheets"""
    from io import BytesIO
    import pandas as pd
    from utils import hist_latest
    
    # Apply hist_latest to get only the latest values for export
    cohort_export = cohort.copy()
    
    # Columns that should show only latest value in exports
    latest_only_cols = ['latest_source', 'lifecycle_stage', 'original_source', 'original_source_d1', 'original_source_d2',
                        'canal_de_adquisicion', 'last_referrer']
    
    for col in latest_only_cols:
        if col in cohort_export.columns:
            cohort_export[col] = cohort_export[col].apply(hist_latest)
    
    output = BytesIO()
    
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        # 1. Executive Summary (use cohort_export with latest values)
        exec_summary = pd.DataFrame({
            'Metric': [
                'Total Contacts',
                'Segments',
                'Average Engagement Score',
                'Median Likelihood to Close',
                'Total Closed Deals',
                'Average Days to Close'
            ],
            'Value': [
                f"{len(cohort_export):,}",
                ', '.join(cohort_export['segment_c2'].unique()),
                f"{cohort_export['engagement_score'].mean():.2f}" if 'engagement_score' in cohort_export.columns else 'N/A',
                f"{cohort_export['likelihood_to_close'].median():.2%}" if 'likelihood_to_close' in cohort_export.columns else 'N/A',
                f"{cohort_export['close_date'].notna().sum():,}" if 'close_date' in cohort_export.columns else 'N/A',
                f"{cohort_export['days_to_close'].mean():.1f}" if 'days_to_close' in cohort_export.columns else 'N/A'
            ]
        })
        exec_summary.to_excel(writer, sheet_name="1_executive_summary", index=False)
        
        # 2. Segment Performance
        numeric_cols = ['num_sessions', 'num_pageviews', 'forms_submitted', 'engagement_score']
        numeric_cols = [c for c in numeric_cols if c in cohort_export.columns]
        if numeric_cols:
            segment_perf = cohort_export.groupby('segment_c2')[numeric_cols].agg(['mean', 'median', 'count']).round(2)
            segment_perf.to_excel(writer, sheet_name="2_segment_performance")
        
        # 3. Segment Counts
        counts_c2 = cohort_export['segment_c2'].value_counts().to_frame('count')
        counts_c2.to_excel(writer, sheet_name="3_segment_counts")
        
        # 4. Engagement Means
        if numeric_cols:
            numeric_means = cohort_export.groupby('segment_c2')[numeric_cols].mean().round(2)
            numeric_means.to_excel(writer, sheet_name="4_engagement_means")
        
        # 5. Engagement Medians
        if numeric_cols:
            numeric_medians = cohort_export.groupby('segment_c2')[numeric_cols].median().round(2)
            numeric_medians.to_excel(writer, sheet_name="5_engagement_medians")
        
        # 6. Geo Analysis
        if 'geo_tier' in cohort_export.columns:
            geo_tier_counts = cohort_export.groupby(['segment_c2', 'geo_tier']).size().reset_index(name='count')
            geo_tier_counts.to_excel(writer, sheet_name="6_geo_analysis", index=False)
        
        # 7-9. Top Countries, States, Cities
        if 'country_any' in cohort_export.columns:
            top_countries = cohort_export['country_any'].value_counts().head(20).reset_index()
            top_countries.columns = ['Country', 'Count']
            top_countries.to_excel(writer, sheet_name="7_top_countries", index=False)
        
        if 'state_any' in cohort_export.columns:
            top_states = cohort_export['state_any'].value_counts().head(20).reset_index()
            top_states.columns = ['State', 'Count']
            top_states.to_excel(writer, sheet_name="8_top_states", index=False)
        
        if 'city_any' in cohort_export.columns:
            top_cities = cohort_export['city_any'].value_counts().head(20).reset_index()
            top_cities.columns = ['City', 'Count']
            top_cities.to_excel(writer, sheet_name="9_top_cities", index=False)
        
        # 10-11. Lifecycle Analysis (using latest values only)
        if 'lifecycle_stage' in cohort_export.columns:
            lifecycle_dist = cohort_export.groupby(['segment_c2', 'lifecycle_stage']).size().reset_index(name='count')
            lifecycle_pct = lifecycle_dist.pivot(index='segment_c2', columns='lifecycle_stage', values='count').fillna(0)
            lifecycle_pct = lifecycle_pct.div(lifecycle_pct.sum(axis=1), axis=0) * 100
            lifecycle_pct.to_excel(writer, sheet_name="10_lifecycle_analysis")
            
            lifecycle_top = cohort_export.groupby('segment_c2')['lifecycle_stage'].agg(lambda x: x.mode()[0] if len(x.mode()) > 0 else 'Unknown').reset_index()
            lifecycle_top.columns = ['Segment', 'Most Common Stage']
            lifecycle_top.to_excel(writer, sheet_name="11_lifecycle_top_by_segment", index=False)
        
        # 12. Traffic Sources (using latest source only)
        if 'latest_source' in cohort_export.columns:
            latest_source_pct = cohort_export.groupby(['segment_c2', 'latest_source']).size().unstack(fill_value=0)
            latest_source_pct_norm = latest_source_pct.div(latest_source_pct.sum(axis=1), axis=0) * 100
            latest_source_pct_norm.to_excel(writer, sheet_name="12_traffic_sources")
        
        # 13. Likelihood to Close
        if 'likelihood_to_close' in cohort_export.columns:
            l2c_summary = cohort_export.groupby('segment_c2')['likelihood_to_close'].agg(['mean', 'median', 'std', 'min', 'max']).round(3)
            l2c_summary.to_excel(writer, sheet_name="13_likelihood_to_close")
        
        # 14-16. Closure Analysis
        if 'close_date' in cohort_export.columns:
            cohort_copy = cohort_export.copy()
            cohort_copy['is_closed'] = cohort_copy['close_date'].notna()
            
            closure_summary = cohort_copy.groupby('segment_c2').agg({
                'is_closed': ['sum', 'mean'],
                'days_to_close': ['mean', 'median', 'std']
            }).round(2)
            closure_summary.to_excel(writer, sheet_name="14_closure_rates")
            
            # TTC buckets
            if 'ttc_bucket' in cohort_export.columns:
                ttc_seg = cohort_export.groupby(['segment_c2', 'ttc_bucket']).size().unstack(fill_value=0)
                ttc_seg_pct = ttc_seg.div(ttc_seg.sum(axis=1), axis=0) * 100
                ttc_seg_pct.to_excel(writer, sheet_name="15_time_to_close_buckets")
                
                # By segment
                closure_by_segment = cohort_copy.groupby('segment_c2').agg({
                    'is_closed': ['sum', 'mean'],
                    'days_to_close': ['mean', 'median']
                }).round(2)
                closure_by_segment.to_excel(writer, sheet_name="16_closure_stats_by_segment")
        
        # 17. Closure by Geo
        if 'close_date' in cohort_export.columns and 'geo_tier' in cohort_export.columns:
            closure_by_geo = cohort_copy.groupby('geo_tier').agg({
                'is_closed': ['sum', 'mean'],
                'days_to_close': ['mean', 'median']
            }).round(2)
            closure_by_geo.to_excel(writer, sheet_name="17_closure_stats_by_geo")
        
        # 18-19. TTC Buckets by Segment and Geo
        if 'ttc_bucket' in cohort_export.columns:
            ttc_bucket_by_segment = cohort_export.groupby(['segment_c2', 'ttc_bucket']).size().unstack(fill_value=0)
            ttc_bucket_by_segment.to_excel(writer, sheet_name="18_ttc_buckets_by_segment")
            
            if 'geo_tier' in cohort_export.columns:
                ttc_bucket_by_geo = cohort_export.groupby(['geo_tier', 'ttc_bucket']).size().unstack(fill_value=0)
                ttc_bucket_by_geo.to_excel(writer, sheet_name="19_ttc_buckets_by_geo")
        
        # 20. Comprehensive Bucket Analysis
        if 'ttc_bucket' in cohort_export.columns:
            segment_bucket_df = cohort_export.groupby(['segment_c2', 'ttc_bucket']).size().reset_index(name='count')
            segment_bucket_df.to_excel(writer, sheet_name="20_comprehensive_bucket_by_segment", index=False)
    
    output.seek(0)
    return output.getvalue()

def render_cluster2(data):
    """Render Cluster 2 analysis interface"""
    
    # Get current geo configuration
    geo_config = get_geo_config()
    
    # Show current configuration at the top
    st.markdown("## 🌍 Cluster 2: Geography & Engagement Segmentation")
    
    col1, col2 = st.columns([3, 1])
    with col1:
        st.markdown(f"**Current Configuration:** 🏠 {geo_config['home_country']} | 📍 {geo_config['local_region']}")
    with col2:
        if st.button("⚙️ Change Settings", key="change_geo_settings"):
            st.info("👈 Use the Geographic Settings in the sidebar to change your home country and local region")
    
    # About this analysis
    with st.expander("ℹ️ About This Analysis", expanded=False):
        st.markdown(f"""
        ### 🎯 What This Cluster Does
        **Segments contacts by geography and engagement** into 6 actionable groups for targeted regional campaigns.
        
        ### 👥 Who Should Use This
        - **Regional Marketing Teams** - Tailor campaigns by geography
        - **Admissions Officers** - Plan visits and events by region
        - **International Recruitment** - Understand international vs domestic performance
        
        ### 🔑 Key Questions Answered
        - Do local contacts close faster than international ones?
        - Which states/countries have the highest engagement?
        - Should we invest more in international recruitment?
        - What's the optimal strategy for each geographic tier?
        
        ### 📊 Segments Defined (Current: {geo_config['home_country']}/{geo_config['local_region']})
        - **2A (Domestic Non-Local, High)** - High engagement from {geo_config['home_country']} outside {geo_config['local_region']}
        - **2B (Domestic Non-Local, Low)** - Low engagement from {geo_config['home_country']} outside {geo_config['local_region']}
        - **2C (International, High)** - High engagement from outside {geo_config['home_country']}
        - **2D (International, Low)** - Low engagement from outside {geo_config['home_country']}
        - **2E (Local, High)** - High engagement from {geo_config['local_region']}
        - **2F (Local, Low)** - Low engagement from {geo_config['local_region']}
        
        ### 💡 Example Insight
        *"2E (Local {geo_config['local_region']}, High) closes in 45 days on average vs 120 days for 2C (International)"*
        → **Action:** Prioritize local high-engagement contacts, create virtual events for international
        
        ### ⚙️ Dynamic Configuration
        This cluster adapts to YOUR geography! Change settings in the sidebar to analyze any country/region.
        """)
    
    st.markdown("---")
    
    if data is None:
        st.error("⚠️ Data not loaded.")
        return
    
    # Process data with geo config and cache busting
    # This ensures the cache refreshes when global filters change the data
    cache_key = f"c2_{len(data)}_{data['Record ID'].iloc[0] if 'Record ID' in data.columns else 'na'}"
    with st.spinner(f"Processing Cluster 2 data for {geo_config['home_country']}..."):
        cohort = process_cluster2_data(data, geo_config, cache_key)
    
    # Show contact count AFTER core filters (APREU + removing other/subscriber)
    if data is not None:
        active_filters = sum(1 for k in st.session_state.keys() if k.startswith('filter_'))
        if active_filters > 0:
            st.info(f"🔍 Analyzing {len(cohort):,} contacts after applying core filters (APREU, excluding 'other'/'subscriber') + global filters")
        else:
            st.info(f"📊 Analyzing {len(cohort):,} contacts after applying core filters (APREU, excluding 'other'/'subscriber')")
    
    if len(cohort) == 0:
        st.warning("No data available after filters.")
        return
    
    # Add cluster-specific filters
    with st.expander("🎛️ Cluster 2 Specific Filters", expanded=False):
        col1, col2, col3 = st.columns(3)
        
        with col1:
            # Segment filter
            available_segments = sorted(cohort['segment_c2'].unique())
            selected_segments = st.multiselect(
                "Filter by Segment (2A-2F):",
                options=available_segments,
                default=available_segments,
                help="Select segments to include"
            )
            
            # Lifecycle stage filter
            if 'lifecycle_stage' in cohort.columns:
                available_lifecycle = sorted(cohort['lifecycle_stage'].dropna().unique())
                selected_lifecycle = st.multiselect(
                    "Filter by Lifecycle Stage:",
                    options=available_lifecycle,
                    default=available_lifecycle,
                    help="Select lifecycle stages to include"
                )
            else:
                selected_lifecycle = None
        
        with col2:
            # Periodo de ingreso filter
            if 'periodo_ingreso' in cohort.columns:
                available_periodos = sorted(cohort['periodo_ingreso'].dropna().unique())
                selected_periodos = st.multiselect(
                    "Filter by Periodo de Ingreso:",
                    options=available_periodos,
                    default=available_periodos,
                    help="Select entry periods to include"
                )
            else:
                selected_periodos = None
            
            # Closure status filter
            closure_options = ["All", "Closed Only", "Open Only"]
            closure_filter = st.radio(
                "Closure Status:",
                options=closure_options,
                index=0,
                help="Filter by closure status"
            )
        
        with col3:
            # Geography tier filter
            available_tiers = sorted(cohort['geo_tier'].unique())
            selected_tiers = st.multiselect(
                "Filter by Geography Tier:",
                options=available_tiers,
                default=available_tiers,
                help="Select geographic tiers to include"
            )
            
            # Country filter (top countries)
            top_countries = cohort['country_any'].value_counts().head(20).index.tolist()
            selected_countries = st.multiselect(
                "Filter by Country (Top 20):",
                options=top_countries,
                default=top_countries,
                help="Select countries to include"
            )
        
        # Apply cluster-specific filters
        cohort_filtered = cohort[
            (cohort['segment_c2'].isin(selected_segments)) &
            (cohort['geo_tier'].isin(selected_tiers)) &
            (cohort['country_any'].isin(selected_countries))
        ]
        
        # Apply lifecycle filter
        if selected_lifecycle is not None and 'lifecycle_stage' in cohort.columns:
            cohort_filtered = cohort_filtered[cohort_filtered['lifecycle_stage'].isin(selected_lifecycle)]
        
        # Apply periodo de ingreso filter
        if selected_periodos is not None and 'periodo_ingreso' in cohort.columns:
            cohort_filtered = cohort_filtered[cohort_filtered['periodo_ingreso'].isin(selected_periodos)]
        
        # Apply closure status filter
        if closure_filter == "Closed Only":
            cohort_filtered = cohort_filtered[cohort_filtered['close_date'].notna()]
        elif closure_filter == "Open Only":
            cohort_filtered = cohort_filtered[cohort_filtered['close_date'].isna()]
        
        st.info(f"✅ Showing {len(cohort_filtered):,} of {len(cohort):,} contacts after cluster filters")
    
    # Use filtered cohort
    cohort = cohort_filtered
    
    # Export functionality
    with st.expander("📥 Export Data", expanded=False):
        st.markdown("**Download filtered data:**")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Export full cohort with notebook-standard columns
            row_cols = [
                # CORE IDENTIFICATION
                "contact_id",
                # MEMBERSHIP
                "segment_c2", "geo_tier", "segment_c2_action",
                # ENGAGEMENT
                "num_sessions", "num_pageviews", "forms_submitted",
                "pageviews_per_session", "forms_per_session", "forms_per_pageview",
                "engagement_score", "is_high_engager",
                "log_sessions", "log_pageviews", "log_forms",
                # OUTCOMES / FUNNEL
                "likelihood_to_close", "create_date", "close_date", "days_to_close", "ttc_bucket",
                # LIFECYCLE STAGE
                "lifecycle_stage",
                # GEOGRAPHY SIGNALS
                "country_any", "state_any", "city_any",
                "ip_country", "ip_state_region",
                "prep_country_bpm", "prep_state_bpm", "prep_city_bpm", "prep_school_bpm",
                # ACADEMIC INFO
                "periodo_ingreso", "periodo_admision",
                # ATTRIBUTION SOURCES
                "original_source", "original_source_d1", "original_source_d2",
                "canal_de_adquisicion", "latest_source", "last_referrer"
            ]
            
            # Filter to existing columns
            row_cols = [c for c in row_cols if c in cohort.columns]
            df_export = cohort[row_cols].copy()
            
            # Add calculated display fields (matching notebook)
            if "likelihood_to_close" in df_export.columns:
                df_export["likelihood_to_close_pct"] = (df_export["likelihood_to_close"] * 100).round(1)
            
            # Format dates
            if "create_date" in df_export.columns:
                df_export["create_date"] = pd.to_datetime(df_export["create_date"]).dt.strftime("%Y-%m-%d").fillna("unknown")
            if "close_date" in df_export.columns:
                df_export["close_date"] = pd.to_datetime(df_export["close_date"]).dt.strftime("%Y-%m-%d").fillna("unknown")
            
            csv_data = df_export.to_csv(index=False, encoding='utf-8-sig')
            st.download_button(
                label="📄 Download Full Data (CSV)",
                data=csv_data.encode('utf-8'),
                file_name=f"cluster2_full_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv",
                use_container_width=True
            )
        
        with col2:
            # Export comprehensive XLSX workbook
            with st.spinner("Generating comprehensive Excel workbook..."):
                xlsx_data = create_cluster2_xlsx_export(cohort)
                st.download_button(
                    label="📊 Download Comprehensive Workbook (XLSX) - 20+ Sheets",
                    data=xlsx_data,
                    file_name=f"cluster2_summary_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    use_container_width=True,
                    help="Comprehensive analysis workbook with 20+ sheets: executive summary, segment performance, geography, engagement, lifecycle, closure stats, and more!"
                )
    
    # Create tabs
    tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
        "📊 Overview", "🎯 Segment Analysis", "🗺️ Geography Analysis",
        "💰 Business Outcomes", "⚡ Fast/Slow Closers", "🔬 Performance Benchmarks", "🔍 Contact Lookup"
    ])
    
    with tab1:
        render_overview_tab_c2(cohort)
    
    with tab2:
        render_segment_analysis_tab_c2(cohort)
    
    with tab3:
        render_geography_analysis_tab(cohort)
    
    with tab4:
        render_outcomes_tab_c2(cohort)
    
    with tab5:
        render_fast_slow_closers_c2(cohort)
    
    with tab6:
        render_performance_benchmarks_c2(cohort)
    
    with tab7:
        render_contact_lookup_tab_c2(cohort)

def render_overview_tab_c2(cohort):
    """Render overview tab for Cluster 2"""
    st.markdown("### 📊 Executive Summary")
    
    # Key metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Contacts", f"{len(cohort):,}")
    
    with col2:
        local_count = (cohort['geo_tier'] == 'local').sum()
        st.metric("Local (QRO)", f"{local_count:,}")
    
    with col3:
        domestic_count = (cohort['geo_tier'] == 'domestic_non_local').sum()
        st.metric("Domestic (non-QRO)", f"{domestic_count:,}")
    
    with col4:
        intl_count = (cohort['geo_tier'] == 'international').sum()
        st.metric("International", f"{intl_count:,}")
    
    st.markdown("---")
    
    # Segment distribution
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### Segment Distribution (2A-2F)")
        seg_counts = cohort['segment_c2'].value_counts()
        fig = px.pie(
            values=seg_counts.values,
            names=seg_counts.index,
            title="2A-2F Segment Distribution",
            hole=0.4,
            color_discrete_sequence=px.colors.qualitative.Set3
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.markdown("#### Geography Tier Distribution")
        geo_counts = cohort['geo_tier'].value_counts()
        fig = px.pie(
            values=geo_counts.values,
            names=geo_counts.index,
            title="Geographic Distribution",
            hole=0.4,
            color_discrete_sequence=px.colors.qualitative.Pastel
        )
        st.plotly_chart(fig, use_container_width=True)
    
    # Segment summary table - WITHOUT likelihood to close
    st.markdown("#### Segment Performance Summary")
    
    segment_summary = cohort.groupby('segment_c2').agg({
        'contact_id': 'count',
        'num_sessions': 'mean',
        'num_pageviews': 'mean',
        'forms_submitted': 'mean',
        'engagement_score': 'mean',
        'close_date': lambda x: x.notna().sum()
    }).round(2)
    
    segment_summary.columns = ['Contacts', 'Avg Sessions', 'Avg Pageviews', 
                               'Avg Forms', 'Avg Engagement', 'Closed']
    segment_summary['Close Rate %'] = (
        segment_summary['Closed'] / segment_summary['Contacts'] * 100
    ).round(1)
    
    st.dataframe(segment_summary, use_container_width=True)

def render_segment_analysis_tab_c2(cohort):
    """Render segment analysis tab"""
    st.markdown("### 🎯 2A-2F Segment Deep Dive")
    
    # Segment selector
    segments = sorted(cohort['segment_c2'].unique())
    selected_segment = st.selectbox("Select Segment for Details:", segments)
    
    seg_data = cohort[cohort['segment_c2'] == selected_segment]
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Total Contacts", f"{len(seg_data):,}")
    
    with col2:
        close_rate = calculate_close_rate(seg_data)
        st.metric("Close Rate", f"{close_rate:.1f}%")
    
    with col3:
        avg_eng = seg_data['engagement_score'].mean()
        st.metric("Avg Engagement", f"{avg_eng:.2f}")
    
    st.markdown("---")
    
    # Action recommendation
    if 'segment_c2_action' in seg_data.columns:
        action = seg_data['segment_c2_action'].iloc[0]
        st.info(f"**Recommended Action:** {action}")
    
    # Engagement distribution
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### Engagement Score Distribution")
        fig = px.histogram(
            seg_data, x='engagement_score',
            title=f"Engagement Score Distribution - {selected_segment}",
            nbins=30,
            color_discrete_sequence=['#3498db']
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.markdown("#### Sessions Distribution")
        fig = px.histogram(
            seg_data, x='num_sessions',
            title=f"Sessions Distribution - {selected_segment}",
            nbins=20,
            color_discrete_sequence=['#e74c3c']
        )
        st.plotly_chart(fig, use_container_width=True)
    
    # Lifecycle distribution
    if 'lifecycle_stage' in seg_data.columns:
        st.markdown("#### Lifecycle Stage Distribution")
        lifecycle_counts = seg_data['lifecycle_stage'].value_counts().head(10)
        fig = px.bar(
            x=lifecycle_counts.index,
            y=lifecycle_counts.values,
            title=f"Top Lifecycle Stages - {selected_segment}",
            labels={'x': 'Lifecycle Stage', 'y': 'Count'},
            color=lifecycle_counts.values,
            color_continuous_scale='Viridis'
        )
        st.plotly_chart(fig, use_container_width=True)

def render_geography_analysis_tab(cohort):
    """Render geography analysis tab"""
    st.markdown("### 🗺️ Geographic Distribution Analysis")
    
    # Top countries
    st.markdown("#### Top Countries")
    country_counts = cohort['country_any'].value_counts().head(15)
    country_counts = country_counts[country_counts.index != 'unknown']
    
    fig = px.bar(
        x=country_counts.values,
        y=country_counts.index,
        orientation='h',
        title="Top 15 Countries",
        labels={'x': 'Contacts', 'y': 'Country'},
        color=country_counts.values,
        color_continuous_scale='Blues'
    )
    fig.update_layout(showlegend=False, height=500)
    st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("---")
    
    # Top Mexican states (for domestic contacts)
    st.markdown("#### Top Mexican States (Domestic Contacts)")
    domestic = cohort[cohort['geo_tier'].isin(['local', 'domestic_non_local'])]
    
    if len(domestic) > 0:
        state_counts = domestic['state_any'].value_counts().head(15)
        state_counts = state_counts[state_counts.index != 'unknown']
        
        fig = px.bar(
            x=state_counts.values,
            y=state_counts.index,
            orientation='h',
            title="Top 15 Mexican States",
            labels={'x': 'Contacts', 'y': 'State'},
            color=state_counts.values,
            color_continuous_scale='Greens'
        )
        fig.update_layout(showlegend=False, height=500)
        st.plotly_chart(fig, use_container_width=True)
        
        # State performance metrics
        st.markdown("#### State Performance (Top 10 by Volume)")
        
        state_performance = domestic.groupby('state_any').agg({
            'contact_id': 'count',
            'engagement_score': 'mean',
            'close_date': lambda x: x.notna().sum()
        })
        state_performance.columns = ['Total', 'Avg Engagement', 'Closed']
        state_performance['Close Rate %'] = (
            state_performance['Closed'] / state_performance['Total'] * 100
        ).round(1)
        
        state_performance = state_performance[state_performance.index != 'unknown']
        state_performance = state_performance.sort_values('Total', ascending=False).head(10)
        
        st.dataframe(state_performance, use_container_width=True)
    else:
        st.info("No domestic contacts to analyze.")

def render_outcomes_tab_c2(cohort):
    """Render business outcomes tab"""
    st.markdown("### 💰 Business Outcomes by Geography")
    
    # Lifecycle Stage Analysis
    st.markdown("#### 🔄 Lifecycle Stage Distribution")
    
    if 'lifecycle_stage' in cohort.columns:
        lifecycle_counts = cohort['lifecycle_stage'].value_counts().head(10)
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            fig = px.bar(
                x=lifecycle_counts.values,
                y=lifecycle_counts.index,
                orientation='h',
                title="Top 10 Lifecycle Stages",
                labels={'x': 'Contacts', 'y': 'Lifecycle Stage'},
                color=lifecycle_counts.values,
                color_continuous_scale='Viridis'
            )
            fig.update_layout(showlegend=False, height=400)
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.markdown("**Stage Distribution:**")
            for stage, count in lifecycle_counts.head(5).items():
                pct = (count / len(cohort) * 100)
                st.metric(stage, f"{count:,}", delta=f"{pct:.1f}%")
        
        # Lifecycle by segment
        st.markdown("**Lifecycle Stage by Segment:**")
        
        lifecycle_by_segment = pd.crosstab(
            cohort['lifecycle_stage'],
            cohort['segment_c2'],
            normalize='columns'
        ) * 100
        
        # Show top 8 stages
        top_stages = cohort['lifecycle_stage'].value_counts().head(8).index
        lifecycle_filtered = lifecycle_by_segment.loc[lifecycle_by_segment.index.isin(top_stages)]
        
        st.dataframe(lifecycle_filtered.round(1), use_container_width=True)
        
        st.markdown("---")
    else:
        st.info("Lifecycle stage data not available")
    
    # Close rates by segment
    st.markdown("#### Close Rate Comparison")
    
    segment_close_rates = []
    for seg in sorted(cohort['segment_c2'].unique()):
        seg_data = cohort[cohort['segment_c2'] == seg]
        close_rate = calculate_close_rate(seg_data)
        segment_close_rates.append({'Segment': seg, 'Close Rate %': close_rate})
    
    close_rate_df = pd.DataFrame(segment_close_rates)
    
    fig = px.bar(
        close_rate_df, x='Segment', y='Close Rate %',
        title="Close Rate by Segment",
        color='Close Rate %',
        color_continuous_scale='RdYlGn',
        text='Close Rate %'
    )
    fig.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
    st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("---")
    
    # Time to close analysis
    if 'ttc_bucket' in cohort.columns:
        st.markdown("#### Time-to-Close Analysis")
        
        ttc_dist = pd.crosstab(
            cohort['segment_c2'],
            cohort['ttc_bucket'],
            normalize='index'
        ) * 100
        
        bucket_order = ['Early (≤30 days)', 'Medium (31-60 days)', 'Late (61-120 days)', 
                       'Very Late (>120 days)', 'Still Open']
        ttc_dist = ttc_dist[[col for col in bucket_order if col in ttc_dist.columns]]
        
        fig = px.bar(
            ttc_dist,
            barmode='stack',
            title="Time-to-Close Distribution by Segment (%)",
            labels={'value': 'Percentage', 'variable': 'TTC Bucket'},
            color_discrete_sequence=['#2ecc71', '#f39c12', '#e67e22', '#e74c3c', '#95a5a6']
        )
        st.plotly_chart(fig, use_container_width=True)
    
    # Average days to close by geography tier
    if 'days_to_close' in cohort.columns:
        st.markdown("#### Average Days to Close by Geography")
        
        closed_cohort = cohort[cohort['days_to_close'].notna()]
        if len(closed_cohort) > 0:
            geo_days = closed_cohort.groupby('geo_tier')['days_to_close'].agg(['mean', 'median', 'count'])
            geo_days.columns = ['Avg Days', 'Median Days', 'Closed Count']
            geo_days = geo_days.round(1)
            
            st.dataframe(geo_days, use_container_width=True)

def render_fast_slow_closers_c2(cohort):
    """Render fast/slow closers analysis for Cluster 2"""
    st.markdown("### ⚡ Fast vs Slow Closers Analysis")
    st.markdown("Identify which Segment × Geography combinations close fastest")
    
    # Filter to closed contacts
    closed = cohort[cohort['close_date'].notna()].copy()
    
    if len(closed) == 0:
        st.warning("No closed contacts available for analysis.")
        return
    
    st.markdown(f"**Analyzing {len(closed):,} closed contacts**")
    
    # Define fast and slow
    fast_threshold = 60
    slow_threshold = 180
    
    closed['closure_speed'] = closed['days_to_close'].apply(
        lambda x: 'Fast (≤60 days)' if x <= fast_threshold 
        else ('Slow (>180 days)' if x > slow_threshold else 'Medium')
    )
    
    col1, col2, col3 = st.columns(3)
    with col1:
        fast_count = (closed['closure_speed'] == 'Fast (≤60 days)').sum()
        fast_pct = (fast_count / len(closed) * 100)
        st.metric("Fast Closers", f"{fast_count:,}", delta=f"{fast_pct:.1f}%")
    
    with col2:
        medium_count = (closed['closure_speed'] == 'Medium').sum()
        medium_pct = (medium_count / len(closed) * 100)
        st.metric("Medium Closers", f"{medium_count:,}", delta=f"{medium_pct:.1f}%")
    
    with col3:
        slow_count = (closed['closure_speed'] == 'Slow (>180 days)').sum()
        slow_pct = (slow_count / len(closed) * 100)
        st.metric("Slow Closers", f"{slow_count:,}", delta=f"{slow_pct:.1f}%")
    
    st.markdown("---")
    
    # Fast closers: Segment × Geography analysis
    st.markdown("#### ⚡ Fast Closers (≤60 days): Segment × Geography")
    st.markdown("Which segment + geography combinations close fastest?")
    
    fast_closers = closed[closed['closure_speed'] == 'Fast (≤60 days)']
    
    if len(fast_closers) > 0:
        # Create cross-tab
        fast_crosstab = pd.crosstab(
            fast_closers['segment_c2'],
            fast_closers['geo_tier'],
            margins=True,
            margins_name='Total'
        )
        
        st.markdown("**Counts:**")
        st.dataframe(fast_crosstab, use_container_width=True)
        
        # Heatmap
        try:
            fig = px.imshow(
                fast_crosstab.iloc[:-1, :-1],  # Exclude margins
                labels=dict(x="Geography", y="Segment", color="Count"),
                title="Fast Closers Heatmap: Segment × Geography",
                color_continuous_scale='Greens',
                aspect="auto"
            )
            st.plotly_chart(fig, use_container_width=True)
        except:
            pass
    else:
        st.info("No fast closers in this dataset.")
    
    st.markdown("---")
    
    # Slow closers: Segment × Geography analysis
    st.markdown("#### 🐌 Slow Closers (>180 days): Segment × Geography")
    st.markdown("Which combinations need more attention?")
    
    slow_closers = closed[closed['closure_speed'] == 'Slow (>180 days)']
    
    if len(slow_closers) > 0:
        # Create cross-tab
        slow_crosstab = pd.crosstab(
            slow_closers['segment_c2'],
            slow_closers['geo_tier'],
            margins=True,
            margins_name='Total'
        )
        
        st.markdown("**Counts:**")
        st.dataframe(slow_crosstab, use_container_width=True)
        
        # Heatmap
        try:
            fig = px.imshow(
                slow_crosstab.iloc[:-1, :-1],  # Exclude margins
                labels=dict(x="Geography", y="Segment", color="Count"),
                title="Slow Closers Heatmap: Segment × Geography",
                color_continuous_scale='Reds',
                aspect="auto"
            )
            st.plotly_chart(fig, use_container_width=True)
        except:
            pass
    else:
        st.info("No slow closers in this dataset.")
    
    st.markdown("---")
    
    # Insights
    st.markdown("#### 💡 Key Insights")
    
    insights = []
    
    if len(fast_closers) > 0:
        # Best performing combination
        fast_by_combo = fast_closers.groupby(['segment_c2', 'geo_tier']).size()
        if len(fast_by_combo) > 0:
            best_combo = fast_by_combo.idxmax()
            best_count = fast_by_combo.max()
            insights.append(f"✅ **Best Fast Closer Combination:** {best_combo[0]} + {best_combo[1]} ({best_count} contacts)")
    
    if len(slow_closers) > 0:
        # Worst performing combination
        slow_by_combo = slow_closers.groupby(['segment_c2', 'geo_tier']).size()
        if len(slow_by_combo) > 0:
            worst_combo = slow_by_combo.idxmax()
            worst_count = slow_by_combo.max()
            insights.append(f"⚠️ **Most Common Slow Closer Combination:** {worst_combo[0]} + {worst_combo[1]} ({worst_count} contacts)")
    
    # Overall ratio
    if len(fast_closers) > 0 and len(slow_closers) > 0:
        ratio = len(fast_closers) / len(slow_closers)
        insights.append(f"📊 **Fast/Slow Ratio:** {ratio:.2f}x")
    
    if insights:
        for insight in insights:
            st.markdown(insight)
    else:
        st.info("Not enough data for insights")

def render_performance_benchmarks_c2(cohort):
    """Render performance benchmarks tab for Cluster 2"""
    st.markdown("### 🔬 Performance Benchmarks & Geography Analysis")
    st.markdown("Compare segments and geographies against key performance indicators")
    
    st.markdown("---")
    
    # Benchmark metrics by segment
    st.markdown("#### 📊 Key Performance Indicators by Segment")
    
    benchmark_metrics = cohort.groupby('segment_c2').agg({
        'contact_id': 'count',
        'num_sessions': ['mean', 'median', 'std'],
        'num_pageviews': ['mean', 'median', 'std'],
        'forms_submitted': ['mean', 'median', 'std'],
        'engagement_score': ['mean', 'median', 'std'],
        'close_date': lambda x: x.notna().sum()
    }).round(2)
    
    benchmark_metrics.columns = ['_'.join(col).strip('_') for col in benchmark_metrics.columns.values]
    benchmark_metrics['close_rate_pct'] = (benchmark_metrics['close_date_<lambda>'] / benchmark_metrics['contact_id_count'] * 100).round(1)
    
    st.dataframe(benchmark_metrics, use_container_width=True)
    
    st.markdown("---")
    
    # Geography tier performance
    st.markdown("#### 🗺️ Performance by Geography Tier")
    
    geo_performance = cohort.groupby('geo_tier').agg({
        'contact_id': 'count',
        'num_sessions': 'mean',
        'engagement_score': 'mean',
        'close_date': lambda x: x.notna().sum()
    }).round(2)
    
    geo_performance.columns = ['Count', 'Avg Sessions', 'Avg Engagement', 'Closed']
    geo_performance['Close Rate %'] = (geo_performance['Closed'] / geo_performance['Count'] * 100).round(1)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.dataframe(geo_performance, use_container_width=True)
    
    with col2:
        fig = px.bar(
            x=geo_performance.index,
            y=geo_performance['Close Rate %'],
            title="Close Rate by Geography Tier",
            labels={'x': 'Geography Tier', 'y': 'Close Rate %'},
            color=geo_performance['Close Rate %'],
            color_continuous_scale='RdYlGn'
        )
        st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("---")
    
    # Country performance (top countries)
    st.markdown("#### 🌍 Top Country Performance")
    
    top_countries = cohort['country_any'].value_counts().head(15).index
    country_data = cohort[cohort['country_any'].isin(top_countries)]
    
    country_performance = country_data.groupby('country_any').agg({
        'contact_id': 'count',
        'num_sessions': 'mean',
        'engagement_score': 'mean',
        'close_date': lambda x: x.notna().sum()
    }).round(2)
    
    country_performance.columns = ['Count', 'Avg Sessions', 'Avg Engagement', 'Closed']
    country_performance['Close Rate %'] = (country_performance['Closed'] / country_performance['Count'] * 100).round(1)
    country_performance = country_performance.sort_values('Close Rate %', ascending=False)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.dataframe(country_performance, use_container_width=True)
    
    with col2:
        fig = px.bar(
            x=country_performance.index,
            y=country_performance['Close Rate %'],
            title="Close Rate by Country (Top 15)",
            labels={'x': 'Country', 'y': 'Close Rate %'},
            color=country_performance['Close Rate %'],
            color_continuous_scale='Viridis'
        )
        fig.update_layout(xaxis_tickangle=-45)
        st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("---")
    
    # Engagement distribution by geography
    st.markdown("#### 📈 Engagement Distribution by Geography Tier")
    
    fig = px.box(
        cohort, x='geo_tier', y='engagement_score',
        color='geo_tier',
        title="Engagement Score Distribution by Geography Tier",
        labels={'geo_tier': 'Geography Tier', 'engagement_score': 'Engagement Score'}
    )
    st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("---")
    
    # Segment × Geography heatmap
    st.markdown("#### 🔥 Segment × Geography Performance Heatmap")
    
    heatmap_data = cohort.groupby(['segment_c2', 'geo_tier']).size().reset_index(name='count')
    heatmap_pivot = heatmap_data.pivot(index='segment_c2', columns='geo_tier', values='count').fillna(0)
    
    fig = px.imshow(
        heatmap_pivot,
        labels=dict(x="Geography Tier", y="Segment", color="Contacts"),
        title="Contact Distribution: Segment × Geography Tier",
        color_continuous_scale='Blues',
        aspect="auto"
    )
    st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("---")
    
    # Time to close by geography
    if 'days_to_close' in cohort.columns:
        st.markdown("#### ⏱️ Time-to-Close Analysis by Geography")
        
        closed_cohort = cohort[cohort['days_to_close'].notna()]
        if len(closed_cohort) > 0:
            ttc_by_geo = closed_cohort.groupby('geo_tier')['days_to_close'].agg(['mean', 'median', 'count']).round(1)
            ttc_by_geo.columns = ['Avg Days', 'Median Days', 'Closed Count']
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.dataframe(ttc_by_geo, use_container_width=True)
            
            with col2:
                fig = px.bar(
                    x=ttc_by_geo.index,
                    y=ttc_by_geo['Avg Days'],
                    title="Average Days to Close by Geography Tier",
                    labels={'x': 'Geography Tier', 'y': 'Avg Days to Close'},
                    color=ttc_by_geo['Avg Days'],
                    color_continuous_scale='Reds'
                )
                st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("---")
    
    # Key insights
    st.markdown("#### 💡 Performance Insights")
    
    insights = []
    
    # Best performing segment
    if len(benchmark_metrics) > 0:
        best_segment = benchmark_metrics['close_rate_pct'].idxmax()
        best_rate = benchmark_metrics['close_rate_pct'].max()
        insights.append(f"🏆 **Best Performing Segment:** {best_segment} ({best_rate:.1f}% close rate)")
    
    # Best performing geography
    if len(geo_performance) > 0:
        best_geo = geo_performance['Close Rate %'].idxmax()
        best_geo_rate = geo_performance['Close Rate %'].max()
        insights.append(f"🌍 **Best Performing Geography:** {best_geo} ({best_geo_rate:.1f}% close rate)")
    
    # Best performing country
    if len(country_performance) > 0:
        best_country = country_performance['Close Rate %'].idxmax()
        best_country_rate = country_performance['Close Rate %'].max()
        insights.append(f"🎯 **Best Performing Country:** {best_country} ({best_country_rate:.1f}% close rate)")
    
    # Geography diversity
    unique_countries = cohort['country_any'].nunique()
    unique_states = cohort['state_any'].nunique() if 'state_any' in cohort.columns else 0
    insights.append(f"🌐 **Geographic Reach:** {unique_countries} countries, {unique_states} states/regions")
    
    if insights:
        for insight in insights:
            st.markdown(insight)
    else:
        st.info("Not enough data for insights")

def render_contact_lookup_tab_c2(cohort):
    """Render contact lookup tab"""
    st.markdown("### 🔍 Individual Contact Lookup")
    
    if 'contact_id' not in cohort.columns:
        st.warning("Contact ID not available in dataset.")
        return
    
    contact_id = st.text_input("Enter Contact ID:", placeholder="e.g., 12345")
    
    if contact_id:
        contact_id_str = str(contact_id).strip()
        matches = cohort[cohort['contact_id'].astype(str) == contact_id_str]
        
        if len(matches) == 0:
            st.error(f"No contact found with ID: {contact_id}")
        else:
            contact = matches.iloc[0]
            
            st.markdown("#### Contact Profile")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.markdown("**Identification**")
                st.write(f"**Contact ID:** {contact.get('contact_id', 'N/A')}")
                st.write(f"**Segment:** {contact.get('segment_c2', 'N/A')}")
                st.write(f"**Geography Tier:** {contact.get('geo_tier', 'N/A')}")
                st.write(f"**Action:** {contact.get('segment_c2_action', 'N/A')}")
            
            with col2:
                st.markdown("**Geography**")
                st.write(f"**Country:** {contact.get('country_any', 'N/A')}")
                st.write(f"**State:** {contact.get('state_any', 'N/A')}")
                st.write(f"**City:** {contact.get('city_any', 'N/A')}")
            
            with col3:
                st.markdown("**Engagement**")
                st.write(f"**Sessions:** {int(contact.get('num_sessions', 0)):,}")
                st.write(f"**Pageviews:** {int(contact.get('num_pageviews', 0)):,}")
                st.write(f"**Forms:** {int(contact.get('forms_submitted', 0)):,}")
                st.write(f"**Engagement Score:** {contact.get('engagement_score', 0):.2f}")
                st.write(f"**High Engager:** {'Yes' if contact.get('is_high_engager') else 'No'}")
            
            st.markdown("---")
            st.markdown("#### Business Outcomes")
            
            col1, col2 = st.columns(2)
            
            with col1:
                is_closed = "Yes" if pd.notna(contact.get('close_date')) else "No"
                st.write(f"**Closed:** {is_closed}")
                
                if 'lifecycle_stage' in contact.index:
                    st.write(f"**Lifecycle Stage:** {contact.get('lifecycle_stage', 'N/A')}")
                
                if 'periodo_ingreso' in contact.index:
                    st.write(f"**Periodo de Ingreso:** {contact.get('periodo_ingreso', 'N/A')}")
            
            with col2:
                if pd.notna(contact.get('days_to_close')):
                    st.write(f"**Days to Close:** {contact.get('days_to_close', 0):.0f}")
                    st.write(f"**TTC Bucket:** {contact.get('ttc_bucket', 'N/A')}")
                
                # Likelihood is still available in data but not prominently displayed
                if 'likelihood_pct' in contact.index and pd.notna(contact.get('likelihood_pct')):
                    st.write(f"**Likelihood to Close:** {contact.get('likelihood_pct', 0):.1f}%")

