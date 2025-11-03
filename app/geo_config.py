"""
Geographic Configuration Module
Allows users to define their own domestic/local regions dynamically
"""

import streamlit as st
import pandas as pd
from utils import normalize_text

# Default configuration (Mexico/Querétaro)
DEFAULT_CONFIG = {
    'home_country': 'Mexico',
    'home_country_aliases': ['mexico', 'mx', 'mex'],
    'local_city': 'Querétaro',
    'local_region': 'Querétaro',
    'local_aliases': ['queretaro', 'qro', 'santiago de queretaro'],
}

def render_geo_config_ui():
    """Render the geographic configuration interface in sidebar"""
    
    st.markdown("### 🌎 Configuración Geográfica")
    
    with st.expander("⚙️ Configurar Tu Geografía", expanded=False):
        st.markdown("""
        **Personaliza el análisis geográfico para tu región:**
        
        Define qué significan "nacional" y "local" para tu organización.
        """)
        
        # Home Country Configuration
        st.markdown("#### 🏠 País de Origen (Nacional)")
        home_country = st.text_input(
            "Tu país de origen:",
            value=st.session_state.get('geo_home_country', 'Mexico'),
            help="Los contactos de este país serán clasificados como 'nacionales'"
        )
        
        home_aliases = st.text_input(
            "Alias del país (separados por comas):",
            value=st.session_state.get('geo_home_aliases', 'mexico, mx, mex'),
            help="Nombres/códigos alternativos para tu país (ej., USA, US, United States)"
        )
        
        st.markdown("---")
        
        # Local Region Configuration
        st.markdown("#### 📍 Región Local (Tu Ciudad/Estado)")
        local_region = st.text_input(
            "Nombre de tu región local:",
            value=st.session_state.get('geo_local_region', 'Querétaro'),
            help="Tu ciudad o estado específico (ej., California, São Paulo, Querétaro)"
        )
        
        local_aliases = st.text_input(
            "Alias de la región local (separados por comas):",
            value=st.session_state.get('geo_local_aliases', 'queretaro, qro, queretaro de arteaga'),
            help="Nombres alternativos para tu región (ej., SF, San Francisco, San Fran)"
        )
        
        st.markdown("---")
        
        # Geographic Tier Definitions
        st.markdown("#### 📊 Lógica de Clasificación")
        st.info("""
        **Los contactos serán clasificados como:**
        - 🏠 **Local**: De tu ciudad/región especificada
        - 🇲🇽 **Foráneo (no local)**: De tu país, pero no de la región local
        - 🌍 **Internacional**: De fuera de tu país
        """)
        
        # Apply button
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("✅ Aplicar Configuración", use_container_width=True):
                # Parse aliases
                home_aliases_list = [a.strip().lower() for a in home_aliases.split(',') if a.strip()]
                local_aliases_list = [a.strip().lower() for a in local_aliases.split(',') if a.strip()]
                
                # Save to session state
                st.session_state['geo_home_country'] = home_country
                st.session_state['geo_home_aliases'] = home_aliases
                st.session_state['geo_home_aliases_list'] = home_aliases_list
                st.session_state['geo_local_region'] = local_region
                st.session_state['geo_local_aliases'] = local_aliases
                st.session_state['geo_local_aliases_list'] = local_aliases_list
                st.session_state['geo_config_applied'] = True
                
                # Clear cached data to force re-analysis
                st.cache_data.clear()
                
                st.success(f"✅ ¡Configuración aplicada! País: {home_country}, Local: {local_region}")
                st.rerun()
        
        with col2:
            if st.button("🔄 Restablecer a Predeterminado", use_container_width=True):
                # Reset to Mexico/Querétaro defaults
                st.session_state['geo_home_country'] = 'Mexico'
                st.session_state['geo_home_aliases'] = 'mexico, mx, mex'
                st.session_state['geo_local_region'] = 'Querétaro'
                st.session_state['geo_local_aliases'] = 'queretaro, qro, queretaro de arteaga'
                st.session_state['geo_config_applied'] = True
                st.cache_data.clear()
                st.success("✅ Restablecido a valores predeterminados de México/Querétaro")
                st.rerun()
        
        # Show current configuration
        if st.session_state.get('geo_config_applied', False):
            st.markdown("---")
            st.markdown("**Configuración Actual:**")
            st.write(f"🏠 **País de Origen:** {st.session_state.get('geo_home_country', 'Mexico')}")
            st.write(f"📍 **Región Local:** {st.session_state.get('geo_local_region', 'Querétaro')}")

