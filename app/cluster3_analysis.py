"""
Cluster 3: Convertidores Impulsados por Promoción (Actividades APREU)
Segmenta contactos por actividades promocionales y canales de entrada
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
from datetime import datetime
from utils import (
    hist_latest, hist_all, hist_concat_text,
    create_segment_pie_chart, create_bar_chart,
    calculate_close_rate, calculate_days_to_close, categorize_ttc,
    display_metrics, create_download_button, display_dataframe_with_style
)

# APREU Activity Classification
DIGITAL_ACTIVITIES = [
    'sitio web', 'sitio', 'website', 'web', 
    'formulario', 'formulario rua', 'rua', 'form',
    'google ads', 'facebook ads', 'ads', 'paid search',
    'organic search', 'organic', 'seo',
    'landing page', 'lp'
]

EVENT_ACTIVITIES = [
    'open day', 'openday', 'open house', 
    'fogatada', 'fogata',
    'tdla', 'tour de la admision', 'tour admisión',
    'gira panama', 'gira panamá', 'panama', 'panamá',
    'feria', 'feria universitaria', 'expo',
    'evento carrera', 'eventos carreras',
    'visita campus', 'campus tour', 'recorrido',
    'conferencia', 'charla', 'webinar',
    'día de puertas abiertas'
]

MESSAGING_ACTIVITIES = [
    'whatsapp', 'whats app', 'wa', 
    'mensaje directo', 'direct message', 'dm',
    'chat', 'messenger',
    'contacto directo', 'direct contact',
    'llamada', 'phone call', 'call'
]

NICHE_ACTIVITIES = [
    'lion leaders', 'lion leader', 'leaders',
    'programa especial', 'special program',
    'beca', 'scholarship', 'becas',
    'intercambio', 'exchange',
    'embajador', 'ambassador', 'embajadores',
    'referido', 'referral', 'referred',
    'alumni', 'ex-alumno'
]

def detect_activity_type(text, activity_dict):
    """Search for activity keywords in text and return count of matches"""
    if pd.isna(text) or text == "":
        return 0
    
    text_lower = str(text).lower()
    count = 0
    
    for keyword in activity_dict:
        if keyword in text_lower:
            count += 1
    
    return count

def classify_entry_channel(apreu_hist, first_conv, recent_conv):
    """Classify contact into entry channel segment (3A/3B/3C/3D)"""
    all_text = f"{apreu_hist} {first_conv} {recent_conv}".lower()
    
    # Count each type of activity
    digital_count = detect_activity_type(all_text, DIGITAL_ACTIVITIES)
    event_count = detect_activity_type(all_text, EVENT_ACTIVITIES)
    messaging_count = detect_activity_type(all_text, MESSAGING_ACTIVITIES)
    niche_count = detect_activity_type(all_text, NICHE_ACTIVITIES)
    
    activity_scores = {
        '3A_Digital': digital_count,
        '3B_Event': event_count,
        '3C_Messaging': messaging_count,
        '3D_Niche': niche_count
    }
    
    max_score = max(activity_scores.values())
    
    if max_score == 0:
        return 'Unknown'
    
    # Priority: Event > Digital > Messaging > Niche
    if activity_scores['3B_Event'] == max_score and max_score > 0:
        return '3B_Event'
    elif activity_scores['3A_Digital'] == max_score and max_score > 0:
        return '3A_Digital'
    elif activity_scores['3C_Messaging'] == max_score and max_score > 0:
        return '3C_Messaging'
    elif activity_scores['3D_Niche'] == max_score and max_score > 0:
        return '3D_Niche'
    else:
        return 'Unknown'

@st.cache_data
def process_cluster3_data(_data, cache_key=None):
    """Process data for Cluster 3 analysis
    
    Args:
        _data: Input dataframe (underscore prevents caching on this param)
        cache_key: String to bust cache when filters change (NO underscore = used for cache hashing)
    """
    
    df = _data.copy()
    
    # Column mapping
    column_map = {
        'Record ID': 'contact_id',
        'Actividades de promoción APREU': 'apreu_activities',
        'First Conversion': 'first_conversion',
        'Recent Conversion': 'recent_conversion',
        'First Conversion Date': 'first_conversion_date',
        'Recent Conversion Date': 'recent_conversion_date',
        'Preparatoria BPM': 'prep_bpm',
        '¿Cuál es el nombre de tu preparatoria?': 'prep_name',
        'Preparatoria donde estudia': 'prep_donde_estudia',
        '¿Qué año de preparatoria estás cursando?': 'prep_year',
        'Number of Sessions': 'num_sessions',
        'Number of Pageviews': 'num_pageviews',
        'Number of Form Submissions': 'forms_submitted',
        'Marketing emails delivered': 'email_delivered',
        'Marketing emails opened': 'email_opened',
        'Marketing emails clicked': 'email_clicked',
        'Likelihood to close': 'likelihood_to_close',
        'Create Date': 'create_date',
        'Close Date': 'close_date',
        'Lifecycle Stage': 'lifecycle_stage',
        'Propiedad del contacto': 'propiedad_del_contacto'
    }
    
    df = df.rename(columns=column_map)
    
    # Fallback: Check if close_date wasn't renamed (column didn't exist)
    # Try to find alternative close date column names
    if 'close_date' not in df.columns:
        possible_close_cols = [col for col in df.columns if 'close' in col.lower() and 'date' in col.lower()]
        if possible_close_cols:
            df = df.rename(columns={possible_close_cols[0]: 'close_date'})
    
    # Parse historical APREU activities
    if 'apreu_activities' in df.columns:
        df['apreu_hist_all'] = df['apreu_activities'].apply(hist_concat_text)
        df['apreu_activities_list'] = df['apreu_activities'].apply(hist_all)
        df['apreu_activity_count'] = df['apreu_activities_list'].apply(len)
        df['apreu_activity_diversity'] = df['apreu_activities_list'].apply(lambda x: len(set(x)))
    else:
        df['apreu_hist_all'] = ""
        df['apreu_activities_list'] = [[] for _ in range(len(df))]
        df['apreu_activity_count'] = 0
        df['apreu_activity_diversity'] = 0
    
    # Apply hist_latest to other fields
    for col in ['first_conversion', 'recent_conversion', 'prep_bpm', 'prep_name', 
                'prep_donde_estudia', 'prep_year', 'lifecycle_stage', 'propiedad_del_contacto']:
        if col in df.columns:
            df[col] = df[col].apply(hist_latest)
    
    # Convert numeric columns (apply hist_latest first!)
    numeric_cols = ['num_sessions', 'num_pageviews', 'forms_submitted', 
                   'email_delivered', 'email_opened', 'email_clicked', 'likelihood_to_close']
    
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col].apply(hist_latest), errors='coerce').fillna(0)
    
    # Convert date columns (HubSpot timestamps to datetime)
    # CRITICAL: Apply hist_latest FIRST to extract the latest date from history string!
    def convert_hubspot_timestamp(val):
        """Convert HubSpot timestamp (milliseconds since epoch) to datetime."""
        if pd.isna(val):
            return pd.NaT
        # If already a datetime, return as-is
        if isinstance(val, (pd.Timestamp, datetime)):
            return val
        # First extract latest value from history string
        val = hist_latest(val)
        if pd.isna(val):
            return pd.NaT
        try:
            timestamp_ms = int(float(str(val).strip()))
            return pd.to_datetime(timestamp_ms, unit='ms')
        except (ValueError, TypeError):
            return pd.NaT
    
    date_cols = ['create_date', 'close_date', 'first_conversion_date', 'recent_conversion_date']
    for col in date_cols:
        if col in df.columns:
            df[col] = df[col].apply(convert_hubspot_timestamp)
    
    # Calculate days_to_close (matching notebook logic)
    if 'create_date' in df.columns and 'close_date' in df.columns:
        raw_days = (df['close_date'] - df['create_date']).dt.days
        df['days_to_close'] = raw_days.where(raw_days >= 0)
        df['ttc_bucket'] = df['days_to_close'].apply(categorize_ttc)
    else:
        df['days_to_close'] = np.nan
        df['ttc_bucket'] = "Desconocido"
    
    # Filter for APREU contacts (matching Clusters 1 & 2 approach)
    if 'propiedad_del_contacto' in df.columns:
        df = df[df['propiedad_del_contacto'].str.upper() == 'APREU'].copy()
    
    # Filter out "Other" and "subscriber" lifecycle stages
    if 'lifecycle_stage' in df.columns:
        df = df[~df['lifecycle_stage'].str.lower().isin(['other', 'subscriber'])].copy()
    
    # Fill NaN values for classification
    df['apreu_hist_all'] = df['apreu_hist_all'].fillna("")
    df['first_conversion'] = df['first_conversion'].fillna("")
    df['recent_conversion'] = df['recent_conversion'].fillna("")
    
    # Classify entry channel
    df['entry_channel'] = df.apply(
        lambda row: classify_entry_channel(
            row['apreu_hist_all'], 
            row['first_conversion'], 
            row['recent_conversion']
        ), 
        axis=1
    )
    
    # Create segment labels with descriptive names
    segment_descriptions = {
        '3A_Digital': '3A - Digital Primero (Sitio Web, Formularios)',
        '3B_Event': '3B - Eventos Primero (Open Day, Fogatada, TDLA)',
        '3C_Messaging': '3C - Mensajería Primero (WhatsApp, DM)',
        '3D_Niche': '3D - Nicho/Bajo Volumen (Programas Especiales)',
        'Unknown': 'Desconocido'
    }
    
    df['segment_c3'] = df['entry_channel'].map(segment_descriptions)
    
    # Action tags
    action_tags = {
        '3A_Digital': 'Embudo de admisión acelerado + secuencias de email automatizadas',
        '3B_Event': 'Seguimiento post-evento dentro de 48h + comunicación de próximos pasos',
        '3C_Messaging': 'WhatsApp/email personalizado + prioridad de respuesta rápida (<2h)',
        '3D_Niche': 'Evaluar ROI + soporte especializado + considerar escalamiento',
        'Unknown': 'Necesita clasificación - analizar manualmente'
    }
    
    df['action_tag'] = df['entry_channel'].map(action_tags)
    
    # Consolidate preparatoria
    def consolidate_prepa(row):
        for field in ['prep_bpm', 'prep_name', 'prep_donde_estudia']:
            if field in row and pd.notna(row[field]) and str(row[field]).strip() not in ['', 'nan', 'None']:
                return str(row[field]).strip()
                return "Desconocido"
    
    df['preparatoria'] = df.apply(consolidate_prepa, axis=1)
    
    # Normalize preparatoria year
    if 'prep_year' in df.columns:
        def normalize_year(val):
            if pd.isna(val):
                return "Desconocido"
            s = str(val).strip().lower()
            if any(x in s for x in ['1', 'primer', 'first', 'uno']):
                return "1st Year"
            elif any(x in s for x in ['2', 'segundo', 'second', 'dos']):
                return "2nd Year"
            elif any(x in s for x in ['3', 'tercer', 'third', 'tres']):
                return "3rd Year"
            else:
                return "Desconocido"
        
        df['prep_year_normalized'] = df['prep_year'].apply(normalize_year)
    else:
        df['prep_year_normalized'] = "Desconocido"
    
    # Feature engineering
    df['log_sessions'] = np.log1p(df.get('num_sessions', 0))
    df['log_pageviews'] = np.log1p(df.get('num_pageviews', 0))
    df['log_forms'] = np.log1p(df.get('forms_submitted', 0))
    df['engagement_score'] = df['log_sessions'] + df['log_pageviews'] + df['log_forms']
    
    # Email engagement
    email_open_rate = np.where(
        df['email_delivered'] > 0,
        df['email_opened'] / df['email_delivered'],
        0
    )
    
    email_click_rate = np.where(
        df['email_opened'] > 0,
        df['email_clicked'] / df['email_opened'],
        0
    )
    
    df['email_engagement_score'] = (email_open_rate * 0.5) + (email_click_rate * 0.5)
    
    # Conversion journey duration (matching notebook logic)
    if 'first_conversion_date' in df.columns and 'recent_conversion_date' in df.columns:
        df['conversion_journey_days'] = (
            df['recent_conversion_date'] - df['first_conversion_date']
        ).dt.days
        df['conversion_journey_days'] = df['conversion_journey_days'].where(
            df['conversion_journey_days'] >= 0
        )
    
    # Normalize likelihood
    if 'likelihood_to_close' in df.columns:
        max_val = df['likelihood_to_close'].max()
        if max_val > 1:
            df['likelihood_pct'] = df['likelihood_to_close']
        else:
            df['likelihood_pct'] = df['likelihood_to_close'] * 100
    else:
        df['likelihood_pct'] = 0
    
    # Calculate is_closed (contacts with a close_date)
    if 'close_date' in df.columns:
        df['is_closed'] = df['close_date'].notna().astype(int)
    else:
        df['is_closed'] = 0
    
    return df

def create_cluster3_xlsx_export(cohort):
    """Create comprehensive XLSX workbook with 30+ analysis sheets"""
    from io import BytesIO
    import pandas as pd
    from utils import hist_latest
    
    # Apply hist_latest to get only the latest values for export
    cohort_export = cohort.copy()
    
    # Columns that should show only latest value in exports
    latest_only_cols = ['lifecycle_stage', 'first_conversion', 'recent_conversion']
    
    for col in latest_only_cols:
        if col in cohort_export.columns:
            cohort_export[col] = cohort_export[col].apply(hist_latest)
    
    output = BytesIO()
    
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        # 1. Executive Summary (use cohort_export with latest values)
        exec_summary = pd.DataFrame({
            'Métrica': ['Total Contactos', 'Segmentos', 'Compromiso Promedio', 'Total Cerrados', 'Días Prom hasta Cierre', 'Actividades Prom'],
            'Valor': [
                f"{len(cohort_export):,}",
                ', '.join(cohort_export['segment_c3'].unique()) if 'segment_c3' in cohort_export.columns else 'N/A',
                f"{cohort_export['engagement_score'].mean():.2f}" if 'engagement_score' in cohort_export.columns else 'N/A',
                f"{cohort_export['is_closed'].sum():,}" if 'is_closed' in cohort_export.columns else 'N/A',
                f"{cohort_export['days_to_close'].mean():.1f}" if 'days_to_close' in cohort_export.columns else 'N/A',
                f"{cohort_export['apreu_activity_count'].mean():.1f}" if 'apreu_activity_count' in cohort_export.columns else 'N/A'
            ]
        })
        exec_summary.to_excel(writer, sheet_name="1_executive_summary", index=False)
        
        # 2. Segment Counts
        if 'segment_c3' in cohort_export.columns:
            seg_counts = cohort_export['segment_c3'].value_counts().reset_index()
            seg_counts.columns = ['Segment', 'Count']
            seg_counts.to_excel(writer, sheet_name="2_segment_counts", index=False)
        
        # 3. Segment Distribution %
        if 'segment_c3' in cohort_export.columns:
            seg_dist = (cohort_export['segment_c3'].value_counts(normalize=True) * 100).round(2).reset_index()
            seg_dist.columns = ['Segment', 'Percentage']
            seg_dist.to_excel(writer, sheet_name="3_segment_distribution", index=False)
        
        # 4. Segment Performance
        if 'segment_c3' in cohort_export.columns:
            numeric_cols = ['num_sessions', 'num_pageviews', 'forms_submitted', 'engagement_score']
            numeric_cols = [c for c in numeric_cols if c in cohort_export.columns]
            if numeric_cols:
                seg_perf = cohort_export.groupby('segment_c3')[numeric_cols].agg(['mean', 'median']).round(2)
                seg_perf.to_excel(writer, sheet_name="4_segment_performance")
        
        # 5. Activity Participation
        if 'apreu_activity_count' in cohort_export.columns:
            activity_dist = cohort_export['apreu_activity_count'].value_counts().sort_index().reset_index()
            activity_dist.columns = ['Activity Count', 'Contacts']
            activity_dist.to_excel(writer, sheet_name="5_activity_participation", index=False)
        
        # 6. Activity by Segment
        if 'segment_c3' in cohort_export.columns and 'apreu_activity_count' in cohort_export.columns:
            activity_by_seg = cohort_export.groupby('segment_c3')['apreu_activity_count'].agg(['mean', 'median', 'max']).round(2)
            activity_by_seg.to_excel(writer, sheet_name="6_activity_by_segment")
        
        # 7. Activity Diversity
        if 'apreu_activity_diversity' in cohort_export.columns:
            diversity_dist = cohort_export['apreu_activity_diversity'].value_counts().sort_index().reset_index()
            diversity_dist.columns = ['Diversity', 'Contacts']
            diversity_dist.to_excel(writer, sheet_name="7_activity_diversity", index=False)
        
        # 8. Conversion Journey
        if 'conversion_journey_days' in cohort_export.columns:
            journey_stats = cohort_export.groupby('segment_c3')['conversion_journey_days'].agg(['mean', 'median', 'min', 'max']).round(1)
            journey_stats.to_excel(writer, sheet_name="8_conversion_journey", index=False)
        
        # 9-10. Preparatoria Analysis
        if 'preparatoria' in cohort_export.columns:
            top_prepas = cohort_export['preparatoria'].value_counts().head(20).reset_index()
            top_prepas.columns = ['Preparatoria', 'Count']
            top_prepas.to_excel(writer, sheet_name="9_top_prepas_overall", index=False)
            
            if 'segment_c3' in cohort_export.columns:
                prepas_by_seg = cohort_export.groupby(['segment_c3', 'preparatoria']).size().unstack(fill_value=0).iloc[:, :15]
                prepas_by_seg.to_excel(writer, sheet_name="10_prepas_by_segment")
        
        # 11-12. Email Engagement
        email_cols = [c for c in ['email_delivered', 'email_opened', 'email_clicked', 'email_engagement_score'] if c in cohort_export.columns]
        if email_cols and 'segment_c3' in cohort_export.columns:
            email_by_seg = cohort_export.groupby('segment_c3')[email_cols].mean().round(2)
            email_by_seg.to_excel(writer, sheet_name="11_email_by_segment")
            
            email_overall = cohort_export[email_cols].describe().round(2)
            email_overall.to_excel(writer, sheet_name="12_email_overall_stats")
        
        # 13. Lifecycle Analysis (using latest values only)
        if 'lifecycle_stage' in cohort_export.columns and 'segment_c3' in cohort_export.columns:
            lifecycle_by_seg = cohort_export.groupby(['segment_c3', 'lifecycle_stage']).size().unstack(fill_value=0)
            lifecycle_by_seg.to_excel(writer, sheet_name="13_lifecycle_by_segment")
        
        # 14-16. Closure Analysis
        if 'is_closed' in cohort_export.columns:
            closure_by_seg = cohort_export.groupby('segment_c3').agg({
                'is_closed': ['sum', 'mean'],
                'days_to_close': ['mean', 'median']
            }).round(2)
            closure_by_seg.to_excel(writer, sheet_name="14_closure_by_segment")
            
            if 'ttc_bucket' in cohort_export.columns:
                ttc_by_seg = cohort_export.groupby(['segment_c3', 'ttc_bucket']).size().unstack(fill_value=0)
                ttc_by_seg.to_excel(writer, sheet_name="15_ttc_buckets")
                
                ttc_overall = cohort_export['ttc_bucket'].value_counts().sort_index().to_frame('count')
                ttc_overall.to_excel(writer, sheet_name="16_ttc_overall")
    
    output.seek(0)
    return output.getvalue()

def render_cluster3(data):
    """Render Cluster 3 analysis interface"""
    
    st.markdown("## 🎪 Cluster 3: Actividades APREU y Canales de Entrada")
    
    # About this analysis
    with st.expander("ℹ️ Acerca de Este Análisis", expanded=False):
        st.markdown("""
        ### 🎯 Qué Hace Este Cluster
        **Segmenta contactos por actividades promocionales y canales de entrada** para optimizar el ROI de eventos y estrategias de conversión.
        
        ### 👥 Quién Debe Usar Esto
        - **Equipos de Planificación de Eventos** - Identificar actividades de alto ROI
        - **Coordinadores APREU** - Optimizar calendario promocional
        - **Equipos de Admisiones** - Adaptar seguimiento por canal de entrada
        - **Planificadores de Presupuesto** - Asignar recursos a eventos efectivos
        
        ### 🔑 Preguntas Clave Respondidas
        - ¿Qué actividades APREU impulsan más conversiones?
        - ¿Los asistentes a Open Day cierran más rápido que los leads de WhatsApp?
        - ¿Qué preparatorias deberíamos dirigir para eventos?
        - ¿Cuál es el ROI de cada actividad promocional?
        - ¿Cuántas actividades atiende el convertidor promedio?
        
        ### 📊 Segmentos Definidos
        - **3A (Digital-Primero)** - Sitio web, formularios, entradas en línea → Secuencias de nutrición automatizadas
        - **3B (Evento-Primero)** - Open Day, Fogatada, eventos presenciales → Seguimiento de 48 horas
        - **3C (Mensajería-Primero)** - WhatsApp, contacto directo → Respuesta personalizada y rápida
        - **3D (Nicho/Bajo-Volumen)** - Programas especializados, campañas pequeñas → Evaluación de ROI
        
        ### 💡 Ejemplo de Insight
        *"Los contactos 3B (Evento-Primero) que asisten a Fogatada tienen una tasa de cierre del 42% vs 18% para solo digital"*
        → **Acción:** Invertir más en Fogatada, priorizar seguimiento de eventos dentro de 48 horas
        
        ### 🎪 Viaje de Actividad
        Se rastrea y visualiza el historial completo de actividades APREU de cada contacto para insights profundos sobre rutas de conversión.
        """)
    
    st.markdown("---")
    
    if data is None:
        st.error("⚠️ Datos no cargados.")
        return
    
    # Process data with cache busting based on data length
    # This ensures the cache refreshes when global filters change the data
    cache_key = f"c3_{len(data)}_{data['Record ID'].iloc[0] if 'Record ID' in data.columns else 'na'}"
    with st.spinner("Procesando datos del Cluster 3..."):
        cohort = process_cluster3_data(data, cache_key)
    
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
    
    # Export functionality
    with st.expander("📥 Exportar Datos", expanded=False):
        st.markdown("**Descargar datos filtrados:**")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Export full cohort with notebook-standard columns
            csv_columns = [
                "contact_id",
                "segment_c3",
                "entry_channel",
                "action_tag",
                "preparatoria",
                "prep_year_normalized",
                "apreu_activity_count",
                "apreu_activity_diversity",
                "first_conversion",
                "recent_conversion",
                "conversion_journey_days",
                "num_sessions",
                "num_pageviews",
                "forms_submitted",
                "engagement_score",
                "email_delivered",
                "email_opened",
                "email_clicked",
                "email_engagement_score",
                "likelihood_pct",
                "lifecycle_stage",
                "is_closed",
                "days_to_close",
                "ttc_bucket",
                "create_date",
                "close_date",
                "periodo_ingreso",
                "periodo_admision_bpm"
            ]
            
            # Filter to existing columns
            csv_columns = [c for c in csv_columns if c in cohort.columns]
            df_export = cohort[csv_columns].copy()
            
            # Format dates
            if "create_date" in df_export.columns:
                df_export["create_date"] = pd.to_datetime(df_export["create_date"]).dt.strftime("%Y-%m-%d").fillna("unknown")
            if "close_date" in df_export.columns:
                df_export["close_date"] = pd.to_datetime(df_export["close_date"]).dt.strftime("%Y-%m-%d").fillna("unknown")
            
            csv_data = df_export.to_csv(index=False, encoding='utf-8-sig')
            st.download_button(
                label="📄 Descargar Datos Completos (CSV)",
                data=csv_data.encode('utf-8'),
                file_name=f"cluster3_full_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv",
                use_container_width=True
            )
        
        with col2:
            # Export comprehensive XLSX workbook
            with st.spinner("Generando libro de trabajo Excel integral..."):
                xlsx_data = create_cluster3_xlsx_export(cohort)
                st.download_button(
                    label="📊 Descargar Libro de Trabajo Integral (XLSX) - 30+ Hojas",
                    data=xlsx_data,
                    file_name=f"cluster3_summary_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    use_container_width=True,
                    help="Libro de trabajo de análisis integral con 30+ hojas: resumen ejecutivo, rendimiento de segmentos, análisis de actividades, insights de preparatorias, compromiso por email, ¡y más!"
                )
    
    # Create tabs
    tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8 = st.tabs([
        "📊 Resumen", "🎯 Análisis de Segmento", "🎪 Análisis de Actividad",
        "🏫 Análisis de Preparatoria", "📧 Email y Conversión", "⚡ Cerradores Rápidos/Lentos", 
        "📅 Período Académico", "🔍 Búsqueda de Contactos"
    ])
    
    with tab1:
        render_overview_tab_c3(cohort)
    
    with tab2:
        render_segment_analysis_tab_c3(cohort)
    
    with tab3:
        render_activity_analysis_tab(cohort)
    
    with tab4:
        render_preparatoria_analysis_tab(cohort)
    
    with tab5:
        render_email_conversion_tab_c3(cohort)
    
    with tab6:
        render_fast_slow_closers_c3(cohort)
    
    with tab7:
        render_academic_period_tab_c3(cohort)
    
    with tab8:
        render_contact_lookup_tab_c3(cohort)

def render_overview_tab_c3(cohort):
    """Render overview tab for Cluster 3"""
    st.markdown("### 📊 Resumen Ejecutivo")
    
    # Key metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Contactos", f"{len(cohort):,}")
    
    with col2:
        has_activities = (cohort['apreu_activity_count'] > 0).sum()
        st.metric("Con Actividades APREU", f"{has_activities:,}")
    
    with col3:
        total_activities = cohort['apreu_activity_count'].sum()
        st.metric("Total Actividades", f"{int(total_activities):,}")
    
    with col4:
        close_rate = calculate_close_rate(cohort)
        st.metric("Tasa de Cierre General", f"{close_rate:.1f}%")
    
    st.markdown("---")
    
    # Segment distribution
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### Distribución de Canal de Entrada (3A-3D)")
        seg_counts = cohort['segment_c3'].value_counts()
        seg_counts = seg_counts[seg_counts.index != 'Desconocido']
        
        fig = px.pie(
            values=seg_counts.values,
            names=seg_counts.index,
            title="Distribución de Canal de Entrada - Leyenda: 3A=Digital Primero, 3B=Eventos Primero, 3C=Mensajería Primero, 3D=Nicho/Bajo Volumen",
            hole=0.4,
            color_discrete_sequence=px.colors.qualitative.Set3
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.markdown("#### Distribución de Participación en Actividades")
        
        # Activity count bins
        bins = [0, 1, 2, 3, 5, 10, float('inf')]
        labels = ['0', '1', '2', '3-4', '5-9', '10+']
        cohort_copy = cohort.copy()
        cohort_copy['activity_bins'] = pd.cut(
            cohort_copy['apreu_activity_count'], 
            bins=bins, 
            labels=labels,
            right=False
        )
        
        activity_dist = cohort_copy['activity_bins'].value_counts()
        
        # Create DataFrame for proper Plotly plotting
        activity_df = pd.DataFrame({
            'Actividades Asistidas': activity_dist.index,
            'Contactos': activity_dist.values
        })
        
        fig = px.bar(
            activity_df,
            x='Actividades Asistidas',
            y='Contactos',
            title="Distribución por Número de Actividades"
        )
        fig.update_traces(marker_color='#3498db')
        fig.update_layout(showlegend=False)
        st.plotly_chart(fig, use_container_width=True)
    
    # Segment performance table
    st.markdown("#### Resumen de Rendimiento por Segmento")
    
    analyzed = cohort[cohort['segment_c3'] != 'Desconocido']
    
    segment_summary = analyzed.groupby('segment_c3').agg({
        'contact_id': 'count',
        'apreu_activity_count': 'mean',
        'num_sessions': 'mean',
        'forms_submitted': 'mean',
        'engagement_score': 'mean',
        'email_engagement_score': 'mean',
        'is_closed': ['sum', 'mean']
    }).round(2)
    
    # Flatten multi-level columns
    segment_summary.columns = ['Contacts', 'Avg Activities', 'Avg Sessions', 
                               'Avg Forms', 'Avg Engagement', 'Email Engagement', 'Closed', 'Close Rate']
    segment_summary['Close Rate %'] = (segment_summary['Close Rate'] * 100).round(1)
    segment_summary = segment_summary.drop('Close Rate', axis=1)
    
    st.dataframe(segment_summary, use_container_width=True)

def render_segment_analysis_tab_c3(cohort):
    """Render segment analysis tab"""
    st.markdown("### 🎯 Análisis Profundo de Canal de Entrada (3A-3D)")
    
    # Filter out Unknown
    analyzed = cohort[cohort['segment_c3'] != 'Desconocido']
    
    # Segment selector
    segments = sorted(analyzed['segment_c3'].unique())
    selected_segment = st.selectbox("Seleccionar Canal de Entrada para Detalles:", segments)
    
    seg_data = analyzed[analyzed['segment_c3'] == selected_segment]
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Contactos", f"{len(seg_data):,}")
    
    with col2:
        close_rate = calculate_close_rate(seg_data)
        st.metric("Tasa de Cierre", f"{close_rate:.1f}%")
    
    with col3:
        avg_activities = seg_data['apreu_activity_count'].mean()
        st.metric("Actividades Promedio", f"{avg_activities:.1f}")
    
    with col4:
        avg_eng = seg_data['engagement_score'].mean()
        st.metric("Compromiso Promedio", f"{avg_eng:.2f}")
    
    st.markdown("---")
    
    # Action recommendation
    if 'action_tag' in seg_data.columns:
        action = seg_data['action_tag'].iloc[0]
        st.info(f"**Acción Recomendada:** {action}")
    
    # Segment description
    descriptions = {
        '3A - Digital Primero (Sitio Web, Formularios)': "Contactos que entran a través del sitio web, formularios y canales en línea. Mejor adecuados para secuencias de nutrición automatizadas.",
        '3B - Eventos Primero (Open Day, Fogatada, TDLA)': "Contactos de eventos presenciales y virtuales (Open Day, Fogatada, TDLA). Requieren seguimiento inmediato post-evento.",
        '3C - Mensajería Primero (WhatsApp, DM)': "Contactos vía WhatsApp y mensajería directa. Esperan respuestas personalizadas y rápidas.",
        '3D - Nicho/Bajo Volumen (Programas Especiales)': "Contactos de programas especiales y campañas pequeñas. Evaluar ROI y considerar escalamiento."
    }
    
    if selected_segment in descriptions:
        st.markdown(f"**Perfil:** {descriptions[selected_segment]}")
    
    st.markdown("---")
    
    # Key metrics comparison
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### Principales Actividades APREU")
        
        # Extract activities for this segment
        all_activities = []
        for activities_list in seg_data['apreu_activities_list']:
            if activities_list:
                all_activities.extend(activities_list)
        
        if all_activities:
            activity_counts = Counter(all_activities)
            top_activities = pd.DataFrame(
                activity_counts.most_common(10),
                columns=['Actividad', 'Conteo']
            )
            
            fig = px.bar(
                top_activities, x='Conteo', y='Actividad',
                orientation='h',
                title=f"Top 10 Actividades - {selected_segment}"
            )
            fig.update_traces(marker_color='#3498db')
            fig.update_layout(showlegend=False, height=400)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No hay actividades registradas para este segmento.")
    
    with col2:
        st.markdown("#### Compromiso por Email")
        
        email_metrics = {
            'Prom Entregados': seg_data['email_delivered'].mean(),
            'Prom Abiertos': seg_data['email_opened'].mean(),
            'Prom Clics': seg_data['email_clicked'].mean(),
            'Puntuación Compromiso': seg_data['email_engagement_score'].mean()
        }
        
        email_df = pd.DataFrame(list(email_metrics.items()), columns=['Métrica', 'Valor'])
        email_df['Valor'] = email_df['Valor'].round(2)
        
        fig = px.bar(
            email_df, x='Métrica', y='Valor',
            title=f"Métricas de Email - {selected_segment}"
        )
        fig.update_traces(marker_color='#2ecc71')
        fig.update_layout(showlegend=False, height=400)
        st.plotly_chart(fig, use_container_width=True)
    
    # Conversion events
    st.markdown("#### Principales Eventos de Conversión")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**Primera Conversión**")
        first_conv = seg_data['first_conversion'].value_counts().head(10)
        first_conv = first_conv[first_conv.index != '']
        if len(first_conv) > 0:
            st.dataframe(first_conv.to_frame('Conteo'), use_container_width=True)
        else:
            st.info("No hay datos de conversión disponibles.")
    
    with col2:
        st.markdown("**Conversión Reciente**")
        recent_conv = seg_data['recent_conversion'].value_counts().head(10)
        recent_conv = recent_conv[recent_conv.index != '']
        if len(recent_conv) > 0:
            st.dataframe(recent_conv.to_frame('Conteo'), use_container_width=True)
        else:
            st.info("No hay datos de conversión disponibles.")

def render_activity_analysis_tab(cohort):
    """Render activity analysis tab"""
    st.markdown("### 🎪 Análisis de Actividades APREU")
    
    # Filter to contacts with activities
    with_activities = cohort[cohort['apreu_activity_count'] > 0]
    
    st.markdown(f"**Contactos con actividades APREU:** {len(with_activities):,} de {len(cohort):,}")
    
    # Extract all activities
    all_activities = []
    for activities_list in with_activities['apreu_activities_list']:
        if activities_list:
            all_activities.extend(activities_list)
    
    if not all_activities:
        st.warning("No se encontraron actividades APREU en el dataset.")
        return
    
    st.markdown(f"**Total de instancias de actividades:** {len(all_activities):,}")
    
    # Top activities
    st.markdown("#### Top 20 Actividades APREU")
    
    activity_counts = Counter(all_activities)
    top_activities_df = pd.DataFrame(
        activity_counts.most_common(20),
        columns=['Actividad', 'Conteo']
    )
    top_activities_df['Porcentaje'] = (
        top_activities_df['Conteo'] / top_activities_df['Conteo'].sum() * 100
    ).round(2)
    
    fig = px.bar(
        top_activities_df, x='Conteo', y='Actividad',
        orientation='h',
        title="Top 20 Actividades APREU por Volumen",
        hover_data=['Porcentaje']
    )
    fig.update_traces(marker_color='#9b59b6')
    fig.update_layout(showlegend=False, height=600)
    st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("---")
    
    # Activity conversion rates
    st.markdown("#### Análisis de Conversión por Actividad")
    
    activity_conversion = []
    for activity in top_activities_df.head(15)['Actividad']:
        contacts_with_activity = with_activities[
            with_activities['apreu_activities_list'].apply(
                lambda x: activity in x if x else False
            )
        ]
        
        if len(contacts_with_activity) > 0:
            # Use mean() directly like the notebook for consistency
            close_rate = contacts_with_activity['is_closed'].mean() * 100
            closed = contacts_with_activity['is_closed'].sum()
            
            avg_days = contacts_with_activity['days_to_close'].mean()
            
            activity_conversion.append({
                'Actividad': activity,
                'Total': len(contacts_with_activity),
                'Cerrados': int(closed),
                'Tasa de Cierre %': round(close_rate, 2),
                'Días Prom': round(avg_days, 1) if pd.notna(avg_days) else np.nan
            })
    
    if activity_conversion:
        activity_conv_df = pd.DataFrame(activity_conversion).sort_values('Tasa de Cierre %', ascending=False)
        st.dataframe(activity_conv_df, use_container_width=True, height=400)
    
    st.markdown("---")
    
    # Activity by entry channel
    st.markdown("#### Distribución de Actividades por Canal de Entrada")
    
    # Create mapping
    activity_segment_map = []
    analyzed = with_activities[with_activities['segment_c3'] != 'Unknown']
    
    for idx, row in analyzed.iterrows():
        activities = row['apreu_activities_list']
        segment = row['segment_c3']
        if activities:
            for activity in activities:
                activity_segment_map.append({'activity': activity, 'segment': segment})
    
    if activity_segment_map:
        activity_segment_df = pd.DataFrame(activity_segment_map)
        
        # Get top 10 activities
        top_10_activities = top_activities_df.head(10)['Actividad'].tolist()
        
        activity_segment_filtered = activity_segment_df[
            activity_segment_df['activity'].isin(top_10_activities)
        ]
        
        if not activity_segment_filtered.empty:
            activity_by_segment = pd.crosstab(
                activity_segment_filtered['activity'],
                activity_segment_filtered['segment']
            )
            
            fig = px.bar(
                activity_by_segment,
                barmode='group',
                title="Top 10 Actividades por Canal de Entrada",
                labels={'value': 'Conteo', 'variable': 'Canal de Entrada'},
                color_discrete_sequence=px.colors.qualitative.Set2
            )
            fig.update_layout(height=500)
            st.plotly_chart(fig, use_container_width=True)

def render_preparatoria_analysis_tab(cohort):
    """Render preparatoria analysis tab"""
    st.markdown("### 🏫 Análisis de Preparatoria")
    
    # Filter to contacts with preparatoria data
    with_prepa = cohort[cohort['preparatoria'] != 'Unknown']
    
    if len(with_prepa) == 0:
        st.warning("No hay datos de preparatoria disponibles.")
        return
    
    st.markdown(f"**Contactos con datos de preparatoria:** {len(with_prepa):,} de {len(cohort):,}")
    
    # Top preparatorias
    st.markdown("#### Top 20 Preparatorias por Volumen")
    
    top_prepas = with_prepa['preparatoria'].value_counts().head(20)
    
    # Create DataFrame for proper Plotly plotting
    prepas_df = pd.DataFrame({
        'Preparatoria': top_prepas.index,
        'Contactos': top_prepas.values
    })
    
    fig = px.bar(
        prepas_df,
        x='Contactos',
        y='Preparatoria',
        orientation='h',
        title="Top 20 Preparatorias"
    )
    fig.update_traces(marker_color='#3498db')
    fig.update_layout(showlegend=False, height=600)
    st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("---")
    
    # Preparatoria performance
    st.markdown("#### Métricas de Rendimiento por Preparatoria")
    
    top_prepa_list = top_prepas.head(15).index.tolist()
    top_prepa_data = with_prepa[with_prepa['preparatoria'].isin(top_prepa_list)]
    
    prepa_performance = top_prepa_data.groupby('preparatoria').agg({
        'contact_id': 'count',
        'is_closed': ['sum', 'mean'],
        'days_to_close': 'mean',
        'likelihood_pct': 'mean',
        'engagement_score': 'mean',
        'apreu_activity_count': 'mean'
    }).round(2)
    
    # Flatten multi-level columns
    prepa_performance.columns = ['Total', 'Closed', 'Close Rate', 'Avg Days', 'Avg Likelihood', 
                                 'Avg Engagement', 'Avg Activities']
    prepa_performance['Close Rate %'] = (prepa_performance['Close Rate'] * 100).round(1)
    prepa_performance = prepa_performance.drop('Close Rate', axis=1)
    
    prepa_performance = prepa_performance.sort_values('Close Rate %', ascending=False)
    
    st.dataframe(prepa_performance, use_container_width=True, height=400)
    
    st.markdown("---")
    
    # Preparatoria by entry channel
    st.markdown("#### Distribución de Preparatorias por Canal de Entrada")
    
    analyzed = top_prepa_data[top_prepa_data['segment_c3'] != 'Unknown']
    
    if len(analyzed) > 0:
        prepa_by_segment = pd.crosstab(
            analyzed['preparatoria'],
            analyzed['segment_c3']
        ).head(10)
        
        fig = px.bar(
            prepa_by_segment,
            barmode='group',
            title="Top 10 Preparatorias por Canal de Entrada",
            labels={'value': 'Conteo', 'variable': 'Canal de Entrada'},
            color_discrete_sequence=px.colors.qualitative.Set3
        )
        fig.update_layout(height=500)
        st.plotly_chart(fig, use_container_width=True)
    
    # Preparatoria year distribution
    st.markdown("#### Distribución por Año de Preparatoria")
    
    prep_year_dist = with_prepa['prep_year_normalized'].value_counts()
    
    fig = px.pie(
        values=prep_year_dist.values,
        names=prep_year_dist.index,
        title="Distribución por Año de Preparatoria",
        hole=0.3
    )
    st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("---")
    
    # Activity Participation % by Preparatoria (NEW - from notebook)
    st.markdown("#### Participación en Actividades % por Preparatoria")
    st.markdown("*Muestra qué porcentaje de los contactos de cada preparatoria asistió a cada actividad*")
    
    # Get top activities
    all_activities = []
    for activities_list in with_prepa['apreu_activities_list']:
        if activities_list:
            all_activities.extend(activities_list)
    
    if all_activities:
        activity_counts = Counter(all_activities)
        top_activities_list = [act for act, _ in activity_counts.most_common(10)]
        
        # Calculate participation % for top 15 preparatorias
        prepa_activity_participation = []
        
        for prepa in top_prepa_list[:15]:
            prepa_contacts = with_prepa[with_prepa['preparatoria'] == prepa]
            total_prepa_contacts = len(prepa_contacts)
            
            row_data = {
                'Preparatoria': prepa,
                'Total Contactos': total_prepa_contacts
            }
            
            # For each activity, calculate what % of this prepa's contacts attended it
            for activity in top_activities_list:
                contacts_with_activity = prepa_contacts[
                    prepa_contacts['apreu_activities_list'].apply(
                        lambda x: activity in x if x else False
                    )
                ]
                
                participation_pct = (len(contacts_with_activity) / total_prepa_contacts * 100) if total_prepa_contacts > 0 else 0
                row_data[activity] = round(participation_pct, 1)
            
            prepa_activity_participation.append(row_data)
        
        if prepa_activity_participation:
            prepa_activity_pct_df = pd.DataFrame(prepa_activity_participation)
            prepa_activity_pct_df = prepa_activity_pct_df.sort_values('Total Contactos', ascending=False)
            
            # Display with styled background (higher % = darker blue)
            st.dataframe(
                prepa_activity_pct_df.style.background_gradient(
                    subset=[col for col in prepa_activity_pct_df.columns if col not in ['Preparatoria', 'Total Contactos']],
                    cmap='Blues',
                    vmin=0,
                    vmax=100
                ),
                use_container_width=True,
                height=500
            )
            
            st.markdown("💡 **Insight:** Porcentajes más altos (azul más oscuro) indican actividades que son particularmente populares con preparatorias específicas. Usa esto para dirigir actividades promocionales a escuelas secundarias específicas.")
    else:
        st.info("No hay datos de actividad disponibles para análisis de participación.")

def render_email_conversion_tab_c3(cohort):
    """Render email engagement and conversion timeline analysis"""
    st.markdown("### 📧 Compromiso por Email y Línea de Tiempo de Conversión")
    
    # Email Engagement Metrics
    st.markdown("#### 📨 Compromiso por Email por Canal de Entrada")
    
    # FIX: Use correct column names that match the data processing
    email_fields = {
        'Email Entregados': 'email_delivered',
        'Email Abiertos': 'email_opened',
        'Email Clics': 'email_clicked'
    }
    
    # Check which email fields are available
    available_email_fields = {}
    for display_name, col_name in email_fields.items():
        if col_name in cohort.columns:
            available_email_fields[display_name] = col_name
    
    if available_email_fields:
        email_by_segment = cohort.groupby('segment_c3')[list(available_email_fields.values())].agg(['sum', 'mean']).round(2)
        
        # Flatten column names
        email_by_segment.columns = [f'{col[0]}_{col[1]}' for col in email_by_segment.columns]
        
        st.dataframe(email_by_segment, use_container_width=True)
        
        # Email engagement score distribution
        if 'email_engagement_score' in cohort.columns or any('email' in col.lower() for col in cohort.columns):
            st.markdown("**Distribución de Compromiso por Email:**")
            
            # Calculate email engagement if not present
            if 'email_engagement_score' not in cohort.columns and available_email_fields:
                email_score = pd.Series(0, index=cohort.index)
                for field_col in available_email_fields.values():
                    if field_col in cohort.columns:
                        email_score += cohort[field_col].fillna(0)
                cohort_temp = cohort.copy()
                cohort_temp['email_engagement_score'] = email_score
            else:
                cohort_temp = cohort
            
            if 'email_engagement_score' in cohort_temp.columns:
                email_dist = cohort_temp.groupby('segment_c3')['email_engagement_score'].describe()[['mean', '50%', 'max']]
                email_dist.columns = ['Promedio', 'Mediana', 'Máximo']
                st.dataframe(email_dist.round(2), use_container_width=True)
        
        st.markdown("---")
    else:
        st.info("Datos de compromiso por email no disponibles en el dataset")
    
    # Conversion Timeline Analysis
    st.markdown("#### ⏱️ Línea de Tiempo de Conversión y Duración del Recorrido")
    
    conversion_fields = {
        'first_conversion': 'Evento de Primera Conversión',
        'recent_conversion': 'Evento de Conversión Reciente',
        'conversion_journey_days': 'Duración del Recorrido (días)'
    }
    
    has_conversion_data = any(field in cohort.columns for field in conversion_fields.keys())
    
    if has_conversion_data:
        # Conversion event counts
        st.markdown("**Distribución de Eventos de Conversión:**")
        
        if 'first_conversion' in cohort.columns:
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("**Principales Eventos de Primera Conversión:**")
                first_conv = cohort['first_conversion'].value_counts().head(10)
                st.dataframe(pd.DataFrame({
                    'Evento': first_conv.index,
                    'Conteo': first_conv.values,
                    '%': (first_conv.values / first_conv.sum() * 100).round(1)
                }), use_container_width=True, hide_index=True)
            
            with col2:
                if 'recent_conversion' in cohort.columns:
                    st.markdown("**Principales Eventos de Conversión Reciente:**")
                    recent_conv = cohort['recent_conversion'].value_counts().head(10)
                    st.dataframe(pd.DataFrame({
                        'Evento': recent_conv.index,
                        'Conteo': recent_conv.values,
                        '%': (recent_conv.values / recent_conv.sum() * 100).round(1)
                    }), use_container_width=True, hide_index=True)
        
        # Conversion journey duration
        if 'conversion_journey_days' in cohort.columns:
            st.markdown("---")
            st.markdown("**Análisis de Duración del Recorrido de Conversión:**")
            
            journey_stats = cohort[cohort['conversion_journey_days'].notna()].groupby('segment_c3')['conversion_journey_days'].agg([
                'count', 'mean', 'median', 'min', 'max'
            ]).round(1)
            
            journey_stats.columns = ['Contactos', 'Días Prom', 'Días Mediana', 'Días Mín', 'Días Máx']
            
            st.dataframe(journey_stats, use_container_width=True)
            
            # Journey duration distribution
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("**Distribución de Duración del Recorrido:**")
                journey_buckets = pd.cut(
                    cohort['conversion_journey_days'].dropna(),
                    bins=[0, 7, 30, 60, 90, 180, float('inf')],
                    labels=['0-7 días', '8-30 días', '31-60 días', '61-90 días', '91-180 días', '180+ días']
                )
                journey_dist = journey_buckets.value_counts().sort_index()
                
                # Create DataFrame for proper Plotly plotting
                journey_buckets_df = pd.DataFrame({
                    'Duración': journey_dist.index,
                    'Contactos': journey_dist.values
                })
                
                fig = px.bar(
                    journey_buckets_df,
                    x='Duración',
                    y='Contactos',
                    title="Categorías de Duración del Recorrido de Conversión"
                )
                fig.update_traces(marker_color='#3498db')
                fig.update_layout(showlegend=False)
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                st.markdown("**Recorrido Promedio por Segmento:**")
                avg_journey = cohort[cohort['conversion_journey_days'].notna()].groupby('segment_c3')['conversion_journey_days'].mean().sort_values()
                
                # Create DataFrame for proper Plotly plotting
                journey_df = pd.DataFrame({
                    'Segmento': avg_journey.index,
                    'Días': avg_journey.values
                })
                
                fig = px.bar(
                    journey_df,
                    x='Días',
                    y='Segmento',
                    orientation='h',
                    title="Duración Promedio del Recorrido por Canal de Entrada"
                )
                # Use a single professional color
                fig.update_traces(marker_color='#2ecc71')
                fig.update_layout(showlegend=False)
                st.plotly_chart(fig, use_container_width=True)
        
        st.markdown("---")
        
        # Conversion event performance
        st.markdown("**Conversion Event Performance (Close Rates):**")
        
        if 'first_conversion' in cohort.columns and 'is_closed' in cohort.columns:
            conv_performance = []
            top_events = cohort['first_conversion'].value_counts().head(12).index
            
            for event in top_events:
                event_contacts = cohort[cohort['first_conversion'] == event]
                # Use mean() directly like the notebook for consistency
                close_rate = event_contacts['is_closed'].mean() * 100 if len(event_contacts) > 0 else 0
                closed = event_contacts['is_closed'].sum()
                
                conv_performance.append({
                    'First Conversion Event': event,
                    'Contacts': len(event_contacts),
                    'Closed': int(closed),
                    'Close Rate %': round(close_rate, 2)
                })
            
            if conv_performance:
                conv_df = pd.DataFrame(conv_performance).sort_values('Close Rate %', ascending=False)
                st.dataframe(conv_df, use_container_width=True)
    else:
        st.info("Datos de línea de tiempo de conversión no disponibles en el dataset")
    
    # Lifecycle Stage Analysis
    st.markdown("---")
    st.markdown("#### 🔄 Distribución de Etapa del Ciclo de Vida")
    
    if 'lifecycle_stage' in cohort.columns:
        lifecycle_by_segment = pd.crosstab(
            cohort['segment_c3'],
            cohort['lifecycle_stage'],
            normalize='index'
        ) * 100
        
        # Show top 8 stages
        top_stages = cohort['lifecycle_stage'].value_counts().head(8).index
        lifecycle_filtered = lifecycle_by_segment[lifecycle_by_segment.columns.intersection(top_stages)]
        
        st.dataframe(lifecycle_filtered.round(1), use_container_width=True)
    else:
        st.info("Datos de etapa del ciclo de vida no disponibles")

def render_fast_slow_closers_c3(cohort):
    """Render fast/slow closers analysis for Cluster 3"""
    st.markdown("### ⚡ Análisis de Cerradores Rápidos vs Lentos")
    st.markdown("Identifica qué combinaciones de Canal de Entrada × Actividad cierran más rápido")
    
    # Filter to closed contacts
    closed = cohort[cohort['is_closed'] == 1].copy()
    
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
    
    # Fast closers by segment
    st.markdown("#### ⚡ Cerradores Rápidos por Canal de Entrada")
    
    fast_closers = closed[closed['closure_speed'] == 'Fast (≤60 days)']
    
    if len(fast_closers) > 0:
        fast_by_segment = fast_closers['segment_c3'].value_counts()
        
        # Create DataFrame for proper Plotly plotting
        fast_df = pd.DataFrame({
            'Canal de Entrada': fast_by_segment.index,
            'Conteo': fast_by_segment.values
        })
        
        fig = px.bar(
            fast_df,
            x='Conteo',
            y='Canal de Entrada',
            orientation='h',
            title="Cerradores Rápidos por Canal de Entrada"
        )
        fig.update_traces(marker_color='#2ecc71')
        fig.update_layout(showlegend=False, height=400)
        st.plotly_chart(fig, use_container_width=True)
        
        # Average activities for fast closers
        st.markdown("**Cerradores Rápidos - Patrones de Actividad:**")
        fast_stats = fast_closers.groupby('segment_c3').agg({
            'apreu_activity_count': 'mean',
            'apreu_activity_diversity': 'mean',
            'engagement_score': 'mean'
        }).round(2)
        fast_stats.columns = ['Actividades Prom', 'Diversidad Prom', 'Compromiso Prom']
        st.dataframe(fast_stats, use_container_width=True)
    else:
        st.info("No hay cerradores rápidos en este dataset.")
    
    st.markdown("---")
    
    # Slow closers by segment
    st.markdown("#### 🐌 Cerradores Lentos por Canal de Entrada")
    
    slow_closers = closed[closed['closure_speed'] == 'Slow (>180 days)']
    
    if len(slow_closers) > 0:
        slow_by_segment = slow_closers['segment_c3'].value_counts()
        
        # Create DataFrame for proper Plotly plotting
        slow_df = pd.DataFrame({
            'Canal de Entrada': slow_by_segment.index,
            'Conteo': slow_by_segment.values
        })
        
        fig = px.bar(
            slow_df,
            x='Conteo',
            y='Canal de Entrada',
            orientation='h',
            title="Cerradores Lentos por Canal de Entrada"
        )
        fig.update_traces(marker_color='#e74c3c')
        fig.update_layout(showlegend=False, height=400)
        st.plotly_chart(fig, use_container_width=True)
        
        # Average activities for slow closers
        st.markdown("**Cerradores Lentos - Patrones de Actividad:**")
        slow_stats = slow_closers.groupby('segment_c3').agg({
            'apreu_activity_count': 'mean',
            'apreu_activity_diversity': 'mean',
            'engagement_score': 'mean'
        }).round(2)
        slow_stats.columns = ['Actividades Prom', 'Diversidad Prom', 'Compromiso Prom']
        st.dataframe(slow_stats, use_container_width=True)
    else:
        st.info("No hay cerradores lentos en este dataset.")
    
    st.markdown("---")
    
    # Insights
    st.markdown("#### 💡 Insights Clave")
    
    insights = []
    
    if len(fast_closers) > 0:
        # Best performing segment
        best_segment = fast_by_segment.idxmax()
        best_count = fast_by_segment.max()
        insights.append(f"✅ **Mejor Canal de Entrada para Cerradores Rápidos:** {best_segment} ({best_count} contactos)")
        
        # Average activities
        avg_activities = fast_closers['apreu_activity_count'].mean()
        insights.append(f"📊 **Actividades Promedio de Cerradores Rápidos:** {avg_activities:.1f}")
    
    if len(slow_closers) > 0:
        # Most common slow segment
        worst_segment = slow_by_segment.idxmax()
        worst_count = slow_by_segment.max()
        insights.append(f"⚠️ **Canal Más Común de Cerradores Lentos:** {worst_segment} ({worst_count} contactos)")
        
        # Average activities
        avg_activities = slow_closers['apreu_activity_count'].mean()
        insights.append(f"📊 **Actividades Promedio de Cerradores Lentos:** {avg_activities:.1f}")
    
    # Overall ratio
    if len(fast_closers) > 0 and len(slow_closers) > 0:
        ratio = len(fast_closers) / len(slow_closers)
        insights.append(f"⚖️ **Proporción Rápidos/Lentos:** {ratio:.2f}x")
    
    if insights:
        for insight in insights:
            st.markdown(insight)
    else:
        st.info("No hay suficientes datos para insights")

def visualize_apreu_journey(contact_id, cohort):
    """
    Visualize the APREU activities journey of a contact over time.
    Shows APREU activities on the top line and conversions on the bottom line.
    Returns a matplotlib figure for display in Streamlit.
    """
    # Find the contact
    key = str(contact_id).strip()
    matches = cohort[cohort['contact_id'].astype(str) == key]
    
    if len(matches) == 0:
        return None
    
    contact = matches.iloc[0]
    
    # Get APREU activities list
    activities = contact.get('apreu_activities_list', [])
    first_conv = contact.get('first_conversion', None)
    recent_conv = contact.get('recent_conversion', None)
    segment = contact.get('segment_c3', 'N/A')
    
    # Separate activities and conversions
    activity_steps = []
    conversion_steps = []
    
    # Add APREU activities
    if activities and isinstance(activities, (list, tuple)) and len(activities) > 0:
        for i, activity in enumerate(activities):
            if activity and str(activity) not in ['', 'nan', 'None']:
                activity_steps.append({
                    'step': f'Activity {i+1}',
                    'value': str(activity),
                    'type': 'activity',
                    'color': '#2196F3'  # Blue for activities
                })
    
    # Add first conversion if available
    if pd.notna(first_conv) and str(first_conv) not in ['', 'nan', 'None']:
        conversion_steps.append({
            'step': 'First Conversion',
            'value': str(first_conv),
            'type': 'conversion',
            'color': '#4CAF50'  # Green for conversions
        })
    
    # Add recent conversion if different from first
    if pd.notna(recent_conv) and str(recent_conv) not in ['', 'nan', 'None']:
        if recent_conv != first_conv:
            conversion_steps.append({
                'step': 'Recent Conversion',
                'value': str(recent_conv),
                'type': 'conversion',
                'color': '#FF9800'  # Orange for recent conversion
            })
    
    # If no data found
    if not activity_steps and not conversion_steps:
        return None
    
    # Create visualization - TWO ROWS LAYOUT
    box_width = 2.5
    box_spacing = 0.8
    
    # Calculate width based on maximum items in either row
    max_items = max(len(activity_steps), len(conversion_steps))
    total_width = max(max_items * (box_width + box_spacing) + 1, 16)
    
    fig, ax = plt.subplots(figsize=(total_width, 9))
    ax.set_xlim(0, total_width)
    ax.set_ylim(0, 6.5)
    ax.axis('off')
    
    # Title
    ax.text(total_width / 2, 6.0, f'APREU Journey: Contact {contact_id}',
            ha='center', va='top', fontsize=16, fontweight='bold')
    ax.text(total_width / 2, 5.6, f'Segment: {segment}',
            ha='center', va='top', fontsize=12, style='italic')
    
    # Draw ACTIVITIES on TOP ROW
    if activity_steps:
        ax.text(0.5, 4.5, 'APREU Activities:',
                ha='left', va='bottom', fontsize=11, fontweight='bold',
                color='#2196F3')
        
        y_pos = 3.7
        current_x = 0.5
        
        for i, step in enumerate(activity_steps):
            # Draw box
            box = FancyBboxPatch(
                (current_x, y_pos - 0.4),
                box_width, 0.8,
                boxstyle="round,pad=0.1",
                facecolor=step['color'],
                edgecolor='darkgray',
                alpha=0.7,
                linewidth=2
            )
            ax.add_patch(box)
            
            # Add step label (above box)
            ax.text(current_x + box_width/2, y_pos + 0.6,
                    step['step'],
                    ha='center', va='bottom',
                    fontsize=9, fontweight='bold')
            
            # Add value text (inside box, wrapped if needed)
            value_text = step['value']
            if len(value_text) > 25:
                # Wrap long text
                words = value_text.split()
                lines = []
                current_line = []
                for word in words:
                    test_line = ' '.join(current_line + [word])
                    if len(test_line) <= 25:
                        current_line.append(word)
                    else:
                        if current_line:
                            lines.append(' '.join(current_line))
                        current_line = [word]
                if current_line:
                    lines.append(' '.join(current_line))
                value_text = '\n'.join(lines)
            
            ax.text(current_x + box_width/2, y_pos,
                    value_text,
                    ha='center', va='center',
                    fontsize=8)
            
            # Draw arrow to next activity
            if i < len(activity_steps) - 1:
                arrow = FancyArrowPatch(
                    (current_x + box_width, y_pos),
                    (current_x + box_width + box_spacing, y_pos),
                    arrowstyle='->,head_width=0.4,head_length=0.4',
                    color='gray',
                    linewidth=2
                )
                ax.add_patch(arrow)
            
            current_x += box_width + box_spacing
    
    # Draw CONVERSIONS on BOTTOM ROW
    if conversion_steps:
        ax.text(0.5, 2.3, 'Conversions:',
                ha='left', va='bottom', fontsize=11, fontweight='bold',
                color='#4CAF50')
        
        y_pos = 1.5
        current_x = 0.5
        
        for i, step in enumerate(conversion_steps):
            # Draw box
            box = FancyBboxPatch(
                (current_x, y_pos - 0.4),
                box_width, 0.8,
                boxstyle="round,pad=0.1",
                facecolor=step['color'],
                edgecolor='darkgray',
                alpha=0.7,
                linewidth=2
            )
            ax.add_patch(box)
            
            # Add step label (above box)
            ax.text(current_x + box_width/2, y_pos + 0.6,
                    step['step'],
                    ha='center', va='bottom',
                    fontsize=9, fontweight='bold')
            
            # Add value text (inside box, wrapped if needed)
            value_text = step['value']
            if len(value_text) > 25:
                # Wrap long text
                words = value_text.split()
                lines = []
                current_line = []
                for word in words:
                    test_line = ' '.join(current_line + [word])
                    if len(test_line) <= 25:
                        current_line.append(word)
                    else:
                        if current_line:
                            lines.append(' '.join(current_line))
                        current_line = [word]
                if current_line:
                    lines.append(' '.join(current_line))
                value_text = '\n'.join(lines)
            
            ax.text(current_x + box_width/2, y_pos,
                    value_text,
                    ha='center', va='center',
                    fontsize=8)
            
            # Draw arrow to next conversion
            if i < len(conversion_steps) - 1:
                arrow = FancyArrowPatch(
                    (current_x + box_width, y_pos),
                    (current_x + box_width + box_spacing, y_pos),
                    arrowstyle='->,head_width=0.4,head_length=0.4',
                    color='gray',
                    linewidth=2
                )
                ax.add_patch(arrow)
            
            current_x += box_width + box_spacing
    
    # Summary text
    summary_parts = []
    if activity_steps:
        summary_parts.append(f"Activities: {len(activity_steps)}")
    if conversion_steps:
        summary_parts.append(f"Conversions: {len(conversion_steps)}")
    summary_text = " | ".join(summary_parts)
    
    ax.text(total_width / 2, 0.3, summary_text,
            fontsize=10, ha='center', style='italic', color='gray')
    
    plt.tight_layout()
    return fig

def render_academic_period_tab_c3(cohort):
    """Render academic period analysis tab for Cluster 3"""
    st.markdown("### 📅 Análisis de Período Académico (Estacional)")
    st.markdown("Comprende los ciclos de inscripción y tendencias estacionales para actividades APREU")
    
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
        
        **Formato:** YYYYMM (ej., 202408 para Agosto 2024)
        
        Este análisis muestra:
        - Patrones de inscripción estacionales
        - Efectividad de actividades APREU por período
        - Rendimiento del canal de entrada a lo largo del tiempo
        """)
        return
    
    # Convert academic period to readable format
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
            # 05 = Special, 10 = Spring, 35 = Summer, 60 = Fall, 75 = Winter/Special
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
                return "Desconocido"
    
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
            'Período de Admisión': periodo_counts.index,
            'Número de Contactos': periodo_counts.values
        })
        
        # Simple bar chart with single color for clarity
        fig = px.bar(
            periodo_df,
            x='Período de Admisión',
            y='Número de Contactos',
            title="Contactos por Período de Admisión (Cronológico)"
        )
        # Use a single professional color
        fig.update_traces(marker_color='#9b59b6')
        fig.update_layout(
            showlegend=False, 
            xaxis_tickangle=-45,
            yaxis_title="Número de Contactos",
            xaxis_title="Período de Admisión"
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.markdown("**Top 5 Períodos Más Grandes:**")
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
    
    # 2. Activity metrics by period
    st.markdown("#### 🎪 APREU Activity Metrics by Period")
    
    activity_cols = ['num_apreu_activities', 'num_unique_apreu_types', 'promocion_count', 'evento_count']
    available_activity = [col for col in activity_cols if col in cohort_periodo.columns]
    
    if available_activity:
        periodo_activity = cohort_periodo.groupby('periodo_readable')[available_activity].mean().round(2)
        periodo_activity = periodo_activity.sort_index()
        
        st.dataframe(periodo_activity, use_container_width=True)
        
        # Activity trend
        if 'num_apreu_activities' in available_activity:
            fig = px.line(
                x=periodo_activity.index,
                y=periodo_activity['num_apreu_activities'],
                title="Promedio de Actividades APREU por Contacto por Período",
                labels={'x': 'Período', 'y': 'Actividades Prom'},
                markers=True
            )
            fig.update_layout(xaxis_tickangle=-45)
            st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("---")
    
    # 3. Segment distribution by period
    st.markdown("#### 🎯 Segment Distribution by Period")
    
    if 'segment_apreu' in cohort_periodo.columns:
        seg_by_period = pd.crosstab(
            cohort_periodo['periodo_readable'],
            cohort_periodo['segment_apreu'],
            normalize='index'
        ) * 100
        
        seg_by_period = seg_by_period.sort_index()
        
        st.dataframe(seg_by_period.round(1), use_container_width=True)
        
        # Stacked bar chart
        fig = px.bar(
            seg_by_period,
            barmode='stack',
            title="Distribución de Segmentos por Período (3A=Digital, 3B=Eventos, 3C=Mensajería, 3D=Nicho)",
            labels={'value': '% de Contactos', 'variable': 'Segmento'},
            color_discrete_sequence=px.colors.qualitative.Pastel
        )
        fig.update_layout(xaxis_tickangle=-45)
        st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("---")
    
    # 4. Entry channel distribution by period
    st.markdown("#### 🚪 Distribución de Canal de Entrada por Período")
    
    if 'entry_channel' in cohort_periodo.columns:
        # Get top entry channels
        top_channels = cohort_periodo['entry_channel'].value_counts().head(6).index
        
        channel_by_period = pd.crosstab(
            cohort_periodo['periodo_readable'],
            cohort_periodo['entry_channel'],
            normalize='index'
        ) * 100
        
        channel_by_period = channel_by_period.sort_index()
        
        # Filter to top channels
        channel_filtered = channel_by_period[channel_by_period.columns.intersection(top_channels)]
        
        st.dataframe(channel_filtered.round(1), use_container_width=True)
    
    st.markdown("---")
    
    # 5. Close rates by period
    st.markdown("#### 💰 Performance by Period")
    
    periodo_performance = []
    for period in periodo_counts.head(10).index:
        period_data = cohort_periodo[cohort_periodo['periodo_readable'] == period]
        
        total = len(period_data)
        # Use is_closed field and mean() like the notebook for consistency
        if 'is_closed' in period_data.columns:
            close_rate = period_data['is_closed'].mean() * 100
            closed = period_data['is_closed'].sum()
        else:
            close_rate = 0
            closed = 0
        
        avg_activities = period_data['num_apreu_activities'].mean() if 'num_apreu_activities' in period_data.columns else 0
        
        periodo_performance.append({
            'Period': period,
            'Total': total,
            'Closed': int(closed),
            'Close Rate %': round(close_rate, 2),
            'Avg Activities': round(avg_activities, 2)
        })
    
    if periodo_performance:
        perf_df = pd.DataFrame(periodo_performance)
        st.dataframe(perf_df, use_container_width=True)
        
        # Close rate trend
        fig = px.line(
            perf_df, x='Period', y='Close Rate %',
            title="Tendencia de Tasa de Cierre por Período de Admisión",
            markers=True,
            color_discrete_sequence=['#9C27B0']
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
        
        # Period with highest activity
        most_active = max(periodo_performance, key=lambda x: x['Avg Activities'])
        insights.append(f"🎪 **Most Active Period:** {most_active['Period']} ({most_active['Avg Activities']:.2f} avg activities)")
    
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

def render_contact_lookup_tab_c3(cohort):
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
            
            st.markdown("#### Perfil del Contacto")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.markdown("**Identificación**")
                st.write(f"**ID de Contacto:** {contact.get('contact_id', 'N/A')}")
                st.write(f"**Canal de Entrada:** {contact.get('segment_c3', 'N/A')}")
                st.write(f"**Etiqueta de Acción:** {contact.get('action_tag', 'N/A')}")
                st.write(f"**Preparatoria:** {contact.get('preparatoria', 'Desconocido')}")
                st.write(f"**Año de Prep:** {contact.get('prep_year_normalized', 'Desconocido')}")
            
            with col2:
                st.markdown("**Actividades APREU**")
                st.write(f"**Total de Actividades:** {int(contact.get('apreu_activity_count', 0))}")
                st.write(f"**Diversidad de Actividades:** {int(contact.get('apreu_activity_diversity', 0))}")
                st.write(f"**Primera Conversión:** {contact.get('first_conversion', 'Ninguna')[:30]}")
                st.write(f"**Conversión Reciente:** {contact.get('recent_conversion', 'Ninguna')[:30]}")
                
                if pd.notna(contact.get('conversion_journey_days')):
                    st.write(f"**Duración del Recorrido:** {contact.get('conversion_journey_days', 0):.0f} días")
            
            with col3:
                st.markdown("**Compromiso y Resultados**")
                st.write(f"**Sesiones:** {int(contact.get('num_sessions', 0)):,}")
                st.write(f"**Formularios:** {int(contact.get('forms_submitted', 0)):,}")
                st.write(f"**Puntuación de Compromiso:** {contact.get('engagement_score', 0):.2f}")
                
                if 'likelihood_pct' in contact.index:
                    st.write(f"**Probabilidad:** {contact.get('likelihood_pct', 0):.1f}%")
                
                is_closed = "Sí" if contact.get('is_closed', 0) == 1 else "No"
                st.write(f"**Cerrado:** {is_closed}")
                
                if 'lifecycle_stage' in contact.index:
                    st.write(f"**Ciclo de Vida:** {contact.get('lifecycle_stage', 'N/A')}")
            
            st.markdown("---")
            st.markdown("#### Actividades a las que Asistió")
            
            activities = contact.get('apreu_activities_list', [])
            if activities:
                st.markdown(f"**{len(activities)} actividades registradas:**")
                for i, activity in enumerate(activities, 1):
                    st.write(f"{i}. {activity}")
            else:
                st.info("No se registraron actividades APREU para este contacto.")
            
            # Show journey visualization
            st.markdown("---")
            st.markdown("#### 🗺️ Visualización del Recorrido APREU")
            
            fig = visualize_apreu_journey(contact_id, cohort)
            if fig:
                st.pyplot(fig)
                plt.close(fig)
            else:
                st.info("📊 No hay datos de recorrido disponibles para visualización")

