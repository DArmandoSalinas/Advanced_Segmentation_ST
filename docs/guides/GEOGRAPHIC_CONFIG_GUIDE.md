# 🌎 Dynamic Geographic Configuration Guide

## Overview

The app now features **dynamic geographic configuration**, allowing you to define what "domestic" and "local" mean for **YOUR** organization - not just for Mexico/Querétaro!

This transforms Cluster 2 from a Mexico-specific tool into a **universal geographic segmentation platform** usable by any organization worldwide.

---

## 🎯 **The Problem We Solved**

### **Before (Static):**
- ❌ Hardcoded for Mexico and Querétaro
- ❌ Only useful for Mexican organizations
- ❌ Required code changes for different regions
- ❌ Not reproducible for other countries

### **After (Dynamic):**
- ✅ Configurable for ANY country and region
- ✅ Universal - works worldwide
- ✅ Zero code changes needed
- ✅ Fully reproducible anywhere

---

## 🚀 **How to Use**

### **Step 1: Open Geographic Settings**

In the sidebar, find the new section:
```
🌎 Geographic Settings
 └─ ⚙️ Configure Your Geography (click to expand)
```

### **Step 2: Define Your Geography**

**Set Your Home Country:**
```
Your home country: [United States]
Country aliases: usa, us, united states, america
```

**Set Your Local Region:**
```
Your local region name: [California]
Local region aliases: california, ca, san francisco, sf, los angeles
```

### **Step 3: Apply Settings**

Click **"✅ Apply Settings"**
- Settings are saved to your session
- Data is automatically re-analyzed
- Cluster 2 now uses YOUR geography!

### **Step 4: Analyze Your Data**

Navigate to Cluster 2 and see:
- **Local**: Your city/region (e.g., California)
- **Domestic**: Your country, but not local (e.g., Other US states)
- **International**: Outside your country

---

## 📋 **Configuration Fields Explained**

### **Home Country**

**What it is:**
- Your organization's primary country
- Defines what "domestic" means

**Examples:**
- `Mexico`, `United States`, `Brazil`, `Spain`, `India`

**Impact:**
- Contacts from this country → "Domestic"
- Contacts from other countries → "International"

### **Country Aliases**

**What it is:**
- Alternative names or codes for your country
- Helps match variations in your data

**Examples:**
- USA: `usa, us, united states, america`
- Mexico: `mexico, mx, mex`
- Brazil: `brazil, brasil, br`

**Why needed:**
- Your data might use "USA", "US", or "United States"
- Aliases catch all variations

### **Local Region**

**What it is:**
- Your specific city, state, or region
- Defines what "local" means

**Examples:**
- `California`, `São Paulo`, `Querétaro`, `Madrid`, `Bavaria`

**Impact:**
- Contacts from this region → "Local"
- Contacts from your country but not this region → "Domestic (non-local)"

### **Local Region Aliases**

**What it is:**
- Alternative names for your region

**Examples:**
- California: `california, ca, san francisco, sf, los angeles, la`
- Querétaro: `queretaro, qro, queretaro de arteaga`

**Why needed:**
- Catches abbreviations (CA, SF, LA)
- Matches variations in data entry

---

## 🌍 **Example Configurations**

### **For a US Company (San Francisco)**

```yaml
Home Country: United States
Country Aliases: usa, us, united states, america, u.s.
Local Region: San Francisco
Local Aliases: san francisco, sf, bay area, silicon valley
```

**Result:**
- 🏠 **Local**: San Francisco Bay Area contacts
- 🇺🇸 **Domestic**: Other US states (NY, TX, etc.)
- 🌍 **International**: Canada, Mexico, Europe, etc.

### **For a Brazilian Company (São Paulo)**

```yaml
Home Country: Brazil
Country Aliases: brazil, brasil, br
Local Region: São Paulo
Local Aliases: sao paulo, são paulo, sp, sampa
```

**Result:**
- 🏠 **Local**: São Paulo contacts
- 🇧🇷 **Domestic**: Other Brazilian states (RJ, MG, etc.)
- 🌍 **International**: Argentina, USA, Portugal, etc.

### **For a Spanish Company (Madrid)**

```yaml
Home Country: Spain
Country Aliases: spain, españa, es, espana
Local Region: Madrid
Local Aliases: madrid, comunidad de madrid
```

**Result:**
- 🏠 **Local**: Madrid region contacts
- 🇪🇸 **Domestic**: Other Spanish regions (Barcelona, Valencia, etc.)
- 🌍 **International**: France, UK, Latin America, etc.

### **For an Indian Company (Bangalore)**

