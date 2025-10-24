# Cluster 2: Geography & Engagement Segmentation

## Overview

The `Cluster2.ipynb` notebook implements a sophisticated geographic and engagement-based segmentation system designed to categorize prospects into 6 actionable subclusters. This segmentation combines geographical location data with engagement metrics to create targeted marketing strategies that account for both where prospects are located and how they interact with APREU's digital presence.

## Purpose

This segmentation addresses the critical need to understand **geographic distribution patterns** and **engagement behaviors** within the APREU prospect database. By combining location data with engagement metrics, the system enables geographically-aware marketing campaigns that can be tailored to specific regions while optimizing for engagement levels.

## Key Features

### 🌍 **Advanced Geographic Classification**
- **Multi-Level Geography**: Analyzes country, state, and city-level data for comprehensive location understanding
- **Mexican State Recognition**: Recognizes all 32 Mexican states with their variants and abbreviations
- **International Detection**: Identifies international prospects with enhanced detection capabilities
- **Local Market Focus**: Specialized handling for Querétaro (QRO) local market identification
- **Text Normalization**: Handles accents, special characters, and various naming conventions

### 📊 **Comprehensive Engagement Analysis**
- **Multi-Metric Scoring**: Combines sessions, pageviews, and form submissions into engagement scores
- **Quantile-Based Thresholds**: Uses statistical analysis to define high/low engagement per geography
- **Relative Performance**: Compares engagement levels within geographic segments
- **Behavioral Patterns**: Identifies engagement patterns specific to geographic regions

### 🎯 **Six-Tier Segmentation Matrix**
The system creates 6 distinct segments based on geography × engagement:

| Segment | Geography | Engagement | Target Profile |
|---------|-----------|------------|----------------|
| **2A** | Domestic (non-QRO) | High | High-engagement prospects from other Mexican states |
| **2B** | Domestic (non-QRO) | Low | Low-engagement prospects from other Mexican states |
| **2C** | International | High | High-engagement international applicants |
| **2D** | International | Low | Low-engagement international applicants |
| **2E** | Local (QRO) | High | High-engagement local Querétaro prospects |
| **2F** | Local (QRO) | Low | Low-engagement local Querétaro prospects |

## Workflow

### 1. **Data Loading & Column Resolution**
```python
# Load contact data from HubSpot extraction
df_contacts = pd.read_csv('contacts_campus_Qro_.csv')

# Resolve column aliases for geography and engagement fields
# Handle multiple naming conventions across different data exports
```

### 2. **Geographic Data Processing**
The notebook processes multiple geographic data sources:

**Primary Geography Fields:**
- `IP Country`, `IP State/Region` - IP-based location data
- `Ciudad preparatoria BPM` - High school city
- `Preparatoria BPM` - High school name
- `Estado de preparatoria BPM` - High school state
- `Estado de procedencia` - State of origin
- `País preparatoria BPM` - High school country

**Geographic Classification Logic:**
```python
def classify_geography(row):
    # Check for Querétaro (local)
    if is_queretaro(row):
        return 'local'
    # Check for other Mexican states
    elif is_mexican_state(row):
        return 'domestic_non_local'
    # Check for international
    elif is_international(row):
        return 'international'
    else:
        return 'unknown'
```

### 3. **Enhanced Geographic Detection**
**Mexican State Recognition:**
- Recognizes all 32 Mexican states with their full names
- Handles common abbreviations and variants
- Special handling for CDMX (Ciudad de México, DF, etc.)
- Consolidates state name variations to canonical names

**International Detection:**
- Identifies international indicators ("Soy Extranjero", etc.)
- Country-level classification
- Handles various international naming conventions

**Local Market Focus:**
- Specialized Querétaro detection
- Handles various QRO naming conventions
- Identifies local market opportunities

### 4. **Engagement Scoring System**
```python
# Calculate comprehensive engagement score
def calculate_engagement_score(row):
    sessions = row['Number of Sessions'] or 0
    pageviews = row['Number of Pageviews'] or 0
    forms = row['Forms Submitted'] or 0
    
    # Weighted engagement score
    engagement_score = (sessions * 1.0) + (pageviews * 0.5) + (forms * 2.0)
    return engagement_score
```

**Engagement Classification:**
- **High Engagement**: Top quantile within each geographic segment
- **Low Engagement**: Below high engagement threshold
- **Relative Thresholds**: Different thresholds for different geographic segments

### 5. **Segment Assignment & Profiling**
```python
# Assign segment labels based on geography × engagement
def assign_segment(geography, is_high_engager):
    if geography == 'domestic_non_local':
        return '2A' if is_high_engager else '2B'
    elif geography == 'international':
        return '2C' if is_high_engager else '2D'
    elif geography == 'local':
        return '2E' if is_high_engager else '2F'
    else:
        return 'unknown'
```

### 6. **Comprehensive Analysis Pipeline**
- **Segment Performance**: Metrics and KPIs for each of the 6 segments
- **Geographic Distribution**: Country, state, and city-level analysis
- **Engagement Patterns**: Behavior analysis by geography
- **Conversion Analysis**: Time-to-close and conversion rates by segment
- **Traffic Source Analysis**: Attribution patterns by geography and engagement

## Technical Architecture

### **Data Sources**
- **Geography Fields**: Multiple location data sources for comprehensive coverage
- **Engagement Metrics**: `Number of Sessions`, `Number of Pageviews`, `Forms Submitted`
- **Business Metrics**: `Likelihood to close`, `Create Date`, `Close Date`, `Lifecycle Stage`
- **Attribution Data**: `Original Source`, `Latest Traffic Source`, `Last Referring Site`

