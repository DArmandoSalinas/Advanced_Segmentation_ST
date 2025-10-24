# 📤 File Upload Feature Guide

## Overview

The APREU Advanced Segmentation app now supports **CSV file uploads**, making it more flexible and reproducible for any user!

---

## 🎯 Key Features

### **1. Dual Data Source Options**

Choose between:
- **📂 Use Default File** - Load the pre-configured `contacts_campus_Qro_.csv`
- **⬆️ Upload CSV** - Upload your own HubSpot contact export

### **2. Data Validation**

The app automatically validates your uploaded data:
- ✅ Checks for required columns
- ⚠️ Warns about missing optional fields
- 📊 Shows which clusters will work with your data

### **3. Data Preview**

After uploading, you can:
- View the first 3 rows of data
- See total columns and rows
- Check column structure

### **4. Smart Error Handling**

- Clear error messages if file format is wrong
- Suggestions for fixing issues
- Graceful fallback to default file

---

## 📋 How to Use

### **Option A: Use Default File** (Existing Workflow)

1. Ensure `contacts_campus_Qro_.csv` is in the app directory
2. Select "📂 Use Default File" in the sidebar
3. App loads automatically ✅

### **Option B: Upload Your Own CSV**

1. **Prepare Your Data:**
   - Export contacts from HubSpot as CSV
   - Ensure it includes the required fields (see below)

2. **Upload the File:**
   - Select "⬆️ Upload CSV" in the sidebar
   - Click the upload button
   - Choose your CSV file
   
3. **Review Validation:**
   - Check the success message: "✅ Loaded X contacts"
   - Expand "📋 Data Preview" to see your data
   - Review any warnings in "⚠️ Warnings" section
   
4. **Start Analyzing:**
   - Select a cluster from Navigation
   - Explore your data!

---

## 📊 Required Data Format

### **Minimum Required Fields:**

**Essential:**
- `Record ID` - Unique contact identifier

**For Full Functionality:**
- `Number of Sessions` - Site visit count
- `Number of Pageviews` - Page view count
- `Number of Form Submissions` - Form submission count

### **Cluster-Specific Fields:**

**Cluster 1 (Social Engagement):**
- `Original Source`
- `Latest Traffic Source`
- `Broadcast Clicks`
- `LinkedIn Clicks`
- `Twitter Clicks`
- `Facebook Clicks`
- `Canal de adquisición`

**Cluster 2 (Geography & Engagement):**
- `IP Country`
- `IP State/Region`
- `País preparatoria BPM`
- `Estado de preparatoria BPM`
- `Ciudad preparatoria BPM`

**Cluster 3 (APREU Activities):**
- `Actividades de promoción APREU`
- `First Conversion`
- `Recent Conversion`
- `Preparatoria BPM`

### **Optional but Recommended:**

- `Close Date` - For conversion analysis
- `Create Date` - For time-to-close calculation
- `Likelihood to close` - For predictive scoring
- `Lifecycle Stage` - For funnel analysis
- `Propiedad del contacto` - For contact owner filtering

---

## ✅ Data Validation Details

### **What Happens During Validation:**

1. **Basic Check:**
   - Verifies `Record ID` exists
   - If missing: ❌ Error - Cannot proceed

2. **Cluster Readiness:**
   - Checks cluster-specific required fields
   - If missing: ⚠️ Warning - That cluster may not work properly

3. **Result Display:**
   - ✅ Success: All basic requirements met
   - ⚠️ Warnings: Some clusters may have limited functionality
   - ❌ Error: Missing critical fields

### **Example Validation Output:**

**Good Data:**
```
✅ Loaded 75,000 contacts

📋 Data Preview
Columns: 44
Rows: 75,000
[Shows first 3 rows]
```

**Data with Warnings:**
```
✅ Loaded 50,000 contacts

⚠️ Warnings
- Cluster 3 may not work: missing 'Actividades de promoción APREU'
```

**Invalid Data:**
```
❌ Invalid data: Missing required columns: Record ID
```

---

## 🎨 User Interface Changes

### **New Sidebar Section: "📁 Data Source"**

Located at the top of the sidebar, this section includes:

1. **Radio buttons** to choose data source
2. **File uploader** (when Upload CSV is selected)
3. **Success/Error messages**
4. **Data preview expander**
5. **Warnings expander** (if applicable)

### **New Help Section: "📥 Need Help?"**

Includes:
- Required data format guide
- Field descriptions
- "View Sample Data Structure" button

### **Disabled Navigation**

If no data is loaded:
- Navigation options are disabled
- Main content shows getting started guide
- Clear instructions for loading data

---

## 🔧 Technical Details

### **Implementation:**

**Modified Files:**
1. `utils.py` - Updated `load_data()` to accept uploaded files
2. `utils.py` - Added `validate_data()` function
3. `streamlit_app.py` - Added file uploader UI and validation logic

**Key Functions:**

```python
# Load data from uploaded file or default
load_data(uploaded_file=None)

# Validate required columns
validate_data(df) -> {
    'is_valid': bool,
    'missing_basic': list,
    'cluster1_ready': bool,
    'cluster2_ready': bool,
    'cluster3_ready': bool,
    'warnings': list
}
```

