# 🚀 Quick Start Guide - New Filter System

## What Changed?

Your app now has **smarter, more practical filters** that align with how admissions and marketing teams actually work!

---

## 🎛️ New Global Filters (Sidebar)

### 📅 Academic Period Filter
**Instead of:** Date ranges  
**Now:** Select admission periods like "2024 Fall", "2025 Spring"

**Example:**
```
✓ Select: "2024 Fall"
✓ Result: All contacts admitted for Fall 2024 semester
```

**Tip:** Leave empty to see all periods

---

### 💰 Likelihood to Close
**What it does:** Filter by how likely contacts are to close  
**How:** Slider from 0% to 100%

**Example:**
```
✓ Set slider: 70%
✓ Result: Only high-probability prospects (>= 70%)
```

**Tip:** Set to 0% to see all contacts

---

### 🔄 Lifecycle Stage (Latest Only!)
**What changed:** Now uses CURRENT lifecycle stage (not history)  
**How:** Multi-select dropdown

**Example:**
```
✓ Select: "MQL" and "SQL"
✓ Result: Only current Marketing & Sales Qualified Leads
✗ Won't show: Contacts who were MQL but now Closed
```

**Tip:** Leave empty to see all stages

---

### 📊 Closure Status
**What it does:** Filter by open vs closed deals  
**Options:**
- All Contacts (default)
- Closed Only
- Open Only

**Example:**
```
✓ Select: "Open Only"
✓ Result: Only active prospects, no closed deals
```

---

## ✨ What We Removed (and Why)

### ❌ Date Range Filter
**Replaced with:** Academic Period Filter  
**Why:** Teams think in terms of admission cycles, not arbitrary dates

### ❌ Min Sessions, Pageviews, Forms Filters
**Where they went:** Now available as cluster-specific filters  
**Why:** Engagement filtering makes more sense within each analysis type

---

## 💡 Common Use Cases

### Use Case 1: Find High-Priority Fall 2024 Prospects
```yaml
Step 1: Global Filters
  - Academic Period: "2024 Fall"
  - Lifecycle: "MQL", "SQL"
  - Likelihood: 70%
  - Closure: "Open Only"

Step 2: Navigate to Cluster 1 (Social)

Step 3: Cluster 1 Filters
  - Segment: "1A"
  - Platform: "Instagram"

Result: High-engagement Instagram prospects for Fall 2024
Action: Export → Upload to Meta Ads for retargeting
```

---

### Use Case 2: Analyze What Worked in 2024
```yaml
Step 1: Global Filters
  - Academic Period: Select all 2024 periods
  - Closure: "Closed Only"

Step 2: Navigate to Cluster 2 (Geography)

Step 3: Review Performance Benchmarks Tab
  - See which geographies closed best
  - Compare local vs international

Result: Data-driven insights for 2025 planning
```

---

### Use Case 3: Current MQLs Need Nurture
```yaml
Step 1: Global Filters
  - Lifecycle: "MQL" only
  - Closure: "Open Only"
  - Likelihood: 40-60% (medium range)

Step 2: Navigate to Cluster 3 (APREU)

Step 3: Review Activity Analysis
  - See which activities they attended
  - Identify gaps in journey

Result: Targeted nurture campaign list
Action: Export → Create personalized follow-up sequence
```

---

## 🎯 Pro Tips

### Tip 1: Start Broad, Then Narrow
```
✓ Apply 1-2 global filters first
✓ Navigate to relevant cluster
✓ Apply cluster-specific filters
✓ Export when you find your target segment
```

### Tip 2: Use Filter Summary
```
✓ Look for "🔍 Active Filters" expander
✓ See exactly what's being filtered
✓ Check resulting contact count
```

### Tip 3: Reset When Confused
```
✓ Click "🔄 Reset All Filters" in sidebar
✓ Start fresh with different approach
```

### Tip 4: Combine Filters Strategically
```
Good Combo: Periodo + Likelihood + Lifecycle
Purpose: Find high-quality prospects from specific intake

Good Combo: Closure Status + Periodo
Purpose: Analyze conversion rates by admission period

Good Combo: Lifecycle + Cluster Filters
Purpose: Deep dive into specific segment behavior
```

---

## 🔍 Understanding Your Results

### When you see: "✅ 1,234 of 10,000 contacts after filters"

**This means:**
- Started with 10,000 contacts
- Applied filters reduced to 1,234 matches
- That's 12.3% of your data
- ✅ This is your focused, actionable segment!

**If you see 0 contacts:**
- Filters are too restrictive
- Try removing one filter at a time
- Check if periodo codes exist in your data

---

## 📊 Data Requirements

### For filters to work, your CSV needs:

**Required:**
- Record ID (always required)

**For Global Filters:**
- `Periodo de ingreso` field (format: YYYYMM like 202408)
- `Lifecycle Stage` field
- `Likelihood to close` field
- `Close Date` field

**Format Notes:**
- Periodo: Must be 6-digit codes (202408, not "Aug 2024")
- Lifecycle: Can have historical values (will use latest)
- Likelihood: Can be 0-1 or 0-100 scale (auto-detected)

---

## 🆘 Troubleshooting

### Problem: "Periodo filter is empty"
**Solution:** Check your data has `Periodo de ingreso` field with valid YYYYMM codes

### Problem: "Lifecycle filter shows weird values"
**Solution:** Data might have "Other" or "subscriber" - these are filtered out. If dropdown is empty, check your Lifecycle Stage data.

### Problem: "Filters not working"
**Solution:** 
1. Check you have data loaded
2. Try "🔄 Reset All Filters"
3. Apply one filter at a time to isolate issue

### Problem: "Too many/few results"
**Solution:** Adjust threshold values (likelihood slider, select more/fewer periodos)

---

## 📈 What's Next?

### You can now:
1. ✅ Filter by academic periods (admission cycles)
2. ✅ Filter by business criteria (likelihood, lifecycle, closure)
3. ✅ Drill down with cluster-specific filters
4. ✅ Export targeted segments for campaigns
5. ✅ Benchmark performance across segments

### Coming soon:
- Cluster 3 specific filters
- Segment comparison tool
- Data quality indicators

---

## 🎓 Quick Reference Card

```
╔══════════════════════════════════════════════════════════╗
║                    FILTER QUICK GUIDE                    ║
╠══════════════════════════════════════════════════════════╣
║  📅 PERIODO        →  Select admission semester(s)       ║
║  💰 LIKELIHOOD     →  Slider 0-100% (min threshold)      ║
║  🔄 LIFECYCLE      →  Multi-select (uses LATEST)         ║
║  📊 CLOSURE        →  Radio: All / Closed / Open         ║
╠══════════════════════════════════════════════════════════╣
║  🔄 RESET          →  Button in sidebar                  ║
║  🔍 VIEW ACTIVE    →  Expander shows applied filters     ║
║  📥 EXPORT         →  Available in each cluster          ║
╚══════════════════════════════════════════════════════════╝
```

---

**Need more help?** 
- Check `FILTER_CHANGES_SUMMARY.md` for technical details
- Review sidebar "📖 Quick Reference" sections
- Look at "Required Data Format" in sidebar

**Ready to analyze?**
1. Load your data
2. Apply 1-2 global filters
3. Pick a cluster
4. Add cluster filters if needed
5. Explore & export!

---

**Version:** 2.1 - Simplified & Practical  
**Date:** October 22, 2025  
**Status:** ✅ All changes tested and working