```yaml
Home Country: India
Country Aliases: india, in, bharat
Local Region: Karnataka
Local Aliases: karnataka, bangalore, bengaluru, blr
```

**Result:**
- 🏠 **Local**: Karnataka/Bangalore contacts
- 🇮🇳 **Domestic**: Other Indian states (Maharashtra, Delhi, etc.)
- 🌍 **International**: USA, UK, Middle East, etc.

---

## 🎨 **Impact on Cluster 2 Segments**

### **Segment Definitions (Dynamic)**

With your configuration, segments adapt:

**2A: Domestic (non-local), High Engagement**
- Before: "MX non-QRO, High Engagement"
- After: "[YOUR_COUNTRY] non-[YOUR_REGION], High Engagement"
- Example: "United States non-California, High Engagement"

**2B: Domestic (non-local), Low Engagement**
- Before: "MX non-QRO, Low Engagement"
- After: "[YOUR_COUNTRY] non-[YOUR_REGION], Low Engagement"

**2C: International, High Engagement**
- Always: "International, High Engagement"
- (This one doesn't change - it's relative to any home country)

**2D: International, Low Engagement**
- Always: "International, Low Engagement"

**2E: Local, High Engagement**
- Before: "Local QRO, High Engagement"
- After: "Local [YOUR_REGION], High Engagement"
- Example: "Local California, High Engagement"

**2F: Local, Low Engagement**
- Before: "Local QRO, Low Engagement"
- After: "Local [YOUR_REGION], Low Engagement"

### **Action Plans (Dynamic)**

Action recommendations also adapt:

**For 2A:**
- Before: "Digital engagement + virtual events (MX non-QRO)"
- After: "Digital engagement + virtual events ([YOUR_COUNTRY] non-[YOUR_REGION])"

**For 2E:**
- Before: "In-person APREU + campus tours (Local QRO)"
- After: "In-person events + local engagement (Local [YOUR_REGION])"

---

## 🔄 **How It Works Technically**

### **Configuration Storage**

Settings are stored in **Streamlit session state**:
```python
st.session_state['geo_home_country'] = 'United States'
st.session_state['geo_local_region'] = 'California'
st.session_state['geo_home_aliases_list'] = ['usa', 'us', 'united states']
st.session_state['geo_local_aliases_list'] = ['california', 'ca', 'san francisco']
```

### **Dynamic Classification**

When you upload data or change settings:

1. **Settings Retrieved:**
   ```python
   geo_config = get_geo_config()
   # Returns your current settings
   ```

2. **Data Classified:**
   ```python
   df['geo_tier'] = df.apply(
       lambda row: classify_geo_tier_dynamic(row, geo_config), 
       axis=1
   )
   # Uses YOUR settings to classify each contact
   ```

3. **Segments Assigned:**
   ```python
   # 2A-2F assigned based on YOUR geographic tiers
   ```

### **Cache Invalidation**

When you change settings:
- Old cache is cleared: `st.cache_data.clear()`
- Data is re-processed with new settings
- Fresh analysis with your new geography

---

## 💡 **Best Practices**

### **For Accurate Classification:**

1. **Include Common Aliases:**
   ```
   Good: usa, us, united states, america, u.s.
   Better: usa, us, united states, america, u.s., usa., us.
   ```

2. **Think About Data Variations:**
   - Your data might have "CA" or "California"
   - Include both full names and abbreviations

3. **Consider Sub-regions:**
   - For large cities: include neighborhoods/districts
   - California: `san francisco, sf, los angeles, la, san diego`

4. **Test Your Settings:**
   - Upload data and check classification
   - Look at the "Top States" or "Top Cities" tables
   - Adjust aliases if contacts are miscategorized

### **For Multi-Location Organizations:**

If your org has multiple "local" regions:

**Option A: Run Analysis Multiple Times**
- Set local to "California" → Analyze → Export
- Change to "Texas" → Analyze → Export
- Compare results

**Option B: Focus on Primary Location**
- Set local to your headquarters/main office
- Other locations will be "domestic"

---

## 🎯 **Use Cases**

### **Use Case 1: US University (Multiple Campuses)**

**Scenario:** University with campuses in CA, TX, NY wants to analyze recruitment.

**Configuration:**
```
Home: United States
Local: California  (for CA campus analysis)
```

**Segments:**
- 2E/2F: California prospects (can attend in-person events)
- 2A/2B: Other US states (virtual events, regional partnerships)
- 2C/2D: International students (visa support, special programs)

**Action:**
- Run once for each campus location
- Compare local engagement across campuses

### **Use Case 2: Global Company (Regional Analysis)**

**Scenario:** Company operating in LATAM wants regional insights.

**Configuration:**
```
Home: Brazil
Local: São Paulo  (headquarters)
```

