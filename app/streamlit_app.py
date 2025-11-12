"""
APREU Segmentación Avanzada - POC Interactivo
Una aplicación Streamlit integral que muestra tres estrategias de segmentación distintas.
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path
import os
from datetime import datetime

# Page configuration
st.set_page_config(
    page_title="SEGMENTACIÓN AVANZADA DE APREU",
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
    st.markdown('<h1 class="main-header">🎯 APREU SEGMENTACIÓN AVANZADA</h1>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Prueba de Concepto - Análisis Interactivo por Segmentación</p>', unsafe_allow_html=True)
    
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
        
        st.markdown("### 📁 Fuente de Datos")
        
        # File upload option
        data_source = st.radio(
            "Elegir fuente de datos:",
            ["📂 Usar Archivo Predeterminado", "⬆️ Subir CSV", "☁️ Cargar desde Cloud Storage"],
            index=0
        )
        
        uploaded_file = None
        
        # Initialize session state for data persistence
        if 'loaded_data' not in st.session_state:
            st.session_state.loaded_data = None
        if 'data_source_info' not in st.session_state:
            st.session_state.data_source_info = None
        
        # Use cached data if available
        data = st.session_state.loaded_data
        gcs_bucket = None
        gcs_path = None
        
        if data_source == "☁️ Cargar desde Cloud Storage":
            st.markdown("**Cargar desde Google Cloud Storage:**")
            st.info("💡 **Para archivos grandes (>32MB):** Usa el bucket compartido del proyecto. Solo necesitas especificar la ruta de tu archivo.")
            
            # Get default bucket from environment or use project default
            PROJECT_BUCKET = os.getenv("GCS_BUCKET_NAME", "data_clusters")
            
            # Show current loaded data info if available
            if st.session_state.loaded_data is not None and st.session_state.data_source_info:
                source_info = st.session_state.data_source_info.get('source', 'Datos cargados')
                st.success(f"✅ **Datos ya cargados:** {source_info} ({len(st.session_state.loaded_data):,} contactos)")
                if st.button("🔄 Recargar desde Cloud Storage"):
                    st.session_state.loaded_data = None
                    st.session_state.data_source_info = None
                    st.rerun()
                st.markdown("---")
            
            st.markdown(f"**📦 Bucket del proyecto:** `{PROJECT_BUCKET}` (pre-configurado)")
            st.caption("💡 Todos los archivos se guardan en este bucket compartido del proyecto")
            
            gcs_bucket = PROJECT_BUCKET  # Use project bucket automatically
            
            gcs_path = st.text_input(
                "📁 Ruta del archivo en el bucket",
                value=st.session_state.data_source_info.get('path', '') if st.session_state.data_source_info else "",
                help="Ejemplo: contacts_campus_Qro_.csv o uploads/20241112_095136_archivo.csv. La ruta es el nombre que aparece en la columna 'Name' de Cloud Storage."
            )
            
            if st.button("🔄 Cargar desde Cloud Storage", type="primary"):
                if not gcs_path:
                    st.error("❌ Por favor ingresa la ruta del archivo en el bucket")
                else:
                    try:
                        with st.spinner("📥 Cargando archivo desde Cloud Storage..."):
                            data = load_data(gcs_bucket=gcs_bucket, gcs_path=gcs_path)
                            validation = validate_data(data)
                            
                            if validation['is_valid']:
                                # Save to session state for persistence
                                st.session_state.loaded_data = data
                                st.session_state.data_source_info = {
                                    'type': 'gcs',
                                    'bucket': gcs_bucket,
                                    'path': gcs_path,
                                    'source': f"gs://{gcs_bucket}/{gcs_path}"
                                }
                                
                                st.success(f"✅ Cargados {len(data):,} contactos desde Cloud Storage")
                                st.info("💡 Los datos están guardados y disponibles para todos los clusters. Puedes navegar entre clusters sin recargar.")
                                
                                # Show data preview
                                with st.expander("📋 Vista Previa de Datos"):
                                    st.write(f"**Fuente:** gs://{gcs_bucket}/{gcs_path}")
                                    st.write(f"**Columnas:** {len(data.columns)}")
                                    st.write(f"**Filas:** {len(data):,}")
                                    st.dataframe(data.head(3), use_container_width=True)
                                
                                # Show warnings if any
                                if validation['warnings']:
                                    with st.expander("⚠️ Advertencias", expanded=False):
                                        for warning in validation['warnings']:
                                            st.warning(warning)
                                
                                # Update data variable
                                data = st.session_state.loaded_data
                            else:
                                st.error(f"❌ Datos inválidos: Faltan columnas requeridas: {', '.join(validation['missing_basic'])}")
                                data = None
                                st.session_state.loaded_data = None
                                st.session_state.data_source_info = None
                    except Exception as e:
                        st.error(f"❌ Error cargando desde Cloud Storage: {e}")
                        st.info("""
                        **Verifica:**
                        1. El nombre del bucket es correcto
                        2. La ruta del archivo es correcta
                        3. El servicio tiene permisos para leer el bucket
                        4. El archivo existe en Cloud Storage
                        """)
                        data = None
                        st.session_state.loaded_data = None
                        st.session_state.data_source_info = None
            
            with st.expander("📖 ¿Cómo identificar la ruta del archivo?"):
                st.markdown("""
                **La ruta es el nombre que aparece en la columna "Name" de Cloud Storage:**
                
                - **Si el archivo está en la raíz del bucket:**
                  - Solo el nombre: `contacts_campus_Qro_.csv`
                
                - **Si el archivo está en una carpeta:**
                  - Incluye la carpeta: `datos/contacts_campus_Qro_.csv`
                  - O con subcarpetas: `uploads/2024/noviembre/archivo.csv`
                
                **Ejemplo práctico:**
                - Bucket: `data_clusters`
                - Nombre en la lista: `contacts_campus_Qro_.csv`
                - **Ruta a usar:** `contacts_campus_Qro_.csv` ✅
                """)
            
            with st.expander("📤 ¿Cómo subir un archivo al bucket del proyecto?"):
                st.markdown("""
                Tienes **3 formas** de subir archivos al bucket `data_clusters`:
                
                **🌐 Opción 1: Desde la Consola de GCP (Más fácil)**
                1. Ve a [Cloud Storage](https://console.cloud.google.com/storage/browser/data_clusters)
                2. Haz clic en el botón **"Upload"** (arriba)
                3. Selecciona tu archivo CSV desde tu computadora
                4. Espera a que termine la subida
                5. **Anota el nombre** que aparece en la lista (esa es la ruta)
                6. Usa esa ruta en la aplicación
                
                **💻 Opción 2: Desde la línea de comandos**
                ```bash
                # Subir archivo a la raíz del bucket
                gsutil cp archivo.csv gs://data_clusters/
                # Ruta: archivo.csv
                
                # Subir archivo a una carpeta
                gsutil cp archivo.csv gs://data_clusters/datos/
                # Ruta: datos/archivo.csv
                ```
                
                **📤 Opción 3: Desde esta aplicación (Automático)**
                - Selecciona **"⬆️ Subir CSV"** arriba
                - Si el archivo es grande, se sube automáticamente al bucket
                - No necesitas hacer nada más
                
                **💡 Recomendación:** Para archivos grandes, usa la Opción 3 (desde la app) - es la más fácil y automática.
                """)
        
        elif data_source == "⬆️ Subir CSV":
            st.markdown("**Subir Exportación de Contactos de HubSpot:**")
            
            # Get default bucket name from environment or use project default
            PROJECT_BUCKET = os.getenv("GCS_BUCKET_NAME", "data_clusters")
            
            uploaded_file = st.file_uploader(
                "Elegir un archivo CSV",
                type=['csv'],
                help="Sube tu archivo CSV. Archivos grandes se subirán automáticamente a Cloud Storage."
            )
            
            if uploaded_file is not None:
                # Check file size (in bytes)
                file_size_mb = uploaded_file.size / (1024 * 1024)
                
                # If file is large, offer to upload to Cloud Storage
                if file_size_mb > 25:  # Close to the 32MB limit
                    st.warning(f"⚠️ **Archivo grande detectado ({file_size_mb:.1f}MB)**")
                    st.info("💡 Este archivo es grande. Te recomendamos subirlo a Cloud Storage para evitar problemas.")
                    
                    use_gcs = st.checkbox(
                        "☁️ Subir a Cloud Storage automáticamente",
                        value=True,
                        help="El archivo se subirá a Cloud Storage y luego se cargará desde ahí"
                    )
                    
                    if use_gcs:
                        st.markdown(f"**📦 Bucket del proyecto:** `{PROJECT_BUCKET}` (pre-configurado)")
                        st.caption("💡 Tu archivo se guardará automáticamente en el bucket compartido del proyecto")
                        
                        gcs_bucket_upload = PROJECT_BUCKET  # Use project bucket automatically
                        
                        # Generate a unique filename in uploads folder
                        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                        default_gcs_path = f"uploads/{timestamp}_{uploaded_file.name}"
                        gcs_path_upload = st.text_input(
                            "📁 Ruta donde guardar (opcional)",
                            value=default_gcs_path,
                            help=f"Se guardará en: gs://{PROJECT_BUCKET}/uploads/ con nombre único. Puedes cambiarlo si quieres."
                        )
                        
                        if st.button("☁️ Subir y Cargar desde Cloud Storage", type="primary"):
                            try:
                                with st.spinner("📤 Subiendo archivo a Cloud Storage..."):
                                    # Upload to Cloud Storage
                                    from utils import upload_to_gcs
                                    upload_to_gcs(uploaded_file, gcs_bucket_upload, gcs_path_upload)
                                    st.success(f"✅ Archivo subido a gs://{gcs_bucket_upload}/{gcs_path_upload}")
                                
                                with st.spinner("📥 Cargando datos desde Cloud Storage..."):
                                    # Load from Cloud Storage
                                    data = load_data(gcs_bucket=gcs_bucket_upload, gcs_path=gcs_path_upload)
                                    validation = validate_data(data)
                                    
                                    if validation['is_valid']:
                                        # Save to session state
                                        st.session_state.loaded_data = data
                                        st.session_state.data_source_info = {
                                            'type': 'gcs_upload',
                                            'bucket': gcs_bucket_upload,
                                            'path': gcs_path_upload,
                                            'source': f"gs://{gcs_bucket_upload}/{gcs_path_upload}"
                                        }
                                        
                                        st.success(f"✅ Cargados {len(data):,} contactos")
                                        st.info("💡 Los datos están guardados y disponibles para todos los clusters.")
                                        
                                        # Show data preview
                                        with st.expander("📋 Vista Previa de Datos"):
                                            st.write(f"**Fuente:** gs://{gcs_bucket_upload}/{gcs_path_upload}")
                                            st.write(f"**Columnas:** {len(data.columns)}")
                                            st.write(f"**Filas:** {len(data):,}")
                                            st.dataframe(data.head(3), use_container_width=True)
                                        
                                        # Show warnings if any
                                        if validation['warnings']:
                                            with st.expander("⚠️ Advertencias", expanded=False):
                                                for warning in validation['warnings']:
                                                    st.warning(warning)
                                        
                                        # Update data variable
                                        data = st.session_state.loaded_data
                                    else:
                                        st.error(f"❌ Datos inválidos: Faltan columnas requeridas: {', '.join(validation['missing_basic'])}")
                                        data = None
                                        st.session_state.loaded_data = None
                                        st.session_state.data_source_info = None
                            except Exception as e:
                                st.error(f"❌ Error: {e}")
                                st.info("""
                                **Verifica:**
                                1. El bucket existe y tiene permisos correctos
                                2. El servicio tiene permisos para escribir en el bucket
                                3. Ejecuta: `./configurar_cloud_storage.sh` para configurar permisos
                                """)
                                data = None
                        else:
                            data = None
                    else:
                        # Try to load directly (may fail if too large)
                        try:
                            data = load_data(uploaded_file)
                            validation = validate_data(data)
                            
                            if validation['is_valid']:
                                # Save to session state
                                st.session_state.loaded_data = data
                                st.session_state.data_source_info = {
                                    'type': 'upload',
                                    'source': uploaded_file.name
                                }
                                st.info("💡 Los datos están guardados y disponibles para todos los clusters.")
                                # Update data variable
                                data = st.session_state.loaded_data
                        except Exception as e:
                            error_msg = str(e)
                            if "413" in error_msg or "Payload Too Large" in error_msg:
                                st.error("❌ **Error: Archivo demasiado grande para subir directamente**")
                                st.info("💡 Por favor activa la opción 'Subir a Cloud Storage automáticamente' arriba.")
                                data = None
                                st.session_state.loaded_data = None
                                st.session_state.data_source_info = None
                            else:
                                raise
                else:
                    # Small file, try to load directly
                    try:
                        data = load_data(uploaded_file)
                        validation = validate_data(data)
                        
                        if validation['is_valid']:
                            # Save to session state
                            st.session_state.loaded_data = data
                            st.session_state.data_source_info = {
                                'type': 'upload',
                                'source': uploaded_file.name
                            }
                            st.info("💡 Los datos están guardados y disponibles para todos los clusters.")
                            # Update data variable
                            data = st.session_state.loaded_data
                    except Exception as e:
                        error_msg = str(e)
                        if "413" in error_msg or "Payload Too Large" in error_msg:
                            st.error("❌ **Error: Archivo demasiado grande**")
                            st.info("💡 Intenta usar la opción '☁️ Cargar desde Cloud Storage' para archivos grandes.")
                            data = None
                            st.session_state.loaded_data = None
                            st.session_state.data_source_info = None
                        else:
                            raise
                
            else:
                st.info("👆 Por favor sube un archivo CSV para comenzar el análisis")
        else:
            # Use default file
            try:
                # Check if we already have data loaded
                if st.session_state.loaded_data is not None:
                    data = st.session_state.loaded_data
                    if st.session_state.data_source_info:
                        st.success(f"✅ Datos ya cargados: {st.session_state.data_source_info.get('source', 'Archivo predeterminado')}")
                    else:
                        st.success(f"✅ Usando datos cargados previamente ({len(data):,} contactos)")
                else:
                    data = load_data()
                    # Save to session state
                    st.session_state.loaded_data = data
                    st.session_state.data_source_info = {
                        'type': 'default',
                        'source': 'data/raw/contacts_campus_Qro_.csv'
                    }
                    st.success(f"✅ Cargados {len(data):,} contactos")
                    st.info("💡 Los datos están guardados y disponibles para todos los clusters.")
                
                    with st.expander("ℹ️ Información de Datos"):
                        if st.session_state.data_source_info:
                            st.write(f"**Fuente:** {st.session_state.data_source_info.get('source', 'Archivo predeterminado')}")
                        else:
                            st.write("**Archivo:** data/raw/contacts_campus_Qro_.csv")
                        st.write(f"**Columnas:** {len(data.columns)}")
                        st.write(f"**Filas:** {len(data):,}")
            except Exception as e:
                st.error(f"❌ Error cargando archivo predeterminado: {e}")
                st.info("💡 Intenta subir tu propio archivo CSV")
                data = None
                st.session_state.loaded_data = None
                st.session_state.data_source_info = None
        
        st.markdown("---")
        
        # Global Filters Section
        st.markdown("### 🎛️ Filtros Globales")
        
        with st.expander("📅 Filtro de Período Académico", expanded=False):
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
                                5: "Especial",
                                10: "Primavera", 
                                35: "Verano",
                                60: "Otoño",
                                75: "Invierno/Especial"
                            }
                            
                            semester = period_map.get(period_code, f"Desconocido({period_code})")
                            return f"{year} {semester}"
                        except:
                            return "Desconocido"
                    
                    import pandas as pd
                    from utils import hist_latest
                    
                    # Get latest periodo values
                    periodo_latest = data[periodo_col].apply(hist_latest)
                    periodo_readable = periodo_latest.apply(convert_periodo)
                    available_periodos = sorted([p for p in periodo_readable.unique() if p != "Desconocido"])
                    
                    if available_periodos:
                        selected_periodos = st.multiselect(
                            "Seleccionar Período(s) de Ingreso:",
                            options=available_periodos,
                            default=[],
                            help="Filtrar contactos por su período de ingreso (dejar vacío para todos)"
                        )
                        
                        st.session_state['filter_periodos'] = selected_periodos
                    else:
                        st.info("No se encontraron datos válidos de período de ingreso")
                else:
                    st.info("📅 Campo de período de ingreso no encontrado en el dataset")
            else:
                st.info("Cargar datos para ver filtro de período")
        
        with st.expander("💼 Filtro de Estado de Cierre", expanded=False):
            closure_status = st.radio(
                "Estado de Cierre:",
                ["Todos los Contactos", "Solo Cerrados", "Solo Abiertos"],
                index=0,
                help="Filtrar por estado de cierre de tratos"
            )
            
            # Store in session state
            st.session_state['filter_closure_status'] = closure_status
        
        with st.expander("🔄 Filtros de Ciclo de Vida", expanded=False):
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
                            "Seleccionar Etapas del Ciclo de Vida (dejar vacío para todas):",
                            options=available_stages,
                            default=[],
                            help="Filtrar a etapas específicas del ciclo de vida (usa solo el valor MÁS RECIENTE)"
                        )
                        
                        st.session_state['filter_lifecycle_stages'] = selected_stages
                    else:
                        st.info("No se encontraron etapas válidas del ciclo de vida")
                else:
                    st.info("Datos de etapa del ciclo de vida no disponibles")
        
        # Reset filters button
        if st.button("🔄 Restablecer Todos los Filtros", use_container_width=True):
            for key in list(st.session_state.keys()):
                if key.startswith('filter_'):
                    del st.session_state[key]
            st.rerun()
        
        # Show active filters count
        active_filters = sum(1 for k in st.session_state.keys() if k.startswith('filter_'))
        if active_filters > 0:
            st.info(f"✅ {active_filters} filtro(s) activo(s)")
        
        st.markdown("---")
        
        # Geographic configuration (for Cluster 2)
        render_geo_config_ui()
        
        st.markdown("---")
        st.markdown("### 📊 Navegación")
        
        cluster_choice = st.radio(
            "Seleccionar Estrategia de Segmentación:",
            ["🏠 Resumen", "📱 Cluster 1: Compromiso Social", "🌍 Cluster 2: Geografía y Compromiso", 
             "🎪 Cluster 3: Actividades APREU"],
            index=0,
            disabled=(data is None)
        )
        
        st.markdown("---")
        st.markdown("### 📖 Referencia Rápida")
        
        with st.expander("🎯 ¿Qué Cluster Debo Usar?"):
            st.markdown("""
            **📱 Cluster 1: Estrategia de Redes Sociales**
            - *Cuándo:* Optimizar campañas de redes sociales
            - *Para:* Asignación de presupuesto por plataforma
            - *Responde:* ¿Qué plataformas convierten mejor?
            
            **🌍 Cluster 2: Campañas Regionales**
            - *Cuándo:* Planificar alcance geográfico
            - *Para:* Estrategia de marketing regional
            - *Responde:* ¿Qué regiones tienen mejor rendimiento?
            
            **🎪 Cluster 3: Planificación de Eventos**
            - *Cuándo:* Optimizar actividades promocionales
            - *Para:* Análisis de ROI de eventos APREU
            - *Responde:* ¿Qué eventos impulsan conversiones?
            
            ---
            
            **💡 Consejo Pro:** ¡Usa múltiples clusters juntos!
            - Cluster 1 + 2 = Estrategia social por región
            - Cluster 2 + 3 = Planificación de eventos por geografía
            - Los 3 = Estrategia de marketing integral
            """)
        
        st.markdown("---")
        st.markdown("### ℹ️ Acerca de")
        st.info("""
        **POC de Segmentación Avanzada**
        
        Esta aplicación muestra tres enfoques complementarios de segmentación:
        
        - **Cluster 1**: Actividad en redes sociales y compromiso por plataforma
        - **Cluster 2**: Distribución geográfica y niveles de compromiso  
        - **Cluster 3**: Actividades promocionales y canales de entrada
        
        **Filtros Globales Disponibles:**
        - 📅 Período Académico (Período de Ingreso)
        - 🔄 Etapa del Ciclo de Vida (valor más reciente)
        - 💼 Estado de Cierre (Abierto/Cerrado/Todos)
        
        Cada cluster también tiene filtros específicos para análisis más profundos.
        
        **Pipeline de Datos:**
        1. Total Contactos → 2. Contactos APREU → 3. Remover "other"/"subscriber" → 4. Contactos de Trabajo
        """)
        
        # Download template
        st.markdown("---")
        st.markdown("### 📥 ¿Necesitas Ayuda?")
        
        with st.expander("Formato de Datos Requerido"):
            st.markdown("""
            **Tu CSV debe incluir:**
            
            **Campos Básicos:**
            - Record ID (identificador de contacto)
            - Propiedad del contacto (para filtrar por APREU)
            
            **Para Filtros Globales:**
            - Período de ingreso (período de admisión - formato: YYYYMM, ej., 202460 = Otoño 2024)
            - Etapa del Ciclo de Vida (usará el valor más reciente, removerá "other" y "subscriber")
            - Fecha de Cierre (para filtro de estado de cierre)
            
            **Para Cluster 1 (Social):**
            - Fuente Original
            - Clics de Broadcast/LinkedIn/Twitter/Facebook
            - Número de Sesiones, Páginas Vistas, Envíos de Formularios
            
            **Para Cluster 2 (Geografía):**
            - País IP, Estado/Región IP
            - Campos de ubicación de preparatoria
            - Número de Sesiones, Páginas Vistas, Envíos de Formularios
            
            **Para Cluster 3 (APREU):**
            - Actividades de promoción APREU
            - Primera Conversión/Conversión Reciente
            - Información de preparatoria
            
            **Nota:** Los campos con valores históricos (delimitador: //) usarán el valor más reciente para filtrar.
            
            **Códigos de Período:** 05=Especial, 10=Primavera, 35=Verano, 60=Otoño, 75=Invierno/Especial
            """)
        
        if st.button("📄 Ver Estructura de Datos de Ejemplo", use_container_width=True):
            if data is not None:
                st.info("Columnas de ejemplo de los datos cargados:")
                st.code('\n'.join(data.columns[:20].tolist()))
            else:
                st.info("Cargar datos primero para ver estructura de columnas")
    
    # Main content area
    if data is None:
        st.warning("⚠️ No hay datos cargados. Por favor elige una opción para cargar tus datos.")
        st.markdown("---")
        st.markdown("### 🚀 Comenzando - Cómo Cargar tus Datos")
        st.markdown("""
        Tienes **3 opciones** para cargar tus datos. Elige la que mejor se adapte a tu situación:
        """)
        
        # Option 1
        with st.expander("📂 Opción 1: Usar Archivo Predeterminado", expanded=False):
            st.markdown("""
            **¿Cuándo usar esta opción?**
            - Si ya tienes un archivo CSV guardado en el servidor
            - Para pruebas rápidas con datos de ejemplo
            
            **Pasos:**
            1. Asegúrate de que el archivo `contacts_campus_Qro_.csv` esté en el directorio `data/raw/`
            2. En la barra lateral izquierda, selecciona **"📂 Usar Archivo Predeterminado"**
            3. Los datos se cargarán automáticamente
            
            **✅ Ventajas:** Rápido, no necesitas subir nada
            """)
        
        # Option 2
        with st.expander("⬆️ Opción 2: Subir CSV Directamente", expanded=False):
            st.markdown("""
            **¿Cuándo usar esta opción?**
            - Si tu archivo CSV es **menor a 25MB**
            - Para archivos pequeños o medianos
            - Cuando quieres subir datos directamente desde tu computadora
            
            **Pasos:**
            1. Exporta tus contactos de HubSpot como archivo CSV
            2. En la barra lateral, selecciona **"⬆️ Subir CSV"**
            3. Haz clic en el botón de subir y selecciona tu archivo CSV
            4. Espera a que se valide y cargue (puede tardar unos segundos)
            
            **✅ Ventajas:** Fácil y rápido para archivos pequeños  
            **⚠️ Limitación:** Archivos mayores a 32MB pueden fallar
            """)
        
        # Option 3 - Cloud Storage
        with st.expander("☁️ Opción 3: Cargar desde Cloud Storage (Recomendado para archivos grandes)", expanded=True):
            st.markdown("""
            **¿Cuándo usar esta opción?**
            - Si tu archivo CSV es **mayor a 25MB** o muy grande
            - Cuando necesitas trabajar con archivos de cualquier tamaño
            - Para archivos que ya están en Google Cloud Storage
            
            **Pasos:**
            
            **A) Si tu archivo ya está en Cloud Storage:**
            1. En la barra lateral, selecciona **"☁️ Cargar desde Cloud Storage"**
            2. El bucket ya está pre-configurado (`data_clusters`) - no necesitas cambiarlo
            3. Ingresa solo la **ruta del archivo** (ej: `contacts_campus_Qro_.csv`)
               - 💡 La ruta es el nombre que aparece en la columna "Name" de Cloud Storage
               - Si está en una carpeta: `uploads/20241112_095136_archivo.csv`
            4. Haz clic en **"🔄 Cargar desde Cloud Storage"**
            
            **B) Si necesitas subir tu archivo primero:**
            1. Sube tu archivo CSV al bucket del proyecto:
               - Desde la [consola de GCP](https://console.cloud.google.com/storage): Ve a Cloud Storage → Bucket `data_clusters` → "Upload"
               - O desde la línea de comandos: `gsutil cp archivo.csv gs://data_clusters/`
            2. Luego sigue los pasos del punto A arriba (solo necesitas la ruta del archivo)
            
            **💡 Simplificado:** El bucket `data_clusters` está pre-configurado para todo el proyecto. Solo necesitas especificar la ruta de tu archivo.
            
            **✅ Ventajas:** 
            - ✅ Funciona con archivos de **cualquier tamaño** (sin límites)
            - ✅ Los datos se guardan y están disponibles para todos los clusters
            - ✅ No necesitas recargar al cambiar de cluster
            
            **💡 Tip:** Si subes un archivo grande directamente (Opción 2), la aplicación te ofrecerá subirlo automáticamente a Cloud Storage.
            """)
        
        st.markdown("---")
        st.markdown("### 💡 Consejos Importantes")
        st.info("""
        **📊 Una vez cargados los datos:**
        - Los datos quedan **guardados en tu sesión**
        - Puedes navegar entre todos los clusters sin recargar
        - Los datos estarán disponibles hasta que cierres la aplicación o recargues
        
        **🔍 ¿Necesitas ayuda?**
        - Revisa la sección **"Formato de Datos Requerido"** en la barra lateral
        - Ve la estructura de datos de ejemplo usando el botón en la barra lateral
        - Si tienes problemas, verifica que tu archivo CSV tenga las columnas requeridas
        """)
        
        st.markdown("---")
        st.markdown("### ❓ ¿Cuál Opción Elegir?")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("""
            **📂 Archivo Predeterminado**
            - ✅ Ya está configurado
            - ✅ Carga instantánea
            - ⚠️ Solo si existe el archivo
            """)
        
        with col2:
            st.markdown("""
            **⬆️ Subir CSV**
            - ✅ Fácil y directo
            - ✅ Para archivos < 25MB
            - ⚠️ Límite de tamaño
            """)
        
        with col3:
            st.markdown("""
            **☁️ Cloud Storage**
            - ✅ Sin límite de tamaño
            - ✅ Archivos grandes
            - ✅ Más estable
            """)
    else:
        # Apply global filters
        filtered_data, filters_applied = apply_global_filters(data)
        
        # Show filter status
        if len(filters_applied) > 0:
            with st.expander(f"🔍 Filtros Activos ({len(filters_applied)})", expanded=False):
                st.markdown("**Filtros aplicados:**")
                for f in filters_applied:
                    st.markdown(f"- {f}")
                st.markdown(f"**Resultado:** {len(filtered_data):,} de {len(data):,} contactos ({len(filtered_data)/len(data)*100:.1f}%)")
        
        # Route to appropriate cluster with filtered data
        if cluster_choice == "🏠 Resumen":
            render_overview(filtered_data)
        elif cluster_choice == "📱 Cluster 1: Compromiso Social":
            render_cluster1(filtered_data)
        elif cluster_choice == "🌍 Cluster 2: Geografía y Compromiso":
            render_cluster2(filtered_data)
        elif cluster_choice == "🎪 Cluster 3: Actividades APREU":
            render_cluster3(filtered_data)

def render_overview(data):
    """Render the overview dashboard"""
    
    st.markdown("## 📊 Resumen Ejecutivo")
    st.markdown("---")
    
    if data is None:
        st.error("⚠️ Datos no cargados. Por favor revisa el archivo de datos.")
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
    st.markdown("### 📊 Pipeline de Contactos")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Contactos", f"{total_contacts:,}", help="Todos los contactos en el dataset")
    
    with col2:
        apreu_pct = (apreu_count / total_contacts * 100) if total_contacts > 0 else 0
        st.metric("Contactos APREU", f"{apreu_count:,}", delta=f"{apreu_pct:.1f}%", help="Contactos donde Propiedad = APREU")
    
    with col3:
        removed = apreu_count - working_count
        st.metric("Después de Limpieza", f"{working_count:,}", delta=f"-{removed:,}", delta_color="off", help="Contactos APREU después de remover etapas 'other' y 'subscriber' del ciclo de vida")
    
    with col4:
        st.metric("Tratos Cerrados", f"{closed_count:,}", delta=f"{close_rate:.1f}%", help="Contactos cerrados del conjunto de trabajo")
    
    st.markdown("---")
    
    # Cluster Comparison Section
    st.markdown("### 🎯 Comparación de Estrategias de Segmentación")
    
    tab1, tab2, tab3 = st.tabs(["📱 Cluster 1", "🌍 Cluster 2", "🎪 Cluster 3"])
    
    with tab1:
        st.markdown("""
        #### Cluster 1: Prospectos Socialmente Comprometidos
        
        **Objetivo:** Identificar y segmentar prospectos con actividad en redes sociales usando análisis avanzado de datos históricos 
        y detección multi-plataforma.
        
        **Características Clave:**
        - ✅ Análisis integral de datos históricos (TODOS los valores, no solo el más reciente)
        - ✅ Detección multi-plataforma (12+ plataformas: Instagram, TikTok, LinkedIn, Facebook, etc.)
        - ✅ Filtrado inteligente para contactos APREU
        - ✅ Etiquetado inteligente de plataformas usando datos históricos + clics
        - ✅ Análisis avanzado de cierre con buckets de tiempo-hasta-cierre
        - ✅ Seguimiento de integración del ciclo de vida
        - ✅ Filtros interactivos (segmento, plataforma, clics sociales, puntuación de compromiso)
        - ✅ Benchmarking de rendimiento con análisis de cuartiles
        - ✅ Exportaciones CSV (datos completos, resumen, desglose por plataforma)
        
        **Segmentos:**
        - **1A. Alto Compromiso + Actividad Social**: Usuarios sociales activos, mayor tasa de cierre
        - **1B. Bajo Compromiso + Actividad Social**: Presencia social pero interacción mínima
        
        **Superposiciones de Plataforma:** Compromiso combinado + etiquetas de plataforma (ej., "1A + Google_Ads", "1B + Facebook")
        
        **Pestañas Disponibles:** Resumen, Análisis de Segmento, Análisis de Plataforma, Resultados de Negocio, Cerradores Rápidos/Lentos, Período Académico, Benchmarks de Rendimiento, Búsqueda de Contactos
        """)
        
        col1, col2 = st.columns(2)
        with col1:
            st.info("**Caso de Uso Principal:** Optimización del equipo de redes sociales, asignación de presupuesto por plataforma, campañas de remarketing")
        with col2:
            st.success("**Esperado:** Contactos comprometidos divididos en 1A/1B con etiquetas de plataforma")
    
    with tab2:
        st.markdown("""
        #### Cluster 2: Segmentación por Geografía y Compromiso
        
        **Objetivo:** Segmentar contactos por geografía (Local/Foráneo/Internacional) y nivel de compromiso 
        en 6 subclusters accionables.
        
        **Características Clave:**
        - ✅ Clasificación geográfica (Local, Foráneo, Internacional) - ¡Configurable!
        - ✅ Puntuación de compromiso por nivel geo con umbrales de cuantil (percentil 70)
        - ✅ Normalización mejorada de estados (32 estados mexicanos + variantes CDMX)
        - ✅ Análisis de rendimiento a nivel estatal y clasificación de niveles
        - ✅ Configuración geo dinámica (cambiar país de origen y región local)
        - ✅ Análisis de tiempo-hasta-cierre por geografía
        - ✅ Filtros interactivos (segmento, nivel geo, país, nivel de compromiso)
        - ✅ Benchmarking de rendimiento por geografía y país
        - ✅ Exportaciones CSV (datos completos, resumen, desglose geográfico)
        
        **Segmentos:**
        - **2A**: Foráneo (no local), Alto Compromiso
        - **2B**: Foráneo (no local), Bajo Compromiso  
        - **2C**: Internacional, Alto Compromiso
        - **2D**: Internacional, Bajo Compromiso
        - **2E**: Local, Alto Compromiso
        - **2F**: Local, Bajo Compromiso
        
        **Pestañas Disponibles:** Resumen, Análisis de Segmento, Análisis Geográfico, Resultados de Negocio, Cerradores Rápidos/Lentos, Benchmarks de Rendimiento, Búsqueda de Contactos
        """)
        
        col1, col2 = st.columns(2)
        with col1:
            st.info("**Caso de Uso Principal:** Campañas de marketing regional, reclutamiento internacional, compromiso local QRO")
        with col2:
            st.success("**Segmentos Esperados:** 6 segmentos principales (2A-2F) + sub-segmentos específicos por estado para foráneos")
    
    with tab3:
        st.markdown("""
        #### Cluster 3: Convertidores Impulsados por Promoción (Actividades APREU)
        
        **Objetivo:** Segmentar contactos por actividades promocionales y canales de entrada usando análisis 
        integral de actividades históricas APREU.
        
        **Características Clave:**
        - ✅ Análisis integral de actividades históricas APREU (TODOS los eventos asistidos)
        - ✅ Detección multi-actividad (Open Day, Fogatada, TDLA, Gira Panamá, WhatsApp, etc.)
        - ✅ Clasificación inteligente de canales de entrada (Digital/Evento/Mensajería/Nicho)
        - ✅ Análisis cruzado de preparatoria por actividad
        - ✅ Seguimiento de eventos de conversión (primera + conversión reciente)
        - ✅ Visualización del viaje de actividad por contacto
        - ✅ Análisis de compromiso por email y línea de tiempo de conversión
        - ✅ Análisis de período académico con tendencias estacionales
        
        **Segmentos:**
        - **3A. Canal Digital**: Sitio web, formularios, entradas en línea → secuencias automatizadas
        - **3B. Canal Eventos**: Open Day, Fogatada, eventos en vivo → seguimiento 48h
        - **3C. Canal Mensajería**: WhatsApp, contacto directo → respuesta personalizada y rápida
        - **3D. Canal Nicho**: Programas especializados, campañas pequeñas → evaluación de ROI
        
        **Pestañas Disponibles:** Resumen, Análisis de Segmento, Análisis de Actividad, Análisis de Preparatoria, Email y Conversión, Cerradores Rápidos/Lentos, Período Académico, Búsqueda de Contactos
        """)
        
        col1, col2 = st.columns(2)
        with col1:
            st.info("**Caso de Uso Principal:** Análisis de ROI de eventos, optimización de campañas APREU, asociaciones con preparatorias")
        with col2:
            st.success("**Segmentos Esperados:** 4 canales de entrada (3A-3D) con insights de actividad y preparatoria")
    
    st.markdown("---")
    
    # Quick Start Guide
    st.markdown("### 🚀 Guía de Inicio Rápido")
    
    st.markdown("""
    **Cómo usar esta aplicación:**
    
    1. **Selecciona un cluster** desde la navegación de la barra lateral
    2. **Explora distribuciones de segmentos** y métricas de rendimiento
    3. **Analiza desgloses detallados** usando filtros interactivos
    4. **Busca contactos individuales** usando la herramienta de búsqueda de contactos
    5. **Exporta datos** para análisis adicional o activación de campañas
    
    **Consejos de Navegación:**
    - Usa la **barra lateral** para cambiar entre clusters
    - Cada cluster tiene **múltiples pestañas** para diferentes análisis
    - **Pasa el cursor sobre los gráficos** para información detallada
    - Usa **filtros** para profundizar en segmentos específicos
    - La función de **búsqueda de contactos** está disponible en cada cluster
    """)
    
    st.markdown("---")
    
    # Data Quality Summary
    with st.expander("📋 Resumen de Calidad de Datos", expanded=False):
        st.markdown("#### Cobertura de Datos por Cluster")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("**Cluster 1: Compromiso Social**")
            social_fields = ['Original Source', 'Latest Traffic Source', 'Broadcast Clicks', 
                           'LinkedIn Clicks', 'Twitter Clicks', 'Facebook Clicks']
            # Handle both original and lowercase column names
            coverage = 0
            for field in social_fields:
                if field in data.columns:
                    coverage += data[field].notna().sum()
                elif field.lower().replace(' ', '_') in data.columns:
                    coverage += data[field.lower().replace(' ', '_')].notna().sum()
            st.metric("Puntos de Datos Disponibles", f"{coverage:,}")
        
        with col2:
            st.markdown("**Cluster 2: Geografía**")
            geo_fields = ['IP Country', 'IP State/Region', 'País preparatoria BPM', 'Estado de preparatoria BPM']
            coverage = 0
            for field in geo_fields:
                if field in data.columns:
                    coverage += data[field].notna().sum()
                elif field.lower().replace(' ', '_').replace('/', '_') in data.columns:
                    coverage += data[field.lower().replace(' ', '_').replace('/', '_')].notna().sum()
            st.metric("Puntos de Datos Disponibles", f"{coverage:,}")
        
        with col3:
            st.markdown("**Cluster 3: Actividades APREU**")
            apreu_fields = ['Actividades de promoción APREU', 'First Conversion', 'Recent Conversion']
            coverage = 0
            for field in apreu_fields:
                if field in data.columns:
                    coverage += data[field].notna().sum()
                elif field.lower().replace(' ', '_') in data.columns:
                    coverage += data[field.lower().replace(' ', '_')].notna().sum()
            st.metric("Puntos de Datos Disponibles", f"{coverage:,}")

if __name__ == "__main__":
    main()