### **Caching:**

The app uses `@st.cache_data` for performance:
- First load of a file: ~30-60 seconds
- Subsequent loads: <1 second (cached)
- Cache key includes file contents (automatic re-cache on file change)

### **Supported File Types:**

- `.csv` files only
- UTF-8 encoding recommended
- Maximum file size: Streamlit default (200MB)

---

## 🚀 Benefits

### **For End Users:**

✅ **No Setup Required** - Just upload and analyze  
✅ **Flexible** - Works with any HubSpot export  
✅ **Instant Feedback** - Know immediately if data is valid  
✅ **Educational** - Learn what fields are needed  

### **For Demonstrations:**

✅ **Reproducible** - Anyone can use their own data  
✅ **No Installation** - No need to place files manually  
✅ **Professional** - Polished POC experience  
✅ **Secure** - Data stays in the session (not saved)  

### **For Development:**

✅ **Testing** - Easy to test with different datasets  
✅ **Debugging** - Clear validation messages  
✅ **Extensible** - Easy to add more validations  

---

## 💡 Usage Examples

### **Example 1: Marketing Team Demo**

```
Scenario: Marketing team wants to see their Q4 data

Steps:
1. Export Q4 contacts from HubSpot
2. Open the Streamlit app
3. Select "⬆️ Upload CSV"
4. Upload Q4_contacts.csv
5. See: "✅ Loaded 12,543 contacts"
6. Navigate to Cluster 1
7. Analyze Q4 social engagement!
```

### **Example 2: International Team Demo**

```
Scenario: International recruitment team wants to analyze their specific contacts

Steps:
1. Filter HubSpot contacts for international leads
2. Export as international_contacts.csv
3. Upload to the app
4. Navigate to Cluster 2 (Geography)
5. See international segment analysis!
```

### **Example 3: Event Team Demo**

```
Scenario: Events team wants to analyze APREU activity ROI

Steps:
1. Export contacts with APREU activities
2. Upload events_contacts.csv
3. Check validation - if missing fields, get clear warnings
4. Navigate to Cluster 3
5. Analyze event participation and ROI!
```

---

## 🆘 Troubleshooting

### **Problem: "Missing required columns" error**

**Solution:**
1. Check your HubSpot export includes `Record ID`
2. Ensure column names match HubSpot format
3. Don't rename columns before uploading

### **Problem: "Cluster X may not work" warning**

**Solution:**
- This is a warning, not an error
- The app will load, but that specific cluster may have issues
- Include the missing fields in your HubSpot export for full functionality

### **Problem: Upload button not appearing**

**Solution:**
1. Ensure you selected "⬆️ Upload CSV" radio button
2. Refresh the page if needed
3. Check browser console for errors

### **Problem: File uploads but no data shown**

**Solution:**
1. Verify the file is actually a CSV (not Excel)
2. Check file encoding (use UTF-8)
3. Ensure file is not corrupted
4. Try with a smaller sample file first

### **Problem: App is slow after uploading large file**

**Expected Behavior:**
- First load: 30-60 seconds for 50K+ rows
- Subsequent navigation: Instant (cached)
- This is normal for large datasets

---

## 📚 Best Practices

### **For Optimal Performance:**

1. **Export Wisely:**
   - Include only necessary columns
   - Filter contacts before exporting
   - Use date ranges to limit size

2. **File Size:**
   - Recommended: <100K rows
   - Maximum tested: 200K rows
   - Larger files will work but may be slower

3. **Data Quality:**
   - Clean data in HubSpot first
   - Remove test contacts
   - Ensure proper field population

### **For Demonstrations:**

1. **Prepare Sample Files:**
   - Keep a clean, small sample file (~5K rows)
   - Include all required fields
   - Test upload before demo

2. **Explain the Feature:**
   - Show validation process
   - Highlight data preview
   - Demonstrate warnings

3. **Compare Results:**
   - Upload different segments
   - Show how analysis changes
   - Highlight flexibility

---

## 🎯 Future Enhancements (Ideas)

Potential improvements for future versions:

- [ ] **Excel file support** (.xlsx)
- [ ] **Data mapping interface** - Map non-standard column names
- [ ] **Multiple file upload** - Compare different datasets
- [ ] **Data export** - Download processed/segmented data
- [ ] **Template download** - Provide sample CSV template
- [ ] **Column auto-detection** - Smart column name matching
- [ ] **Data quality report** - Comprehensive validation report
- [ ] **Save/load sessions** - Resume previous analysis

---

## 📝 Summary

The file upload feature makes the APREU Advanced Segmentation app:

✅ **More Accessible** - Anyone can use it  
✅ **More Flexible** - Works with any data  
✅ **More Professional** - Enterprise-ready POC  
✅ **More Reproducible** - True self-service analytics  

**This transforms the app from a fixed analysis tool into a flexible platform!** 🚀

---

**Ready to try it?**

```bash
streamlit run streamlit_app.py
```

Then select "⬆️ Upload CSV" and start exploring your data! 📊

