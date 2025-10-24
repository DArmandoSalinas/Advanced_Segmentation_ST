# 🗺️ Activity Journey Visualizations

## Overview

The Contact Lookup feature now includes **visual journey timelines** that show the progression of a contact's interactions over time!

---

## ✨ What Was Added

### **Cluster 1: Source Journey Visualization**

**Purpose:** Track how contacts arrived through different traffic sources over time

**What it shows:**
- 📍 **Original Source**: First touchpoint (green)
- 🔄 **Historical Sources**: All subsequent traffic sources (blue)
- ➡️ **Flow**: Visual arrows connecting each touchpoint

**Example Journey:**
```
[Original Source] → [Touch 1] → [Touch 2] → [Touch 3]
  Instagram      →   Facebook →  Google   →   Direct
```

**Use Cases:**
- Understand multi-touch attribution
- See social media influence on leads
- Track source changes over time
- Identify most effective source sequences

---

### **Cluster 3: APREU Journey Visualization**

**Purpose:** Visualize promotional activities and conversion events in a two-row timeline

**What it shows:**

**Top Row - APREU Activities (Blue):**
- All promotional events attended
- In chronological order
- Each activity as a separate box

**Bottom Row - Conversions (Green/Orange):**
- 🟢 First Conversion (green)
- 🟠 Recent Conversion (orange)
- Shows conversion progression

**Example Journey:**
```
APREU Activities:
[Activity 1] → [Activity 2] → [Activity 3]
Open Day      Fogatada       TDLA

Conversions:
[First Conversion] → [Recent Conversion]
 Formulario RUA      Follow-up Email
```

**Use Cases:**
- Track event participation sequence
- See which activities led to conversions
- Understand conversion journey duration
- Identify most effective activity patterns

---

## 🎨 Visual Design

### **Design Features:**

**Color Coding:**
- 🟢 **Green**: Original source / First conversion (starting points)
- 🔵 **Blue**: Historical sources / APREU activities (journey steps)
- 🟠 **Orange**: Recent conversion (current state)
- ⬜ **Gray**: Arrows connecting steps

**Layout:**
- **Cluster 1**: Single horizontal row (left to right flow)
- **Cluster 3**: Two horizontal rows (activities + conversions)
- **Boxes**: Rounded corners, semi-transparent backgrounds
- **Text**: Auto-wrapped for long values
- **Arrows**: Connect sequential steps

**Interactive Elements:**
- Automatic sizing based on journey length
- Summary statistics at bottom
- Clear labels for each step

---

## 📍 Where to Find

### **Cluster 1:**
1. Navigate to "📱 Cluster 1: Social Engagement"
2. Click "🔍 Contact Lookup" tab
3. Enter a Contact ID
4. Scroll to "🗺️ Source Journey Visualization"

### **Cluster 3:**
1. Navigate to "🎪 Cluster 3: APREU Activities"
2. Click "🔍 Contact Lookup" tab
3. Enter a Contact ID
4. Scroll to "🗺️ APREU Journey Visualization"

---

## 🔧 Technical Details

### **Implementation:**

**Technology Stack:**
- **Matplotlib**: For creating journey visualizations
- **FancyBboxPatch**: Rounded boxes for steps
- **FancyArrowPatch**: Arrows connecting steps
- **Streamlit**: `st.pyplot()` for display

**Functions Added:**

**Cluster 1:**
```python
visualize_source_journey(contact_id, cohort, raw_data=None)
# Returns matplotlib figure or None if no data
```

**Cluster 3:**
```python
visualize_apreu_journey(contact_id, cohort)
# Returns matplotlib figure or None if no data
```

**Integration:**
- Both functions called within contact lookup tabs
- Figures displayed with `st.pyplot(fig)`
- Properly closed with `plt.close(fig)` to prevent memory leaks

---

## 📊 Example Use Cases

### **Scenario 1: Multi-touch Attribution (Cluster 1)**

**User Action:**
1. Sales team wants to understand how a high-value lead found them
2. Looks up lead ID in Cluster 1
3. Sees journey: LinkedIn → Instagram → Facebook → Direct

**Insight:**
- LinkedIn was the original touchpoint
- Social media kept them engaged
- Eventually converted via direct traffic
- **Strategy**: Invest more in LinkedIn for similar profiles

---

### **Scenario 2: Event Effectiveness (Cluster 3)**

**User Action:**
1. Marketing wants to know which events drive conversions
2. Looks up converted lead in Cluster 3
3. Sees journey:
   - Activities: Open Day → Fogatada → TDLA
   - Conversions: Formulario RUA (first) → Email Follow-up (recent)

**Insight:**
- Lead attended 3 events before converting
- First conversion was after Fogatada
- Recent conversion shows continued engagement
- **Strategy**: Fogatada appears to be a key conversion driver

---

### **Scenario 3: Journey Duration Analysis (Cluster 3)**

**User Action:**
1. Look up multiple contacts
2. Compare journey visualizations
3. Notice patterns:
   - Quick converters: 1-2 activities
   - Slow converters: 4-5+ activities

