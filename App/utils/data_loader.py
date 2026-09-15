"""
Cached loaders for the model artifacts and the historical TNRERA dataset.

Streamlit re-runs your entire script top-to-bottom on every user interaction
(every slider drag, every dropdown click). Without caching, that means
re-reading a .pkl file and a 943-row CSV from disk on every single click —
noticeable lag for no reason. @st.cache_resource and @st.cache_data tell
Streamlit "run this once, keep the result in memory, reuse it."
- cache_resource: for objects that shouldn't be copied (models, DB connections)
- cache_data: for data that's safe to copy (DataFrames)
"""

from pathlib import Path

import pandas as pd
import streamlit as st

BASE_DIR = Path(__file__).resolve().parent.parent
MODELS_DIR = BASE_DIR / "models"
DATA_DIR = BASE_DIR / "data"

# Tamil Nadu's approximate bounding box. Used only to decide which historical
# rows are safe to plot on the map — never touches the underlying CSV or
# anything that feeds the model.
TN_LAT_RANGE = (7.5, 14.0)
TN_LON_RANGE = (75.0, 81.0)


@st.cache_resource
def load_model():
    """Load the trained LightGBM model. Cached — loaded once per session."""
    import joblib
    model_path = MODELS_DIR / "lgbm_avm_model.pkl"
    if not model_path.exists():
        st.error(
            f"Model file not found at {model_path}. "
            "Export it from 04_TNRERA_MODELLING.ipynb and place it in the "
            "models/ folder — see the README."
        )
        st.stop()
    return joblib.load(model_path)


@st.cache_data
def load_historical_data() -> pd.DataFrame:
    """Load the full TNRERA modelling dataset, unmodified."""
    csv_path = DATA_DIR / "tnrera_projects_for_modelling.csv"
    if not csv_path.exists():
        st.error(f"Data file not found at {csv_path}.")
        st.stop()
    return pd.read_csv(csv_path)


@st.cache_data
def load_map_ready_data() -> pd.DataFrame:
    """
    Historical data filtered to rows with plausible Tamil Nadu coordinates.

    27 of 943 rows have Latitude/Longitude outside Tamil Nadu's bounding box
    (confirmed against the existing Coord_Was_Corrupted / Is_Coordinates_Hardcoded
    flags, which do NOT catch these — likely lat/lon transposition or entry
    errors upstream). Per project decision, these are dropped from the MAP
    ONLY; the underlying CSV and the trained model are untouched.
    """
    df = load_historical_data()
    in_bounds = (
        df["Latitude"].between(*TN_LAT_RANGE)
        & df["Longitude"].between(*TN_LON_RANGE)
    )
    dropped = (~in_bounds).sum()
    if dropped:
        st.caption(
            f"Map shows {in_bounds.sum()} of {len(df)} projects — "
            f"{dropped} excluded for coordinates outside Tamil Nadu."
        )
    return df.loc[in_bounds].copy()


@st.cache_data
def get_district_centroids() -> dict:
    """
    Median lat/lon per district, computed from the map-ready (bad-coordinate-
    filtered) historical data. Used to give the prediction form a sensible
    starting point when a user picks a district but doesn't know exact
    coordinates — NOT used anywhere in the model itself.
    """
    df = load_map_ready_data()
    centroids = df.groupby("Districts")[["Latitude", "Longitude"]].median()
    return {
        district: (row["Latitude"], row["Longitude"])
        for district, row in centroids.iterrows()
    }
