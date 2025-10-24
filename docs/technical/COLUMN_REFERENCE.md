# Column Reference - Expected CSV Format

## Expected Column Names (from your HubSpot export)

This document lists the exact column names your CSV should have. The app will automatically find these using the aliases defined in `app/utils/load.py`.

### Core Identification
- ✅ `Record ID` or `hs_object_id` - Contact ID
- ✅ `Email` or `email` - Email address

### Engagement Metrics (Required for all clusters)
- ✅ `Number of Sessions` - Website visits
- ✅ `Number of Pageviews` - Total page views
- ✅ `Number of Form Submissions` or `Forms Submitted` - Form completions

### Social Engagement (Cluster 1)
- ✅ `Broadcast Clicks` - Main social clicks column
- ✅ `LinkedIn Clicks` - LinkedIn engagement
- ✅ `Twitter Clicks` - Twitter/X engagement
- ✅ `Facebook Clicks` - Facebook engagement

### Traffic Sources (Cluster 1)
- ✅ `Original Source` - First traffic source
- ✅ `Original Source Drill-Down 1` - Source detail level 1
- ✅ `Original Source Drill-Down 2` - Source detail level 2
- ✅ `Canal de adquisición` - Acquisition channel
- ✅ `Latest Traffic Source` or `Latest Source` - Most recent source
- ✅ `Last Referring Site` - Last referrer URL

### Geography (Cluster 2)
- ✅ `IP Country` - Country from IP
- ✅ `IP State/Region` - State from IP
- ✅ `Ciudad preparatoria BPM` - Prep school city
- ✅ `Preparatoria BPM` - Prep school name
- ✅ `Estado de preparatoria BPM` - Prep school state
- ✅ `Estado de procedencia` - State of origin
- ✅ `País preparatoria BPM` - Prep school country

### APREU Activities (Cluster 3)
- ✅ `Actividades de promoción APREU` - All APREU activities (// delimited)
- ✅ `¿Cuál es el nombre de tu preparatoria?` - Prep school name (user entered)
- ✅ `Preparatoria donde estudia` - Current prep school
- ✅ `¿Qué año de preparatoria estás cursando?` - Prep year

### Conversion & Lifecycle
- ✅ `First Conversion` - First conversion event name
- ✅ `First Conversion Date` - First conversion timestamp
- ✅ `Recent Conversion` - Latest conversion event name
- ✅ `Recent Conversion Date` - Latest conversion timestamp
- ✅ `Lifecycle Stage` - Current lifecycle stage
- ✅ `Likelihood to close` - Predictive score

### Email Engagement (Cluster 3)
- ✅ `Marketing emails delivered` - Emails sent
- ✅ `Marketing emails opened` - Emails opened
- ✅ `Marketing emails clicked` - Emails clicked

### Dates & Business
- ✅ `Create Date` - Contact creation date
- ✅ `Close Date` - Deal close date

### Academic Periods
- ✅ `Periodo de ingreso` or `Periodo de ingreso a licenciatura (MQL)`
- ✅ `Periodo de admisión BPM` or `Periodo de admisión BPM (Solicitante → Nuevo Ingreso)`

### **CRITICAL** - APREU Filtering
- ✅ `Propiedad del contacto` - **MUST** contain "APREU" to be included

---

## How the App Uses These Columns

### On CSV Upload:

1. **APREU Filter** (Most Important!)
   ```
   Keeps only contacts where: "Propiedad del contacto" == "APREU"
   Expected: ~77,067 contacts from ~128,923 total
   ```

2. **Lifecycle Filter**
   ```
   Excludes lifecycle stages: "Other" and "subscriber"  
   Expected: ~74,868 contacts after filtering
   ```

3. **Cluster 1: Social Engagement**
   ```
   Uses: Broadcast/LinkedIn/Twitter/Facebook Clicks
   Plus: Original Source, Canal de adquisición, Latest Traffic Source
   Result: Identifies socially engaged contacts → 1A/1B segments
   ```

4. **Cluster 2: Geography**
   ```
   Uses: IP Country/State + all preparatoria geography fields
   Result: Classifies into local/domestic/international → 2A-2F segments
   ```

5. **Cluster 3: APREU Activities**
   ```
   Uses: "Actividades de promoción APREU" (parses // delimited history)
   Result: Classifies by entry channel → 3A-3D segments
   ```

---

## Missing Columns?

The app will gracefully handle missing columns:

- **Shows warnings** for missing critical columns
- **Disables features** that require missing columns
- **Continues processing** with available data

Check the sidebar after upload to see which features are available.

---

## Column Format Notes

### History Fields (// delimited)
Many columns use HubSpot's history format:
```
"value1//value2//value3"
```

The app automatically:
- Parses ALL historical values (for Cluster 1 & 3)
- Uses LATEST value for most fields
- Concatenates text for keyword matching

### Date Fields
Timestamps can be:
- HubSpot milliseconds (e.g., `1698508800000`)
- ISO date strings (e.g., `2023-10-28T12:00:00Z`)

The app converts both formats automatically.

### Numeric Fields
- Empty values → 0
- Text values → converted to numeric or 0
- inf/NaN → 0 (safe division)

---

## Quick Validation

After uploading, check these numbers match:

| Metric | Expected (from notebooks) |
|--------|---------------------------|
| Total contacts uploaded | ~128,923 |
| APREU contacts | ~77,067 |
| After lifecycle filter | ~74,868 |
| Socially engaged (Cluster 1) | Check notebook |
| Geo-classified (Cluster 2) | ~69,309 |
| APREU-tagged (Cluster 3) | Check notebook |

If numbers don't match, the column names might be slightly different in your CSV.

---

## Troubleshooting

**"No socially engaged contacts found"**
→ Check: `Broadcast Clicks`, `LinkedIn Clicks`, `Twitter Clicks`, `Facebook Clicks` columns exist

**"No geo-classified contacts found"**
→ Check: `IP Country`, `IP State/Region`, or preparatoria geo columns exist

**"No APREU-tagged contacts found"**
→ Check: `Actividades de promoción APREU` column exists

**Numbers way too low**
→ Check: `Propiedad del contacto` column has "APREU" values

---

**Need help?** Check `FIXES_APPLIED.md` for details on what was changed to match your notebooks.

