# Data Transparency Implementation Plan

## Problem Statement
U.S. government data sources may be subject to political manipulation, incomplete reporting, or selective disclosure. Users deserve to know exactly where data comes from, how trustworthy it is, and whether it has been independently verified.

---

## Current Data Sources Audit

### Government Sources (Requires Scrutiny)
| Source | Data Used | Risk Level | Notes |
|--------|-----------|------------|-------|
| ICE.gov Statistics | Detention population, arrests, deportations | HIGH | Agency self-reporting; historically underreported deaths |
| DHS Reports | Budget figures, enforcement stats | HIGH | Political messaging often embedded |
| CBP Data | Border encounters | HIGH | Definitions change between administrations |

### Independent Sources (Higher Trust)
| Source | Data Used | Verification | Notes |
|--------|-----------|--------------|-------|
| ACLU | Abuse complaints, deaths, conditions | Cross-referenced with lawsuits | Advocacy org but legally rigorous |
| Human Rights Watch | Facility conditions, abuse | On-ground investigations | International credibility |
| Physicians for Human Rights | Medical neglect, preventable deaths | Medical expertise | 95% preventable deaths finding |
| Freedom for Immigrants | Detention conditions, hotline reports | Direct detainee contact | First-hand accounts |
| Brennan Center | Budget analysis, policy impact | Academic methodology | Nonpartisan legal analysis |

### Academic/Research Sources (Highest Trust)
| Source | Data Used | Methodology | Notes |
|--------|-----------|-------------|-------|
| Penn Wharton Budget Model | Cost per deportation estimates | Economic modeling | $70,236 average figure |
| Migration Policy Institute | Policy analysis, demographic data | Peer-reviewed | Nonpartisan research |
| CATO Institute | Libertarian analysis, cost-benefit | Economic analysis | Right-leaning but data-rigorous |

### Media Sources (Contextual)
| Source | Data Used | Notes |
|--------|-----------|-------|
| The Guardian | Investigative reporting | Strong immigration beat |
| CBS News | Breaking news, official statements | Mainstream verification |
| ProPublica | Investigative data journalism | FOIA-based reporting |

---

## Transparency Features to Implement

### 1. Source Trust Badges
Visual indicators on every data point showing source category:

```
🏛️ GOVERNMENT - Official federal source (verify independently)
✅ VERIFIED - Independently corroborated by 2+ sources
🔬 ACADEMIC - Peer-reviewed or academic institution
📰 MEDIA - Journalistic investigation
🏢 NGO - Non-governmental organization research
⚠️ UNVERIFIED - Single source, not independently confirmed
```

### 2. Data Provenance Tracking
For each statistic, store and display:
- Original source URL
- Date retrieved
- Last verified date
- Cross-reference sources (if any)
- Methodology notes
- Known limitations/caveats

### 3. Source Preference Hierarchy
When multiple sources exist for same data:
1. **Primary**: Independent verification (ACLU, HRW, academic)
2. **Secondary**: Government data cross-checked with independent
3. **Tertiary**: Government data alone (flagged as such)
4. **Avoid**: Government data contradicted by independent sources

### 4. Contradiction Alerts
When government data conflicts with independent findings:
- Display both figures
- Explain the discrepancy
- Let users see the range
- Example: "ICE reports 10 deaths; ACLU documents 15 deaths including unreported cases"

### 5. Methodology Page
Dedicated page explaining:
- How data was collected
- Source selection criteria
- Update frequency
- Known gaps and limitations
- How users can verify independently

### 6. Real-Time Source Verification
- Links to original sources (not just citations)
- Archive.org backup links for government pages that may change
- FOIA request tracking for pending data

---

## Database Schema Changes

### New Table: `data_sources_detailed`
```sql
CREATE TABLE data_sources_detailed (
    id INTEGER PRIMARY KEY,
    source_name TEXT NOT NULL,
    source_type TEXT CHECK(source_type IN ('government', 'ngo', 'academic', 'media', 'legal')),
    trust_level TEXT CHECK(trust_level IN ('high', 'medium', 'low', 'contested')),
    url TEXT,
    archive_url TEXT,
    last_verified DATE,
    verification_notes TEXT,
    known_limitations TEXT,
    political_lean TEXT,
    funding_transparency TEXT
);
```

