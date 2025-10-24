# Cluster 1: Social Engagement Segmentation

## Overview

The `Cluster1.ipynb` notebook implements an advanced segmentation system designed to identify and categorize prospects based on their social media engagement patterns. This notebook focuses on **socially engaged prospects** within the APREU (Admissions and Promotion) dataset, using sophisticated historical data analysis and multi-platform detection to create actionable marketing segments.

## Purpose

This segmentation addresses a critical marketing challenge: **identifying prospects who are actively engaged across social media platforms** and understanding their engagement patterns to optimize marketing campaigns. The analysis goes beyond simple social media presence to understand the depth and breadth of social engagement, enabling targeted marketing strategies based on actual behavior patterns.

## Key Features

### 🎯 **Advanced Social Media Detection**
- **Multi-Platform Recognition**: Identifies activity across 12+ social platforms including Instagram, TikTok, YouTube, LinkedIn, Facebook, Twitter, Google Ads, Eventbrite, WhatsApp, MAKE, and AtomChat
- **Historical Data Analysis**: Parses complete historical engagement data from HubSpot properties, not just current values
- **Smart Platform Tagging**: Uses historical data as the primary signal with click data as validation (20K+ contacts analyzed)
- **Engagement Scoring**: Combines multiple engagement metrics to create comprehensive social engagement scores

### 📊 **Comprehensive Data Integration**
- **HubSpot API Integration**: Direct integration with HubSpot's contact and engagement data
- **Historical Value Parsing**: Processes HubSpot's `//` delimited historical format for complete timeline analysis
- **Multi-Source Attribution**: Analyzes both current and historical source data for complete attribution tracking
- **Lifecycle Integration**: Tracks contacts through different funnel stages with lifecycle stage distribution

### 🔍 **Intelligent Segmentation**
- **KMeans Clustering**: Uses machine learning to identify natural groupings in social engagement patterns
- **Two-Tier Segmentation**: Creates main segments (1A/1B) with distinct engagement profiles
- **Actionable Insights**: Provides specific marketing recommendations for each segment
- **Performance Tracking**: Monitors conversion rates and engagement metrics by segment

## Workflow

### 1. **Data Loading & Preparation**
```python
# Load historical contact data from HubSpot extraction
df_contacts = pd.read_csv('contacts_campus_Qro_.csv')

# Resolve column aliases for HubSpot properties
# Map various naming conventions to canonical column names
```

### 2. **Historical Data Processing**
The notebook processes HubSpot's historical data format where multiple values are stored as:
```
"value1 // value2 // value3"
```

**Key Processing Steps:**
- **Parse Historical Strings**: Split delimited values and maintain chronological order
- **Create Historical Columns**: Generate `*_hist_all` columns with complete historical data
- **Platform Detection**: Scan 12+ text fields for social media platform keywords
- **Engagement Metrics**: Calculate comprehensive engagement scores

### 3. **Platform Signal Extraction**
```python
# Scan multiple fields for platform keywords
platforms = ['instagram', 'tiktok', 'youtube', 'linkedin', 'facebook', 'twitter', 
             'google ads', 'eventbrite', 'whatsapp', 'make', 'atomchat']

# Count platform mentions across historical and current data
for platform in platforms:
    platform_count = count_platform_mentions(platform, historical_data)
```

### 4. **Contact Filtering & Validation**
- **APREU Focus**: Filters for contacts owned by APREU team
- **Lifecycle Filtering**: Excludes "Other" and "subscriber" stages
- **Data Quality**: Validates data completeness and handles missing values
- **Timestamp Processing**: Converts HubSpot timestamps to readable datetime objects

### 5. **Social Engagement Definition**
Contacts are classified as "socially engaged" if they meet ANY of these criteria:
- **Social Clicks**: Have recorded clicks on social media content
- **Platform Mentions**: Show platform activity in historical source data
- **Social Keywords**: Contain social media references in source/referrer fields

### 6. **Feature Engineering**
```python
# Log transformations for skewed data
df['log_social_clicks_total'] = np.log1p(df['social_clicks_total'])
df['log_num_sessions'] = np.log1p(df['Number of Sessions'])

# Efficiency ratios
df['pageviews_per_session'] = df['Number of Pageviews'] / df['Number of Sessions']
df['forms_per_session'] = df['Forms Submitted'] / df['Number of Sessions']
```

### 7. **Machine Learning Segmentation**
- **KMeans Clustering**: Groups contacts into 2 main segments based on engagement patterns
- **Feature Scaling**: Normalizes features for optimal clustering performance
- **Segment Validation**: Analyzes segment characteristics and performance metrics

## Target Segments

### **Segment 1A: High Engagement + Social Activity**
**Profile**: Active social users with strong website engagement
- **Characteristics**: 
  - High social media platform diversity
  - Strong website engagement (sessions, pageviews, forms)
  - Higher conversion rates
  - Active across multiple touchpoints
- **Marketing Actions**:
  - Fast-track with immediate follow-up
  - Cross-platform retargeting campaigns
  - APREU event invitations
  - Personalized content delivery

### **Segment 1B: Low Engagement + Social Activity**
**Profile**: Social media presence but minimal website interaction
- **Characteristics**:
  - Social platform presence but limited engagement
  - Lower website interaction rates
  - Needs activation and nurturing
  - Potential for growth with proper engagement
