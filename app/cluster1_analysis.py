"""
Cluster 1: Prospectos Socialmente Comprometidos
Identifica y segmenta prospectos con actividad en redes sociales usando análisis de datos históricos
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
from collections import Counter
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from utils import (
    hist_latest, hist_all, hist_concat_text, normalize_text,
    create_segment_pie_chart, create_bar_chart, create_funnel_chart,
    calculate_close_rate, calculate_days_to_close, categorize_ttc,
    display_metrics, create_download_button, display_dataframe_with_style
)

# Platform keywords dictionary
PLATFORM_KEYWORDS = {
    'Facebook': ['facebook', 'fb.com', 'facebook.com', 'facebook ads', 'facebook lead ads', 'fb ads', 'meta ads', 'fb.me'],
    'Instagram': ['instagram', 'ig.com', 'instagram.com', 'instagram ads', 'ig ads', 'insta', 'instagr.am'],
    'LinkedIn': ['linkedin', 'linkedin.com', 'linkedin ads', 'lnkd.in', 'linked in'],
    'Twitter': ['twitter', 'twitter.com', 'x.com', 'twitter ads', 't.co', 'tweet', 'x ads'],
    'TikTok': ['tiktok', 'tiktok.com', 'tiktok ads', 'tt ads', 'tik tok'],
    'YouTube': ['youtube', 'youtube.com', 'youtu.be', 'youtube ads', 'yt.com', 'youtube.mx'],
    'Google_Ads': ['google ads', 'google adwords', 'adwords', 'googleads', 'paid_search', 'cpc', 'ppc', 'sem'],
    'Eventbrite': ['eventbrite', 'eventbrite.com', 'eventbrite.mx', 'evbuc.com'],
    'WhatsApp': ['whatsapp', 'whatsapp.com', 'wa.me', 'whatsapp business'],
    'MAKE': ['make.com', 'make', 'integromat'],
    'AtomChat': ['atomchat', 'atom chat'],
    'Organic_Social': ['organic_social', 'organic social', 'social']
}

def detect_platforms_in_text(text, platform_keywords=PLATFORM_KEYWORDS):
    """Search for platform keywords in text and return a Counter of platform mentions"""
    if pd.isna(text) or text == "":
        return Counter()
    
    text_lower = str(text).lower()
    platform_counts = Counter()
    
    for platform, keywords in platform_keywords.items():
        for keyword in keywords:
            keyword_lower = keyword.lower()
            count = text_lower.count(keyword_lower)
            if count > 0:
                platform_counts[platform] += count
    
    return platform_counts

def extract_platform_signals(row, text_columns):
    """Extract platform signals from multiple text columns for a single row"""
    all_counts = Counter()
    
    for col in text_columns:
        if col in row.index and pd.notna(row[col]):
            text = row[col]
            counts = detect_platforms_in_text(text)
            all_counts.update(counts)
    
    return all_counts

def detect_offline_source(text):
    """Check if text contains 'offline' indicator"""
    if pd.isna(text) or text == "":
        return False
    
    text_lower = str(text).lower()
    return 'offline' in text_lower

def count_offline_mentions(text):
    """Count total number of offline mentions in historical data"""
    if pd.isna(text) or text == "":
        return 0
    
    text_lower = str(text).lower()
    return text_lower.count('offline')

@st.cache_data
def process_cluster1_data(_data, cache_key=None):
    """Process data for Cluster 1 analysis
    
    Args:
        _data: Input dataframe (underscore prevents caching on this param)
        cache_key: String to bust cache when filters change (NO underscore = used for cache hashing)
    """
    
    df = _data.copy()
    
    # Column mapping
    column_map = {
        'Record ID': 'contact_id',
        'Broadcast Clicks': 'broadcast_clicks',
        'LinkedIn Clicks': 'linkedin_clicks',
        'Twitter Clicks': 'twitter_clicks',
        'Facebook Clicks': 'facebook_clicks',
        'Number of Sessions': 'num_sessions',
        'Number of Pageviews': 'num_pageviews',
        'Number of Form Submissions': 'forms_submitted',
        'Original Source': 'original_source',
        'Original Source Drill-Down 1': 'original_source_d1',
        'Original Source Drill-Down 2': 'original_source_d2',
        'Canal de adquisición': 'canal_de_adquisicion',
        'Latest Traffic Source': 'latest_source',
        'Last Referring Site': 'last_referrer',
        'Likelihood to close': 'likelihood_to_close',
        'Create Date': 'create_date',
        'Close Date': 'close_date',
        'Lifecycle Stage': 'lifecycle_stage',
        'Propiedad del contacto': 'propiedad_del_contacto'
    }
    
    # Rename columns
    df = df.rename(columns=column_map)
    
    # Apply hist_latest to get latest values
    text_cols = ['original_source', 'original_source_d1', 'original_source_d2', 
                 'canal_de_adquisicion', 'latest_source', 'last_referrer']
    
    for col in text_cols:
        if col in df.columns:
            df[f'{col}_latest'] = df[col].apply(hist_latest)
            df[f'{col}_hist_all'] = df[col].apply(hist_concat_text)
    
    # Convert numeric columns
    numeric_cols = ['broadcast_clicks', 'linkedin_clicks', 'twitter_clicks', 'facebook_clicks',
                   'num_sessions', 'num_pageviews', 'forms_submitted', 'likelihood_to_close']
    
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col].apply(hist_latest), errors='coerce').fillna(0)
    
    # Calculate total social clicks
    click_cols = ['broadcast_clicks', 'linkedin_clicks', 'twitter_clicks', 'facebook_clicks']
    df['social_clicks_total'] = df[[c for c in click_cols if c in df.columns]].sum(axis=1)
    
    # Filter for APREU contacts only
    if 'propiedad_del_contacto' in df.columns:
        df['propiedad_del_contacto'] = df['propiedad_del_contacto'].apply(hist_latest)
        df = df[df['propiedad_del_contacto'].str.upper() == 'APREU'].copy()
    
    # Filter out "Other" and "subscriber" lifecycle stages
    if 'lifecycle_stage' in df.columns:
        df['lifecycle_stage'] = df['lifecycle_stage'].apply(hist_latest)
        df = df[~df['lifecycle_stage'].str.lower().isin(['other', 'subscriber'])].copy()
    
    # Filter for paid_social and paid_search only
    if 'original_source_latest' in df.columns:
        df = df[df['original_source_latest'].str.lower().isin(['paid_social', 'paid_search'])].copy()
    
    # Extract platform signals from historical data
    search_columns = [f'{c}_hist_all' for c in text_cols if f'{c}_hist_all' in df.columns]
    search_columns += [f'{c}_latest' for c in text_cols if f'{c}_latest' in df.columns]
    
    platform_signals = df.apply(
        lambda row: extract_platform_signals(row, search_columns), 
        axis=1
    )
    
    # Create platform count columns
    for platform in PLATFORM_KEYWORDS.keys():
        df[f'platform_count_{platform}'] = platform_signals.apply(
            lambda counter: counter.get(platform, 0)
        )
    
    # Total platform mentions and diversity
    platform_count_cols = [f'platform_count_{p}' for p in PLATFORM_KEYWORDS.keys()]
    df['platform_mentions_total'] = df[platform_count_cols].sum(axis=1)
    df['platform_diversity'] = (df[platform_count_cols] > 0).sum(axis=1)
    
    # Define socially engaged cohort
    has_clicks = df['social_clicks_total'] > 0
    has_platform_mentions = df['platform_mentions_total'] > 0
    
    social_keywords = ['facebook', 'instagram', 'linkedin', 'twitter', 'tiktok', 'youtube', 
                      'social', 'fb', 'ig', 'ads', 'eventbrite', 'make', 'atomchat']
    
    def is_social_source(val):
        if pd.isna(val):
            return False
        val_lower = str(val).lower()
        return any(kw in val_lower for kw in social_keywords)
    
    has_social_source = False
    for col in ['original_source_latest', 'original_source_d1_latest', 'original_source_d2_latest',
                'canal_de_adquisicion_latest', 'latest_source_latest', 'last_referrer_latest']:
        if col in df.columns:
            has_social_source = has_social_source | df[col].apply(is_social_source)
    
    df['is_socially_engaged'] = has_clicks | has_platform_mentions | has_social_source
    
    # Filter to socially engaged cohort
    cohort = df[df['is_socially_engaged']].copy()
    
    # Feature engineering
    for col in ['social_clicks_total', 'num_sessions', 'num_pageviews', 'forms_submitted']:
        if col in cohort.columns:
            cohort[f'log_{col}'] = np.log1p(cohort[col])
    
    # Ratios
    cohort['pageviews_per_session'] = cohort['num_pageviews'] / (1 + cohort['num_sessions'])
    cohort['forms_per_session'] = cohort['forms_submitted'] / (1 + cohort['num_sessions'])
    cohort['forms_per_click'] = cohort['forms_submitted'] / (1 + cohort['social_clicks_total'])
    
    # Replace inf/nan
    for c in ['pageviews_per_session', 'forms_per_session', 'forms_per_click']:
        cohort[c] = cohort[c].replace([np.inf, -np.inf], np.nan).fillna(0)
    
    # Clustering
    feature_cols = [
        'log_social_clicks_total', 'log_num_sessions',
        'log_num_pageviews', 'log_forms_submitted',
        'pageviews_per_session', 'forms_per_session', 'forms_per_click'
    ]
    
    feature_cols = [c for c in feature_cols if c in cohort.columns]
    
    if len(cohort) > 0 and len(feature_cols) > 0:
        X_num = cohort[feature_cols].fillna(0)
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X_num)
        
        kmeans = KMeans(n_clusters=2, random_state=42, n_init=10)
        cohort['cluster'] = kmeans.fit_predict(X_scaled)
        
        # Calculate engagement scores
        cohort['engagement_score'] = (
            cohort.get('log_num_sessions', 0) +
            cohort.get('log_num_pageviews', 0) +
            cohort.get('log_forms_submitted', 0)
        )
        cohort['social_intensity'] = cohort.get('log_social_clicks_total', 0)
        
        # Label clusters
        cluster_stats = (
            cohort.groupby('cluster')[['engagement_score', 'social_intensity']]
            .mean()
            .assign(combined=lambda df: df['engagement_score'] + df['social_intensity'])
        )
        
        cluster_1A = cluster_stats['combined'].idxmax()
        cluster_1B = [c for c in cluster_stats.index if c != cluster_1A][0]
        
        label_map = {cluster_1A: '1A - Alto Compromiso', cluster_1B: '1B - Bajo Compromiso'}
        cohort['segment_engagement'] = cohort['cluster'].map(label_map)
        
        # Platform tagging
        def platform_tag(row):
            platform_scores = {}
            for platform in ['Facebook', 'Instagram', 'LinkedIn', 'Twitter', 'TikTok',
                           'YouTube', 'Google_Ads', 'Eventbrite', 'WhatsApp', 'MAKE']:
                count_col = f'platform_count_{platform}'
                if count_col in row.index:
                    platform_scores[platform] = row[count_col]
            
            if platform_scores:
                dominant = max(platform_scores.items(), key=lambda x: x[1])
                if dominant[1] > 0:
                    return dominant[0]
            
            return 'Mixed'
        
        cohort['platform_tag'] = cohort.apply(platform_tag, axis=1)
        cohort['segment_overlay'] = cohort['segment_engagement'] + ' + ' + cohort['platform_tag']
    else:
        cohort['segment_engagement'] = 'Unknown'
        cohort['platform_tag'] = 'Unknown'
        cohort['segment_overlay'] = 'Unknown'
    
    # Detect offline sources - using FULL HISTORICAL DATA for richer analysis
    # Instead of just latest, we count ALL offline mentions across interaction history
    
    # Extract offline mention counts from historical data
    offline_count_original = pd.Series(0, index=cohort.index)
    offline_count_latest = pd.Series(0, index=cohort.index)
    
    # Check original source fields (full history)
    for col in ['original_source_hist_all', 'original_source_d1_hist_all', 'original_source_d2_hist_all']:
        if col in cohort.columns:
            offline_count_original = offline_count_original + cohort[col].apply(count_offline_mentions)
    
    # Check latest source fields (full history) 
    for col in ['latest_source_hist_all', 'last_referrer_hist_all']:
        if col in cohort.columns:
            offline_count_latest = offline_count_latest + cohort[col].apply(count_offline_mentions)
    
    # Total offline mentions across all history
    cohort['offline_mentions_total'] = offline_count_original + offline_count_latest
    cohort['has_offline_source'] = cohort['offline_mentions_total'] > 0
    
    # Classification based on where offline appears in journey
    cohort['offline_type'] = 'Online'
    cohort['offline_intensity'] = 'None'
    
    # Classify by offline touchpoints
    has_original_offline = offline_count_original > 0
    has_latest_offline = offline_count_latest > 0
    
    cohort.loc[has_original_offline & ~has_latest_offline, 'offline_type'] = 'Offline (Original Only)'
    cohort.loc[~has_original_offline & has_latest_offline, 'offline_type'] = 'Offline (Latest Only)'
    cohort.loc[has_original_offline & has_latest_offline, 'offline_type'] = 'Offline (Throughout)'
    
    # Intensity based on total mentions
    cohort['offline_intensity'] = cohort['offline_mentions_total'].apply(
        lambda x: 'None' if x == 0 else ('Low (1-2)' if x <= 2 else ('Medium (3-5)' if x <= 5 else 'High (6+)'))
    )
    
    # Calculate days to close and TTC bucket
    if 'create_date' in cohort.columns and 'close_date' in cohort.columns:
        cohort['days_to_close'] = cohort.apply(
            lambda row: calculate_days_to_close(row['create_date'], row['close_date']),
            axis=1
        )
        cohort['ttc_bucket'] = cohort['days_to_close'].apply(categorize_ttc)
    
    # Normalize likelihood to close
    if 'likelihood_to_close' in cohort.columns:
        s = cohort['likelihood_to_close']
        s = np.where(s > 1, s / 100.0, s)
        cohort['likelihood_to_close_norm'] = pd.Series(s, index=cohort.index).clip(0, 1)
    
    return cohort

def create_cluster1_xlsx_export(cohort):
    """Create comprehensive XLSX workbook with 25+ analysis sheets"""
    from io import BytesIO
    import pandas as pd
    from utils import hist_latest
    
    # Apply hist_latest to get only the latest values for export
    cohort_export = cohort.copy()
    
    # Columns that should show only latest value in exports
    latest_only_cols = ['latest_source', 'lifecycle_stage', 'original_source', 
                        'canal_de_adquisicion', 'last_referrer']
    
    for col in latest_only_cols:
        if col in cohort_export.columns:
            cohort_export[col] = cohort_export[col].apply(hist_latest)
    
    output = BytesIO()
    
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        # Use cohort_export instead of cohort for all sheets
        # 1. Counts by engagement
        counts_eng = cohort_export['segment_engagement'].value_counts().to_frame('count')
        counts_eng.to_excel(writer, sheet_name="1_counts_by_engagement")
        
        # 2. Counts by platform
        counts_plat = cohort_export['platform_tag'].value_counts().to_frame('count')
        counts_plat.to_excel(writer, sheet_name="2_counts_by_platform")
        
        # 3. Counts by overlay
        counts_overlay = cohort_export['segment_overlay'].value_counts().to_frame('count')
        counts_overlay.to_excel(writer, sheet_name="3_counts_by_overlay")
        
        # 4. Overlay share
        shares_overlay = (cohort_export['segment_overlay'].value_counts(normalize=True) * 100).round(2).to_frame('pct')
        shares_overlay.to_excel(writer, sheet_name="4_overlay_share")
        
        # 5. Numeric means by engagement
        numeric_cols = ['num_sessions', 'num_pageviews', 'forms_submitted', 'social_clicks_total', 'engagement_score']
        numeric_cols = [c for c in numeric_cols if c in cohort_export.columns]
        if numeric_cols:
            numeric_means_by_eng = cohort_export.groupby('segment_engagement')[numeric_cols].mean().round(2)
            numeric_means_by_eng.to_excel(writer, sheet_name="5_means_by_engagement")
        
        # 6. Numeric means by overlay
        if numeric_cols:
            numeric_means_by_overlay = cohort_export.groupby('segment_overlay')[numeric_cols].mean().round(2)
            numeric_means_by_overlay.to_excel(writer, sheet_name="6_means_by_overlay")
        
        # 7. Latest source by overlay (using latest values only)
        if 'latest_source' in cohort_export.columns:
            latest_source_pct = cohort_export.groupby(['segment_overlay', 'latest_source']).size().unstack(fill_value=0)
            latest_source_pct_norm = latest_source_pct.div(latest_source_pct.sum(axis=1), axis=0) * 100
            latest_source_pct_norm.to_excel(writer, sheet_name="7_latest_source_by_overlay")
        
        # 8-9. Lifecycle by engagement (using latest values only)
        if 'lifecycle_stage' in cohort_export.columns:
            lifecycle_by_eng = cohort_export.groupby(['segment_engagement', 'lifecycle_stage']).size().unstack(fill_value=0)
            lifecycle_by_eng.to_excel(writer, sheet_name="8_lifecycle_by_engagement")
            
            lifecycle_by_overlay = cohort_export.groupby(['segment_overlay', 'lifecycle_stage']).size().unstack(fill_value=0)
            lifecycle_by_overlay.to_excel(writer, sheet_name="9_lifecycle_by_overlay")
        
        # 10-11. Most common lifecycle stage (using latest values only)
        if 'lifecycle_stage' in cohort_export.columns:
            most_common_by_eng = cohort_export.groupby('segment_engagement')['lifecycle_stage'].agg(lambda x: x.mode()[0] if len(x.mode()) > 0 else 'Unknown').to_frame('most_common_stage')
            most_common_by_eng.to_excel(writer, sheet_name="10_most_common_stage_eng")
            
            most_common_by_overlay = cohort_export.groupby('segment_overlay')['lifecycle_stage'].agg(lambda x: x.mode()[0] if len(x.mode()) > 0 else 'Unknown').to_frame('most_common_stage')
            most_common_by_overlay.to_excel(writer, sheet_name="11_most_common_stage_overlay")
        
        # 12-13. Likelihood by segment
        if 'likelihood_to_close_norm' in cohort_export.columns:
            likelihood_by_eng = cohort_export.groupby('segment_engagement')['likelihood_to_close_norm'].agg(['mean', 'median', 'std']).round(3)
            likelihood_by_eng.to_excel(writer, sheet_name="12_likelihood_by_engagement")
            
            likelihood_by_overlay = cohort_export.groupby('segment_overlay')['likelihood_to_close_norm'].agg(['mean', 'median', 'std']).round(3)
            likelihood_by_overlay.to_excel(writer, sheet_name="13_likelihood_by_overlay")
        
        # 14-15. Closure stats
        if 'close_date' in cohort_export.columns:
            cohort_copy = cohort_export.copy()
            cohort_copy['is_closed'] = cohort_copy['close_date'].notna()
            
            closure_by_eng = cohort_copy.groupby('segment_engagement').agg({
                'is_closed': ['sum', 'mean'],
                'days_to_close': ['mean', 'median']
            }).round(2)
            closure_by_eng.to_excel(writer, sheet_name="14_closure_stats_by_eng")
            
            closure_by_overlay = cohort_copy.groupby('segment_overlay').agg({
                'is_closed': ['sum', 'mean'],
                'days_to_close': ['mean', 'median']
            }).round(2)
            closure_by_overlay.to_excel(writer, sheet_name="15_closure_stats_by_overlay")
        
        # 16-17. Time-to-close buckets
        if 'ttc_bucket' in cohort_export.columns:
            ttc_by_eng = cohort_export.groupby(['segment_engagement', 'ttc_bucket']).size().unstack(fill_value=0)
            ttc_by_eng.to_excel(writer, sheet_name="16_ttc_buckets_by_eng")
            
            ttc_by_overlay = cohort_export.groupby(['segment_overlay', 'ttc_bucket']).size().unstack(fill_value=0)
            ttc_by_overlay.to_excel(writer, sheet_name="17_ttc_buckets_by_overlay")
        
        # 18-19. Comprehensive bucket analysis
        if 'ttc_bucket' in cohort_export.columns and 'close_date' in cohort_export.columns:
            segment_bucket_df = cohort_export.groupby(['segment_engagement', 'ttc_bucket']).size().reset_index(name='count')
            segment_bucket_df.to_excel(writer, sheet_name="18_comprehensive_bucket_eng", index=False)
            
            overlay_bucket_df = cohort_export.groupby(['segment_overlay', 'ttc_bucket']).size().reset_index(name='count')
            overlay_bucket_df.to_excel(writer, sheet_name="19_comprehensive_bucket_overlay", index=False)
        
        # 20. Overall bucket summary
        if 'ttc_bucket' in cohort_export.columns:
            bucket_summary = cohort_export['ttc_bucket'].value_counts().to_frame('count')
            bucket_summary.to_excel(writer, sheet_name="20_overall_bucket_summary")
        
        # 21-22. Fast/Slow closers cross-analysis
        if 'days_to_close' in cohort_export.columns and cohort_export['days_to_close'].notna().sum() > 0:
            closed = cohort_export[cohort_export['close_date'].notna()].copy()
            if len(closed) > 0:
                median_ttc = closed['days_to_close'].median()
                closed['closer_type'] = closed['days_to_close'].apply(lambda x: 'Fast' if x <= median_ttc else 'Slow')
                
                fast_cross = pd.crosstab(closed['segment_engagement'], closed['platform_tag'], 
                                        values=closed['days_to_close'], aggfunc='count', margins=True).fillna(0)
                slow_cross = fast_cross.copy()  # Simplified for now
                
                fast_cross.to_excel(writer, sheet_name="21_fast_closers_eng_x_platform")
                slow_cross.to_excel(writer, sheet_name="22_slow_closers_eng_x_platform")
        
        # 23-24. Platform breakdown
        platform_breakdown_overall = cohort_export.groupby('platform_tag').size().to_frame('count')
        platform_breakdown_overall.to_excel(writer, sheet_name="23_platform_breakdown_overall")
        
        platform_within_eng = cohort_export.groupby(['segment_engagement', 'platform_tag']).size().unstack(fill_value=0)
        platform_within_eng.to_excel(writer, sheet_name="24_platform_within_engagement")
        
        # 25-26. Offline analysis
        if 'offline_type' in cohort_export.columns:
            offline_counts = cohort_export['offline_type'].value_counts().to_frame('count')
            offline_counts.to_excel(writer, sheet_name="25_offline_type_counts")
            
            offline_by_eng = cohort_export.groupby(['segment_engagement', 'offline_type']).size().unstack(fill_value=0)
            offline_by_eng.to_excel(writer, sheet_name="26_offline_by_engagement")
        
        # 27-28. Offline intensity analysis (based on historical mentions)
        if 'offline_intensity' in cohort_export.columns:
            intensity_counts = cohort_export['offline_intensity'].value_counts().to_frame('count')
            intensity_counts.to_excel(writer, sheet_name="27_offline_intensity_counts")
            
            intensity_by_eng = cohort_export.groupby(['segment_engagement', 'offline_intensity']).size().unstack(fill_value=0)
            intensity_by_eng.to_excel(writer, sheet_name="28_offline_intensity_by_engagement")
        
        # 29. Run metadata
        meta = pd.DataFrame({
            'Campo': ['Fecha de Exportación', 'Total Contactos', 'Contactos Filtrados', 'Segmentos'],
            'Valor': [
                pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S'),
                str(len(cohort_export)),
                str(len(cohort_export)),
                ', '.join(cohort_export['segment_engagement'].unique())
            ]
        })
        meta.to_excel(writer, sheet_name="29_run_metadata", index=False)
    
    output.seek(0)
    return output.getvalue()

def render_cluster1(data):
    """Render Cluster 1 analysis interface"""
    
    st.markdown("## 📱 Cluster 1: Prospectos Socialmente Comprometidos")
    
    # About this analysis
    with st.expander("ℹ️ Acerca de Este Análisis", expanded=False):
        st.markdown("""
        ### 🎯 Qué Hace Este Cluster
        **Identifica prospectos con actividad en redes sociales** usando análisis integral de datos históricos y detección multi-plataforma.
        
        ### 👥 Quién Debe Usar Esto
        - **Equipos de Redes Sociales** - Optimizar estrategia por plataforma
        - **Marketing Digital** - Asignar presupuesto de redes sociales
        - **Campañas de Remarketing** - Dirigir por preferencia de plataforma
        
        ### 🔑 Preguntas Clave Respondidas
        - ¿Qué plataformas sociales impulsan más compromiso?
        - ¿Los leads de Instagram cierran más rápido que los de Facebook?
        - ¿Cuál es el ROI de cada plataforma de redes sociales?
        - ¿Qué combinación de plataforma + compromiso funciona mejor?
        
        ### 📊 Segmentos Definidos
        - **1A (Alto Compromiso)** - Usuarios sociales activos con fuerte interacción (sesiones, formularios, páginas vistas)
        - **1B (Bajo Compromiso)** - Presencia social pero compromiso mínimo en el sitio web
        - **Superposiciones de Plataforma** - Etiquetas combinadas como "1A + Instagram", "1B + Facebook" para targeting preciso
        
        ### 💡 Ejemplo de Insight
        *"Los contactos 1A + Instagram tienen una tasa de cierre del 35% y cierran 20 días más rápido que 1B + Facebook"*
        → **Acción:** Aumentar gasto en anuncios de Instagram, crear contenido específico para 1A
        """)
    
    st.markdown("---")
    
    if data is None:
        st.error("⚠️ Datos no cargados.")
        return
    
    # Process data with cache busting based on data length
    # This ensures the cache refreshes when global filters change the data
    cache_key = f"c1_{len(data)}_{data['Record ID'].iloc[0] if 'Record ID' in data.columns else 'na'}"
    with st.spinner("Procesando datos del Cluster 1..."):
        cohort = process_cluster1_data(data, cache_key)
    
    # Show contact count AFTER core filters (APREU + removing other/subscriber)
    if data is not None:
        active_filters = sum(1 for k in st.session_state.keys() if k.startswith('filter_'))
        if active_filters > 0:
            st.info(f"🔍 Analizando {len(cohort):,} contactos después de aplicar filtros principales (APREU, excluyendo 'other'/'subscriber') + filtros globales")
        else:
            st.info(f"📊 Analizando {len(cohort):,} contactos después de aplicar filtros principales (APREU, excluyendo 'other'/'subscriber')")
    
    if len(cohort) == 0:
        st.warning("No se encontraron prospectos socialmente comprometidos con los filtros actuales.")
        return
    
    # Add cluster-specific filters
    with st.expander("🎛️ Filtros Específicos del Cluster 1", expanded=False):
        col1, col2 = st.columns(2)
        
        with col1:
            # Segment filter
            available_segments = sorted(cohort['segment_engagement'].unique())
            selected_segments = st.multiselect(
                "Filtrar por Segmento:",
                options=available_segments,
                default=available_segments,
                help="Seleccionar segmentos de compromiso a incluir"
            )
            
            # Platform filter
            available_platforms = sorted(cohort['platform_tag'].unique())
            selected_platforms = st.multiselect(
                "Filtrar por Plataforma:",
                options=available_platforms,
                default=available_platforms,
                help="Seleccionar plataformas a incluir"
            )
        
        with col2:
            # Social clicks filter
            min_social_clicks = st.number_input(
                "Mín. Clics Sociales:", 
                min_value=0, 
                value=0,
                help="Filtrar contactos con al menos esta cantidad de clics sociales"
            )
            
            # Engagement score filter
            if 'engagement_score' in cohort.columns:
                min_engagement = st.slider(
                    "Puntuación Mín. de Compromiso:",
                    min_value=float(cohort['engagement_score'].min()),
                    max_value=float(cohort['engagement_score'].max()),
                    value=float(cohort['engagement_score'].min()),
                    help="Filtrar por puntuación mínima de compromiso"
                )
            else:
                min_engagement = 0
        
        # Apply cluster-specific filters
        cohort_filtered = cohort[
            (cohort['segment_engagement'].isin(selected_segments)) &
            (cohort['platform_tag'].isin(selected_platforms)) &
            (cohort['social_clicks_total'] >= min_social_clicks)
        ]
        
        if 'engagement_score' in cohort.columns and min_engagement > 0:
            cohort_filtered = cohort_filtered[cohort_filtered['engagement_score'] >= min_engagement]
        
        st.info(f"✅ Mostrando {len(cohort_filtered):,} de {len(cohort):,} contactos después de filtros del cluster")
    
    # Use filtered cohort for all subsequent analysis
    cohort = cohort_filtered
    
    # Export functionality
    with st.expander("📥 Exportar Datos", expanded=False):
        st.markdown("**Descargar datos filtrados:**")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Export full cohort with notebook-standard columns
            export_cols = [
                # identifiers
                "contact_id",
                # raw clicks & engagement
                "broadcast_clicks", "linkedin_clicks", "twitter_clicks", "facebook_clicks",
                "social_clicks_total", "num_sessions", "num_pageviews", "forms_submitted",
                # engineered scores
                "pageviews_per_session", "forms_per_session", "forms_per_click",
                "engagement_score", "social_intensity",
                # sources/referrers
                "original_source", "original_source_d1", "original_source_d2",
                "canal_de_adquisicion", "latest_source", "last_referrer", "last_referrer_domain",
                # cluster results
                "cluster",
                # overlay labels
                "segment_engagement", "platform_tag", "segment_overlay",
                # online vs offline - historical engagement
                "offline_type", "has_offline_source", "offline_mentions_total", "offline_intensity",
                # lifecycle & outcomes
                "lifecycle_stage", "likelihood_to_close_norm",
                # dates & closure
                "create_date", "close_date", "days_to_close", "ttc_bucket",
                # academic periods
                "periodo_ingreso", "periodo_admision"
            ]
            
            # Filter to existing columns
            export_cols = [c for c in export_cols if c in cohort.columns]
            df_export = cohort[export_cols].copy()
            
            # Format dates
            if "create_date" in df_export.columns:
                df_export["create_date"] = pd.to_datetime(df_export["create_date"]).dt.strftime("%Y-%m-%d").fillna("unknown")
            if "close_date" in df_export.columns:
                df_export["close_date"] = pd.to_datetime(df_export["close_date"]).dt.strftime("%Y-%m-%d").fillna("unknown")
            if "days_to_close" in df_export.columns:
                df_export["days_to_close"] = df_export["days_to_close"].fillna("unknown")
            
            csv_data = df_export.to_csv(index=False, encoding='utf-8-sig')
            st.download_button(
                    label="📄 Descargar Datos Completos (CSV)",
                data=csv_data.encode('utf-8'),
                file_name=f"cluster1_full_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv",
                use_container_width=True
            )
        
        with col2:
            # Export comprehensive XLSX workbook
            with st.spinner("Generando libro de trabajo Excel integral..."):
                xlsx_data = create_cluster1_xlsx_export(cohort)
                st.download_button(
                    label="📊 Descargar Libro de Trabajo Integral (XLSX) - 25+ Hojas",
                    data=xlsx_data,
                    file_name=f"cluster1_summary_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    use_container_width=True,
                    help="Libro de trabajo de análisis integral con 25+ hojas: conteos, métricas de compromiso, ciclo de vida, estadísticas de cierre, desgloses por plataforma, ¡y más!"
                )
    
    # Create tabs for different analyses
    tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8, tab9 = st.tabs([
        "📊 Resumen", "🎯 Análisis de Segmento", "🏷️ Análisis de Plataforma", 
        "💰 Resultados de Negocio", "⚡ Cerradores Rápidos/Lentos", "🌐 En Línea vs Fuera de Línea",
        "📅 Período Académico", "🔬 Benchmarks de Rendimiento", "🔍 Búsqueda de Contactos"
    ])
    
    with tab1:
        render_overview_tab(cohort)
    
    with tab2:
        render_segment_analysis_tab(cohort)
    
    with tab3:
        render_platform_analysis_tab(cohort)
    
    with tab4:
        render_outcomes_tab(cohort)
    
    with tab5:
        render_fast_slow_closers_c1(cohort)
    
    with tab6:
        render_online_offline_analysis_tab(cohort)
    
    with tab7:
        render_academic_period_tab(cohort)
    
    with tab8:
        render_performance_benchmarks_c1(cohort)
    
    with tab9:
        render_contact_lookup_tab(cohort)

def render_overview_tab(cohort):
    """Render overview tab"""
    st.markdown("### 📊 Resumen Ejecutivo")
    
    # Key metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Socialmente Comprometidos", f"{len(cohort):,}")
    
    with col2:
        seg_1a_count = (cohort['segment_engagement'] == '1A - Alto Compromiso').sum()
        st.metric("1A (Alto Compromiso)", f"{seg_1a_count:,}")
    
    with col3:
        seg_1b_count = (cohort['segment_engagement'] == '1B - Bajo Compromiso').sum()
        st.metric("1B (Bajo Compromiso)", f"{seg_1b_count:,}")
    
    with col4:
        close_rate = calculate_close_rate(cohort)
        st.metric("Tasa de Cierre General", f"{close_rate:.1f}%")
    
    st.markdown("---")
    
    # Segment distribution chart
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### Distribución de Segmentos de Compromiso")
        fig = create_segment_pie_chart(cohort, 'segment_engagement', title="Distribución por Compromiso - Leyenda: 1A=Alto Compromiso, 1B=Bajo Compromiso")
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.markdown("#### Principales Plataformas")
        platform_counts = cohort['platform_tag'].value_counts().head(10)
        fig = px.bar(
            x=platform_counts.values,
            y=platform_counts.index,
            orientation='h',
            title="Top 10 Etiquetas de Plataformas",
            labels={'x': 'Contactos', 'y': 'Plataforma'},
            color=platform_counts.values,
            color_continuous_scale='Viridis'
        )
        fig.update_layout(showlegend=False, height=400)
        st.plotly_chart(fig, use_container_width=True)
    
    # Platform mention summary
    st.markdown("#### Resumen de Detección de Plataformas")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        contacts_with_platform = (cohort['platform_mentions_total'] > 0).sum()
        st.metric("Contactos con Señales de Plataforma", f"{contacts_with_platform:,}")
    
    with col2:
        contacts_with_2plus = (cohort['platform_diversity'] >= 2).sum()
        st.metric("Contactos con 2+ Plataformas", f"{contacts_with_2plus:,}")
    
    with col3:
        avg_diversity = cohort['platform_diversity'].mean()
        st.metric("Diversidad Promedio de Plataformas", f"{avg_diversity:.1f}")

def render_segment_analysis_tab(cohort):
    """Render segment analysis tab"""
    st.markdown("### 🎯 1A vs 1B Comparación de Segmentos")
    
    # Segment comparison metrics
    segment_comparison = cohort.groupby('segment_engagement').agg({
        'contact_id': 'count',
        'num_sessions': 'mean',
        'num_pageviews': 'mean',
        'forms_submitted': 'mean',
        'engagement_score': 'mean',
        'social_clicks_total': 'mean',
        'close_date': lambda x: x.notna().sum()
    }).round(2)
    
    segment_comparison.columns = ['Contacts', 'Avg Sessions', 'Avg Pageviews', 
                                  'Avg Forms', 'Avg Engagement Score', 
                                  'Avg Social Clicks', 'Closed Count']
    
    segment_comparison['Close Rate %'] = (
        segment_comparison['Closed Count'] / segment_comparison['Contacts'] * 100
    ).round(1)
    
    st.dataframe(segment_comparison, use_container_width=True)
    
    st.markdown("---")
    
    # Engagement metrics comparison
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### Distribución de Puntuación de Compromiso")
        fig = px.box(
            cohort, x='segment_engagement', y='engagement_score',
            color='segment_engagement',
            title="Puntuación de Compromiso por Segmento (1A=Alto Compromiso, 1B=Bajo Compromiso)",
            labels={'segment_engagement': 'Segmento', 'engagement_score': 'Puntuación de Compromiso'},
            color_discrete_map={'1A - Alto Compromiso': '#2ecc71', '1B - Bajo Compromiso': '#e74c3c'}
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.markdown("#### Distribución de Sesiones")
        fig = px.box(
            cohort, x='segment_engagement', y='num_sessions',
            color='segment_engagement',
            title="Número de Sesiones por Segmento (1A=Alto Compromiso, 1B=Bajo Compromiso)",
            labels={'segment_engagement': 'Segmento', 'num_sessions': 'Sesiones'},
            color_discrete_map={'1A - Alto Compromiso': '#2ecc71', '1B - Bajo Compromiso': '#e74c3c'}
        )
        st.plotly_chart(fig, use_container_width=True)
    
    # Lifecycle stage distribution
    st.markdown("#### Distribución de Etapa del Ciclo de Vida por Segmento")
    
    if 'lifecycle_stage' in cohort.columns:
        lifecycle_dist = pd.crosstab(
            cohort['segment_engagement'],
            cohort['lifecycle_stage'],
            normalize='index'
        ) * 100
        
        fig = px.bar(
            lifecycle_dist,
            barmode='group',
            title="Distribución de Etapa del Ciclo de Vida (%)",
            labels={'value': 'Porcentaje', 'variable': 'Etapa del Ciclo de Vida'},
            color_discrete_sequence=px.colors.qualitative.Set2
        )
        st.plotly_chart(fig, use_container_width=True)

def render_platform_analysis_tab(cohort):
    """Render platform analysis tab"""
    st.markdown("### 🏷️ Análisis de Plataformas")
    
    # Overlay segment distribution
    st.markdown("#### Principales Segmentos de Superposición (Compromiso + Plataforma)")
    
    overlay_counts = cohort['segment_overlay'].value_counts().head(15)
    
    fig = px.bar(
        x=overlay_counts.values,
        y=overlay_counts.index,
        orientation='h',
        title="Top 15 Segmentos de Superposición",
        labels={'x': 'Contactos', 'y': 'Segmento de Superposición'},
        color=overlay_counts.values,
        color_continuous_scale='Blues'
    )
    fig.update_layout(showlegend=False, height=600)
    st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("---")
    
    # Platform breakdown within each engagement segment
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### Distribución de Plataformas en 1A")
        seg_1a = cohort[cohort['segment_engagement'] == '1A - Alto Compromiso']
        platform_1a = seg_1a['platform_tag'].value_counts().head(8)
        
        fig = px.pie(
            values=platform_1a.values,
            names=platform_1a.index,
            title="Mezcla de Plataformas 1A",
            hole=0.3
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.markdown("#### Distribución de Plataformas en 1B")
        seg_1b = cohort[cohort['segment_engagement'] == '1B - Bajo Compromiso']
        platform_1b = seg_1b['platform_tag'].value_counts().head(8)
        
        fig = px.pie(
            values=platform_1b.values,
            names=platform_1b.index,
            title="Mezcla de Plataformas 1B",
            hole=0.3
        )
        st.plotly_chart(fig, use_container_width=True)
    
    # Platform mention details
    st.markdown("#### Estadísticas de Menciones de Plataformas")
    
    platform_stats = []
    for platform in PLATFORM_KEYWORDS.keys():
        col = f'platform_count_{platform}'
        if col in cohort.columns:
            contacts_with = (cohort[col] > 0).sum()
            total_mentions = cohort[col].sum()
            avg = cohort[cohort[col] > 0][col].mean() if contacts_with > 0 else 0
            
            platform_stats.append({
                'Platform': platform,
                'Contacts': contacts_with,
                'Total Mentions': int(total_mentions),
                'Avg Mentions': round(avg, 1)
            })
    
    platform_stats_df = pd.DataFrame(platform_stats).sort_values('Contacts', ascending=False)
    st.dataframe(platform_stats_df, use_container_width=True, height=400)

def render_fast_slow_closers_c1(cohort):
    """Render fast/slow closers analysis"""
    st.markdown("### ⚡ Análisis de Cerradores Rápidos vs Lentos")
    st.markdown("Identifica qué combinaciones cierran más rápido para optimizar tu estrategia")
    
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
    
    # Fast closers: Segment × Platform analysis
    st.markdown("#### ⚡ Fast Closers (≤60 days): Engagement × Platform")
    st.markdown("¿Qué combinaciones cierran más rápido?")
    
    fast_closers = closed[closed['closure_speed'] == 'Fast (≤60 days)']
    
    if len(fast_closers) > 0:
        # Create cross-tab
        fast_crosstab = pd.crosstab(
            fast_closers['segment_engagement'],
            fast_closers['platform_tag'],
            margins=True,
            margins_name='Total'
        )
        
        st.markdown("**Conteos:**")
        st.dataframe(fast_crosstab, use_container_width=True)
        
        # Heatmap
        try:
            fig = px.imshow(
                fast_crosstab.iloc[:-1, :-1],  # Exclude margins
                labels=dict(x="Plataforma", y="Segmento", color="Conteo"),
                title="Mapa de Calor Cerradores Rápidos: Compromiso × Plataforma",
                color_continuous_scale='Greens',
                aspect="auto"
            )
            st.plotly_chart(fig, use_container_width=True)
        except:
            # If heatmap fails, show bar chart instead
            pass
    else:
        st.info("No hay cerradores rápidos en este dataset.")
    
    st.markdown("---")
    
    # Slow closers: Segment × Platform analysis
    st.markdown("#### 🐌 Slow Closers (>180 days): Engagement × Platform")
    st.markdown("¿Qué combinaciones necesitan más atención?")
    
    slow_closers = closed[closed['closure_speed'] == 'Slow (>180 days)']
    
    if len(slow_closers) > 0:
        # Create cross-tab
        slow_crosstab = pd.crosstab(
            slow_closers['segment_engagement'],
            slow_closers['platform_tag'],
            margins=True,
            margins_name='Total'
        )
        
        st.markdown("**Conteos:**")
        st.dataframe(slow_crosstab, use_container_width=True)
        
        # Heatmap
        try:
            fig = px.imshow(
                slow_crosstab.iloc[:-1, :-1],  # Exclude margins
                labels=dict(x="Plataforma", y="Segmento", color="Conteo"),
                title="Mapa de Calor Cerradores Lentos: Compromiso × Plataforma",
                color_continuous_scale='Reds',
                aspect="auto"
            )
            st.plotly_chart(fig, use_container_width=True)
        except:
            # If heatmap fails, show bar chart instead
            pass
    else:
        st.info("No hay cerradores lentos en este dataset.")
    
    st.markdown("---")
    
    # Insights
    st.markdown("#### 💡 Insights Clave")
    
    insights = []
    
    if len(fast_closers) > 0:
        # Best performing combination
        fast_by_combo = fast_closers.groupby(['segment_engagement', 'platform_tag']).size()
        if len(fast_by_combo) > 0:
            best_combo = fast_by_combo.idxmax()
            best_count = fast_by_combo.max()
            insights.append(f"✅ **Best Fast Closer Combination:** {best_combo[0]} + {best_combo[1]} ({best_count} contacts)")
    
    if len(slow_closers) > 0:
        # Worst performing combination
        slow_by_combo = slow_closers.groupby(['segment_engagement', 'platform_tag']).size()
        if len(slow_by_combo) > 0:
            worst_combo = slow_by_combo.idxmax()
            worst_count = slow_by_combo.max()
            insights.append(f"⚠️ **Most Common Slow Closer Combination:** {worst_combo[0]} + {worst_combo[1]} ({worst_count} contacts)")
    
    # Overall ratio
    if len(fast_closers) > 0 and len(slow_closers) > 0:
        ratio = len(fast_closers) / len(slow_closers)
        insights.append(f"📊 **Fast/Slow Ratio:** {ratio:.2f}x (For every slow closer, you have {ratio:.1f} fast closers)")
    
    if insights:
        for insight in insights:
            st.markdown(insight)
    else:
        st.info("No hay suficientes datos para insights")

def render_outcomes_tab(cohort):
    """Render business outcomes tab"""
    st.markdown("### 💰 Resultados de Negocio y Rendimiento")
    
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
            st.markdown("**Distribución por Etapa:**")
            for stage, count in lifecycle_counts.head(5).items():
                pct = (count / len(cohort) * 100)
                st.metric(stage, f"{count:,}", delta=f"{pct:.1f}%")
        
        # Lifecycle by segment
        st.markdown("**Etapa del Ciclo de Vida por Segmento de Compromiso:**")
        
        lifecycle_by_segment = pd.crosstab(
            cohort['lifecycle_stage'],
            cohort['segment_engagement'],
            normalize='columns'
        ) * 100
        
        # Show top 8 stages
        top_stages = cohort['lifecycle_stage'].value_counts().head(8).index
        lifecycle_filtered = lifecycle_by_segment.loc[lifecycle_by_segment.index.isin(top_stages)]
        
        st.dataframe(lifecycle_filtered.round(1), use_container_width=True)
        
        st.markdown("---")
    else:
        st.info("Datos de etapa del ciclo de vida no disponibles")
    
    # Traffic Source Analysis
    st.markdown("#### 🔗 Rendimiento de Fuente de Tráfico")
    
    if 'latest_source' in cohort.columns:
        top_sources = cohort['latest_source'].value_counts().head(10)
        
        # Source performance metrics
        source_performance = []
        for source in top_sources.head(8).index:
            source_contacts = cohort[cohort['latest_source'] == source]
            closed = source_contacts['close_date'].notna().sum()
            close_rate = (closed / len(source_contacts) * 100) if len(source_contacts) > 0 else 0
            avg_engagement = source_contacts['engagement_score'].mean() if 'engagement_score' in source_contacts.columns else 0
            
            source_performance.append({
                'Fuente de Tráfico': source,
                'Contactos': len(source_contacts),
                'Cerrados': closed,
                'Tasa de Cierre %': round(close_rate, 1),
                'Compromiso Prom.': round(avg_engagement, 2)
            })
        
        if source_performance:
            source_df = pd.DataFrame(source_performance).sort_values('Tasa de Cierre %', ascending=False)
            st.dataframe(source_df, use_container_width=True)
        
        st.markdown("---")
    
    # Close rate by segment
    col1, col2, col3 = st.columns(3)
    
    with col1:
        seg_1a = cohort[cohort['segment_engagement'] == '1A - Alto Compromiso']
        close_rate_1a = calculate_close_rate(seg_1a)
        st.metric("1A Close Rate", f"{close_rate_1a:.1f}%")
    
    with col2:
        seg_1b = cohort[cohort['segment_engagement'] == '1B - Bajo Compromiso']
        close_rate_1b = calculate_close_rate(seg_1b)
        st.metric("1B Close Rate", f"{close_rate_1b:.1f}%")
    
    with col3:
        if 'likelihood_to_close_norm' in cohort.columns:
            avg_likelihood = cohort['likelihood_to_close_norm'].mean() * 100
            st.metric("Probabilidad Promedio de Cierre", f"{avg_likelihood:.1f}%")
    
    st.markdown("---")
    
    # Time to close analysis
    if 'ttc_bucket' in cohort.columns:
        st.markdown("#### Análisis de Tiempo hasta Cierre")
        
        ttc_dist = pd.crosstab(
            cohort['segment_engagement'],
            cohort['ttc_bucket'],
            normalize='index'
        ) * 100
        
        # Reorder columns
        bucket_order = ['Early (≤30 days)', 'Medium (31-60 days)', 'Late (61-120 days)', 
                       'Very Late (>120 days)', 'Still Open']
        ttc_dist = ttc_dist[[col for col in bucket_order if col in ttc_dist.columns]]
        
        fig = px.bar(
            ttc_dist,
            barmode='group',
            title="Distribución de Tiempo hasta Cierre por Segmento (%)",
            labels={'value': 'Porcentaje', 'variable': 'Grupo TTC'},
            color_discrete_sequence=['#2ecc71', '#f39c12', '#e67e22', '#e74c3c', '#95a5a6']
        )
        st.plotly_chart(fig, use_container_width=True)
        
        # Average days to close
        if 'days_to_close' in cohort.columns:
            st.markdown("#### Días Promedio hasta Cierre (Solo Contactos Cerrados)")
            
            closed_cohort = cohort[cohort['days_to_close'].notna()]
            if len(closed_cohort) > 0:
                avg_days = closed_cohort.groupby('segment_engagement')['days_to_close'].agg(['mean', 'median']).round(1)
                st.dataframe(avg_days, use_container_width=True)
    
    st.markdown("---")
    
    # Top performing overlays
    st.markdown("#### Segmentos de Superposición con Mejor Rendimiento")
    
    overlay_performance = cohort.groupby('segment_overlay').agg({
        'contact_id': 'count',
        'close_date': lambda x: x.notna().sum()
    })
    overlay_performance.columns = ['Total', 'Cerrados']
    overlay_performance['Tasa de Cierre %'] = (
        overlay_performance['Cerrados'] / overlay_performance['Total'] * 100
    ).round(1)
    
    # Filter to segments with at least 20 contacts
    overlay_performance = overlay_performance[overlay_performance['Total'] >= 20]
    overlay_performance = overlay_performance.sort_values('Tasa de Cierre %', ascending=False).head(15)
    
    st.dataframe(overlay_performance, use_container_width=True)

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
    
    # Step 1: Original Source
    original_source = contact.get('original_source', None)
    if original_source and str(original_source) not in ["Unknown", "nan", "", "None"]:
        journey_steps.append({
            'step': 'Original Source',
            'value': str(original_source),
            'color': '#4CAF50'
        })
    
    # Step 2: Historical Latest Source values (if available in raw data)
    if raw_data is not None and 'Latest Traffic Source' in raw_data.columns:
        raw_matches = raw_data[raw_data['Record ID'].astype(str) == key]
        if len(raw_matches) > 0:
            latest_source_raw = raw_matches.iloc[0]['Latest Traffic Source']
            historical_sources = hist_all(latest_source_raw)
            
            for i, source in enumerate(historical_sources):
                if str(source) not in ["Unknown", "nan", "", "None"]:
                    journey_steps.append({
                        'step': f'Touch {i+1}',
                        'value': str(source),
                        'color': '#2196F3'
                    })
    else:
        # Use latest source from processed data if available
        latest_source = contact.get('latest_source', None)
        if latest_source and str(latest_source) not in ["Unknown", "nan", "", "None"]:
            journey_steps.append({
                'step': 'Latest Source',
                'value': str(latest_source),
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

def render_online_offline_analysis_tab(cohort):
    """Render online vs offline analysis tab"""
    st.markdown("### 🌐 Análisis de Compromiso En Línea vs Fuera de Línea")
    st.markdown("Comprende la mezcla de puntos de contacto en línea (sociales) y fuera de línea en el compromiso de tus prospectos")
    
    # Check if offline data is available
    if 'offline_type' not in cohort.columns:
        st.warning("⚠️ Datos de fuente fuera de línea no disponibles en este dataset")
        return
    
    st.markdown("---")
    
    # 1. Overall online vs offline breakdown
    st.markdown("#### 📊 Distribución General En Línea vs Fuera de Línea")
    
    offline_counts = cohort['offline_type'].value_counts()
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        fig = px.pie(
            values=offline_counts.values,
            names=offline_counts.index,
            title="¿Cuántos Contactos Tienen Puntos de Contacto Fuera de Línea?",
            color_discrete_sequence=['#3498db', '#e74c3c', '#f39c12', '#2ecc71']
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.markdown("**Tus Contactos:**")
        for offline_type, count in offline_counts.items():
            pct = (count / len(cohort) * 100)
            st.write(f"• {offline_type}: {count:,} ({pct:.0f}%)")
    
    st.markdown("---")
    
    # 1b. Offline Interaction Intensity (NEW - based on historical data)
    st.markdown("#### 🔥 Intensidad de Interacción Fuera de Línea (Menciones Históricas)")
    st.markdown("*¿Cuántas veces interactuaron los contactos con fuentes fuera de línea?*")
    
    if 'offline_intensity' in cohort.columns:
        intensity_counts = cohort['offline_intensity'].value_counts()
        intensity_order = ['None', 'Low (1-2)', 'Medium (3-5)', 'High (6+)']
        intensity_counts = intensity_counts.reindex([i for i in intensity_order if i in intensity_counts.index])
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Bar chart
            fig = px.bar(
                x=intensity_counts.index,
                y=intensity_counts.values,
                title="Distribución de Intensidad de Interacción Fuera de Línea",
                labels={'x': 'Nivel de Intensidad', 'y': 'Número de Contactos'},
                color=intensity_counts.index,
                color_discrete_map={
                    'None': '#3498db',
                    'Low (1-2)': '#f39c12',
                    'Medium (3-5)': '#e67e22',
                    'High (6+)': '#e74c3c'
                }
            )
            fig.update_layout(showlegend=False)
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.markdown("**Resumen**")
            if 'offline_mentions_total' in cohort.columns:
                offline_contacts = cohort[cohort['offline_mentions_total'] > 0]
                if len(offline_contacts) > 0:
                    pct = (len(offline_contacts) / len(cohort) * 100)
                    st.write(f"**{len(offline_contacts):,} contacts** with offline touches ({pct:.0f}%)")
                    st.write(f"**Average:** {offline_contacts['offline_mentions_total'].mean():.1f} offline touches per contact")
                    st.write(f"**Range:** 1 to {int(offline_contacts['offline_mentions_total'].max())} touches")
                else:
                    st.info("No hay interacciones fuera de línea en tus datos")
    
    st.markdown("---")
    
    # 2. Online vs Offline by Engagement Segment
    st.markdown("#### 🎯 En Línea vs Fuera de Línea por Segmento de Compromiso")
    
    if 'segment_engagement' in cohort.columns:
        offline_by_segment = pd.crosstab(
            cohort['segment_engagement'],
            cohort['offline_type'],
            margins=True,
            margins_name='Total'
        )
        
        st.dataframe(offline_by_segment, use_container_width=True)
        
        # Percentage view
        st.markdown("**Percentage Distribution by Segment:**")
        offline_by_segment_pct = pd.crosstab(
            cohort['segment_engagement'],
            cohort['offline_type'],
            normalize='index'
        ) * 100
        
        st.dataframe(offline_by_segment_pct.round(1), use_container_width=True)
        
        # Stacked bar chart
        fig = px.bar(
            offline_by_segment_pct,
            barmode='stack',
            title="Distribución En Línea vs Fuera de Línea por Segmento (%)",
            labels={'value': '% del Segmento', 'variable': 'Tipo'},
            color_discrete_sequence=['#3498db', '#e74c3c', '#f39c12', '#2ecc71']
        )
        st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("---")
    
    # 3. Online vs Offline by Platform
    st.markdown("#### 🏷️ Online vs Offline by Platform")
    
    if 'platform_tag' in cohort.columns:
        # Get top platforms
        top_platforms = cohort['platform_tag'].value_counts().head(8).index
        cohort_top_platforms = cohort[cohort['platform_tag'].isin(top_platforms)]
        
        offline_by_platform = pd.crosstab(
            cohort_top_platforms['platform_tag'],
            cohort_top_platforms['offline_type']
        )
        
        st.markdown("**Counts by Top 8 Platforms:**")
        st.dataframe(offline_by_platform, use_container_width=True)
        
        # Percentage within each platform
        offline_by_platform_pct = pd.crosstab(
            cohort_top_platforms['platform_tag'],
            cohort_top_platforms['offline_type'],
            normalize='index'
        ) * 100
        
        st.markdown("**Percentage Distribution Within Each Platform:**")
        st.dataframe(offline_by_platform_pct.round(1), use_container_width=True)
    
    st.markdown("---")
    
    # 4. Performance comparison: Online vs Offline
    st.markdown("#### 💰 Métricas de Rendimiento: En Línea vs Fuera de Línea")
    
    performance_metrics = cohort.groupby('offline_type').agg({
        'contact_id': 'count',
        'num_sessions': 'mean',
        'num_pageviews': 'mean',
        'forms_submitted': 'mean',
        'social_clicks_total': 'mean',
        'engagement_score': 'mean',
        'close_date': lambda x: x.notna().sum()
    }).round(2)
    
    performance_metrics.columns = ['Contactos', 'Sesiones Prom', 'Páginas Vistas Prom', 
                                   'Formularios Prom', 'Clics Sociales Prom', 'Compromiso Prom', 'Cerrados']
    
    performance_metrics['Tasa de Cierre %'] = (
        performance_metrics['Cerrados'] / performance_metrics['Contactos'] * 100
    ).round(1)
    
    st.dataframe(performance_metrics, use_container_width=True)
    
    # Visualize close rates
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**Comparación de Tasa de Cierre:**")
        close_rate_data = performance_metrics[['Tasa de Cierre %']].reset_index()
        fig = px.bar(
            close_rate_data,
            x='offline_type',
            y='Tasa de Cierre %',
            title="Tasa de Cierre: En Línea vs Fuera de Línea",
            labels={'offline_type': 'Tipo', 'Tasa de Cierre %': 'Tasa de Cierre %'},
            color='Tasa de Cierre %',
            color_continuous_scale='RdYlGn'
        )
        fig.update_layout(showlegend=False)
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.markdown("**Comparación de Puntuación de Compromiso:**")
        engagement_data = performance_metrics[['Compromiso Prom']].reset_index()
        fig = px.bar(
            engagement_data,
            x='offline_type',
            y='Compromiso Prom',
            title="Puntuación Promedio de Compromiso: En Línea vs Fuera de Línea",
            labels={'offline_type': 'Tipo', 'Compromiso Prom': 'Puntuación de Compromiso'},
            color='Compromiso Prom',
            color_continuous_scale='Viridis'
        )
        fig.update_layout(showlegend=False)
        st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("---")
    
    # 5. Time to close analysis
    st.markdown("#### ⏱️ Time to Close: Online vs Offline")
    
    if 'days_to_close' in cohort.columns:
        closed_cohort = cohort[cohort['days_to_close'].notna()]
        
        if len(closed_cohort) > 0:
            ttc_by_offline = closed_cohort.groupby('offline_type')['days_to_close'].agg(['count', 'mean', 'median', 'std']).round(2)
            ttc_by_offline.columns = ['Count', 'Mean Days', 'Median Days', 'Std Dev']
            
            st.dataframe(ttc_by_offline, use_container_width=True)
            
            # Box plot
            fig = px.box(
                closed_cohort,
                x='offline_type',
                y='days_to_close',
                title="Distribución de Días hasta Cierre: En Línea vs Fuera de Línea",
                labels={'offline_type': 'Tipo', 'days_to_close': 'Días hasta Cierre'},
                color='offline_type',
                color_discrete_sequence=['#3498db', '#e74c3c', '#f39c12', '#2ecc71']
            )
            st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("---")
    
    # 6. Lifecycle stage distribution
    st.markdown("#### 🔄 Etapa del Ciclo de Vida: En Línea vs Fuera de Línea")
    
    if 'lifecycle_stage' in cohort.columns:
        lifecycle_offline = pd.crosstab(
            cohort['offline_type'],
            cohort['lifecycle_stage'],
            normalize='index'
        ) * 100
        
        # Top 6 stages
        top_stages = cohort['lifecycle_stage'].value_counts().head(6).index
        lifecycle_filtered = lifecycle_offline[lifecycle_offline.columns.intersection(top_stages)]
        
        st.markdown("**Principales Etapas del Ciclo de Vida por En Línea/Fuera de Línea (%):**")
        st.dataframe(lifecycle_filtered.round(1), use_container_width=True)
    
    st.markdown("---")
    
    # 7. Key insights
    st.markdown("#### 💡 Insights Clave")
    
    insights = []
    
    # Online vs Offline volume comparison
    online_count = offline_counts.get('Online', 0)
    offline_total = len(cohort) - online_count
    
    if online_count > 0 and offline_total > 0:
        ratio = online_count / offline_total if offline_total > 0 else 0
        insights.append(f"📊 **Proporción de Volumen:** {ratio:.1f}x más contactos En Línea que Fuera de Línea")
    
    # Performance comparison
    if 'Tasa de Cierre %' in performance_metrics.columns:
        online_rate = performance_metrics.loc['Online', 'Tasa de Cierre %'] if 'Online' in performance_metrics.index else 0
        offline_rates = [performance_metrics.loc[idx, 'Tasa de Cierre %'] 
                        for idx in performance_metrics.index if idx != 'Online' and 'Tasa de Cierre %' in performance_metrics.columns]
        
        if offline_rates:
            avg_offline_rate = np.mean(offline_rates)
            if online_rate > avg_offline_rate:
                diff = online_rate - avg_offline_rate
                insights.append(f"✅ **En Línea Rinde Mejor:** {diff:.1f}% mayor tasa de cierre")
            elif avg_offline_rate > online_rate:
                diff = avg_offline_rate - online_rate
                insights.append(f"⚠️ **Fuera de Línea Rinde Mejor:** {diff:.1f}% mayor tasa de cierre")
    
    # Engagement comparison
    if 'Compromiso Prom' in performance_metrics.columns and 'Online' in performance_metrics.index:
        online_engagement = performance_metrics.loc['Online', 'Compromiso Prom']
        offline_engagements = [performance_metrics.loc[idx, 'Compromiso Prom'] 
                              for idx in performance_metrics.index if idx != 'Online']
        
        if offline_engagements:
            avg_offline_engagement = np.mean(offline_engagements)
            if online_engagement > avg_offline_engagement:
                insights.append(f"🚀 **En Línea Más Comprometido:** {online_engagement:.2f} vs {avg_offline_engagement:.2f} promedio fuera de línea")
    
    # Hybrid strategy indicator
    hybrid_count = offline_counts.get('Offline (Both)', 0)
    if hybrid_count > 0:
        hybrid_pct = (hybrid_count / len(cohort) * 100)
        insights.append(f"🔗 **Oportunidad de Estrategia Híbrida:** {hybrid_pct:.1f}% tienen contacto tanto en línea como fuera de línea")
    
    if insights:
        for insight in insights:
            st.markdown(insight)
    else:
        st.info("No hay suficientes datos para insights")

def render_academic_period_tab(cohort):
    """Render academic period analysis tab"""
    st.markdown("### 📅 Academic Period (Seasonal) Analysis")
    st.markdown("Comprende los ciclos de inscripción y tendencias estacionales")
    
    # Look for academic period fields
    period_fields = [
        'periodo_de_ingreso', 'Periodo de ingreso', 'periodo_ingreso',
        'Periodo de ingreso a licenciatura (MQL)', 'PERIODO DE INGRESO'
    ]
    
    period_col = None
    for field in period_fields:
        if field in cohort.columns:
            period_col = field
            break
    
    if period_col is None:
        st.warning("📅 Datos de período académico no disponibles en el dataset")
        st.info("""
        **Campo esperado:** 'Periodo de ingreso' o similar
        
        **Formato:** YYYYMM (p. ej., 202408 para Agosto 2024)
        
        Este análisis muestra:
        - Patrones de inscripción estacionales
        - Rendimiento por período de admisión
        - Tendencias de compromiso a lo largo del tiempo
        """)
        return
    
    # Convert academic period to readable format
    # Based on YYYYMM format where MM codes are:
    # 05 = Special, 10 = Spring, 35 = Summer, 60 = Fall, 75 = Winter/Special
    def convert_academic_period(period_code):
        """Convert YYYYMM to readable format"""
        try:
            if pd.isna(period_code):
                return "Desconocido"
            
            period_str = str(int(period_code)).strip()
            if len(period_str) != 6:
                return "Desconocido"
            
            year = period_str[:4]
            period = int(period_str[4:])
            
            # Map period codes to semester names (from notebooks)
            period_map = {
                5: "Especial",
                10: "Primavera", 
                35: "Verano",
                60: "Otoño",
                75: "Winter/Special"
            }
            
            semester = period_map.get(period, f"Unknown({period})")
            return f"{year} {semester}"
        except:
            return "Unknown"
    
    # Apply conversion
    cohort_periodo = cohort.copy()
    cohort_periodo['periodo_readable'] = cohort_periodo[period_col].apply(convert_academic_period)
    
    # Filter out Unknown
    cohort_periodo = cohort_periodo[cohort_periodo['periodo_readable'] != 'Unknown']
    
    if len(cohort_periodo) == 0:
        st.warning("No se encontraron datos válidos de período académico")
        return
    
    st.success(f"📊 Analizando {len(cohort_periodo):,} contactos con datos válidos de período de admisión")
    
    # 1. Basic counts by period
    st.markdown("#### 📊 Volumen de Contactos por Período de Admisión")
    
    periodo_counts = cohort_periodo['periodo_readable'].value_counts().sort_index()
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Create DataFrame for proper Plotly plotting
        periodo_df = pd.DataFrame({
            'Admission Period': periodo_counts.index,
            'Number of Contacts': periodo_counts.values
        })
        
        # Simple bar chart with single color for clarity
        fig = px.bar(
            periodo_df,
            x='Admission Period',
            y='Number of Contacts',
                title="Contactos por Período de Admisión (Cronológico)"
        )
        # Use a single professional color
        fig.update_traces(marker_color='#3498db')
        fig.update_layout(
            showlegend=False, 
            xaxis_tickangle=-45,
            yaxis_title="Número de Contactos",
            xaxis_title="Período de Admisión"
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.markdown("**Top 5 Largest Periods:**")
        # Sort by count descending to show actual top periods
        top_5 = periodo_counts.nlargest(5)
        for period, count in top_5.items():
            pct = (count / len(cohort_periodo) * 100)
            # Show percentage as label, not as delta (which implies growth)
            st.metric(
                label=period, 
                value=f"{count:,} contactos",
                help=f"Representa {pct:.1f}% de todos los contactos en este análisis"
            )
    
    st.markdown("---")
    
    # 2. Engagement metrics by period
    st.markdown("#### 📈 Engagement Metrics by Period")
    
    engagement_cols = ['engagement_score', 'num_sessions', 'num_pageviews', 'forms_submitted', 'social_clicks_total']
    available_engagement = [col for col in engagement_cols if col in cohort_periodo.columns]
    
    if available_engagement:
        periodo_engagement = cohort_periodo.groupby('periodo_readable')[available_engagement].mean().round(2)
        periodo_engagement = periodo_engagement.sort_index()
        
        st.dataframe(periodo_engagement, use_container_width=True)
        
        # Engagement score trend
        if 'engagement_score' in available_engagement:
            fig = px.line(
                x=periodo_engagement.index,
                y=periodo_engagement['engagement_score'],
                title="Tendencia de Puntuación de Compromiso por Período",
                labels={'x': 'Período', 'y': 'Puntuación Prom. de Compromiso'},
                markers=True
            )
            fig.update_layout(xaxis_tickangle=-45)
            st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("---")
    
    # 3. Segment distribution by period
    st.markdown("#### 🎯 Segment Distribution by Period")
    
    if 'segment_engagement' in cohort_periodo.columns:
        seg_by_period = pd.crosstab(
            cohort_periodo['periodo_readable'],
            cohort_periodo['segment_engagement'],
            normalize='index'
        ) * 100
        
        seg_by_period = seg_by_period.sort_index()
        
        st.dataframe(seg_by_period.round(1), use_container_width=True)
        
        # Stacked bar chart
        fig = px.bar(
            seg_by_period,
            barmode='stack',
            title="Distribución de Segmentos por Período",
            labels={'value': '% de Contactos', 'variable': 'Segmento'},
            color_discrete_sequence=px.colors.qualitative.Set2
        )
        fig.update_layout(xaxis_tickangle=-45)
        st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("---")
    
    # 4. Platform distribution by period
    st.markdown("#### 🏷️ Platform Distribution by Period")
    
    if 'platform_tag' in cohort_periodo.columns:
        # Get top platforms
        top_platforms = cohort_periodo['platform_tag'].value_counts().head(6).index
        
        platform_by_period = pd.crosstab(
            cohort_periodo['periodo_readable'],
            cohort_periodo['platform_tag'],
            normalize='index'
        ) * 100
        
        platform_by_period = platform_by_period.sort_index()
        
        # Filter to top platforms
        platform_filtered = platform_by_period[platform_by_period.columns.intersection(top_platforms)]
        
        st.dataframe(platform_filtered.round(1), use_container_width=True)
    
    st.markdown("---")
    
    # 5. Close rates by period
    st.markdown("#### 💰 Rendimiento por Período")
    
    periodo_performance = []
    for period in periodo_counts.head(10).index:
        period_data = cohort_periodo[cohort_periodo['periodo_readable'] == period]
        
        total = len(period_data)
        closed = period_data['close_date'].notna().sum() if 'close_date' in period_data.columns else 0
        close_rate = (closed / total * 100) if total > 0 else 0
        
        avg_engagement = period_data['engagement_score'].mean() if 'engagement_score' in period_data.columns else 0
        
        periodo_performance.append({
            'Period': period,
            'Total': total,
            'Closed': closed,
            'Close Rate %': round(close_rate, 1),
            'Avg Engagement': round(avg_engagement, 2)
        })
    
    if periodo_performance:
        perf_df = pd.DataFrame(periodo_performance)
        st.dataframe(perf_df, use_container_width=True)
        
        # Close rate trend
        fig = px.line(
            perf_df, x='Period', y='Close Rate %',
            title="Tendencia de Tasa de Cierre por Período de Admisión",
            markers=True,
            color_discrete_sequence=['#2ecc71']
        )
        fig.update_layout(xaxis_tickangle=-45)
        st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("---")
    
    # 6. Lifecycle stages by period
    st.markdown("#### 🔄 Etapa del Ciclo de Vida por Período")
    
    if 'lifecycle_stage' in cohort_periodo.columns:
        # Get top lifecycle stages
        top_stages = cohort_periodo['lifecycle_stage'].value_counts().head(6).index
        
        lifecycle_by_period = pd.crosstab(
            cohort_periodo['periodo_readable'],
            cohort_periodo['lifecycle_stage'],
            normalize='index'
        ) * 100
        
        lifecycle_by_period = lifecycle_by_period.sort_index()
        
        # Filter to top stages
        lifecycle_filtered = lifecycle_by_period[lifecycle_by_period.columns.intersection(top_stages)]
        
        st.dataframe(lifecycle_filtered.round(1), use_container_width=True)
    
    # Key insights
    st.markdown("---")
    st.markdown("#### 💡 Key Insights")
    
    insights = []
    
    # Most popular period
    most_popular = periodo_counts.idxmax()
    most_popular_count = periodo_counts.max()
    insights.append(f"📊 **Most Popular Period:** {most_popular} ({most_popular_count:,} contacts)")
    
    # Best performing period (if close rate data available)
    if periodo_performance:
        best_period = max(periodo_performance, key=lambda x: x['Close Rate %'])
        insights.append(f"🏆 **Best Close Rate:** {best_period['Period']} ({best_period['Close Rate %']:.1f}%)")
    
    # Trend analysis
    if len(periodo_counts) >= 3:
        recent_3 = periodo_counts.tail(3).mean()
        older_3 = periodo_counts.head(3).mean()
        if recent_3 > older_3:
            trend = "increasing"
            emoji = "📈"
        else:
            trend = "decreasing"
            emoji = "📉"
        insights.append(f"{emoji} **Trend:** Volume is {trend} in recent periods")
    
    if insights:
        for insight in insights:
            st.markdown(insight)

def render_performance_benchmarks_c1(cohort):
    """Render performance benchmarks tab"""
    st.markdown("### 🔬 Performance Benchmarks & Comparisons")
    st.markdown("Compara segmentos contra indicadores clave de rendimiento")
    
    st.markdown("---")
    
    # Benchmark metrics by segment
    st.markdown("#### 📊 Key Performance Indicators by Segment")
    
    benchmark_metrics = cohort.groupby('segment_engagement').agg({
        'contact_id': 'count',
        'num_sessions': ['mean', 'median', 'std'],
        'num_pageviews': ['mean', 'median', 'std'],
        'forms_submitted': ['mean', 'median', 'std'],
        'social_clicks_total': ['mean', 'median', 'std'],
        'engagement_score': ['mean', 'median', 'std'],
        'close_date': lambda x: x.notna().sum()
    }).round(2)
    
    # Flatten columns
    benchmark_metrics.columns = ['_'.join(col).strip('_') for col in benchmark_metrics.columns.values]
    benchmark_metrics['close_rate_pct'] = (benchmark_metrics['close_date_<lambda>'] / benchmark_metrics['contact_id_count'] * 100).round(1)
    
    st.dataframe(benchmark_metrics, use_container_width=True)
    
    st.markdown("---")
    
    # Platform performance comparison
    st.markdown("#### 🏷️ Platform Performance Comparison")
    
    platform_performance = cohort.groupby('platform_tag').agg({
        'contact_id': 'count',
        'num_sessions': 'mean',
        'engagement_score': 'mean',
        'close_date': lambda x: x.notna().sum()
    }).round(2)
    
    platform_performance.columns = ['Count', 'Avg Sessions', 'Avg Engagement', 'Closed']
    platform_performance['Close Rate %'] = (platform_performance['Closed'] / platform_performance['Count'] * 100).round(1)
    platform_performance = platform_performance.sort_values('Close Rate %', ascending=False).head(15)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.dataframe(platform_performance, use_container_width=True)
    
    with col2:
        fig = px.bar(
            x=platform_performance.index,
            y=platform_performance['Close Rate %'],
            title="Tasa de Cierre por Plataforma (Top 15)",
            labels={'x': 'Plataforma', 'y': 'Tasa de Cierre %'},
            color=platform_performance['Close Rate %'],
            color_continuous_scale='RdYlGn'
        )
        fig.update_layout(xaxis_tickangle=-45, showlegend=False)
        st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("---")
    
    # Engagement distribution quartiles
    st.markdown("#### 📈 Engagement Score Quartile Analysis")
    
    quartiles = cohort['engagement_score'].quantile([0.25, 0.5, 0.75, 0.9])
    
    def categorize_engagement_quartile(score):
        if score <= quartiles[0.25]:
            return 'Q1 (Bottom 25%)'
        elif score <= quartiles[0.5]:
            return 'Q2 (25-50%)'
        elif score <= quartiles[0.75]:
            return 'Q3 (50-75%)'
        elif score <= quartiles[0.9]:
            return 'Q4 (75-90%)'
        else:
            return 'Top 10%'
    
    cohort_q = cohort.copy()
    cohort_q['engagement_quartile'] = cohort_q['engagement_score'].apply(categorize_engagement_quartile)
    
    quartile_analysis = cohort_q.groupby('engagement_quartile').agg({
        'contact_id': 'count',
        'close_date': lambda x: x.notna().sum()
    })
    quartile_analysis.columns = ['Count', 'Closed']
    quartile_analysis['Close Rate %'] = (quartile_analysis['Closed'] / quartile_analysis['Count'] * 100).round(1)
    
    # Ensure proper ordering
    quartile_order = ['Q1 (Bottom 25%)', 'Q2 (25-50%)', 'Q3 (50-75%)', 'Q4 (75-90%)', 'Top 10%']
    quartile_analysis = quartile_analysis.reindex([q for q in quartile_order if q in quartile_analysis.index])
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.dataframe(quartile_analysis, use_container_width=True)
        
        st.markdown("**Quartile Thresholds:**")
        st.write(f"- Q1: ≤ {quartiles[0.25]:.2f}")
        st.write(f"- Q2: {quartiles[0.25]:.2f} - {quartiles[0.5]:.2f}")
        st.write(f"- Q3: {quartiles[0.5]:.2f} - {quartiles[0.75]:.2f}")
        st.write(f"- Q4: {quartiles[0.75]:.2f} - {quartiles[0.9]:.2f}")
        st.write(f"- Top 10%: > {quartiles[0.9]:.2f}")
    
    with col2:
        fig = px.bar(
            x=quartile_analysis.index,
            y=quartile_analysis['Close Rate %'],
            title="Tasa de Cierre por Cuartil de Compromiso",
            labels={'x': 'Cuartil', 'y': 'Tasa de Cierre %'},
            color=quartile_analysis['Close Rate %'],
            color_continuous_scale='Viridis'
        )
        fig.update_layout(xaxis_tickangle=-45, showlegend=False)
        st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("---")
    
    # Segment × Platform heatmap
    st.markdown("#### 🔥 Segment × Platform Performance Heatmap")
    
    heatmap_data = cohort.groupby(['segment_engagement', 'platform_tag']).size().reset_index(name='count')
    heatmap_pivot = heatmap_data.pivot(index='segment_engagement', columns='platform_tag', values='count').fillna(0)
    
    # Filter to top platforms
    top_platforms = cohort['platform_tag'].value_counts().head(10).index
    heatmap_pivot = heatmap_pivot[heatmap_pivot.columns.intersection(top_platforms)]
    
    fig = px.imshow(
        heatmap_pivot,
        labels=dict(x="Plataforma", y="Segmento", color="Contactos"),
        title="Distribución de Contactos: Segmento × Plataforma (Top 10 Plataformas)",
        color_continuous_scale='Blues',
        aspect="auto"
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
    
    # Best performing platform
    if len(platform_performance) > 0:
        best_platform = platform_performance['Close Rate %'].idxmax()
        best_platform_rate = platform_performance['Close Rate %'].max()
        insights.append(f"🎯 **Best Performing Platform:** {best_platform} ({best_platform_rate:.1f}% close rate)")
    
    # Engagement correlation
    if 'days_to_close' in cohort.columns:
        closed_cohort = cohort[cohort['days_to_close'].notna()]
        if len(closed_cohort) > 0:
            correlation = closed_cohort['engagement_score'].corr(closed_cohort['days_to_close'])
            if correlation < -0.3:
                insights.append(f"⚡ **Strong Inverse Correlation:** Higher engagement scores correlate with faster closing times (r={correlation:.2f})")
            elif correlation > 0.3:
                insights.append(f"⚠️ **Unexpected Pattern:** Higher engagement scores correlate with slower closing times (r={correlation:.2f})")
    
    # Quartile performance
    if len(quartile_analysis) > 0:
        top_10_rate = quartile_analysis.loc['Top 10%', 'Close Rate %'] if 'Top 10%' in quartile_analysis.index else 0
        q1_rate = quartile_analysis.loc['Q1 (Bottom 25%)', 'Close Rate %'] if 'Q1 (Bottom 25%)' in quartile_analysis.index else 0
        if top_10_rate > 0 and q1_rate > 0:
            ratio = top_10_rate / q1_rate if q1_rate > 0 else 0
            insights.append(f"📊 **Performance Gap:** Top 10% converts {ratio:.1f}x better than bottom quartile")
    
    if insights:
        for insight in insights:
            st.markdown(insight)
    else:
        st.info("No hay suficientes datos para insights")

def render_contact_lookup_tab(cohort):
    """Render contact lookup tab"""
    st.markdown("### 🔍 Individual Contact Lookup")
    
    if 'contact_id' not in cohort.columns:
        st.warning("ID de contacto no disponible en el dataset.")
        return
    
    contact_id = st.text_input("Ingresar ID de Contacto:", placeholder="p. ej., 12345")
    
    if contact_id:
        contact_id_str = str(contact_id).strip()
        matches = cohort[cohort['contact_id'].astype(str) == contact_id_str]
        
        if len(matches) == 0:
            st.error(f"No se encontró contacto con ID: {contact_id}")
        else:
            contact = matches.iloc[0]
            
            st.markdown("#### Perfil de Contacto")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.markdown("**Identificación**")
                st.write(f"**ID de Contacto:** {contact.get('contact_id', 'N/A')}")
                st.write(f"**Segmento:** {contact.get('segment_engagement', 'N/A')}")
                st.write(f"**Plataforma:** {contact.get('platform_tag', 'N/A')}")
                st.write(f"**Superposición:** {contact.get('segment_overlay', 'N/A')}")
            
            with col2:
                st.markdown("**Compromiso**")
                st.write(f"**Sesiones:** {int(contact.get('num_sessions', 0)):,}")
                st.write(f"**Páginas Vistas:** {int(contact.get('num_pageviews', 0)):,}")
                st.write(f"**Formularios:** {int(contact.get('forms_submitted', 0)):,}")
                st.write(f"**Clics Sociales:** {int(contact.get('social_clicks_total', 0)):,}")
                st.write(f"**Puntuación de Compromiso:** {contact.get('engagement_score', 0):.2f}")
            
            with col3:
                st.markdown("**Resultados**")
                if 'likelihood_to_close_norm' in contact.index:
                    likelihood = contact.get('likelihood_to_close_norm', 0) * 100
                    st.write(f"**Probabilidad:** {likelihood:.1f}%")
                
                is_closed = "Sí" if pd.notna(contact.get('close_date')) else "No"
                st.write(f"**Cerrado:** {is_closed}")
                
                if pd.notna(contact.get('days_to_close')):
                    st.write(f"**Días hasta Cierre:** {contact.get('days_to_close', 0):.0f}")
                    st.write(f"**Bucket TTC:** {contact.get('ttc_bucket', 'N/A')}")
                
                if 'lifecycle_stage' in contact.index:
                    st.write(f"**Ciclo de Vida:** {contact.get('lifecycle_stage', 'N/A')}")
            
            st.markdown("---")
            st.markdown("#### Señales de Plataforma")
            
            platform_data = []
            for platform in PLATFORM_KEYWORDS.keys():
                col = f'platform_count_{platform}'
                if col in contact.index:
                    count = contact[col]
                    if count > 0:
                        platform_data.append({'Platform': platform, 'Mentions': int(count)})
            
            if platform_data:
                platform_df = pd.DataFrame(platform_data).sort_values('Mentions', ascending=False)
                st.dataframe(platform_df, use_container_width=True)
            else:
                st.info("No se detectaron señales de plataforma para este contacto.")
            
            # Show journey visualization
            st.markdown("---")
            st.markdown("#### 🗺️ Visualización del Viaje de Fuentes")
            
            fig = visualize_source_journey(contact_id, cohort, raw_data=None)
            if fig:
                st.pyplot(fig)
                plt.close(fig)
            else:
                st.info("📊 No hay datos de recorrido disponibles para visualización")

