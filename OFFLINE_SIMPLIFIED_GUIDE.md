# Offline Analysis - Simple Guide for Your Team

## What Is This?

We added a way to see **how many times** your prospects interacted with you offline (phone calls, events, meetings, etc.).

**Why?** Because one offline touchpoint is different from five. We need to know the **frequency**, not just whether it happened.

---

## The Simple Version

### What We Measure

We look at your contact's **entire history** and count every time "OFFLINE" appears in their source records.

**Example:**
- Contact A: 1 offline touch → "Light offline user"
- Contact B: 7 offline touches → "Heavy offline user"
- Contact C: 0 offline touches → "Online only"

### What We Show You

Three new pieces of information for each contact:

#### 1. **Offline Mentions Total**
**What it is:** How many times they engaged offline  
**Range:** 0 to 20+ interactions  
**Why it matters:** Shows commitment level

#### 2. **Offline Intensity** 
**What it is:** Simple grouping of offline frequency  
**Categories:**
- 🟢 **Low (1-2)** - Touched offline once or twice
- 🟡 **Medium (3-5)** - Regular offline contact
- 🔴 **High (6+)** - Very engaged offline

**Why it matters:** Easy segmentation for campaigns

#### 3. **Offline Type**
**What it is:** Where in their journey did offline happen?  
**Simple breakdown:**
- **Online** - Never went offline
- **Offline (Original Only)** - First contact was offline
- **Offline (Latest Only)** - Recent contact was offline
- **Offline (Throughout)** - Mixed offline & online

**Why it matters:** Understand their engagement pattern

---

## Where You See It

### In the Streamlit App

Go to **Cluster 1 → "🌐 Online vs Offline" tab**

You'll see:

1. **Top Section:** Simple chart showing how many contacts are in each intensity level
2. **Key Numbers:**
   - How many contacts have ANY offline engagement
   - Average times they touched offline
   - Highest number of offline touches
   - Total offline touchpoints

### Example Output

```
💬 Total Offline Contacts: 324 (42% of your prospects)
📊 Average Offline Touches: 3.2 times
📈 Max Someone Touched Offline: 8 times
🔢 Total Offline Touchpoints: 1,036

Distribution:
  🟢 Low (1-2):      145 contacts
  🟡 Medium (3-5):   122 contacts  
  🔴 High (6+):       57 contacts
```

---

## What It Means for Your Business

### Scenario 1: "Do offline contacts buy more?"
✅ **How to check:** Compare close rates for Low vs High intensity contacts

### Scenario 2: "Which prospect is most likely to convert?"
✅ **How to check:** Look for High (6+) intensity contacts - they've touched offline many times

### Scenario 3: "Should we do more offline outreach?"
✅ **How to check:** See what % of your best contacts are High intensity

### Scenario 4: "Are we wasting money on offline?"
✅ **How to check:** Compare conversion rates by intensity level

---

## Practical Actions

### Finding Your "Hot" Offline Users
📥 **Download the CSV** → Filter for `offline_intensity = 'High (6+)'`

✅ **Result:** List of contacts who engaged offline 6+ times

### Creating Targeted Campaigns
📊 **Compare by intensity:**
- Send different messaging to Low vs High intensity contacts
- Heavy offline users (High 6+) probably like personal touch
- New offline contacts (Low 1-2) might need warming

### Measuring Offline ROI
💰 **Track by segment:**
- Compare revenue from High intensity vs Online only
- See if offline investment pays off

---

## The Data You Get

### In Downloads

#### CSV File
New columns added to your contact export:
- `offline_mentions_total` - Raw count (0, 1, 2, 3...)
- `offline_intensity` - Category (Low/Medium/High)

#### Excel File  
Two new sheets:
- **Sheet 27:** How many contacts in each intensity level
- **Sheet 28:** Breakdown by your engagement segments (1A vs 1B)

---

## Common Questions

### Q: "Why do we count historical offline touches?"
**A:** Because a contact who touched offline 1 time behaves differently than someone who touched offline 7 times. The number tells us engagement level.

### Q: "What if no one has offline touches?"
**A:** All contacts will show as "Online" and offline_intensity will be "None". That's fine - it just means your data doesn't have offline records.

### Q: "Can I change what counts as offline?"
**A:** Yes, but we currently count any mention of the word "offline" in source records. Talk to tech team if you need to adjust.

### Q: "How do I use this for decisions?"
**A:** Look for patterns:
- Do High intensity (6+) contacts close faster? → Invest in offline
- Do they buy bigger deals? → Focus on High intensity
- Are they concentrated in one segment? → Target that segment offline

### Q: "Is Low (1-2) intensity bad?"
**A:** Not bad, just means light engagement. They might become High intensity over time, or they might be early in the journey.

---

## Decision Framework

### "Should We Increase Offline Efforts?"

**YES if:**
- ✅ High (6+) intensity contacts have 50%+ higher close rate
- ✅ 30%+ of your best customers are High intensity
- ✅ Average time-to-close is faster for High intensity

**NO if:**
- ❌ High intensity has same or lower conversion rate
- ❌ Cost per offline touch exceeds revenue impact
- ❌ Online-only contacts are outperforming

**INVESTIGATE if:**
- 🔍 Results are mixed or unclear
- 🔍 Only small sample sizes in each intensity
- 🔍 Data quality is questionable

---

## Key Metrics to Track

### Monthly/Quarterly
1. **% of contacts in each intensity** - Are we increasing offline?
2. **Close rate by intensity** - Which intensity converts best?
3. **Avg offline touches per deal** - Are we touching enough?
4. **Cost per offline touch vs revenue** - ROI check

### For Reports
- Show simple chart: Online vs Low vs Medium vs High
- Compare close rates in a table
- Highlight if High intensity is outperforming

---

## Tips for Your Team

### For Sales
- Use `offline_intensity` to prioritize follow-ups
- High (6+) contacts need conversion focus
- Low (1-2) contacts might need nurturing first

### For Marketing
- Create different messaging for each intensity level
- Test if adding offline touchpoints improves conversion
- Measure impact of offline campaigns on intensity increase

### For Leadership
- Simple metric: % of High intensity contacts
- Compare to competitors if possible
- Track quarterly trend

---

## That's It!

**Simple summary:**
- We count offline touchpoints (0, 1, 2... 8, 9...)
- We group them (Low 1-2, Medium 3-5, High 6+)
- We show you the distribution
- You use that to make decisions

**Not complicated, just useful data.**

Need help interpreting your specific results? Ask us!

---

**Last Updated:** October 2025  
**For:** Your entire team  
**Level:** Non-technical explanation

