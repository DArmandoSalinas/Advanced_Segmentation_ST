"""
Cluster 2: Segmentación por Geografía y Compromiso
Segmenta contactos por geografía (Local/Foráneo/Internacional) y nivel de compromiso
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
from utils import (
    hist_latest, hist_all, normalize_text,
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
    
    # Normalize United States variations to a single format
    def normalize_united_states(country):
        if pd.isna(country) or country == "unknown" or country == "":
            return country
        country_lower = str(country).lower().strip()
        # Normalize variations of United States
        us_variations = [
            "estados unidos de america",
            "estados unidos de américa", 
            "united states of america",
            "united states",
            "usa",
            "us",
            "u.s.a.",
            "u.s."
        ]
        if country_lower in us_variations:
            return "estados unidos"
        return country
    
    df['country_any'] = df['country_any'].apply(normalize_united_states)
    
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
    
    # Assign 2A-2F segments with descriptive names
    def assign_c2(row):
        tier = row['geo_tier']
        hi = bool(row['is_high_engager'])
        if tier == 'domestic_non_local':
            return '2A - Foráneo, Alto Compromiso' if hi else '2B - Foráneo, Bajo Compromiso'
        if tier == 'international':
            return '2C - Internacional, Alto Compromiso' if hi else '2D - Internacional, Bajo Compromiso'
        if tier == 'local':
            return '2E - Local, Alto Compromiso' if hi else '2F - Local, Bajo Compromiso'
        return '2Z - Sin Geografía'
    
    df['segment_c2'] = df.apply(assign_c2, axis=1)
    
    # Dynamic action map based on geo config
    local_name = geo_config['local_region']
    country_name = geo_config['home_country']
    
    ACTION_MAP = {
        '2A - Foráneo, Alto Compromiso': f'Compromiso digital + eventos virtuales ({country_name} fuera de {local_name})',
        '2B - Foráneo, Bajo Compromiso': f'Empuje WhatsApp/email ({country_name} fuera de {local_name})',
        '2C - Internacional, Alto Compromiso': 'Webinars + Q&A virtual (Internacional)',
        '2D - Internacional, Bajo Compromiso': 'Campañas de concientización (Internacional)',
        '2E - Local, Alto Compromiso': f'Eventos presenciales + compromiso local (Local {local_name})',
        '2F - Local, Bajo Compromiso': f'Nutrición local + WhatsApp (Local {local_name})',
        '2Z - Sin Geografía': 'Investigar geografía faltante'
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
            return "Desconocido"
        
        try:
            period_str = str(period_code).strip()
            if len(period_str) != 6:
                return f"Invalid: {period_code}"
            
            year = int(period_str[:4])
            period = int(period_str[4:])
            
            # Map period codes to semester names
            period_map = {
                5: "Especial",
                10: "Primavera", 
                35: "Verano",
                60: "Otoño",
                75: "Invierno/Especial"
            }
            
            semester = period_map.get(period, f"Desconocido({period})")
            return f"{year} {semester}"
            
        except (ValueError, IndexError):
            return f"Inválido: {period_code}"
    
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
            'Métrica': [
                'Total Contactos',
                'Segmentos',
                'Puntuación Promedio de Compromiso',
                'Mediana de Probabilidad de Cierre',
                'Total de Tratos Cerrados',
                'Días Promedio hasta Cierre'
            ],
            'Valor': [
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
            top_countries.columns = ['País', 'Conteo']
            top_countries.to_excel(writer, sheet_name="7_top_countries", index=False)
        
        if 'state_any' in cohort_export.columns:
            top_states = cohort_export['state_any'].value_counts().head(20).reset_index()
            top_states.columns = ['Estado', 'Conteo']
            top_states.to_excel(writer, sheet_name="8_top_states", index=False)
        
        if 'city_any' in cohort_export.columns:
            top_cities = cohort_export['city_any'].value_counts().head(20).reset_index()
            top_cities.columns = ['Ciudad', 'Conteo']
            top_cities.to_excel(writer, sheet_name="9_top_cities", index=False)
        
        # 10-11. Lifecycle Analysis (using latest values only)
        if 'lifecycle_stage' in cohort_export.columns:
            lifecycle_dist = cohort_export.groupby(['segment_c2', 'lifecycle_stage']).size().reset_index(name='count')
            lifecycle_pct = lifecycle_dist.pivot(index='segment_c2', columns='lifecycle_stage', values='count').fillna(0)
            lifecycle_pct = lifecycle_pct.div(lifecycle_pct.sum(axis=1), axis=0) * 100
            lifecycle_pct.to_excel(writer, sheet_name="10_lifecycle_analysis")
            
            lifecycle_top = cohort_export.groupby('segment_c2')['lifecycle_stage'].agg(lambda x: x.mode()[0] if len(x.mode()) > 0 else 'Desconocido').reset_index()
            lifecycle_top.columns = ['Segmento', 'Etapa Más Común']
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
    st.markdown("## 🌍 Cluster 2: Segmentación por Geografía y Compromiso")
    
    col1, col2 = st.columns([3, 1])
    with col1:
        st.markdown(f"**Configuración Actual:** 🏠 {geo_config['home_country']} | 📍 {geo_config['local_region']}")
    with col2:
        if st.button("⚙️ Cambiar Configuración", key="change_geo_settings"):
            st.info("👈 Usa la Configuración Geográfica en la barra lateral para cambiar tu país de origen y región local")
    
    # About this analysis
    with st.expander("ℹ️ Acerca de Este Análisis", expanded=False):
        st.markdown(f"""
        ### 🎯 Qué Hace Este Cluster
        **Segmenta contactos por geografía y compromiso** en 6 grupos accionables para campañas regionales dirigidas.
        
        ### 👥 Quién Debe Usar Esto
        - **Equipos de Marketing Regional** - Adaptar campañas por geografía
        - **Oficiales de Admisiones** - Planificar visitas y eventos por región
        - **Reclutamiento Internacional** - Entender rendimiento internacional vs nacional
        
        ### 🔑 Preguntas Clave Respondidas
        - ¿Los contactos locales cierran más rápido que los internacionales?
        - ¿Qué estados/países tienen el mayor compromiso?
        - ¿Deberíamos invertir más en reclutamiento internacional?
        - ¿Cuál es la estrategia óptima para cada nivel geográfico?
        
        ### 📊 Segmentos Definidos (Actual: {geo_config['home_country']}/{geo_config['local_region']})
        - **2A (Foráneo, Alto)** - Alto compromiso de {geo_config['home_country']} fuera de {geo_config['local_region']}
        - **2B (Foráneo, Bajo)** - Bajo compromiso de {geo_config['home_country']} fuera de {geo_config['local_region']}
        - **2C (Internacional, Alto)** - Alto compromiso de fuera de {geo_config['home_country']}
        - **2D (Internacional, Bajo)** - Bajo compromiso de fuera de {geo_config['home_country']}
        - **2E (Local, Alto)** - Alto compromiso de {geo_config['local_region']}
        - **2F (Local, Bajo)** - Bajo compromiso de {geo_config['local_region']}
        - **2Z (Sin Geografía): Investigar geografía faltante**
        
        ### 💡 Ejemplo de Insight
        *"2E (Local {geo_config['local_region']}, Alto) cierra en 45 días en promedio vs 120 días para 2C (Internacional)"*
        → **Acción:** Priorizar contactos locales de alto compromiso, crear eventos virtuales para internacionales
        
        ### ⚙️ Configuración Dinámica
        ¡Este cluster se adapta a TU geografía! Cambia la configuración en la barra lateral para analizar cualquier país/región.
        """)
    
    st.markdown("---")
    
    if data is None:
        st.error("⚠️ Datos no cargados.")
        return
    
    # Process data with geo config and cache busting
    # This ensures the cache refreshes when global filters change the data
    cache_key = f"c2_{len(data)}_{data['Record ID'].iloc[0] if 'Record ID' in data.columns else 'na'}"
    with st.spinner(f"Procesando datos del Cluster 2 para {geo_config['home_country']}..."):
        cohort = process_cluster2_data(data, geo_config, cache_key)
    
    # Show contact count AFTER core filters (APREU + removing other/subscriber)
    if data is not None:
        active_filters = sum(1 for k in st.session_state.keys() if k.startswith('filter_'))
        if active_filters > 0:
            st.info(f"🔍 Analizando {len(cohort):,} contactos después de aplicar filtros principales (APREU, excluyendo 'other'/'subscriber') + filtros globales")
        else:
            st.info(f"📊 Analizando {len(cohort):,} contactos después de aplicar filtros principales (APREU, excluyendo 'other'/'subscriber')")
    
    if len(cohort) == 0:
        st.warning("No hay datos disponibles después de los filtros.")
        return
    
    # Add cluster-specific filters
    with st.expander("🎛️ Filtros Específicos del Cluster 2", expanded=False):
        col1, col2, col3 = st.columns(3)
        
        with col1:
            # Segment filter
            available_segments = sorted(cohort['segment_c2'].unique())
            selected_segments = st.multiselect(
                "Filtrar por Segmento (2A-2F):",
                options=available_segments,
                default=available_segments,
                help="Seleccionar segmentos a incluir"
            )
            
            # Lifecycle stage filter
            if 'lifecycle_stage' in cohort.columns:
                available_lifecycle = sorted(cohort['lifecycle_stage'].dropna().unique())
                selected_lifecycle = st.multiselect(
                    "Filtrar por Etapa del Ciclo de Vida:",
                    options=available_lifecycle,
                    default=available_lifecycle,
                    help="Seleccionar etapas del ciclo de vida a incluir"
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
                    help="Seleccionar períodos de ingreso a incluir"
                )
            else:
                selected_periodos = None
            
            # Closure status filter
            closure_options = ["Todos", "Solo Cerrados", "Solo Abiertos"]
            closure_filter = st.radio(
                "Estado de Cierre:",
                options=closure_options,
                index=0,
                help="Filtrar por estado de cierre"
            )
        
        with col3:
            # Geography tier filter
            available_tiers = sorted(cohort['geo_tier'].unique())
            selected_tiers = st.multiselect(
                "Filtrar por Nivel Geográfico:",
                options=available_tiers,
                default=available_tiers,
                help="Seleccionar niveles geográficos a incluir"
            )
            
            # Country filter (top countries)
            top_countries = cohort['country_any'].value_counts().head(20).index.tolist()
            selected_countries = st.multiselect(
                "Filtrar por País (Top 20):",
                options=top_countries,
                default=top_countries,
                help="Seleccionar países a incluir"
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
        if closure_filter == "Solo Cerrados":
            cohort_filtered = cohort_filtered[cohort_filtered['close_date'].notna()]
        elif closure_filter == "Solo Abiertos":
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
            with st.spinner("Generando libro de trabajo Excel integral..."):
                xlsx_data = create_cluster2_xlsx_export(cohort)
                st.download_button(
                    label="📊 Descargar Libro de Trabajo Integral (XLSX) - 20+ Hojas",
                    data=xlsx_data,
                    file_name=f"cluster2_summary_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    use_container_width=True,
                    help="Libro de trabajo de análisis integral con 20+ hojas: resumen ejecutivo, rendimiento de segmentos, geografía, compromiso, ciclo de vida, estadísticas de cierre, ¡y más!"
                )
    
    # Create tabs
    tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
        "📊 Resumen", "🎯 Análisis de Segmento", "🗺️ Análisis Geográfico",
        "💰 Resultados de Negocio", "⚡ Cerradores Rápidos/Lentos", "🔬 Benchmarks de Rendimiento", "🔍 Búsqueda de Contactos"
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
    st.markdown("### 📊 Resumen Ejecutivo")
    
    # Key metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Contactos", f"{len(cohort):,}")
    
    with col2:
        local_count = (cohort['geo_tier'] == 'local').sum()
        st.metric("Local (QRO)", f"{local_count:,}")
    
    with col3:
        domestic_count = (cohort['geo_tier'] == 'domestic_non_local').sum()
        st.metric("Foráneo (no-QRO)", f"{domestic_count:,}")
    
    with col4:
        intl_count = (cohort['geo_tier'] == 'international').sum()
        st.metric("Internacional", f"{intl_count:,}")
    
    st.markdown("---")
    
    # Segment distribution
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### Distribución de Segmentos (2A-2F)")
        seg_counts = cohort['segment_c2'].value_counts()
        fig = px.pie(
            values=seg_counts.values,
            names=seg_counts.index,
            title="Segmentos por Ubicación y Compromiso",
            hole=0.4,
            color_discrete_sequence=px.colors.qualitative.Set3
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.markdown("#### Distribución por Nivel Geográfico")
        geo_counts = cohort['geo_tier'].value_counts()
        
        # Translate geo_tier names to Spanish
        geo_labels_map = {
            'local': 'Local',
            'domestic_non_local': 'Foráneo',
            'international': 'Internacional',
            'unknown': 'Desconocido'
        }
        geo_counts_translated = geo_counts.copy()
        geo_counts_translated.index = geo_counts_translated.index.map(lambda x: geo_labels_map.get(x, x))
        
        fig = px.pie(
            values=geo_counts_translated.values,
            names=geo_counts_translated.index,
            title="Niveles Geográficos",
            hole=0.4,
            color_discrete_sequence=px.colors.qualitative.Pastel
        )
        st.plotly_chart(fig, use_container_width=True)
    
    # Segment summary table - WITHOUT likelihood to close
    st.markdown("#### Resumen de Rendimiento por Segmento")
    
    segment_summary = cohort.groupby('segment_c2').agg({
        'contact_id': 'count',
        'num_sessions': 'mean',
        'num_pageviews': 'mean',
        'forms_submitted': 'mean',
        'engagement_score': 'mean',
        'close_date': lambda x: x.notna().sum()
    }).round(2)
    
    segment_summary.columns = ['Contactos', 'Sesiones Prom', 'Páginas Vistas Prom', 
                               'Formularios Prom', 'Compromiso Prom', 'Cerrados']
    segment_summary['Tasa de Cierre %'] = (
        segment_summary['Cerrados'] / segment_summary['Contactos'] * 100
    ).round(1)
    
    st.dataframe(segment_summary, use_container_width=True)

def render_segment_analysis_tab_c2(cohort):
    """Render segment analysis tab"""
    st.markdown("### 🎯 Análisis Profundo de Segmentos 2A-2F")
    
    # Segment selector
    segments = sorted(cohort['segment_c2'].unique())
    selected_segment = st.selectbox("Seleccionar Segmento para Detalles:", segments)
    
    seg_data = cohort[cohort['segment_c2'] == selected_segment]
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Total Contactos", f"{len(seg_data):,}")
    
    with col2:
        close_rate = calculate_close_rate(seg_data)
        st.metric("Tasa de Cierre", f"{close_rate:.1f}%")
    
    with col3:
        avg_eng = seg_data['engagement_score'].mean()
        st.metric("Compromiso Promedio", f"{avg_eng:.2f}")
    
    st.markdown("---")
    
    # Action recommendation
    if 'segment_c2_action' in seg_data.columns:
        action = seg_data['segment_c2_action'].iloc[0]
        st.info(f"**Acción Recomendada:** {action}")
    
    # Engagement distribution
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### Distribución de Puntuación de Compromiso")
        fig = px.histogram(
            seg_data, x='engagement_score',
            title=f"Distribución de Puntuación de Compromiso - {selected_segment}",
            nbins=30,
            color_discrete_sequence=['#3498db']
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.markdown("#### Distribución de Sesiones")
        fig = px.histogram(
            seg_data, x='num_sessions',
            title=f"Distribución de Sesiones - {selected_segment}",
            nbins=20,
            color_discrete_sequence=['#e74c3c']
        )
        st.plotly_chart(fig, use_container_width=True)
    
    # Lifecycle distribution
    if 'lifecycle_stage' in seg_data.columns:
        st.markdown("#### Distribución de Etapa del Ciclo de Vida")
        lifecycle_counts = seg_data['lifecycle_stage'].value_counts().head(10)
        fig = px.bar(
            x=lifecycle_counts.index,
            y=lifecycle_counts.values,
            title=f"Principales Etapas del Ciclo de Vida - {selected_segment}",
            labels={'x': 'Etapa del Ciclo de Vida', 'y': 'Conteo'},
            color=lifecycle_counts.values,
            color_continuous_scale='Viridis'
        )
        st.plotly_chart(fig, use_container_width=True)

def render_geography_analysis_tab(cohort):
    """Render geography analysis tab"""
    st.markdown("### 🗺️ Análisis de Distribución Geográfica")
    
    # Top countries
    st.markdown("#### Principales Países")
    country_counts = cohort['country_any'].value_counts().head(15)
    country_counts = country_counts[country_counts.index != 'unknown']
    
    fig = px.bar(
        x=country_counts.values,
        y=country_counts.index,
        orientation='h',
        title="Top 15 Países",
        labels={'x': 'Contactos', 'y': 'País'},
        color=country_counts.values,
        color_continuous_scale='Blues'
    )
    fig.update_layout(showlegend=False, height=500)
    st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("---")
    
    # Country Performance Analysis
    st.markdown("#### 🌍 Rendimiento por País")
    st.markdown("Análisis completo de rendimiento de los principales países")
    
    # Filter out unknown countries
    country_data = cohort[cohort['country_any'] != 'unknown'].copy()
    
    if len(country_data) > 0:
        # Get top countries by volume
        top_countries = country_data['country_any'].value_counts().head(15).index
        
        # Calculate comprehensive performance metrics by country
        country_performance = country_data[country_data['country_any'].isin(top_countries)].groupby('country_any').agg({
            'contact_id': 'count',
            'num_sessions': 'mean',
            'num_pageviews': 'mean',
            'forms_submitted': 'mean',
            'engagement_score': 'mean',
            'close_date': lambda x: x.notna().sum(),
            'days_to_close': lambda x: x.dropna().mean() if x.dropna().any() else None
        }).round(2)
        
        country_performance.columns = ['Total', 'Sesiones Prom', 'Páginas Prom', 'Formularios Prom', 
                                      'Compromiso Prom', 'Cerrados', 'Días Prom hasta Cierre']
        country_performance['Tasa de Cierre %'] = (
            country_performance['Cerrados'] / country_performance['Total'] * 100
        ).round(1)
        
        # Sort by total contacts
        country_performance = country_performance.sort_values('Total', ascending=False)
        
        # Display table
        st.markdown("**Métricas de Rendimiento por País (Top 15 por Volumen):**")
        st.dataframe(country_performance, use_container_width=True)
        
        # Visualizations
        col1, col2 = st.columns(2)
        
        with col1:
            # Close rate by country
            fig = px.bar(
                x=country_performance.index,
                y=country_performance['Tasa de Cierre %'],
                title="Tasa de Cierre por País",
                labels={'x': 'País', 'y': 'Tasa de Cierre %'},
                color=country_performance['Tasa de Cierre %'],
                color_continuous_scale='RdYlGn'
            )
            fig.update_layout(xaxis_tickangle=-45, height=400)
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Engagement score by country
            fig = px.bar(
                x=country_performance.index,
                y=country_performance['Compromiso Prom'],
                title="Compromiso Promedio por País",
                labels={'x': 'País', 'y': 'Compromiso Promedio'},
                color=country_performance['Compromiso Prom'],
                color_continuous_scale='Blues'
            )
            fig.update_layout(xaxis_tickangle=-45, height=400)
            st.plotly_chart(fig, use_container_width=True)
        
        # Days to close by country (if available)
        if country_performance['Días Prom hasta Cierre'].notna().any():
            st.markdown("**Tiempo hasta Cierre por País:**")
            country_ttc = country_performance[country_performance['Días Prom hasta Cierre'].notna()].copy()
            country_ttc = country_ttc.sort_values('Días Prom hasta Cierre', ascending=True)
            
            fig = px.bar(
                x=country_ttc.index,
                y=country_ttc['Días Prom hasta Cierre'],
                title="Días Promedio hasta Cierre por País",
                labels={'x': 'País', 'y': 'Días Promedio'},
                color=country_ttc['Días Prom hasta Cierre'],
                color_continuous_scale='Reds'
            )
            fig.update_layout(xaxis_tickangle=-45, height=400)
            st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No hay datos de países disponibles para análisis.")
    
    st.markdown("---")
    
    # Top Mexican states (for domestic/foráneo contacts)
    st.markdown("#### Principales Estados Mexicanos (Contactos Nacionales: Local + Foráneo)")
    domestic = cohort[cohort['geo_tier'].isin(['local', 'domestic_non_local'])]
    
    if len(domestic) > 0:
        state_counts = domestic['state_any'].value_counts().head(15)
        state_counts = state_counts[state_counts.index != 'unknown']
        
        fig = px.bar(
            x=state_counts.values,
            y=state_counts.index,
            orientation='h',
            title="Top 15 Estados Mexicanos",
            labels={'x': 'Contactos', 'y': 'Estado'},
            color=state_counts.values,
            color_continuous_scale='Greens'
        )
        fig.update_layout(showlegend=False, height=500)
        st.plotly_chart(fig, use_container_width=True)
        
        st.markdown("---")
        
        # State Performance Analysis
        st.markdown("#### 📊 Rendimiento por Estado")
        st.markdown("Análisis completo de rendimiento de los principales estados")
        
        # Filter out unknown states
        state_data = domestic[domestic['state_any'] != 'unknown'].copy()
        
        if len(state_data) > 0:
            # Get top states by volume
            top_states = state_data['state_any'].value_counts().head(15).index
            
            # Calculate comprehensive performance metrics by state
            state_performance = state_data[state_data['state_any'].isin(top_states)].groupby('state_any').agg({
                'contact_id': 'count',
                'num_sessions': 'mean',
                'num_pageviews': 'mean',
                'forms_submitted': 'mean',
                'engagement_score': 'mean',
                'close_date': lambda x: x.notna().sum(),
                'days_to_close': lambda x: x.dropna().mean() if x.dropna().any() else None
            }).round(2)
            
            state_performance.columns = ['Total', 'Sesiones Prom', 'Páginas Prom', 'Formularios Prom', 
                                       'Compromiso Prom', 'Cerrados', 'Días Prom hasta Cierre']
            state_performance['Tasa de Cierre %'] = (
                state_performance['Cerrados'] / state_performance['Total'] * 100
            ).round(1)
            
            # Sort by total contacts
            state_performance = state_performance.sort_values('Total', ascending=False)
            
            # Display table
            st.markdown("**Métricas de Rendimiento por Estado (Top 15 por Volumen):**")
            st.dataframe(state_performance, use_container_width=True)
            
            # Visualizations
            col1, col2 = st.columns(2)
            
            with col1:
                # Close rate by state
                fig = px.bar(
                    x=state_performance.index,
                    y=state_performance['Tasa de Cierre %'],
                    title="Tasa de Cierre por Estado",
                    labels={'x': 'Estado', 'y': 'Tasa de Cierre %'},
                    color=state_performance['Tasa de Cierre %'],
                    color_continuous_scale='RdYlGn'
                )
                fig.update_layout(xaxis_tickangle=-45, height=400)
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                # Engagement score by state
                fig = px.bar(
                    x=state_performance.index,
                    y=state_performance['Compromiso Prom'],
                    title="Compromiso Promedio por Estado",
                    labels={'x': 'Estado', 'y': 'Compromiso Promedio'},
                    color=state_performance['Compromiso Prom'],
                    color_continuous_scale='Blues'
                )
                fig.update_layout(xaxis_tickangle=-45, height=400)
                st.plotly_chart(fig, use_container_width=True)
            
            # Days to close by state (if available)
            if state_performance['Días Prom hasta Cierre'].notna().any():
                st.markdown("**Tiempo hasta Cierre por Estado:**")
                state_ttc = state_performance[state_performance['Días Prom hasta Cierre'].notna()].copy()
                state_ttc = state_ttc.sort_values('Días Prom hasta Cierre', ascending=True)
                
                fig = px.bar(
                    x=state_ttc.index,
                    y=state_ttc['Días Prom hasta Cierre'],
                    title="Días Promedio hasta Cierre por Estado",
                    labels={'x': 'Estado', 'y': 'Días Promedio'},
                    color=state_ttc['Días Prom hasta Cierre'],
                    color_continuous_scale='Reds'
                )
                fig.update_layout(xaxis_tickangle=-45, height=400)
                st.plotly_chart(fig, use_container_width=True)
            
            # Additional metrics visualization
            st.markdown("**Comparación de Métricas Clave por Estado:**")
            col1, col2 = st.columns(2)
            
            with col1:
                # Sessions per state
                fig = px.bar(
                    x=state_performance.index,
                    y=state_performance['Sesiones Prom'],
                    title="Sesiones Promedio por Estado",
                    labels={'x': 'Estado', 'y': 'Sesiones Promedio'},
                    color=state_performance['Sesiones Prom'],
                    color_continuous_scale='Purples'
                )
                fig.update_layout(xaxis_tickangle=-45, height=400)
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                # Forms submitted per state
                fig = px.bar(
                    x=state_performance.index,
                    y=state_performance['Formularios Prom'],
                    title="Formularios Promedio por Estado",
                    labels={'x': 'Estado', 'y': 'Formularios Promedio'},
                    color=state_performance['Formularios Prom'],
                    color_continuous_scale='Oranges'
                )
                fig.update_layout(xaxis_tickangle=-45, height=400)
                st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No hay datos de estados disponibles para análisis.")
    else:
        st.info("No hay contactos nacionales para analizar.")

def render_outcomes_tab_c2(cohort):
    """Render business outcomes tab"""
    st.markdown("### 💰 Resultados de Negocio por Geografía")
    
    # Lifecycle Stage Analysis
    st.markdown("#### 🔄 Distribución de Etapa del Ciclo de Vida")
    
    if 'lifecycle_stage' in cohort.columns:
        lifecycle_counts = cohort['lifecycle_stage'].value_counts().head(10)
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            fig = px.bar(
                x=lifecycle_counts.values,
                y=lifecycle_counts.index,
                orientation='h',
                title="Top 10 Etapas del Ciclo de Vida",
                labels={'x': 'Contactos', 'y': 'Etapa del Ciclo de Vida'},
                color=lifecycle_counts.values,
                color_continuous_scale='Viridis'
            )
            fig.update_layout(showlegend=False, height=400)
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.markdown("**Distribución de Etapas:**")
            for stage, count in lifecycle_counts.head(5).items():
                pct = (count / len(cohort) * 100)
                st.metric(stage, f"{count:,}", delta=f"{pct:.1f}%")
        
        # Lifecycle by segment
        st.markdown("**Etapa del Ciclo de Vida por Segmento:**")
        
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
        st.info("Datos de etapa del ciclo de vida no disponibles")
    
    # Traffic Sources Analysis (matching notebook)
    st.markdown("#### 📊 Análisis de Fuentes de Tráfico por Segmento")
    st.markdown("Distribución de fuentes por donde los contactos llegan a cada segmento")
    
    if 'latest_source' in cohort.columns:
        # Calculate latest source percentage by segment (matching notebook logic)
        src_pct_list = []
        for seg, grp in cohort.groupby("segment_c2"):
            vc = grp['latest_source'].fillna("unknown").astype(str).str.strip().replace({"": "unknown"}).value_counts(normalize=True)
            df = vc.mul(100).round(1).to_frame(name="percent").reset_index().rename(columns={"index": "latest_source"})
            df.insert(0, "segment", seg)
            src_pct_list.append(df)
        
        if src_pct_list:
            latest_source_pct = pd.concat(src_pct_list, ignore_index=True)
            
            # Display table
            st.markdown("**Porcentaje de Fuentes por Segmento:**")
            st.dataframe(latest_source_pct, use_container_width=True)
            
            # Create visualization - stacked bar chart
            st.markdown("**Visualización de Fuentes por Segmento:**")
            
            # Get top sources across all segments
            top_sources = latest_source_pct.groupby('latest_source')['percent'].sum().sort_values(ascending=False).head(10).index
            latest_source_pct_filtered = latest_source_pct[latest_source_pct['latest_source'].isin(top_sources)]
            
            # Create stacked bar chart using long format
            fig = px.bar(
                latest_source_pct_filtered,
                x='segment',
                y='percent',
                color='latest_source',
                barmode='stack',
                title="Distribución de Fuentes de Tráfico por Segmento (%)",
                labels={'percent': 'Porcentaje (%)', 'segment': 'Segmento', 'latest_source': 'Fuente de Tráfico'},
                color_discrete_sequence=px.colors.qualitative.Set3
            )
            fig.update_layout(height=500, xaxis_title="Segmento", yaxis_title="Porcentaje (%)")
            st.plotly_chart(fig, use_container_width=True)
            
            # Create horizontal bar chart for better readability
            st.markdown("**Top Fuentes por Segmento (Top 5 por segmento):**")
            col1, col2 = st.columns(2)
            
            with col1:
                # Show top 5 sources for each segment
                for seg in sorted(latest_source_pct['segment'].unique()):
                    seg_data = latest_source_pct[latest_source_pct['segment'] == seg].sort_values('percent', ascending=False).head(5)
                    st.markdown(f"**{seg}:**")
                    for _, row in seg_data.iterrows():
                        st.write(f"  • {row['latest_source']}: {row['percent']:.1f}%")
            
            with col2:
                # Overall source distribution
                overall_sources = latest_source_pct.groupby('latest_source')['percent'].mean().sort_values(ascending=False).head(10)
                st.markdown("**Top Fuentes Promedio (todos los segmentos):**")
                fig = px.bar(
                    x=overall_sources.values,
                    y=overall_sources.index,
                    orientation='h',
                    title="Top 10 Fuentes Promedio",
                    labels={'x': 'Porcentaje Promedio (%)', 'y': 'Fuente'},
                    color=overall_sources.values,
                    color_continuous_scale='Blues'
                )
                fig.update_layout(showlegend=False, height=400)
                st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No hay datos de fuentes de tráfico disponibles")
    else:
        st.info("Columna 'latest_source' no disponible en el dataset")
    
    st.markdown("---")
    
    # Close rates by segment
    st.markdown("#### Comparación de Tasa de Cierre")
    
    segment_close_rates = []
    for seg in sorted(cohort['segment_c2'].unique()):
        seg_data = cohort[cohort['segment_c2'] == seg]
        close_rate = calculate_close_rate(seg_data)
        segment_close_rates.append({'Segmento': seg, 'Tasa de Cierre %': close_rate})
    
    close_rate_df = pd.DataFrame(segment_close_rates)
    close_rate_df.columns = ['Segmento', 'Tasa de Cierre %']
    
    fig = px.bar(
        close_rate_df, x='Segmento', y='Tasa de Cierre %',
        title="Tasa de Cierre por Segmento Geográfico (2A-2F con descripciones completas en ejes)",
        color='Tasa de Cierre %',
        color_continuous_scale='RdYlGn',
        text='Tasa de Cierre %'
    )
    fig.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
    st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("---")
    
    # Time to close analysis
    if 'ttc_bucket' in cohort.columns:
        st.markdown("#### Análisis de Tiempo hasta Cierre")
        
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
            title="Distribución de Tiempo hasta Cierre por Segmento Geográfico (2A-2F) (%)",
            labels={'value': 'Porcentaje', 'variable': 'Categoría TTC'},
            color_discrete_sequence=['#2ecc71', '#f39c12', '#e67e22', '#e74c3c', '#95a5a6']
        )
        st.plotly_chart(fig, use_container_width=True)
    
    # Average days to close by geography tier
    if 'days_to_close' in cohort.columns:
        st.markdown("#### Días Promedio hasta Cierre por Geografía")
        
        closed_cohort = cohort[cohort['days_to_close'].notna()]
        if len(closed_cohort) > 0:
            geo_days = closed_cohort.groupby('geo_tier')['days_to_close'].agg(['mean', 'median', 'count'])
            geo_days.columns = ['Días Prom', 'Días Mediana', 'Conteo Cerrados']
            geo_days = geo_days.round(1)
            
            st.dataframe(geo_days, use_container_width=True)

def render_fast_slow_closers_c2(cohort):
    """Render fast/slow closers analysis for Cluster 2"""
    st.markdown("### ⚡ Análisis de Cerradores Rápidos vs Lentos")
    st.markdown("Identifica qué combinaciones de Segmento × Geografía cierran más rápido")
    
    # Filter to closed contacts
    closed = cohort[cohort['close_date'].notna()].copy()
    
    if len(closed) == 0:
        st.warning("No hay contactos cerrados disponibles para análisis.")
        return
    
    st.markdown(f"**Analizando {len(closed):,} contactos cerrados**")
    
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
        st.metric("Cerradores Rápidos", f"{fast_count:,}", delta=f"{fast_pct:.1f}%")
    
    with col2:
        medium_count = (closed['closure_speed'] == 'Medium').sum()
        medium_pct = (medium_count / len(closed) * 100)
        st.metric("Cerradores Medios", f"{medium_count:,}", delta=f"{medium_pct:.1f}%")
    
    with col3:
        slow_count = (closed['closure_speed'] == 'Slow (>180 days)').sum()
        slow_pct = (slow_count / len(closed) * 100)
        st.metric("Cerradores Lentos", f"{slow_count:,}", delta=f"{slow_pct:.1f}%")
    
    st.markdown("---")
    
    # Fast closers: Segment × Geography analysis
    st.markdown("#### ⚡ Cerradores Rápidos (≤60 días): Segmento × Geografía")
    st.markdown("¿Qué combinaciones de segmento + geografía cierran más rápido?")
    
    fast_closers = closed[closed['closure_speed'] == 'Fast (≤60 days)']
    
    if len(fast_closers) > 0:
        # Create cross-tab
        fast_crosstab = pd.crosstab(
            fast_closers['segment_c2'],
            fast_closers['geo_tier'],
            margins=True,
            margins_name='Total'
        )
        
        st.markdown("**Conteos:**")
        st.dataframe(fast_crosstab, use_container_width=True)
        
        # Heatmap
        try:
            fig = px.imshow(
                fast_crosstab.iloc[:-1, :-1],  # Exclude margins
                labels=dict(x="Geografía", y="Segmento", color="Conteo"),
                title="Mapa de Calor Cerradores Rápidos: Segmento × Geografía",
                color_continuous_scale='Greens',
                aspect="auto"
            )
            st.plotly_chart(fig, use_container_width=True)
        except:
            pass
    else:
        st.info("No hay cerradores rápidos en este dataset.")
    
    st.markdown("---")
    
    # Slow closers: Segment × Geography analysis
    st.markdown("#### 🐌 Cerradores Lentos (>180 días): Segmento × Geografía")
    st.markdown("¿Qué combinaciones necesitan más atención?")
    
    slow_closers = closed[closed['closure_speed'] == 'Slow (>180 days)']
    
    if len(slow_closers) > 0:
        # Create cross-tab
        slow_crosstab = pd.crosstab(
            slow_closers['segment_c2'],
            slow_closers['geo_tier'],
            margins=True,
            margins_name='Total'
        )
        
        st.markdown("**Conteos:**")
        st.dataframe(slow_crosstab, use_container_width=True)
        
        # Heatmap
        try:
            fig = px.imshow(
                slow_crosstab.iloc[:-1, :-1],  # Exclude margins
                labels=dict(x="Geografía", y="Segmento", color="Conteo"),
                title="Mapa de Calor Cerradores Lentos: Segmento × Geografía",
                color_continuous_scale='Reds',
                aspect="auto"
            )
            st.plotly_chart(fig, use_container_width=True)
        except:
            pass
    else:
        st.info("No hay cerradores lentos en este dataset.")
    
    st.markdown("---")
    
    # Insights
    st.markdown("#### 💡 Insights Clave")
    
    insights = []
    
    if len(fast_closers) > 0:
        # Best performing combination
        fast_by_combo = fast_closers.groupby(['segment_c2', 'geo_tier']).size()
        if len(fast_by_combo) > 0:
            best_combo = fast_by_combo.idxmax()
            best_count = fast_by_combo.max()
            insights.append(f"✅ **Mejor Combinación de Cerradores Rápidos:** {best_combo[0]} + {best_combo[1]} ({best_count} contactos)")
    
    if len(slow_closers) > 0:
        # Worst performing combination
        slow_by_combo = slow_closers.groupby(['segment_c2', 'geo_tier']).size()
        if len(slow_by_combo) > 0:
            worst_combo = slow_by_combo.idxmax()
            worst_count = slow_by_combo.max()
            insights.append(f"⚠️ **Combinación Más Común de Cerradores Lentos:** {worst_combo[0]} + {worst_combo[1]} ({worst_count} contactos)")
    
    # Overall ratio
    if len(fast_closers) > 0 and len(slow_closers) > 0:
        ratio = len(fast_closers) / len(slow_closers)
        insights.append(f"📊 **Proporción Rápidos/Lentos:** {ratio:.2f}x")
    
    if insights:
        for insight in insights:
            st.markdown(insight)
    else:
        st.info("No hay suficientes datos para insights")

def render_performance_benchmarks_c2(cohort):
    """Render performance benchmarks tab for Cluster 2"""
    st.markdown("### 🔬 Benchmarks de Rendimiento y Análisis Geográfico")
    st.markdown("Compara segmentos y geografías contra indicadores clave de rendimiento")
    
    st.markdown("---")
    
    # Benchmark metrics by segment
    st.markdown("#### 📊 Indicadores Clave de Rendimiento por Segmento")
    
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
    st.markdown("#### 🗺️ Rendimiento por Nivel Geográfico")
    
    geo_performance = cohort.groupby('geo_tier').agg({
        'contact_id': 'count',
        'num_sessions': 'mean',
        'engagement_score': 'mean',
        'close_date': lambda x: x.notna().sum()
    }).round(2)
    
    geo_performance.columns = ['Conteo', 'Sesiones Prom', 'Compromiso Prom', 'Cerrados']
    geo_performance['Tasa de Cierre %'] = (geo_performance['Cerrados'] / geo_performance['Conteo'] * 100).round(1)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.dataframe(geo_performance, use_container_width=True)
    
    with col2:
        fig = px.bar(
            x=geo_performance.index,
            y=geo_performance['Tasa de Cierre %'],
            title="Tasa de Cierre por Nivel Geográfico",
            labels={'x': 'Nivel Geográfico', 'y': 'Tasa de Cierre %'},
            color=geo_performance['Tasa de Cierre %'],
            color_continuous_scale='RdYlGn'
        )
        st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("---")
    
    # Country performance (top countries)
    st.markdown("#### 🌍 Rendimiento de Principales Países")
    
    top_countries = cohort['country_any'].value_counts().head(15).index
    country_data = cohort[cohort['country_any'].isin(top_countries)]
    
    country_performance = country_data.groupby('country_any').agg({
        'contact_id': 'count',
        'num_sessions': 'mean',
        'engagement_score': 'mean',
        'close_date': lambda x: x.notna().sum()
    }).round(2)
    
    country_performance.columns = ['Conteo', 'Sesiones Prom', 'Compromiso Prom', 'Cerrados']
    country_performance['Tasa de Cierre %'] = (country_performance['Cerrados'] / country_performance['Conteo'] * 100).round(1)
    country_performance = country_performance.sort_values('Tasa de Cierre %', ascending=False)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.dataframe(country_performance, use_container_width=True)
    
    with col2:
        fig = px.bar(
            x=country_performance.index,
            y=country_performance['Tasa de Cierre %'],
            title="Tasa de Cierre por País (Top 15)",
            labels={'x': 'País', 'y': 'Tasa de Cierre %'},
            color=country_performance['Tasa de Cierre %'],
            color_continuous_scale='Viridis'
        )
        fig.update_layout(xaxis_tickangle=-45)
        st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("---")
    
    # Engagement distribution by geography
    st.markdown("#### 📈 Distribución de Compromiso por Nivel Geográfico")
    
    fig = px.box(
        cohort, x='geo_tier', y='engagement_score',
        color='geo_tier',
        title="Distribución de Puntuación de Compromiso por Nivel Geográfico",
        labels={'geo_tier': 'Nivel Geográfico', 'engagement_score': 'Puntuación de Compromiso'}
    )
    st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("---")
    
    # Segment × Geography heatmap
    st.markdown("#### 🔥 Mapa de Calor de Rendimiento Segmento × Geografía")
    
    heatmap_data = cohort.groupby(['segment_c2', 'geo_tier']).size().reset_index(name='count')
    heatmap_pivot = heatmap_data.pivot(index='segment_c2', columns='geo_tier', values='count').fillna(0)
    
    fig = px.imshow(
        heatmap_pivot,
        labels=dict(x="Nivel Geográfico", y="Segmento", color="Contactos"),
        title="Distribución de Contactos: Segmento × Nivel Geográfico",
        color_continuous_scale='Blues',
        aspect="auto"
    )
    st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("---")
    
    # Time to close by geography
    if 'days_to_close' in cohort.columns:
        st.markdown("#### ⏱️ Análisis de Tiempo hasta Cierre por Geografía")
        
        closed_cohort = cohort[cohort['days_to_close'].notna()]
        if len(closed_cohort) > 0:
            ttc_by_geo = closed_cohort.groupby('geo_tier')['days_to_close'].agg(['mean', 'median', 'count']).round(1)
            ttc_by_geo.columns = ['Días Prom', 'Días Mediana', 'Conteo Cerrados']
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.dataframe(ttc_by_geo, use_container_width=True)
            
            with col2:
                fig = px.bar(
                    x=ttc_by_geo.index,
                    y=ttc_by_geo['Días Prom'],
                    title="Días Promedio hasta Cierre por Nivel Geográfico",
                    labels={'x': 'Nivel Geográfico', 'y': 'Días Promedio hasta Cierre'},
                    color=ttc_by_geo['Días Prom'],
                    color_continuous_scale='Reds'
                )
                st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("---")
    
    # Key insights
    st.markdown("#### 💡 Insights de Rendimiento")
    
    insights = []
    
    # Best performing segment
    if len(benchmark_metrics) > 0:
        best_segment = benchmark_metrics['close_rate_pct'].idxmax()
        best_rate = benchmark_metrics['close_rate_pct'].max()
        insights.append(f"🏆 **Mejor Segmento:** {best_segment} ({best_rate:.1f}% tasa de cierre)")
    
    # Best performing geography
    if len(geo_performance) > 0:
        best_geo = geo_performance['Tasa de Cierre %'].idxmax()
        best_geo_rate = geo_performance['Tasa de Cierre %'].max()
        insights.append(f"🌍 **Mejor Geografía:** {best_geo} ({best_geo_rate:.1f}% tasa de cierre)")
    
    # Best performing country
    if len(country_performance) > 0:
        best_country = country_performance['Tasa de Cierre %'].idxmax()
        best_country_rate = country_performance['Tasa de Cierre %'].max()
        insights.append(f"🎯 **Mejor País:** {best_country} ({best_country_rate:.1f}% tasa de cierre)")
    
    # Geography diversity
    unique_countries = cohort['country_any'].nunique()
    unique_states = cohort['state_any'].nunique() if 'state_any' in cohort.columns else 0
    insights.append(f"🌐 **Alcance Geográfico:** {unique_countries} países, {unique_states} estados/regiones")
    
    if insights:
        for insight in insights:
            st.markdown(insight)
    else:
        st.info("No hay suficientes datos para insights")

def visualize_source_journey(contact_id, cohort, raw_data=None):
    """
    Visualize the journey of a contact through different traffic sources over time.
    Returns a matplotlib figure for display in Streamlit.
    """
    # Find the contact
    key = str(contact_id).strip()
    matches = cohort[cohort['contact_id'].astype(str) == key]
    
    if len(matches) == 0:
        return None
    
    contact = matches.iloc[0]
    
    # Collect journey data
    journey_steps = []
    
    # Get original_source and parse historical values
    original_source_raw = contact.get('original_source', None)
    original_source_list = []
    if original_source_raw and str(original_source_raw) not in ["Unknown", "nan", "", "None"]:
        original_source_list = hist_all(original_source_raw)
    
    # Get latest_source and parse historical values
    latest_source_raw = None
    if raw_data is not None and 'Latest Traffic Source' in raw_data.columns:
        raw_matches = raw_data[raw_data['Record ID'].astype(str) == key]
        if len(raw_matches) > 0:
            latest_source_raw = raw_matches.iloc[0]['Latest Traffic Source']
    else:
        latest_source_raw = contact.get('latest_source', None)
    
    latest_source_list = []
    if latest_source_raw and str(latest_source_raw) not in ["Unknown", "nan", "", "None"]:
        latest_source_list = hist_all(latest_source_raw)
    
    # Build complete journey
    # Strategy: Use original_source for the beginning and latest_source for the end
    # Original Source: first value from original_source
    if original_source_list:
        first_source = original_source_list[0]
        journey_steps.append({
            'step': 'Original Source',
            'value': str(first_source),
            'color': '#4CAF50'
        })
        
        # Get the latest source value (last from latest_source if available)
        latest_source_value = None
        if latest_source_list:
            latest_source_value = str(latest_source_list[-1]).strip()
        elif len(original_source_list) > 1:
            latest_source_value = str(original_source_list[-1]).strip()
        
        # Middle steps: all other values from original_source (excluding first and last if it matches latest)
        # These represent intermediate touchpoints
        middle_sources = []
        if len(original_source_list) > 1:
            # Add all values from original_source except the first
            for source in original_source_list[1:]:
                source_str = str(source).strip()
                if source_str not in ["Unknown", "nan", "", "None"]:
                    # Don't add if it's the same as the latest source (we'll add it separately)
                    if latest_source_value and source_str == latest_source_value:
                        continue
                    middle_sources.append(source_str)
        
        # Add middle steps
        for i, source in enumerate(middle_sources):
            journey_steps.append({
                'step': f'Touch {i+1}',
                'value': source,
                'color': '#2196F3'
            })
        
        # Latest Source: last value from latest_source (if available and different from first)
        if latest_source_value and str(first_source).strip() != latest_source_value:
            journey_steps.append({
                'step': 'Latest Source',
                'value': latest_source_value,
                'color': '#2196F3'
            })
    
    # If no journey steps found
    if not journey_steps:
        return None
    
    # Create visualization - HORIZONTAL LAYOUT
    box_width = 2.5
    box_spacing = 0.8
    total_width = len(journey_steps) * (box_width + box_spacing) + 1
    
    fig, ax = plt.subplots(figsize=(max(14, total_width), 5))
    ax.set_xlim(0, total_width)
    ax.set_ylim(0, 3)
    ax.axis('off')
    
    # Title
    ax.text(total_width / 2, 2.6, f'Source Journey for Contact {contact_id}',
            fontsize=16, fontweight='bold', ha='center')
    
    # Draw journey steps HORIZONTALLY (left to right)
    for i, step in enumerate(journey_steps):
        x_pos = 0.5 + i * (box_width + box_spacing)
        y_pos = 1.2
        
        # Draw box for step
        box = FancyBboxPatch(
            (x_pos, y_pos - 0.35), box_width, 0.7,
            boxstyle="round,pad=0.1",
            edgecolor=step['color'],
            facecolor=step['color'],
            alpha=0.3,
            linewidth=2
        )
        ax.add_patch(box)
        
        # Add step label (top of box)
        ax.text(x_pos + box_width/2, y_pos + 0.15, f"{step['step']}",
                fontsize=9, fontweight='bold', ha='center', va='center')
        
        # Add value text (inside box, wrapped if needed)
        value_text = step['value']
        if len(value_text) > 20:
            # Wrap long text
            words = value_text.split()
            lines = []
            current_line = []
            for word in words:
                test_line = ' '.join(current_line + [word])
                if len(test_line) <= 20:
                    current_line.append(word)
                else:
                    if current_line:
                        lines.append(' '.join(current_line))
                    current_line = [word]
            if current_line:
                lines.append(' '.join(current_line))
            value_text = '\n'.join(lines)
        
        ax.text(x_pos + box_width/2, y_pos, value_text,
                fontsize=8, ha='center', va='center', wrap=True)
        
        # Draw arrow to next step
        if i < len(journey_steps) - 1:
            arrow = FancyArrowPatch(
                (x_pos + box_width, y_pos),
                (x_pos + box_width + box_spacing, y_pos),
                arrowstyle='->,head_width=0.4,head_length=0.4',
                color='gray',
                linewidth=2
            )
            ax.add_patch(arrow)
    
    # Summary text
    summary_text = f"Total touchpoints: {len(journey_steps)}"
    ax.text(total_width / 2, 0.3, summary_text,
            fontsize=10, ha='center', style='italic', color='gray')
    
    plt.tight_layout()
    return fig

def render_contact_lookup_tab_c2(cohort):
    """Render contact lookup tab"""
    st.markdown("### 🔍 Búsqueda de Contacto Individual")
    
    if 'contact_id' not in cohort.columns:
        st.warning("ID de contacto no disponible en el dataset.")
        return
    
    contact_id = st.text_input("Ingresar ID de Contacto:", placeholder="ej., 12345")
    
    if contact_id:
        contact_id_str = str(contact_id).strip()
        matches = cohort[cohort['contact_id'].astype(str) == contact_id_str]
        
        if len(matches) == 0:
            st.error(f"No se encontró contacto con ID: {contact_id}")
        else:
            contact = matches.iloc[0]
            
            st.markdown("#### Perfil del Contacto")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.markdown("**Identificación**")
                st.write(f"**ID de Contacto:** {contact.get('contact_id', 'N/A')}")
                st.write(f"**Segmento:** {contact.get('segment_c2', 'N/A')}")
                st.write(f"**Nivel Geográfico:** {contact.get('geo_tier', 'N/A')}")
                st.write(f"**Acción:** {contact.get('segment_c2_action', 'N/A')}")
            
            with col2:
                st.markdown("**Geografía**")
                st.write(f"**País:** {contact.get('country_any', 'N/A')}")
                st.write(f"**Estado:** {contact.get('state_any', 'N/A')}")
                st.write(f"**Ciudad:** {contact.get('city_any', 'N/A')}")
            
            with col3:
                st.markdown("**Compromiso**")
                st.write(f"**Sesiones:** {int(contact.get('num_sessions', 0)):,}")
                st.write(f"**Páginas Vistas:** {int(contact.get('num_pageviews', 0)):,}")
                st.write(f"**Formularios:** {int(contact.get('forms_submitted', 0)):,}")
                st.write(f"**Puntuación de Compromiso:** {contact.get('engagement_score', 0):.2f}")
                st.write(f"**Alto Compromiso:** {'Sí' if contact.get('is_high_engager') else 'No'}")
            
            st.markdown("---")
            st.markdown("#### Resultados de Negocio")
            
            col1, col2 = st.columns(2)
            
            with col1:
                is_closed = "Sí" if pd.notna(contact.get('close_date')) else "No"
                st.write(f"**Cerrado:** {is_closed}")
                
                if 'lifecycle_stage' in contact.index:
                    st.write(f"**Etapa del Ciclo de Vida:** {contact.get('lifecycle_stage', 'N/A')}")
                
                if 'periodo_ingreso' in contact.index:
                    st.write(f"**Periodo de Ingreso:** {contact.get('periodo_ingreso', 'N/A')}")
            
            with col2:
                if pd.notna(contact.get('days_to_close')):
                    st.write(f"**Días hasta Cierre:** {contact.get('days_to_close', 0):.0f}")
                    st.write(f"**Categoría TTC:** {contact.get('ttc_bucket', 'N/A')}")
                
                # Likelihood is still available in data but not prominently displayed
                if 'likelihood_pct' in contact.index and pd.notna(contact.get('likelihood_pct')):
                    st.write(f"**Probabilidad de Cierre:** {contact.get('likelihood_pct', 0):.1f}%")