- **Marketing Actions**:
  - Nurture campaigns to increase engagement
  - Value-driven content to encourage site exploration
  - Social proof and testimonials
  - Gradual relationship building

## Technical Architecture

### **Data Sources**
- **Engagement Metrics**: `Broadcast Clicks`, `LinkedIn Clicks`, `Twitter Clicks`, `Facebook Clicks`
- **Website Activity**: `Number of Sessions`, `Number of Pageviews`, `Forms Submitted`
- **Attribution Data**: `Original Source`, `Original Source Drill-Down 1/2`, `Canal de adquisición`
- **Historical Data**: Complete change history for all properties
- **Business Metrics**: `Likelihood to close`, `Create Date`, `Close Date`, `Lifecycle Stage`

### **Machine Learning Pipeline**
1. **Data Preprocessing**: Cleaning, normalization, and feature engineering
2. **Feature Selection**: Identifying most relevant engagement metrics
3. **Clustering**: KMeans algorithm with optimal parameter tuning
4. **Validation**: Segment analysis and performance metrics
5. **Interpretation**: Business insights and actionable recommendations

### **Performance Optimization**
- **Efficient Data Processing**: Vectorized operations for large datasets
- **Memory Management**: Optimized data structures for 20K+ contacts
- **Scalable Architecture**: Designed to handle growing datasets

## Methodology Rationale

### **Why Social Engagement Segmentation?**
1. **Behavioral Insights**: Social engagement patterns reveal prospect preferences and communication styles
2. **Channel Optimization**: Identifies which social platforms are most effective for different prospect types
3. **Resource Allocation**: Enables targeted marketing spend on high-engagement prospects
4. **Conversion Optimization**: High social engagement often correlates with higher conversion rates

### **Why Historical Data Analysis?**
1. **Complete Picture**: Historical data shows the full customer journey, not just current state
2. **Pattern Recognition**: Identifies trends and changes in engagement over time
3. **Attribution Accuracy**: Provides complete source tracking across the entire customer lifecycle
4. **Predictive Power**: Historical patterns enable better prediction of future behavior

### **Why KMeans Clustering?**
1. **Unsupervised Learning**: Discovers natural groupings without predefined categories
2. **Scalability**: Efficiently handles large datasets with multiple features
3. **Interpretability**: Results are easily understandable and actionable
4. **Flexibility**: Can be easily adapted to different engagement metrics

## Output and Deliverables

### **Data Exports**
- **CSV Files**: Segmented contact lists with engagement scores
- **Excel Workbooks**: Multi-sheet analysis with detailed metrics
- **Visualization**: Charts and graphs showing segment characteristics

### **Analysis Reports**
- **Segment Profiles**: Detailed characteristics of each segment
- **Performance Metrics**: Conversion rates, engagement scores, and ROI by segment
- **Recommendations**: Specific marketing actions for each segment
- **Trend Analysis**: Historical patterns and future predictions

### **Helper Functions**
- **Contact Lookup**: `show_contact_by_id('contact_id')` for individual analysis
- **Segment Analysis**: Functions to analyze specific segment characteristics
- **Performance Tracking**: Tools to monitor segment performance over time

## Usage Instructions

### **Prerequisites**
1. **Historical Data**: Output from `sacar_historicos PLANTILLA.ipynb`
2. **Python Environment**: Required packages (pandas, numpy, scikit-learn, matplotlib)
3. **HubSpot Integration**: Access to HubSpot contact data

### **Configuration Steps**
1. **Data Path**: Update path to historical contact data CSV
2. **Platform Keywords**: Modify platform detection keywords as needed
3. **Engagement Thresholds**: Adjust engagement criteria for segment definition
4. **Clustering Parameters**: Tune KMeans parameters for optimal segmentation

### **Execution Process**
1. **Run Data Loading**: Execute data preparation and cleaning steps
2. **Process Historical Data**: Extract and analyze historical engagement patterns
3. **Apply Segmentation**: Run clustering algorithm and assign segment labels
4. **Generate Reports**: Create analysis reports and export segmented data

## Integration with Other Notebooks

This notebook works in conjunction with:
- **sacar_historicos PLANTILLA.ipynb**: Provides the historical data foundation
- **Cluster2.ipynb**: Geography-based segmentation for cross-analysis
- **Cluster3.ipynb**: Promotion-driven segmentation for comprehensive prospect profiling

## Data Quality Considerations

### **Common Challenges**
- **Incomplete Historical Data**: Some contacts may have limited historical information
- **Platform Detection Accuracy**: Social platform detection relies on text analysis
- **Engagement Metric Consistency**: Different engagement metrics may have varying scales

### **Quality Assurance**
- **Data Validation**: Built-in checks for data completeness and consistency
- **Platform Verification**: Cross-validation of platform detection results
- **Segment Validation**: Analysis of segment characteristics and performance

## Future Enhancements

- **Advanced ML Models**: Integration of more sophisticated clustering algorithms
- **Real-time Updates**: Automated segmentation updates as new data becomes available
- **Cross-Platform Analysis**: Deeper analysis of platform-specific engagement patterns
- **Predictive Modeling**: Machine learning models to predict future engagement behavior

---

*This segmentation system provides a robust foundation for understanding and targeting socially engaged prospects, enabling data-driven marketing decisions and optimized campaign performance.*

