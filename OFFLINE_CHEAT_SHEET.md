# Offline Analysis - 1-Page Cheat Sheet

## 3 Things to Know

### 1. What is "Offline Intensity"?
It's how many times a contact engaged offline (calls, events, meetings, etc.)

| Level | Meaning | Example |
|-------|---------|---------|
| 🟢 None | Never offline | Online-only contact |
| 🟡 Low (1-2) | Touched offline 1-2 times | Called once, went to event |
| 🟠 Medium (3-5) | Regular offline contact | Called 3 times, 1 meeting |
| 🔴 High (6+) | Very engaged offline | Called many times, multiple meetings |

### 2. Where Do I Find It?
**In the App:** Cluster 1 → "🌐 Online vs Offline" tab

**In Downloads:**
- CSV: New columns `offline_intensity` and `offline_mentions_total`
- Excel: Two new sheets about offline data

### 3. What Do I Do With It?

#### Quick Decision Guide
| Question | Answer |
|----------|--------|
| Who should I prioritize? | Contacts with High (6+) intensity |
| Should we expand offline? | Compare High vs Online close rates |
| For a campaign? | Filter by offline_intensity level |
| Measuring success? | Track % in High intensity growing |

---

## The Numbers

### What We Count
- Any mention of "OFFLINE" in source history
- Counted across entire contact journey
- Not just the most recent touch

### Example
```
Contact: Jane
  Touch 1: Facebook
  Touch 2: Offline - Event  ← counted
  Touch 3: Offline - Call   ← counted
  Touch 4: LinkedIn
  Touch 5: Offline - Webinar ← counted

Result: offline_mentions_total = 3
        offline_intensity = "Medium (3-5)"
```

---

## Quick Actions

### Find "Hot" Contacts
```
Download CSV → Filter: offline_intensity = 'High (6+)'
↓
Your most engaged offline contacts
```

### Compare Performance
```
Segment by: offline_intensity
Measure: Close rate or time-to-close
↓
See which intensity converts best
```

### Create Campaigns
```
1. Download CSV
2. Filter by offline_intensity
3. Send targeted messaging per level
```

---

## What Each Column Means

### `offline_intensity`
- **Low (1-2):** Casual offline user → nurture them
- **Medium (3-5):** Regular offline contact → move to close
- **High (6+):** Power offline user → prioritize for closing

### `offline_mentions_total`
- Raw number of offline touches
- Use to sort high-engagement contacts

### `offline_type`
- **Online:** Never went offline
- **Offline (Original Only):** First touch was offline
- **Offline (Latest Only):** Recent touches are offline
- **Offline (Throughout):** Mixed throughout journey

---

## Common Patterns

### If High (6+) Has Better Close Rate
✅ **Action:** Invest more in offline outreach

### If High (6+) Has Similar Close Rate to Online
⚠️ **Action:** Analyze ROI vs cost first

### If Low (1-2) Is Growing
✅ **Action:** Converting contacts from single touch (good sign!)

### If No Offline Data
ℹ️ **Action:** You're online-only or data isn't capturing offline

---

## Share This Info

### With Your Manager
"We're now tracking how many times each prospect engages offline. High-engagement offline contacts (6+ touches) make up X% of our leads."

### With Your Team
"Filter the CSV by offline_intensity to see who we've touched offline most. These are our warmest leads."

### In a Report
**Chart:** Show distribution of Low/Medium/High
**Table:** Compare close rates by intensity
**Metric:** "X% of customers had 6+ offline touches"

---

## That's Really It

1. **Count** offline touches (0, 1, 2... 10...)
2. **Group** them (Low, Medium, High)
3. **Use** that to decide next steps

Simple = useful.

---

**Questions?** Ask your data team. They set it up!

