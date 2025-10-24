# Cluster 3: Promotion-driven Converters (APREU Activities)

## Overview

The `Cluster3.ipynb` notebook segments contacts by their **promotional activity history** and **primary entry channel**, using comprehensive HubSpot historical data to assign each contact to one of four actionable subclusters (3A–3D). The focus is on understanding which APREU activities and entry points drive conversions, how quickly they convert, and how to tailor follow-up strategies by segment.

## Purpose

Identify the **entry mechanisms that most effectively bring prospects into the funnel** (digital, events, messaging, niche programs) and provide **actionable insights** for marketing, admissions, and leadership teams. This segmentation translates promotional activity patterns into clear outreach playbooks and measurable pipeline impact.

## Key Features

### ✅ Historical APREU Activity Intelligence
- **Comprehensive history parsing**: Uses HubSpot historical values (not just latest) to detect participation across activities
- **Multi-activity detection**: Open Day, Fogatada, TDLA, Gira Panamá, WhatsApp campaigns, RUA forms, specialty programs, etc.
- **Preparatoria cross-analysis**: Ranks schools by activity participation and outcomes

### 🎯 Entry Channel Classification (3A–3D)
- **Smart pattern matching** on activities and first conversion events
- Assigns each contact to a primary entry segment:
  - **3A Digital-first**: Website/Form entrants
  - **3B Event-first**: Live/virtual event entrants
  - **3C Messaging-first**: WhatsApp/direct outreach entrants
  - **3D Niche**: Low-volume/special program entrants

### 📈 Outcome & Journey Analytics
- **Conversion timeline**: Journey from create date to first/recent conversion
- **Time-to-close (TTC)**: Days to close with bucketed speeds (Early/Medium/Late/Very Late/Still Open)
- **Likelihood to Close**: HubSpot predictive score by segment

## Workflow

1. **Data Loading & Column Resolution**
   - Load contacts from `contacts_campus_Qro_.csv`
   - Normalize/alias HubSpot property names (APREU-specific fields included)

2. **Historical Activity Parsing**
   - Parse HubSpot historical strings of the form `value1 // value2 // value3`
   - Build activity flags, counts, and diversity metrics per contact

3. **Entry Channel Classification**
   - Detect primary entry channel from activity names + first conversion
   - Label contacts into 3A (Digital), 3B (Event), 3C (Messaging), 3D (Niche)

4. **Engagement & Business Metrics**
   - Compute journey durations, days to close, TTC buckets
   - Aggregate engagement and communication metrics by segment

5. **Profiling & Exports**
   - Create cross-tabs and KPI summaries by segment, activity, and preparatoria
   - Export a multi-sheet Excel workbook and CSV outputs

## Target Segments

### 3A. Digital-first Entrants (Website & Forms)
- **Profile**: Enter via website, RUA forms, or online channels; steady digital activity
- **Action**: Fast-track; automated nurture; retargeting and email optimization

### 3B. Event-first Participants (Live & Virtual Events)
- **Profile**: Open Day, Fogatada, TDLA, Gira Panamá, career events
- **Action**: Post-event personalized follow-up; clear next steps (application, interviews, campus visits)

### 3C. Messaging-first Leads (Direct Contact)
- **Profile**: WhatsApp, direct messaging, or personal outreach
- **Action**: Maintain personalized sequences; prioritize speed-to-first-response

### 3D. Niche/Low-volume Promotions (Special Programs)
- **Profile**: Specialty campaigns (e.g., Lion Leaders, program-specific events)
- **Action**: Tailored high-touch guidance; align messaging with niche intent

## Technical Architecture

### Data Sources
- **Contacts & Activities**: Historical APREU activity properties (full change history)
- **Conversion Events**: First and recent conversion event metadata
- **Engagement**: Sessions, pageviews, forms
- **Business Outcomes**: Likelihood to close, create/close dates, lifecycle stage

### Classification & Metrics Engine
- **Pattern-based classifier** for entry channels (3A–3D)
- **Journey & TTC calculations** with bucket categorization
- **Segment-level aggregations** for engagement, conversions, and outcomes

## Output and Deliverables

### Data Exports
- **CSV**: `cluster3_contacts.csv` with entry segment and key fields
- **Excel**: `segments_cluster3_summary.xlsx` with 32+ worksheets grouped into 8 categories

### Excel Output Guide (selected sheets)

- **CATEGORY 1: EXECUTIVE SUMMARY**
  - `1_executive_summary`: KPIs, segment distribution, top activities, conversion rates