**Insight:**
- Some segments convert faster than others
- Can optimize follow-up cadence
- **Strategy**: Tailor nurture sequences by activity count

---

## 💡 Benefits

### **For Users:**
✅ **Visual Understanding** - See the full journey at a glance  
✅ **Pattern Recognition** - Identify common conversion paths  
✅ **Decision Support** - Data-driven marketing strategy  
✅ **Communication** - Easy to share and explain  

### **For Analysis:**
✅ **Multi-touch Attribution** - Understand all touchpoints  
✅ **Event ROI** - Which activities drive results  
✅ **Source Effectiveness** - Best traffic sources  
✅ **Journey Optimization** - Improve conversion paths  

### **For Strategy:**
✅ **Resource Allocation** - Invest in what works  
✅ **Content Planning** - Create targeted campaigns  
✅ **Segmentation** - Group by journey patterns  
✅ **Personalization** - Tailor outreach by journey stage  

---

## 🚀 Advanced Features

### **Smart Handling:**

**Empty Journeys:**
- Shows: "📊 No journey data available for visualization"
- Graceful fallback, no errors

**Long Text Wrapping:**
- Automatically wraps long activity names
- Keeps visualization readable

**Dynamic Sizing:**
- Figure width adjusts to journey length
- Minimum width ensures readability

**Data Cleaning:**
- Filters out "Unknown", "nan", empty values
- Only shows meaningful steps

---

## 📝 Data Requirements

### **Cluster 1 (Source Journey):**

**Required Fields:**
- `contact_id`: To look up the contact
- `original_source`: First traffic source
- `latest_source`: Most recent source

**Optional Fields:**
- Raw historical data with delimited sources (`//` separated)

**Data Quality:**
- Works with partial data (will show what's available)
- Better with complete historical data

---

### **Cluster 3 (APREU Journey):**

**Required Fields:**
- `contact_id`: To look up the contact
- `apreu_activities_list`: List of activities attended

**Optional Fields:**
- `first_conversion`: First conversion event
- `recent_conversion`: Most recent conversion event
- `segment_c3`: Entry channel segment

**Data Quality:**
- Works even with only activities or only conversions
- Best with both activities and conversion data

---

## 🎯 Future Enhancements (Ideas)

Potential improvements:

- [ ] **Date Labels** - Show dates for each touchpoint
- [ ] **Time Duration** - Display time between steps
- [ ] **Clickable Steps** - Drill down into step details
- [ ] **Export Journey** - Download as PNG/PDF
- [ ] **Comparison View** - Compare multiple journeys
- [ ] **Journey Clustering** - Group similar paths
- [ ] **Animated Playback** - Animate the journey over time
- [ ] **Heatmaps** - Show popular journey combinations

---

## 🐛 Troubleshooting

### **"No journey data available"**

**Possible reasons:**
1. Contact has no source history
2. Contact has no APREU activities
3. All data fields are empty/unknown

**Solution:**
- Check if contact has historical data
- Verify data quality in CSV
- Try a different contact ID

### **Visualization looks cramped**

**Cause:** Very long journey (10+ steps)

**Solution:**
- Function automatically adjusts width
- May need to zoom in browser
- Consider splitting long journeys

### **Import errors**

**Error:** `ModuleNotFoundError: No module named 'matplotlib'`

**Solution:**
```bash
pip install matplotlib>=3.7.0
# or
pip install -r requirements_streamlit.txt
```

---

## 📚 Related Documentation

- **`README_STREAMLIT_APP.md`** - Main app documentation
- **`FILE_UPLOAD_GUIDE.md`** - CSV upload instructions
- **`Cluster1.ipynb`** - Original notebook with journey logic
- **`Cluster3.ipynb`** - Original notebook with APREU journey

---

## ✅ Testing Checklist

**To verify the feature works:**

- [ ] Run the Streamlit app
- [ ] Navigate to Cluster 1 → Contact Lookup
- [ ] Enter a valid Contact ID (e.g., from your data)
- [ ] Verify Source Journey visualization appears
- [ ] Navigate to Cluster 3 → Contact Lookup
- [ ] Enter a valid Contact ID
- [ ] Verify APREU Journey visualization appears
- [ ] Test with different contact IDs
- [ ] Verify graceful handling of missing data
- [ ] Check that visualizations are clear and readable

---

## 🎉 Summary

**What You Get:**

✅ **Visual journey timelines** for Cluster 1 and Cluster 3  
✅ **Professional matplotlib visualizations**  
✅ **Automatic text wrapping and sizing**  
✅ **Graceful error handling**  
✅ **Easy to use** - just enter a contact ID  
✅ **Insightful** - understand the full contact journey  

**From static data to visual stories - see every contact's path!** 🗺️✨

---

## 📞 Support

If you encounter issues:
1. Check data requirements above
2. Verify matplotlib is installed
3. Try a different contact ID
4. Review the troubleshooting section

**The journey visualization feature is ready to use!** 🚀

---

**Updated:** October 20, 2025  
**Version:** 1.0  
**Dependencies:** matplotlib>=3.7.0

