"""
Feature engineering for the TNRERA AVM dashboard.

The model was trained on 30 columns (see decisions log / model export cell in
04_TNRERA_MODELLING.ipynb). Only 13 of those are things a real user can supply
for a *new, hypothetical* project — the rest are either derived from those 13,
or are data-quality audit flags that describe defects in the historical TNRERA
filings and simply don't apply to a fresh input.

This module is the single source of truth for that split, so the prediction
page and the model input schema can never drift apart.
"""

import numpy as np
import pandas as pd

SQM_TO_SQFT = 10.7639

# The exact 30 columns the model was trained on, in the exact order
# X.columns appeared in 04_TNRERA_MODELLING.ipynb. LightGBM (and most
# tree models) don't strictly require column order to match, but the
# categorical dtypes and the *set* of columns must match exactly, so we
# keep the order pinned here to make that easy to eyeball and diff.
MODEL_FEATURE_COLUMNS = [
    'Districts', 'Latitude', 'Longitude', 'Usage', 'Type_of_Building',
    'Site_Extent_Sqm', 'FSI_LIG_Residential', 'FSI_Other_Residential',
    'FSI_Commercial', 'Total_Dwelling_Units', 'Covered_Parking',
    'Open_Parking', 'Visitor_Parking', 'FE_Site_Extent_Sqft',
    'FE_Total_FSI_Area_Sqft', 'FE_FSI', 'FE_Permissable_FSI',
    'FE_Max_Premium_FSI', 'FE_Total_Parking', 'FE_Average_Unit_Size_Sqft',
    'Is_TNUHDB_TNHB', 'Is_Dwelling_Units_Hardcoded',
    'Is_FSI_Imputed_From_Comparable_Avg', 'Coord_Was_Corrupted',
    'Is_Coordinates_Hardcoded', 'FSI_outlier_flag', 'Imputed_Car_Parking',
    'Parking_was_imputed', 'Is_Construction_Cost_Below_Floor',
    'Is_Construction_Cost_Imputed',
]

CATEGORICAL_COLUMNS = ['Districts', 'Usage', 'Type_of_Building']

# Every district present in the training data. A prediction for a district
# outside this list is technically possible (LightGBM will still run) but
# the model has never seen it — treat it as extrapolation, not interpolation.
KNOWN_DISTRICTS = [
    'Chengalpattu', 'Chennai', 'Coimbatore', 'Cuddalore', 'Dindigul', 'Erode',
    'Kancheepuram', 'Karur', 'Krishnagiri', 'Madurai', 'Namakkal', 'Nilgiris',
    'Ranipet', 'Salem', 'Sivagangai', 'Thanjavur', 'Tiruchirappalli',
    'Tirunelveli', 'Tirupathur', 'Tiruppur', 'Tiruvallur', 'Tiruvannamalai',
    'Vellore', 'Virudhunagar',
]

USAGE_OPTIONS = ['Residential', 'Commercial', 'Mixed Development']
BUILDING_TYPE_OPTIONS = ['Non-High Rise Building (NHRB)', 'High Rise Building (HRB)']


def build_feature_row(
    district: str,
    latitude: float,
    longitude: float,
    usage: str,
    building_type: str,
    site_extent_sqm: float,
    fsi_lig_residential: float,
    fsi_other_residential: float,
    fsi_commercial: float,
    total_dwelling_units: float,
    covered_parking: float,
    open_parking: float,
    visitor_parking: float,
) -> pd.DataFrame:
    """
    Turn the 13 user-facing inputs into a single-row DataFrame matching
    MODEL_FEATURE_COLUMNS exactly — same engineered fields, same audit-flag
    defaults, same categorical dtypes as training.

    Returns a 1-row DataFrame ready to pass straight to model.predict().
    """
    is_high_rise = building_type == 'High Rise Building (HRB)'

    # --- Engineered fields — formulas copied verbatim from 03_TNRERA_EDA.ipynb ---
    fe_site_extent_sqft = round(site_extent_sqm * SQM_TO_SQFT)

    fsi_components = [fsi_lig_residential, fsi_other_residential, fsi_commercial]
    # min_count=1 semantics: if ALL three are missing/zero-as-unset, this would
    # be NaN in the notebook. In the dashboard we treat "not entered" as 0,
    # since every project needs *some* built area to be worth predicting on.
    fe_total_fsi_area_sqft = round(sum(fsi_components) * SQM_TO_SQFT)

    fe_fsi = (
        round(fe_total_fsi_area_sqft / fe_site_extent_sqft, 2)
        if fe_site_extent_sqft else 0.0
    )

    fe_permissable_fsi = 2.0  # constant across all rows in training data
    fe_max_premium_fsi = 3.75 if is_high_rise else 2.0

    fe_total_parking = covered_parking + open_parking + visitor_parking

    residential_area_sqft = (fsi_lig_residential + fsi_other_residential) * SQM_TO_SQFT
    fe_average_unit_size_sqft = (
        round(residential_area_sqft / total_dwelling_units)
        if total_dwelling_units else 0.0
    )

    row = {
        'Districts': district,
        'Latitude': latitude,
        'Longitude': longitude,
        'Usage': usage,
        'Type_of_Building': building_type,
        'Site_Extent_Sqm': site_extent_sqm,
        'FSI_LIG_Residential': fsi_lig_residential,
        'FSI_Other_Residential': fsi_other_residential,
        'FSI_Commercial': fsi_commercial,
        'Total_Dwelling_Units': total_dwelling_units,
        'Covered_Parking': covered_parking,
        'Open_Parking': open_parking,
        'Visitor_Parking': visitor_parking,
        'FE_Site_Extent_Sqft': fe_site_extent_sqft,
        'FE_Total_FSI_Area_Sqft': fe_total_fsi_area_sqft,
        'FE_FSI': fe_fsi,
        'FE_Permissable_FSI': fe_permissable_fsi,
        'FE_Max_Premium_FSI': fe_max_premium_fsi,
        'FE_Total_Parking': fe_total_parking,
        'FE_Average_Unit_Size_Sqft': fe_average_unit_size_sqft,
        # --- Data-quality audit flags: a new, hand-entered project has none
        # of the defects these flags describe in the historical TNRERA data,
        # so every one of them is hardcoded to its "clean" value. ---
        'Is_TNUHDB_TNHB': False,               # always False even in training data (these rows are dropped upstream)
        'Is_Dwelling_Units_Hardcoded': False,
        'Is_FSI_Imputed_From_Comparable_Avg': False,
        'Coord_Was_Corrupted': 0,
        'Is_Coordinates_Hardcoded': False,
        'FSI_outlier_flag': fe_fsi > 10,        # keep this one *computed*, not hardcoded — genuinely reflects this input
        'Imputed_Car_Parking': np.nan,
        'Parking_was_imputed': False,
        'Is_Construction_Cost_Below_Floor': False,
        'Is_Construction_Cost_Imputed': False,
    }

    df_row = pd.DataFrame([row], columns=MODEL_FEATURE_COLUMNS)

    for col in CATEGORICAL_COLUMNS:
        df_row[col] = df_row[col].astype('category')

    df_row['Parking_was_imputed'] = df_row['Parking_was_imputed'].astype(bool)

    return df_row


def predict_cost_per_sqft(model, feature_row: pd.DataFrame) -> float:
    """
    Run the model and undo the log1p transform the target was trained on.
    Every prediction MUST go through this — calling model.predict() directly
    anywhere else in the app will silently return a log-scale number that
    looks like a plausible price and isn't.
    """
    log_pred = model.predict(feature_row)[0]
    return float(np.expm1(log_pred))