### New Table: `data_points`
```sql
CREATE TABLE data_points (
    id INTEGER PRIMARY KEY,
    metric_name TEXT NOT NULL,
    value TEXT NOT NULL,
    value_numeric REAL,
    date_reported DATE,
    date_retrieved DATE,
    primary_source_id INTEGER REFERENCES data_sources_detailed(id),
    verification_status TEXT CHECK(verification_status IN ('verified', 'unverified', 'contested', 'retracted')),
    cross_references TEXT,  -- JSON array of other source IDs
    government_figure TEXT,  -- What govt claims (if different)
    independent_figure TEXT, -- What independent sources show
    discrepancy_notes TEXT,
    methodology_notes TEXT,
    caveats TEXT
);
```

### New Table: `source_contradictions`
```sql
CREATE TABLE source_contradictions (
    id INTEGER PRIMARY KEY,
    metric_name TEXT NOT NULL,
    government_claim TEXT,
    government_source_id INTEGER,
    independent_finding TEXT,
    independent_source_id INTEGER,
    discrepancy_explanation TEXT,
    recommended_figure TEXT,
    date_identified DATE
);
```

---

## UI Implementation

### 1. Global Source Indicator
Top of every page:
```
📊 Data Transparency: 73% independently verified | 18% government-only | 9% contested
[View Full Methodology]
```

### 2. Inline Source Tooltips
Every statistic clickable/hoverable showing:
- Source name and type badge
- Original value
- Date retrieved
- Verification status
- "View original source" link
- "Report data issue" link

### 3. Source Filter
Allow users to:
- Hide government-only data
- Show only verified data
- See all sources side-by-side
- Export with full provenance

### 4. Contradiction Highlights
When data is contested:
```
┌─────────────────────────────────────────┐
│ ⚠️ DATA DISCREPANCY                     │
│                                         │
│ Deaths in Custody (2025)                │
│ ICE Official:     10 deaths             │
│ ACLU/PHR:         32 deaths             │
│                                         │
│ Discrepancy: ICE excludes deaths in     │
│ transit and within 24hrs of release     │
│                                         │
│ [Why the difference?] [View both]       │
└─────────────────────────────────────────┘
```

### 5. Methodology Modal
Accessible from every data point:
- Plain-language explanation
- Technical methodology
- Limitations acknowledged
- How to verify yourself
- Suggest a correction

---

## Implementation Phases

### Phase 1: Audit & Categorize (Immediate)
- [ ] Audit all current data points
- [ ] Categorize each source
- [ ] Identify government-only data
- [ ] Find independent alternatives where possible
- [ ] Document known discrepancies

### Phase 2: Database Migration
- [ ] Create new schema tables
- [ ] Migrate existing data with provenance
- [ ] Add verification status to all records
- [ ] Store archive.org links for govt sources

### Phase 3: UI Components
- [ ] Build source badge component
- [ ] Create tooltip system
- [ ] Add methodology page
- [ ] Implement source filter
- [ ] Build contradiction display

### Phase 4: Verification System
- [ ] Cross-reference automation where possible
- [ ] User reporting system for errors
- [ ] Regular verification schedule
- [ ] FOIA tracking integration

### Phase 5: Community Trust
- [ ] Open source all data with provenance
- [ ] Allow community corrections
- [ ] Transparent update log
- [ ] API for researchers

---

## Key Principles

1. **Default to skepticism** of government self-reporting
2. **Prefer independent verification** when available
3. **Show your work** - every number traceable to source
4. **Acknowledge uncertainty** - ranges > false precision
5. **Document discrepancies** openly, don't hide them
6. **Enable verification** - give users tools to check themselves
7. **Update transparently** - log all changes publicly

---

## Example: Applying to Deaths Data

**Current**: "32 deaths in ICE custody (2025)"

**Transparent Version**:
```
DEATHS IN ICE CUSTODY (2025)

Official Figure: 10 deaths (ICE.gov) 🏛️
Independent Count: 32 deaths (ACLU/PHR) ✅

Why the difference?
- ICE excludes deaths within 24 hours of release
- ICE excludes deaths during transport
- ICE excludes deaths in contracted facilities under certain conditions
- Independent sources track all detention-related deaths

Recommended Figure: 32 (using inclusive definition)
Confidence: HIGH - corroborated by multiple independent investigations
Last Verified: January 2026

[View ICE methodology] [View ACLU report] [View PHR investigation]
```

---

## Success Metrics

- 100% of data points have documented provenance
- >70% of key statistics independently verified
- All government-only data clearly flagged
- All known discrepancies documented
- Methodology accessible in <2 clicks from any stat
- User trust score tracking (survey)

