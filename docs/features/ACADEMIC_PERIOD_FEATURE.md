# Academic Period Analysis Feature

## 📅 Overview

The Academic Period analysis provides seasonal and enrollment cycle insights across Cluster 1 (Social Media) and Cluster 3 (APREU Activities). This feature helps understand how admission periods affect engagement, activity, and conversion patterns.

## 🎯 Added To

- **Cluster 1** (Social Media): New tab "📅 Academic Period"
- **Cluster 3** (APREU Activities): New tab "📅 Academic Period"

*(Cluster 2 doesn't include this analysis as it focuses on geographic segmentation without time-based enrollment cycles)*

## 🔧 Technical Implementation

### Period Conversion
- **Input Format**: YYYYMM (e.g., 202408 for August 2024)
- **Output Format**: "YYYY Semester" (e.g., "2024 Fall")

### Semester Classification
- **Spring**: January - May (months 1-5)
- **Summer**: June - July (months 6-7)
- **Fall**: August - December (months 8-12)

### Data Fields
The analysis looks for these field names:
- `periodo_de_ingreso`
- `Periodo de ingreso`
- `periodo_ingreso`
- `Periodo de ingreso a licenciatura (MQL)`
- `PERIODO DE INGRESO`

## 📊 Analysis Components

### 1. Contact Volume by Period
- **Visualization**: Bar chart showing contacts per admission period
- **Metrics**: Top 5 periods with counts and percentages
- **Color**: Blues (Cluster 1), Purples (Cluster 3)

### 2. Engagement/Activity Metrics by Period

**Cluster 1** (Social Engagement):
- Average engagement score
- Sessions, pageviews, forms submitted
- Social clicks
- **Trend Line**: Engagement score over time

**Cluster 3** (APREU Activities):
- Average number of APREU activities
- Unique activity types
- Promocion and Evento counts
- **Trend Line**: Activities per contact over time

### 3. Segment Distribution by Period
- **Cross-tabulation**: Period vs Segment (normalized)
- **Visualization**: Stacked bar chart showing segment proportions
- **Insight**: How segment mix changes across periods

### 4. Platform/Channel Distribution by Period

**Cluster 1**: Top platforms (Facebook, Instagram, etc.) by period

**Cluster 3**: Top entry channels by period

### 5. Performance Metrics by Period
- Total contacts
- Closed won count
- Close rate percentage
- Average engagement (C1) or activities (C3)
- **Trend Line**: Close rate across periods

### 6. Lifecycle Stage Distribution by Period
- Top 6 lifecycle stages
- Cross-tabulation by period
- Shows how contacts progress differently across enrollment cycles

## 💡 Key Insights Section

Automatically generates insights including:

1. **Most Popular Period**: Highest volume admission period
2. **Best Close Rate**: Period with highest conversion rate
3. **Most Active Period** (C3 only): Period with most APREU activities
4. **Volume Trend**: Whether recent periods are increasing/decreasing vs older periods

## 🎨 UI Features

### Visual Design
- **Cluster 1**: Blue color scheme (matching social media branding)
- **Cluster 3**: Purple color scheme (matching APREU activities branding)

### User Experience
- Graceful handling of missing data
- Clear informational messages when period data unavailable
- Success banner showing number of contacts analyzed
- All charts interactive (Plotly)
- Responsive layout with metrics cards

## 📈 Business Use Cases

### For Marketing Teams
- **Seasonal Planning**: Identify peak enrollment periods
- **Resource Allocation**: Staff up during high-volume periods
- **Campaign Timing**: Launch campaigns before strong-performing periods

### For Social Media (Cluster 1)
- **Platform Strategy**: Which platforms work best in which semester?
- **Content Planning**: Adjust content for seasonal trends
- **Budget Optimization**: Allocate budget based on period performance

### For Events (Cluster 3)
- **Event Calendar**: Schedule APREU activities in optimal periods
- **Activity Mix**: Adjust activity types based on seasonal effectiveness
- **ROI Analysis**: Compare event effectiveness across enrollment cycles

## 🔍 Example Insights

```
📊 Most Popular Period: 2024 Fall (2,345 contacts)
🏆 Best Close Rate: 2024 Spring (15.3%)
🎪 Most Active Period: 2023 Fall (3.45 avg activities)
📈 Trend: Volume is increasing in recent periods
```

## 🚀 How to Use

1. **Select Cluster 1 or 3** from the sidebar
2. **Navigate to "📅 Academic Period"** tab
3. **View comprehensive seasonal analysis** automatically calculated
4. **Use insights** for planning upcoming enrollment cycles

## 📝 Data Requirements

**Required**:
- Academic period field (one of the supported names)
- Valid YYYYMM format codes

**Optional** (enhances analysis):
- Close dates (for performance metrics)
- Engagement scores (Cluster 1)
- Activity counts (Cluster 3)
- Lifecycle stages
- Platform tags / Entry channels

## ⚙️ Configuration

No configuration needed! The analysis:
- ✅ Auto-detects period field name
- ✅ Filters out invalid/unknown periods
- ✅ Adapts to available metrics
- ✅ Handles missing data gracefully

## 🎓 Technical Notes

### Performance
- Uses pandas groupby for efficient aggregation
- Caches converted period strings
- Limits to top 10 periods for performance tables

### Data Quality
- Handles non-numeric period codes
- Filters out "Unknown" periods
- Validates 6-digit YYYYMM format
- Converts all period codes to standardized format

### Error Handling
- Graceful fallback if period data missing
- Try-except blocks for conversion errors
- Clear user messages for data issues
- Informative help text when data unavailable

## 📦 Files Modified

1. **cluster1_analysis.py**
   - Added `render_academic_period_tab(cohort)` function
   - Updated tab structure (6 → 7 tabs)
   - ~260 lines of new code

2. **cluster3_analysis.py**
   - Added `render_academic_period_tab_c3(cohort)` function
   - Updated tab structure (7 → 8 tabs)
   - ~260 lines of new code

## 🎉 Impact

- **More Complete**: Adds time-series dimension to analysis
- **More Actionable**: Identifies seasonal patterns for planning
- **More Professional**: Matches notebook's comprehensive approach
- **More Insights**: 6 new analysis sections per cluster

---

**Total Addition**: ~520 lines of analysis code, 2 new interactive tabs