def get_geo_config():
    """Get the current geographic configuration"""
    
    # Initialize defaults if not set
    if 'geo_home_country' not in st.session_state:
        st.session_state['geo_home_country'] = DEFAULT_CONFIG['home_country']
        st.session_state['geo_home_aliases'] = ', '.join(DEFAULT_CONFIG['home_country_aliases'])
        st.session_state['geo_home_aliases_list'] = DEFAULT_CONFIG['home_country_aliases']
        st.session_state['geo_local_region'] = DEFAULT_CONFIG['local_region']
        st.session_state['geo_local_aliases'] = ', '.join(DEFAULT_CONFIG['local_aliases'])
        st.session_state['geo_local_aliases_list'] = DEFAULT_CONFIG['local_aliases']
    
    config = {
        'home_country': st.session_state.get('geo_home_country', 'Mexico'),
        'home_country_aliases': st.session_state.get('geo_home_aliases_list', ['mexico', 'mx', 'mex']),
        'local_region': st.session_state.get('geo_local_region', 'Querétaro'),
        'local_aliases': st.session_state.get('geo_local_aliases_list', ['queretaro', 'qro']),
    }
    
    return config

def is_home_country(country_txt, config):
    """Check if a country value matches the configured home country"""
    if pd.isna(country_txt) or country_txt == "unknown":
        return False
    
    country_lower = str(country_txt).lower().strip()
    
    # Check against home country name and aliases
    if country_lower == config['home_country'].lower():
        return True
    
    for alias in config['home_country_aliases']:
        if country_lower == alias.lower() or alias.lower() in country_lower:
            return True
    
    return False

def is_local_region(location_txt, config):
    """Check if a location value matches the configured local region"""
    if pd.isna(location_txt) or location_txt == "unknown":
        return False
    
    location_lower = str(location_txt).lower().strip()
    
    # Check against local region name and aliases
    for alias in config['local_aliases']:
        if alias.lower() in location_lower:
            return True
    
    return False

def classify_geo_tier_dynamic(row, config):
    """Classify geographic tier using dynamic configuration"""
    
    country = row.get('country_any', 'unknown')
    state = row.get('state_any', 'unknown')
    city = row.get('city_any', 'unknown')
    
    # Check local first (most specific)
    if is_local_region(city, config) or is_local_region(state, config):
        return 'local'
    
    # Check domestic (home country)
    if is_home_country(country, config):
        return 'domestic_non_local'
    
    # International (has country data but not home country)
    if country != 'unknown':
        return 'international'
    
    # Unknown (no location data)
    return 'unknown'

def get_geo_display_names(config):
    """Get display names for the UI based on configuration"""
    return {
        'local': f"Local ({config['local_region']})",
        'domestic_non_local': f"Foráneo (no-{config['local_region']})",
        'international': 'International',
        'unknown': 'Unknown',
        'segment_2A': f"2A: {config['home_country']} (non-{config['local_region']}), High Engagement",
        'segment_2B': f"2B: {config['home_country']} (non-{config['local_region']}), Low Engagement",
        'segment_2C': "2C: International, High Engagement",
        'segment_2D': "2D: International, Low Engagement",
        'segment_2E': f"2E: Local ({config['local_region']}), High Engagement",
        'segment_2F': f"2F: Local ({config['local_region']}), Low Engagement",
    }

# Examples for different organizations
EXAMPLE_CONFIGS = {
    'Mexico (Querétaro)': {
        'home_country': 'Mexico',
        'home_aliases': 'mexico, mx, mex',
        'local_region': 'Querétaro',
        'local_aliases': 'queretaro, qro, queretaro de arteaga',
    },
    'USA (California)': {
        'home_country': 'United States',
        'home_aliases': 'usa, us, united states, america',
        'local_region': 'California',
        'local_aliases': 'california, ca, san francisco, sf, los angeles, la',
    },
    'Brazil (São Paulo)': {
        'home_country': 'Brazil',
        'home_aliases': 'brazil, brasil, br',
        'local_region': 'São Paulo',
        'local_aliases': 'sao paulo, são paulo, sp, sampa',
    },
    'Spain (Madrid)': {
        'home_country': 'Spain',
        'home_aliases': 'spain, españa, es',
        'local_region': 'Madrid',
        'local_aliases': 'madrid, comunidad de madrid',
    },
}

def show_example_configs():
    """Show example configurations for different regions"""
    st.markdown("#### 📝 Configuraciones de Ejemplo")
    
    for region_name, config in EXAMPLE_CONFIGS.items():
        with st.expander(f"Ejemplo: {region_name}"):
            st.code(f"""
Home Country: {config['home_country']}
Country Aliases: {config['home_aliases']}
Local Region: {config['local_region']}
Local Aliases: {config['local_aliases']}
            """)