- **CATEGORY 2: ENTRY CHANNEL SEGMENTS (3A–3D)**
  - `2_segment_counts`: Volume by 3A/3B/3C/3D
  - `3_segment_distribution`: Percentage split across segments
  - `4_segment_performance`: Engagement, conversions, close rates by segment

- **CATEGORY 3: ACTIVITIES**
  - `5_activity_participation`: Counts by APREU activity (Open Day, Fogatada, TDLA, etc.)
  - `6_activity_by_segment`: Activity × entry-channel cross-tab
  - `7_activity_diversity`: Activities per contact
  - `8_top_activities_overall`: Ranked most-attended activities
  - `9_activity_conversion_rates`: Close rates by activity

- **CATEGORY 4: CONVERSION EVENTS**
  - `17_conversion_by_segment`: Conversion metrics by entry channel
  - `19_conversion_event_performance`: Entry points that convert best

- **CATEGORY 5: COMMUNICATION & EMAIL**
  - `21_email_metrics_by_segment`: Email performance by segment

- **CATEGORY 6: BUSINESS OUTCOMES**
  - `24_likelihood_by_segment`: Predictive score by segment
  - `25_closure_stats_by_segment`: Totals/closed/open, close rate %, avg/median TTC
  - `26_lifecycle_by_segment`: Funnel stage distribution

- **CATEGORY 7: PIPELINE SPEED (TTC)**
  - `27_ttc_buckets_by_segment`: Early/Medium/Late/Very Late/Still Open distribution
  - `29_fast_closers_segment_x_activity`: Fast-closing combos by activity × segment
  - `30_slow_closers_segment_x_activity`: Slow closers >120 days (bottlenecks)
  - `31_fast_closers_segment_x_prepa`: Fast-closing combos by preparatoria × segment
  - `32_overall_ttc_summary`: Big-picture pipeline velocity

## Usage Instructions

### Prerequisites
1. **Historical Data**: Output from `sacar_historicos PLANTILLA.ipynb`
2. **Python Environment**: pandas, numpy, matplotlib/seaborn (and standard data tools)
3. **Contacts File**: `contacts_campus_Qro_.csv`

### Configuration
1. Set the data path (e.g., `FILE_PATH = "contacts_campus_Qro_.csv"`).
2. Review/extend activity keywords for APREU events and messaging.
3. Verify column name aliases for APREU and conversion fields.
4. Optionally tune thresholds or rules for entry-channel assignment.

### Execution
1. Run data loading and alias resolution.
2. Parse historical values and build activity features.
3. Classify entry channels into 3A/3B/3C/3D.
4. Compute engagement, journey, and business outcomes.
5. Export the Excel workbook and CSVs.

### How to Read the Output
- **Marketing**: Start at `4_segment_performance` and `21_email_metrics_by_segment` to tailor messaging; use `19_conversion_event_performance` to prioritize high-ROI entry points.
- **Sales/Admissions**: Use `29_fast_closers_segment_x_activity`, `17_conversion_by_segment`, and `24_likelihood_by_segment` to triage and prioritize; respond quickly to **3C (Messaging-first)**.
- **Leadership**: Review `1_executive_summary` and `9_activity_conversion_rates` for KPIs and ROI by initiative; compare channel effectiveness in `4_segment_performance`.

## Integration with Other Notebooks
- **sacar_historicos PLANTILLA.ipynb**: Provides historical property exports used here
- **Cluster1.ipynb**: Social engagement segmentation for cross-channel insights
- **Cluster2.ipynb**: Geography × engagement segmentation for geo-aware strategies

## Data Quality Considerations

### Common Challenges
- **Inconsistent activity naming** across exports (handled via alias mapping/patterns)
- **Historical string parsing** quirks (`//` delimiters, ordering, duplicates)
- **Negative/invalid date deltas** (filtered when computing days to close)

### Quality Assurance
- Historical parsing with validation and de-duplication
- Cross-validation of entry-channel assignment against conversion events
- Sanity checks on TTC calculations and bucket distributions

## Future Enhancements
- NLP-based normalization for activity names and categories
- Automated, incremental refresh as new HubSpot data arrives
- Multi-touch attribution weighting across activities and channels
- Predictive modeling to recommend next-best action by entry segment

---

*This segmentation translates APREU promotional activity patterns into clear entry-channel strategies, enabling faster response times, better prioritization, and measurable pipeline impact across Marketing, Admissions, and Leadership.*