**Segments:**
- 2E/2F: São Paulo contacts (local sales team)
- 2A/2B: Other Brazilian states (regional distributors)
- 2C/2D: Other LATAM countries (export opportunities)

### **Use Case 3: E-Commerce (Market Expansion)**

**Scenario:** E-commerce company expanding from Spain to LATAM.

**First Analysis:**
```
Home: Spain
Local: Madrid
```
See: Spanish market segmentation

**Second Analysis:**
```
Home: Mexico
Local: Ciudad de México
```
See: Mexican market potential

**Compare:** Understand both markets independently

---

## 🔧 **Advanced Features**

### **Reset to Default**

Click **"🔄 Reset to Default"** to return to Mexico/Querétaro configuration.

### **Example Configurations**

The sidebar includes pre-made examples for:
- Mexico (Querétaro)
- USA (California)
- Brazil (São Paulo)
- Spain (Madrid)

View these for inspiration or starting points.

### **Current Configuration Display**

At the top of Cluster 2, you'll always see:
```
Current Configuration: 🏠 United States | 📍 California
```

This reminds you what settings are active.

### **Dynamic Labels Throughout**

All UI elements update automatically:
- Chart titles
- Segment descriptions
- Action recommendations
- Table headers

---

## 📊 **What Changes vs What Doesn't**

### **Changes with Configuration:**
- ✅ Geographic tier classification
- ✅ 2A-2F segment definitions
- ✅ Action plan recommendations
- ✅ UI labels and descriptions
- ✅ Chart titles

### **Stays the Same:**
- ✅ Engagement scoring logic
- ✅ High/Low engagement thresholds
- ✅ Chart types and visualizations
- ✅ Statistical calculations
- ✅ Cluster 1 and Cluster 3 (unaffected)

---

## 🆘 **Troubleshooting**

### **Problem: Contacts misclassified**

**Solution:**
1. Check your data for country/region field values
2. Add those variations to aliases
3. Re-apply settings

**Example:**
- Data has "US" but aliases only have "USA"
- Add "US" to country aliases

### **Problem: Too many "Unknown" contacts**

**Solution:**
- Your data might have poor location data
- Check which fields are populated in your CSV
- Consider using preparatoria/school location fields

### **Problem: Settings don't seem to apply**

**Solution:**
1. Click "✅ Apply Settings" button
2. Wait for "Settings applied!" message
3. Navigate to Cluster 2 to see changes
4. Check "Current Configuration" display

### **Problem: Want to analyze multiple regions**

**Solution:**
- Run analysis once per region
- Change settings between runs
- Export or screenshot results for each
- Compare side-by-side

---

## 🎓 **Educational Value**

This feature teaches important concepts:

1. **Geographic Segmentation Basics:**
   - Local vs Regional vs National vs International
   - How location impacts marketing strategy

2. **Configuration-Driven Analysis:**
   - Same code, different results based on settings
   - Reproducible research with documented parameters

3. **Data Quality Importance:**
   - Clean location data = better classification
   - Aliases and normalization strategies

4. **Multi-Market Strategy:**
   - How to analyze different markets consistently
   - Comparative analysis across regions

---

## 🚀 **Future Enhancements (Ideas)**

Potential improvements for future versions:

- [ ] **Multiple local regions** - Support for orgs with many locations
- [ ] **Save/load configurations** - Store settings for reuse
- [ ] **Configuration templates** - Pre-made setups for different countries
- [ ] **Auto-detect settings** - Suggest config based on data
- [ ] **Region hierarchies** - Define sub-regions within local area
- [ ] **Export with config** - Include settings in exported reports

---

## 📝 **Summary**

**This feature makes your app:**

✅ **Universal** - Works for any country/region  
✅ **Flexible** - Adapt to any organizational structure  
✅ **Reproducible** - Document settings with results  
✅ **Professional** - Production-ready for global use  
✅ **Educational** - Teaches geographic segmentation  

**From Mexico-specific to globally applicable - with zero code changes for users!** 🌍

---

## 🎯 **Quick Start Checklist**

- [ ] Open app sidebar
- [ ] Find "🌎 Geographic Settings"
- [ ] Expand "⚙️ Configure Your Geography"
- [ ] Enter your home country
- [ ] Add country aliases (comma-separated)
- [ ] Enter your local region
- [ ] Add region aliases (comma-separated)
- [ ] Click "✅ Apply Settings"
- [ ] Navigate to Cluster 2
- [ ] See your custom geographic analysis!

**Ready to analyze YOUR geography!** 🚀🌎

---

**Need help?** Check the examples in the sidebar or review this guide for detailed instructions.

