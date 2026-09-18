# Real-Estate-Project-Cost-Estimator

A geospatial Automated Valuation Model (AVM) for Tamil Nadu residential real estate, built on TNRERA project registration data and grounded in TNCDBR-2019/CMDA bylaw domain knowledge — FSI ceilings, HRB/NHRB tiers, setbacks, and parking rules.
This is a portfolio project targeting Spatial Data Scientist, GIS & Urban Data Analyst, and Real Estate AVM Specialist roles in India. The differentiator over a generic price-prediction project is architecture/bylaw domain depth applied to feature engineering, not just model tuning.


## What it does
Predicts `FE_Total_Project_Cost_per_Sqft` for residential projects in Tamil Nadu, using:
TNRERA filings: ~1,030 PDF project registrations, parsed into structured data

The output is a trained LightGBM model, a comparison against HistGradientBoostingRegressor and XGBoost, and a public Streamlit dashboard for interactive price prediction.

### Results, honestly

All three algorithms (HistGradientBoostingRegressor, LightGBM, XGBoost) converge at:

Metric	Range

R²	≈ 0.26 – 0.30

MAE	≈ ₹2,000 – 2,500 / sqft

Median APE	≈ 23 – 27%


That convergence across three different algorithm families is itself the finding: this is a feature/data ceiling, not an algorithm problem. TNRERA filings don't capture finish quality, materials, amenities, or micro-location detail — the things that actually separate a luxury project from a budget one at the same coordinates. Land cost also shows high within-neighborhood variance from plot-level factors (shape, road access) that district- or coordinate-level features can't resolve.
The project treats this ceiling as a documented, evidence-backed result — not a shortfall to explain away — and backs it with map visualizations and a PDF-filing audit (see `notebooks/` and the dashboard's Model Analysis page).

## Repo structure
```
Project_Stick/
├── data_source/        # Raw 1030 TNRERA PDFs and source data (This is not present on GitHub as parsing 1030 pdf files for every prediction would take enormous amount of time)
├── notebooks/          # 01_TNRERA_Data_Cleaning.ipynb → 04_TNRERA_MODELLING.ipynb
├── outputs/            # Generated CSVs, figures
├── App/          	# Streamlit app (Price Predictor + Model Analysis pages)
└── README.md
```

## Pipeline

Data Cleaning & Field Extraction — parse TNRERA PDF filings into structured records; audit-flag anomalies

EDA & Feature Engineering — Creating key metrics from the source features - like FSI, Project Cost per Sqft etc.

Modelling (`04_TNRERA_MODELLING.ipynb`) — train and compare HistGradientBoostingRegressor, LightGBM, and XGBoost natively on NaN + categorical dtypes (no imputation/one-hot needed); log-transform the target

App — LightGBM model (best median APE) exported via `joblib`, served through a Streamlit app with a map-based price predictor and a model comparison page

## Data notes

Free geocoding (Nominatim) collapses Indian addresses to district centroids and was unusable at the required granularity — coordinates are taken directly from TNRERA filings instead
27 of 943 mapped rows had coordinates outside Tamil Nadu's bounding box (7 lat/lon swaps, 20 corrupted); dropped from the dashboard map only, left untouched in the underlying model TNHB/TNUHDB government-scheme rows are excluded from all modeling as they would not capture real market values. See `notebooks/04_TNRERA_MODELLING.ipynb` for the full leakage-column exclusion list.

## Stack

Python, Pandas, NumPy, GeoPandas, Contextily, scikit-learn, LightGBM, XGBoost, Streamlit, Plotly.

