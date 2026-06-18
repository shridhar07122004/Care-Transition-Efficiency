# Care Transition Efficiency & Placement Outcome Analytics

AI-powered analytics platform evaluating the efficiency of the Unaccompanied Children (UAC) care pipeline:

**Apprehension → CBP Custody → HHS Care → Sponsor Placement**

## Features

- **KPI Engine** — Transfer efficiency, discharge effectiveness, throughput, backlog metrics
- **Bottleneck Detection** — Rule-based alerts for transfer, placement, accumulation, and slowdown risks
- **Anomaly Detection** — Isolation Forest for unusual operational events
- **Forecasting** — 30-day Prophet forecasts for apprehensions, transfers, HHS population, and discharges
- **Recommendations** — Automated, human-readable operational guidance
- **Streamlit Dashboard** — 7-page interactive analytics platform with dark theme

## Project Structure

```
care-transition-analytics/
├── data/uac_data.csv          # UAC operational dataset
├── src/                       # Data processing & analytics modules
├── dashboard/                 # Streamlit application
├── notebooks/eda.ipynb        # Exploratory data analysis
├── reports/                   # Research report & executive summary
└── requirements.txt
```

## Dataset

Place the HHS UAC dataset at `data/uac_data.csv`. Expected columns:

| Column | Description |
|--------|-------------|
| Date | Report date |
| Children apprehended and placed in CBP custody* | Daily apprehensions |
| Children in CBP custody | Active CBP population |
| Children transferred out of CBP custody | Daily transfers to HHS |
| Children in HHS Care | Active HHS population |
| Children discharged from HHS Care | Daily sponsor placements |

## Setup

```bash
cd care-transition-analytics
python -m venv venv
venv\Scripts\activate        # Windows
pip install -r requirements.txt
```

## Run Dashboard

```bash
cd care-transition-analytics
pip install -r requirements.txt
cd dashboard
streamlit run app.py
```

## KPI Definitions

| KPI | Formula | Purpose |
|-----|---------|---------|
| Transfer Efficiency | Transfers / CBP Population | CBP → HHS movement rate |
| Discharge Effectiveness | Discharges / HHS Population | Sponsor placement rate |
| Pipeline Throughput | Discharges / Apprehensions | End-to-end flow rate |
| Daily Backlog | Apprehensions − Discharges | Unresolved daily inflow |
| Cumulative Backlog | Running sum of daily backlog | Accumulation severity |
| Outcome Stability | 7-day rolling std of discharge effectiveness | Placement consistency |

## License

For educational and analytical use.
