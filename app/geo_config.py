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
    
    st.markdown("### 🌎 Geographic Settings")
    
    with st.expander("⚙️ Configure Your Geography", expanded=False):
        st.markdown("""
        **Customize geographic analysis for your region:**
        
        Define what "domestic" and "local" mean for your organization.
        """)
        
        # Home Country Configuration
        st.markdown("#### 🏠 Home Country (Domestic)")
        home_country = st.text_input(
            "Your home country:",
            value=st.session_state.get('geo_home_country', 'Mexico'),
            help="Contacts from this country will be classified as 'domestic'"
        )
        
        home_aliases = st.text_input(
            "Country aliases (comma-separated):",
            value=st.session_state.get('geo_home_aliases', 'mexico, mx, mex'),
            help="Alternative names/codes for your country (e.g., USA, US, United States)"
        )
        
        st.markdown("---")
        
        # Local Region Configuration
        st.markdown("#### 📍 Local Region (Your City/State)")
        local_region = st.text_input(
            "Your local region name:",
            value=st.session_state.get('geo_local_region', 'Querétaro'),
            help="Your specific city or state (e.g., California, São Paulo, Querétaro)"
        )
        
        local_aliases = st.text_input(
            "Local region aliases (comma-separated):",
            value=st.session_state.get('geo_local_aliases', 'queretaro, qro, queretaro de arteaga'),
            help="Alternative names for your region (e.g., SF, San Francisco, San Fran)"
        )
        
        st.markdown("---")
        
        # Geographic Tier Definitions
        st.markdown("#### 📊 Classification Logic")
        st.info("""
        **Contacts will be classified as:**
        - 🏠 **Local**: From your specified city/region
        - 🇲🇽 **Domestic (non-local)**: From your country, but not local region
        - 🌍 **International**: From outside your country
        """)
        
        # Apply button
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("✅ Apply Settings", use_container_width=True):
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
                
                st.success(f"✅ Settings applied! Home: {home_country}, Local: {local_region}")
                st.rerun()
        
        with col2:
            if st.button("🔄 Reset to Default", use_container_width=True):
                # Reset to Mexico/Querétaro defaults
                st.session_state['geo_home_country'] = 'Mexico'
                st.session_state['geo_home_aliases'] = 'mexico, mx, mex'
                st.session_state['geo_local_region'] = 'Querétaro'
                st.session_state['geo_local_aliases'] = 'queretaro, qro, queretaro de arteaga'
                st.session_state['geo_config_applied'] = True
                st.cache_data.clear()
                st.success("✅ Reset to Mexico/Querétaro defaults")
                st.rerun()
        
        # Show current configuration
        if st.session_state.get('geo_config_applied', False):
            st.markdown("---")
            st.markdown("**Current Configuration:**")
            st.write(f"🏠 **Home Country:** {st.session_state.get('geo_home_country', 'Mexico')}")
            st.write(f"📍 **Local Region:** {st.session_state.get('geo_local_region', 'Querétaro')}")

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
        'domestic_non_local': f"Domestic (non-{config['local_region']})",
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
    st.markdown("#### 📝 Example Configurations")
    
    for region_name, config in EXAMPLE_CONFIGS.items():
        with st.expander(f"Example: {region_name}"):
            st.code(f"""
Home Country: {config['home_country']}
Country Aliases: {config['home_aliases']}
Local Region: {config['local_region']}
Local Aliases: {config['local_aliases']}
            """)

