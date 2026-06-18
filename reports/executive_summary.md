# Executive Summary — UAC Care Transition Analytics

## Overview

This analytics platform measures how effectively unaccompanied children move through the federal care pipeline: **Apprehension → CBP Custody → HHS Care → Sponsor Placement**. It transforms daily operational data into actionable intelligence for program leadership.

## Key Capabilities

| Capability | Impact |
|------------|--------|
| **Pipeline KPIs** | Quantifies transfer efficiency, placement effectiveness, and throughput |
| **Bottleneck Detection** | Automatically flags transfer delays, placement inefficiencies, and backlog risks |
| **Anomaly Detection** | Identifies unusual operational events requiring investigation |
| **30-Day Forecasting** | Predicts future apprehensions, transfers, HHS load, and discharges |
| **Recommendations** | Generates prioritized, human-readable operational guidance |

## Current Operational Snapshot

The dashboard provides real-time visibility into:
- Total apprehensions, transfers, and discharges
- Average transfer efficiency and discharge effectiveness
- Current cumulative backlog and HHS population
- Active bottleneck alerts with severity classification

## Risk Assessment Framework

| Risk Level | Trigger Conditions |
|------------|-------------------|
| **High** | Transfer efficiency < 50%, discharge effectiveness < 40%, 7-day backlog streak |
| **Moderate** | Declining KPI trends, throughput below historical average |
| **Low** | Stable metrics within operational thresholds |

## Recommended Actions

1. **Increase transfer coordination** when CBP-to-HHS efficiency declines
2. **Allocate shelter resources** when backlog accumulates continuously
3. **Review placement workflows** when discharge effectiveness falls
4. **Use forecasts** to pre-position capacity 30 days ahead

## Dashboard Access

```bash
cd dashboard && streamlit run app.py
```

**Navigation:** Overview → Pipeline → Transfer Analytics → Placement Outcomes → Bottlenecks → Forecasting → Recommendations

---

*One-page summary for stakeholders — Care Transition Analytics Platform*
