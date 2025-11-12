"""
Utility functions shared across all clusters
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path
import unicodedata
import os
from io import BytesIO

# Try to import Google Cloud Storage (optional, for Cloud Storage support)
try:
    from google.cloud import storage
    GCS_AVAILABLE = True
except ImportError:
    GCS_AVAILABLE = False

def upload_to_gcs(uploaded_file, bucket_name, blob_name):
    """Upload file to Google Cloud Storage"""
    if not GCS_AVAILABLE:
        raise ImportError("google-cloud-storage no está instalado. Instálalo con: pip install google-cloud-storage")
    
    try:
        client = storage.Client()
        bucket = client.bucket(bucket_name)
        blob = bucket.blob(blob_name)
        
        # Upload file
        uploaded_file.seek(0)  # Reset file pointer
        blob.upload_from_file(uploaded_file, content_type='text/csv')
        
        return True
    except Exception as e:
        raise Exception(f"Error subiendo a Cloud Storage: {e}")

@st.cache_data
def load_data_from_gcs(bucket_name, blob_name):
    """Load data from Google Cloud Storage"""
    if not GCS_AVAILABLE:
        raise ImportError("google-cloud-storage no está instalado. Instálalo con: pip install google-cloud-storage")
    
    try:
        client = storage.Client()
        bucket = client.bucket(bucket_name)
        blob = bucket.blob(blob_name)
        
        # Download to memory
        file_bytes = blob.download_as_bytes()
        
        # Read CSV from bytes
        df = pd.read_csv(BytesIO(file_bytes), low_memory=True, dtype_backend='pyarrow')
        return df
    except Exception as e:
        raise Exception(f"Error cargando desde Cloud Storage: {e}")

@st.cache_data
def load_data(uploaded_file=None, gcs_bucket=None, gcs_path=None):
    """Load the main contacts dataset from uploaded file, Cloud Storage, or default file"""
    # Priority: GCS > uploaded file > default file
    if gcs_bucket and gcs_path:
        # Load from Cloud Storage
        df = load_data_from_gcs(gcs_bucket, gcs_path)
    elif uploaded_file is not None:
        # Load from uploaded file with memory optimization
        df = pd.read_csv(uploaded_file, low_memory=True, dtype_backend='pyarrow')
    else:
        # Load from default file (relative to this file's location)
        # This works regardless of where streamlit is run from
        current_file = Path(__file__).resolve()
        project_root = current_file.parent.parent  # Go up from app/ to SettingUp/
        file_path = project_root / "data" / "raw" / "contacts_campus_Qro_.csv"
        
        # Try multiple possible locations for deployment
        possible_paths = [
            file_path,  # Original path
            Path("data/raw/contacts_campus_Qro_.csv"),  # Relative to current directory
            Path("/app/data/raw/contacts_campus_Qro_.csv"),  # Railway deployment path
            Path("contacts_campus_Qro_.csv"),  # Same directory
        ]
        
        file_found = False
        for path in possible_paths:
            if path.exists():
                file_path = path
                file_found = True
                break
        
        if not file_found:
            raise FileNotFoundError(f"Data file not found. Tried: {[str(p) for p in possible_paths]}")
        
        df = pd.read_csv(file_path, low_memory=True, dtype_backend='pyarrow')
    
    # Convert HubSpot timestamps
    date_cols = ['Create Date', 'Close Date', 'First Conversion Date', 'Recent Conversion Date']
    for col in date_cols:
        if col in df.columns:
            df[col] = convert_hubspot_timestamp(df[col])
    
    return df

def validate_data(df):
    """Validate that the uploaded data has required columns"""
    required_columns = {
        'basic': ['Record ID'],
        'cluster1': ['Original Source', 'Number of Sessions'],
        'cluster2': ['IP Country', 'Number of Sessions'],
        'cluster3': ['Actividades de promoción APREU', 'Number of Sessions']
    }
    
    validation_results = {
        'is_valid': True,
        'missing_basic': [],
        'cluster1_ready': True,
        'cluster2_ready': True,
        'cluster3_ready': True,
        'warnings': []
    }
    
    # Check basic required columns
    for col in required_columns['basic']:
        if col not in df.columns:
            validation_results['is_valid'] = False
            validation_results['missing_basic'].append(col)
    
    # Check cluster-specific columns (warnings only)
    for col in required_columns['cluster1']:
        if col not in df.columns:
            validation_results['cluster1_ready'] = False
            validation_results['warnings'].append(f"Cluster 1 puede no funcionar: falta '{col}'")
    
    for col in required_columns['cluster2']:
        if col not in df.columns:
            validation_results['cluster2_ready'] = False
            validation_results['warnings'].append(f"Cluster 2 puede no funcionar: falta '{col}'")
    
    for col in required_columns['cluster3']:
        if col not in df.columns:
            validation_results['cluster3_ready'] = False
            validation_results['warnings'].append(f"Cluster 3 puede no funcionar: falta '{col}'")
    
    return validation_results

def apply_global_filters(df):
    """Apply global filters from session state to dataframe"""
    if df is None or len(df) == 0:
        return df, []
    
    filtered_df = df.copy()
    filters_applied = []
    
    # Periodo de ingreso filter
    if 'filter_periodos' in st.session_state and len(st.session_state['filter_periodos']) > 0:
        # Look for periodo column
        periodo_fields = [
            'Periodo de ingreso a licenciatura (MQL)', 
            'Periodo de ingreso',
            'periodo_de_ingreso',
            'PERIODO DE INGRESO'
        ]
        
        periodo_col = None
        for field in periodo_fields:
            if field in filtered_df.columns:
                periodo_col = field
                break
        
        if periodo_col:
            # Convert periodo to readable format
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
            
            # Apply hist_latest and convert
            periodo_latest = filtered_df[periodo_col].apply(hist_latest)
            periodo_readable = periodo_latest.apply(convert_periodo)
            
            # Filter to selected periods
            filtered_df = filtered_df[periodo_readable.isin(st.session_state['filter_periodos'])]
            
            periodo_str = ', '.join(st.session_state['filter_periodos'][:2])
            if len(st.session_state['filter_periodos']) > 2:
                periodo_str += f" (+{len(st.session_state['filter_periodos'])-2} more)"
            filters_applied.append(f"Periodo: {periodo_str}")
    
    # Closure status filter (apply hist_latest to get actual close date)
    if 'filter_closure_status' in st.session_state and st.session_state['filter_closure_status'] != "All Contacts":
        close_date_col = 'close_date' if 'close_date' in filtered_df.columns else 'Close Date'
        if close_date_col in filtered_df.columns:
            # Apply hist_latest to extract the actual latest close date value
            close_date_latest = filtered_df[close_date_col].apply(hist_latest)
            if st.session_state['filter_closure_status'] == "Closed Only":
                filtered_df = filtered_df[close_date_latest.notna()]
                filters_applied.append("Closed Only")
            elif st.session_state['filter_closure_status'] == "Open Only":
                filtered_df = filtered_df[close_date_latest.isna()]
                filters_applied.append("Open Only")
    
    # Lifecycle stage filter (using LATEST value only)
    if 'filter_lifecycle_stages' in st.session_state and len(st.session_state['filter_lifecycle_stages']) > 0:
        lifecycle_col = 'lifecycle_stage' if 'lifecycle_stage' in filtered_df.columns else 'Lifecycle Stage'
        if lifecycle_col in filtered_df.columns:
            # Apply hist_latest to get latest value
            lifecycle_latest = filtered_df[lifecycle_col].apply(hist_latest)
            filtered_df = filtered_df[lifecycle_latest.isin(st.session_state['filter_lifecycle_stages'])]
            
            stages_str = ', '.join(st.session_state['filter_lifecycle_stages'][:3])
            if len(st.session_state['filter_lifecycle_stages']) > 3:
                stages_str += '...'
            filters_applied.append(f"Lifecycle (latest): {stages_str}")
    
    return filtered_df, filters_applied

def convert_hubspot_timestamp(series):
    """Convert HubSpot timestamps (milliseconds) to datetime"""
    def convert_single(val):
        if pd.isna(val):
            return pd.NaT
        try:
            timestamp_ms = int(float(str(val).strip()))
            return pd.to_datetime(timestamp_ms, unit='ms')
        except (ValueError, TypeError):
            return pd.NaT
    
    return series.apply(convert_single)

def hist_latest(val):
    """Extract the latest value from HubSpot history string (// delimited)"""
    if pd.isna(val):
        return np.nan
    s = str(val).strip()
    if s == "":  # Handle empty strings
        return np.nan
    if "//" in s:
        parts = [p.strip() for p in s.split("//") if p.strip() != ""]
        if not parts:
            return np.nan
        return parts[-1]
    return s

def hist_all(val):
    """Parse HubSpot history string and return ALL values as a list"""
    if pd.isna(val):
        return []
    s = str(val).strip()
    if "//" in s:
        parts = [p.strip() for p in s.split("//") if p.strip() != ""]
        return [p for p in parts if p.lower() not in ['nan', 'none', '']]
    return [s] if s.lower() not in ['nan', 'none', ''] else []

def hist_concat_text(val):
    """Concatenate all historical text values with space separator"""
    values = hist_all(val)
    return " ".join(values)

def normalize_text(s):
    """Normalize text by removing accents and converting to lowercase"""
    if pd.isna(s):
        return "unknown"
    s = str(s).strip()
    if s == "":
        return "unknown"
    s = unicodedata.normalize("NFKD", s)
    s = "".join(ch for ch in s if not unicodedata.combining(ch))
    return s.lower()

def display_metrics(metrics_dict, columns=4):
    """Display metrics in a grid layout"""
    cols = st.columns(columns)
    for i, (label, value) in enumerate(metrics_dict.items()):
        with cols[i % columns]:
            if isinstance(value, tuple):
                st.metric(label, value[0], delta=value[1])
            else:
                st.metric(label, value)

def create_segment_pie_chart(df, segment_col, title="Segment Distribution"):
    """Create an interactive pie chart for segment distribution"""
    segment_counts = df[segment_col].value_counts()
    
    fig = px.pie(
        values=segment_counts.values,
        names=segment_counts.index,
        title=title,
        hole=0.4,
        color_discrete_sequence=px.colors.qualitative.Set3
    )
    
    fig.update_traces(
        textposition='inside',
        textinfo='percent+label',
        hovertemplate='<b>%{label}</b><br>Count: %{value:,}<br>Percentage: %{percent}<extra></extra>'
    )
    
    fig.update_layout(
        showlegend=True,
        legend=dict(orientation="v", yanchor="middle", y=0.5, xanchor="left", x=1.1),
        height=500
    )
    
    return fig

def create_bar_chart(df, x_col, y_col, title="", color_col=None, orientation='v'):
    """Create an interactive bar chart"""
    if orientation == 'v':
        fig = px.bar(
            df, x=x_col, y=y_col, color=color_col,
            title=title,
            color_discrete_sequence=px.colors.qualitative.Set2
        )
    else:
        fig = px.bar(
            df, x=y_col, y=x_col, color=color_col,
            title=title,
            orientation='h',
            color_discrete_sequence=px.colors.qualitative.Set2
        )
    
    fig.update_layout(
        hovermode='closest',
        showlegend=True if color_col else False,
        height=500
    )
    
    return fig

def create_funnel_chart(df, stage_col, title="Lifecycle Funnel"):
    """Create a funnel chart for lifecycle stages"""
    stage_counts = df[stage_col].value_counts().sort_values(ascending=False)
    
    fig = go.Figure(go.Funnel(
        y=stage_counts.index,
        x=stage_counts.values,
        textinfo="value+percent initial",
        marker=dict(
            color=px.colors.qualitative.Plotly[:len(stage_counts)]
        ),
        hovertemplate='<b>%{y}</b><br>Count: %{x:,}<br>Percentage: %{percentInitial}<extra></extra>'
    ))
    
    fig.update_layout(
        title=title,
        showlegend=False,
        height=600
    )
    
    return fig

def create_time_series_chart(df, date_col, value_col=None, title="Timeline"):
    """Create a time series chart"""
    if value_col:
        fig = px.line(df, x=date_col, y=value_col, title=title)
    else:
        # Count by date
        date_counts = df[date_col].value_counts().sort_index()
        fig = px.line(x=date_counts.index, y=date_counts.values, title=title)
        fig.update_traces(name='Count')
    
    fig.update_layout(
        xaxis_title="Date",
        yaxis_title="Count" if not value_col else value_col,
        hovermode='x unified',
        height=400
    )
    
    return fig

def create_heatmap(df, x_col, y_col, values_col, title="Heatmap"):
    """Create a heatmap"""
    pivot_df = df.pivot_table(index=y_col, columns=x_col, values=values_col, aggfunc='mean')
    
    fig = px.imshow(
        pivot_df,
        labels=dict(x=x_col, y=y_col, color=values_col),
        title=title,
        aspect="auto",
        color_continuous_scale='RdYlGn'
    )
    
    fig.update_layout(height=600)
    
    return fig

def create_scatter_plot(df, x_col, y_col, color_col=None, size_col=None, title=""):
    """Create an interactive scatter plot"""
    fig = px.scatter(
        df, x=x_col, y=y_col, color=color_col, size=size_col,
        title=title,
        hover_data=df.columns,
        color_continuous_scale='Viridis' if color_col and pd.api.types.is_numeric_dtype(df[color_col]) else None
    )
    
    fig.update_layout(
        hovermode='closest',
        height=500
    )
    
    return fig

def format_percentage(value, decimals=1):
    """Format a decimal value as percentage"""
    if pd.isna(value):
        return "N/A"
    return f"{value * 100:.{decimals}f}%"

def format_number(value):
    """Format a number with thousands separator"""
    if pd.isna(value):
        return "N/A"
    return f"{int(value):,}"

def calculate_close_rate(df):
    """Calculate close rate from dataframe using mean() for consistency with notebooks"""
    # Prefer is_closed field (binary 0/1) for consistency with notebook calculations
    if 'is_closed' in df.columns:
        return df['is_closed'].mean() * 100 if len(df) > 0 else 0
    # Fall back to close_date if is_closed not available
    close_col = 'close_date' if 'close_date' in df.columns else 'Close Date'
    if close_col in df.columns:
        closed = df[close_col].notna().sum()
        total = len(df)
        return (closed / total * 100) if total > 0 else 0
    return 0

def calculate_days_to_close(create_date, close_date):
    """Calculate days to close, filtering out negative values"""
    if pd.isna(create_date) or pd.isna(close_date):
        return np.nan
    
    days = (close_date - create_date).days
    return days if days >= 0 else np.nan

def categorize_ttc(days):
    """Categorize time-to-close into buckets"""
    if pd.isna(days):
        return "Still Open"
    elif days <= 30:
        return "Early (≤30 days)"
    elif days <= 60:
        return "Medium (31-60 days)"
    elif days <= 120:
        return "Late (61-120 days)"
    else:
        return "Very Late (>120 days)"

def convert_academic_period(period_code):
    """Convert YYYYMM academic period codes to readable format"""
    if pd.isna(period_code) or period_code == "":
        return "Unknown"
    
    try:
        period_str = str(period_code).strip()
        if len(period_str) != 6:
            return f"Invalid: {period_code}"
        
        year = int(period_str[:4])
        period = int(period_str[4:])
        
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

def create_download_button(df, filename, label="Download CSV"):
    """Create a download button for a dataframe"""
    csv = df.to_csv(index=False)
    st.download_button(
        label=label,
        data=csv,
        file_name=filename,
        mime='text/csv'
    )

def format_dataframe_for_export(df):
    """
    Format dataframe for CSV export matching notebook standards.
    Applies proper date formatting and historical data processing.
    """
    df_export = df.copy()
    
    # Remove duplicate periodo_de_ingreso column (we use the converted periodo_ingreso)
    if 'periodo_de_ingreso' in df_export.columns and 'periodo_ingreso' in df_export.columns:
        df_export = df_export.drop(columns=['periodo_de_ingreso'])
    
    # Date formatting (matching notebook format)
    # Convert all date/timestamp columns to YYYY-MM-DD format
    date_columns = [
        'create_date', 'close_date', 'first_conversion_date', 'recent_conversion_date',
        'time_first_seen', 'hs_analytics_first_timestamp', 'first_conversion_date_c3',
        'recent_conversion_date_c3'
    ]
    
    for col in date_columns:
        if col in df_export.columns:
            df_export[col] = pd.to_datetime(df_export[col], errors='coerce').dt.strftime('%Y-%m-%d')
            df_export[col] = df_export[col].fillna('unknown')
    
    # Handle days_to_close (numeric or 'unknown')
    if 'days_to_close' in df_export.columns:
        df_export['days_to_close'] = df_export['days_to_close'].apply(
            lambda x: int(x) if pd.notna(x) and str(x) != 'nan' else 'unknown'
        )
    
    # Apply hist_latest to key columns that need latest values only
    latest_only_columns = [
        'propiedad_del_contacto', 'lifecycle_stage', 'original_source', 
        'canal_de_adquisicion', 'latest_source', 'last_referrer',
        'first_conversion', 'recent_conversion', 'prep_bpm', 'prep_name',
        'prep_donde_estudia', 'prep_year'
    ]
    for col in latest_only_columns:
        if col in df_export.columns:
            df_export[col] = df_export[col].apply(hist_latest)
    
    # Apply hist_all to text columns that need all historical values
    hist_all_columns = [
        'original_source_hist_all', 'canal_de_adquisicion_hist_all', 
        'latest_source_hist_all', 'last_referrer_hist_all', 'apreu_hist_all'
    ]
    for col in hist_all_columns:
        if col in df_export.columns:
            # These should already be processed, but ensure proper formatting
            df_export[col] = df_export[col].fillna('')
    
    # Handle academic period columns (already in readable format)
    academic_columns = ['periodo_ingreso', 'periodo_admision']
    for col in academic_columns:
        if col in df_export.columns:
            # Already processed by cluster logic, just ensure no NaN values
            df_export[col] = df_export[col].fillna('unknown')
    
    # Clean up any remaining NaN values
    df_export = df_export.fillna('unknown')
    
    return df_export

def create_export_download_button(df, filename, label="Download CSV", use_proper_formatting=True):
    """
    Create a download button with proper CSV formatting matching notebook standards.
    """
    if use_proper_formatting:
        df_formatted = format_dataframe_for_export(df)
    else:
        df_formatted = df
    
    # Use utf-8-sig encoding like notebooks for proper Excel compatibility
    csv_data = df_formatted.to_csv(index=False, encoding='utf-8-sig')
    
    st.download_button(
        label=label,
        data=csv_data.encode('utf-8'),
        file_name=filename,
        mime='text/csv',
        use_container_width=True
    )

def display_dataframe_with_style(df, height=400):
    """Display a styled dataframe"""
    st.dataframe(
        df,
        use_container_width=True,
        height=height
    )

def create_summary_card(title, metrics_dict, color="#f0f2f6"):
    """Create a styled summary card with multiple metrics"""
    st.markdown(f"""
    <div style="background-color: {color}; padding: 1.5rem; border-radius: 10px; margin-bottom: 1rem;">
        <h3 style="margin-top: 0;">{title}</h3>
    </div>
    """, unsafe_allow_html=True)
    
    cols = st.columns(len(metrics_dict))
    for i, (label, value) in enumerate(metrics_dict.items()):
        with cols[i]:
            if isinstance(value, tuple):
                st.metric(label, value[0], delta=value[1])
            else:
                st.metric(label, value)

