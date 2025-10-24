# HubSpot Historical Data Extraction Template

## Overview

The `sacar_historicos PLANTILLA.ipynb` notebook is a comprehensive data extraction and processing pipeline designed to retrieve historical contact and deal data from HubSpot's API. This template serves as the foundation for extracting complete historical information from HubSpot properties, which is then used by the subsequent clustering notebooks for advanced segmentation analysis.

## Purpose

This notebook addresses a critical limitation in standard HubSpot data exports: **the lack of historical property values**. While HubSpot stores complete change history for all contact and deal properties, standard exports only provide the most recent values. This template extracts the full historical timeline of property changes, enabling sophisticated analysis of prospect behavior patterns over time.

## Key Features

### 🔄 **Comprehensive Historical Data Extraction**
- **Full Property History**: Extracts ALL historical values for each HubSpot property, not just the latest value
- **Chronological Ordering**: Maintains proper timestamp-based ordering of historical changes
- **Delimiter Format**: Uses `//` delimiter to separate historical values for easy parsing in downstream analysis
- **API Rate Limiting**: Implements intelligent pagination and rate limiting to handle large datasets

### 📊 **Multi-Entity Support**
- **Contact Extraction**: Retrieves historical data for all contact properties
- **Deal Extraction**: Extracts historical deal information with associated contacts
- **Flexible Property Mapping**: Supports custom property selection via CSV configuration files

### 🛡️ **Robust Error Handling**
- **API Error Management**: Handles HubSpot API rate limits and errors gracefully
- **Progress Tracking**: Real-time progress monitoring with call counters
- **Data Integrity**: Validates data completeness and handles missing values appropriately
- **Resume Capability**: Designed to handle interruptions and large dataset processing

## Workflow

### 1. **Configuration Setup**
```python
# Load property mapping from CSV
df_merged = pd.read_csv("propiedades_contactos_negocios.csv")

# Configure API access
API_KEY = "your-hubspot-api-key"
```

### 2. **Property Mapping**
The notebook uses a CSV configuration file (`propiedades_contactos_negocios.csv`) that maps:
- **Display Names**: Human-readable property names
- **Internal Names**: HubSpot's internal property identifiers
- **Entity Types**: Whether properties belong to contacts or deals

### 3. **Historical Data Extraction Process**

#### For Contacts:
- **API Endpoint**: `https://api.hubapi.com/contacts/v1/lists/all/contacts/all`
- **Property Mode**: `value_and_history` to retrieve complete change history
- **Pagination**: Handles large contact datasets with `vidOffset` pagination
- **Rate Limiting**: Implements 100-call commit cycles for data persistence

#### For Deals (Commented Out):
- **API Endpoint**: `https://api.hubapi.com/deals/v1/deal/paged`
- **Association Tracking**: Captures contact-deal relationships
- **Historical Processing**: Same historical value extraction methodology

### 4. **Data Processing Pipeline**

#### Historical Value Parsing:
```python
# Extract all historical versions
versions = prop_data.get("versions", [])
if versions:
    # Sort by timestamp for chronological order
    versions.sort(key=lambda v: v["timestamp"])
    
    # Concatenate all values with delimiter
    all_historical_values = " // ".join([v.get("value", "") for v in versions])
    contact_info[prop] = all_historical_values
else:
    # Use current value if no history
    contact_info[prop] = prop_data.get("value", "")
```

#### Data Validation:
- **Empty Value Handling**: Identifies and reports columns with missing data
- **Data Type Consistency**: Ensures consistent data types across historical values
- **Completeness Checks**: Validates data extraction completeness

### 5. **Output Generation**
- **CSV Export**: `contacts_campus_Qro_.csv` - Clean, processed contact data
- **Data Quality Reports**: Column completeness analysis and missing value identification
- **Helper Functions**: Utility functions for data validation and analysis

## Technical Architecture

### **API Integration**
- **Authentication**: Bearer token authentication with HubSpot API
- **Request Management**: Proper header configuration and parameter handling
- **Response Processing**: JSON parsing and error handling

### **Data Structure**
- **Primary Key**: Contact/Deal ID as unique identifier
- **Historical Format**: `"value1 // value2 // value3"` for multi-value properties
- **Metadata**: Timestamps, associations, and property metadata

### **Performance Optimization**
- **Batch Processing**: Processes data in configurable batch sizes
- **Memory Management**: Efficient data structures to handle large datasets
- **Progress Monitoring**: Real-time feedback on extraction progress

## Methodology Rationale

### **Why Historical Data Matters**
1. **Behavioral Patterns**: Historical data reveals how prospects' interests and engagement patterns evolve over time
2. **Attribution Accuracy**: Complete source tracking shows the full customer journey, not just the final touchpoint
3. **Segmentation Quality**: Advanced clustering algorithms require rich, multi-dimensional data for accurate segmentation
4. **Predictive Modeling**: Historical trends enable better prediction of future behavior

### **Why This Approach**
1. **API-First Design**: Direct API access ensures data freshness and completeness
2. **Configurable Properties**: CSV-based configuration allows easy adaptation to different analysis needs
3. **Scalable Architecture**: Designed to handle datasets of varying sizes
4. **Error Resilience**: Robust error handling ensures data integrity even with API limitations

## Usage Instructions

### **Prerequisites**
1. **HubSpot API Access**: Valid API key with appropriate permissions
2. **Property Configuration**: CSV file mapping desired properties
3. **Python Environment**: Required packages (pandas, requests, sqlite3)

### **Configuration Steps**
1. **Update API Key**: Replace placeholder with your HubSpot API key
2. **Configure Properties**: Modify `propiedades_contactos_negocios.csv` with desired properties
3. **Set Filters**: Adjust contact/deal filtering criteria as needed
4. **Run Extraction**: Execute notebook cells in sequence

### **Output Files**
- `contacts_campus_Qro_.csv`: Main output with historical contact data
- Console output: Progress tracking and data quality reports

## Integration with Clustering Notebooks

This template provides the foundational data for three specialized clustering notebooks:

1. **Cluster1.ipynb**: Uses historical social media engagement data for social platform segmentation
2. **Cluster2.ipynb**: Leverages geographical and engagement historical data for geo-based segmentation  
3. **Cluster3.ipynb**: Utilizes promotional activity historical data for conversion-focused segmentation

The historical data format (`value1 // value2 // value3`) is specifically designed to be parsed by the advanced segmentation algorithms in these downstream notebooks.

## Data Quality Considerations

### **Common Issues**
- **API Rate Limits**: HubSpot API has rate limits that may require processing delays
- **Missing Historical Data**: Some properties may not have change history
- **Data Consistency**: Property values may have different formats over time

### **Quality Assurance**
- **Validation Functions**: Built-in functions to check data completeness
- **Progress Monitoring**: Real-time feedback on extraction status
- **Error Logging**: Comprehensive error reporting for troubleshooting

## Future Enhancements

- **Automated Scheduling**: Integration with scheduling systems for regular data updates
- **Incremental Updates**: Delta processing to update only changed records
- **Data Validation**: Enhanced validation rules for data quality assurance
- **Performance Optimization**: Further optimization for very large datasets

---

*This template is designed to be robust and adaptable to various HubSpot data extraction needs while maintaining data integrity and providing comprehensive historical context for advanced analytics.*