### **Geographic Processing Engine**
- **Text Normalization**: Handles accents, special characters, and case variations
- **State Recognition**: Comprehensive Mexican state identification system
- **International Detection**: Multi-language international prospect identification
- **Local Market Logic**: Specialized Querétaro market identification

### **Engagement Analysis System**
- **Multi-Metric Scoring**: Combines multiple engagement indicators
- **Quantile Analysis**: Statistical thresholds for engagement classification
- **Relative Performance**: Compares engagement within geographic segments
- **Behavioral Profiling**: Identifies engagement patterns by geography

## Methodology Rationale

### **Why Geography + Engagement Segmentation?**
1. **Market Understanding**: Geographic data reveals market penetration and opportunities
2. **Cultural Relevance**: Different regions may respond to different marketing approaches
3. **Resource Allocation**: Enables targeted marketing spend by geography and engagement
4. **Conversion Optimization**: Geography often correlates with conversion patterns

### **Why Six-Tier Segmentation?**
1. **Actionable Granularity**: Provides enough detail for targeted campaigns without over-segmentation
2. **Geographic Coverage**: Covers all major geographic categories (local, domestic, international)
3. **Engagement Differentiation**: Separates high and low engagement within each geography
4. **Marketing Efficiency**: Enables focused marketing strategies for each segment

### **Why Quantile-Based Engagement Thresholds?**
1. **Relative Performance**: Engagement levels vary by geography, so relative thresholds are more meaningful
2. **Statistical Robustness**: Quantile-based thresholds are less sensitive to outliers
3. **Adaptive Classification**: Automatically adjusts to different engagement patterns by geography
4. **Fair Comparison**: Enables fair comparison across different geographic segments

## Output and Deliverables

### **Excel Workbook Structure**
The notebook generates a comprehensive multi-sheet Excel workbook:

**Executive Summary (Sheet 1):**
- High-level KPIs and overview metrics
- Segment distribution and performance summary
- Key insights and recommendations

**Segment Performance (Sheets 2-5):**
- Detailed metrics for each of the 6 segments
- Engagement scores and conversion rates
- Geographic distribution within segments

**Geography Analysis (Sheets 6-9):**
- Country-level analysis and trends
- State-level performance metrics
- City-level insights and opportunities

**Lifecycle & Attribution (Sheets 10-12):**
- Funnel stage distribution by segment
- Traffic source analysis by geography
- Attribution patterns and trends

**Business Outcomes (Sheets 13-17):**
- Conversion rates by segment and geography
- Time-to-close analysis
- Revenue and pipeline metrics

**Time-to-Close Analysis (Sheets 18-24):**
- Pipeline velocity by segment
- Conversion timeline analysis
- Forecasting and prediction models

**Engagement & Metadata (Sheets 25-27):**
- Detailed engagement distributions
- Data quality and completeness metrics
- Methodology documentation

### **Helper Functions**
- **`show_contact_by_id('contact_id')`**: Individual contact analysis and profiling
- **`show_state('state_name')`**: State-level metrics and insights
- **Geographic Analysis Tools**: Functions for deep-dive geographic analysis

## Usage Instructions

### **Prerequisites**
1. **Historical Data**: Output from `sacar_historicos PLANTILLA.ipynb`
2. **Python Environment**: Required packages (pandas, numpy, matplotlib, seaborn)
3. **Geographic Data**: Complete location data in contact records

### **Configuration Steps**
1. **Data Path**: Update path to historical contact data CSV
2. **Geographic Fields**: Verify column names for geography data
3. **Engagement Metrics**: Confirm engagement metric column names
4. **Threshold Tuning**: Adjust engagement thresholds if needed

### **Execution Process**
1. **Run Data Loading**: Execute data preparation and cleaning steps
2. **Process Geography**: Run geographic classification and analysis
3. **Calculate Engagement**: Compute engagement scores and classifications
4. **Assign Segments**: Apply segment labels and generate analysis
5. **Export Results**: Create Excel workbook and CSV exports

## Integration with Other Notebooks

This notebook works in conjunction with:
- **sacar_historicos PLANTILLA.ipynb**: Provides the historical data foundation
- **Cluster1.ipynb**: Social engagement segmentation for cross-analysis
- **Cluster3.ipynb**: Promotion-driven segmentation for comprehensive profiling

## Data Quality Considerations

### **Common Challenges**
- **Incomplete Geographic Data**: Some contacts may have missing or incomplete location information
- **Geographic Data Inconsistency**: Different data sources may use different naming conventions
- **Engagement Metric Variations**: Engagement metrics may have different scales or definitions

### **Quality Assurance**
- **Data Validation**: Built-in checks for geographic data completeness
- **Geographic Verification**: Cross-validation of geographic classifications
- **Engagement Validation**: Analysis of engagement score distributions
- **Segment Validation**: Verification of segment assignments and characteristics

## Future Enhancements

- **Advanced Geographic Analysis**: Integration with mapping and GIS tools
- **Cultural Segmentation**: Deeper analysis of cultural factors by geography
- **Market Penetration Analysis**: Analysis of market penetration by geography
- **Predictive Geographic Modeling**: Machine learning models for geographic behavior prediction

---

*This segmentation system provides a comprehensive foundation for understanding geographic distribution and engagement patterns, enabling geographically-aware marketing strategies and optimized campaign performance across different regions.*

