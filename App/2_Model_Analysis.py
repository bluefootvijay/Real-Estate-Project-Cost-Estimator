import sys
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

sys.path.append(str(Path(__file__).resolve().parent.parent))

from utils.data_loader import load_map_ready_data, load_model

st.set_page_config(page_title="Model Analysis", page_icon="📊", layout="wide")
st.title("📊 Model Analysis")

# ---------------------------------------------------------------------------
# 1. Model comparison table
# ---------------------------------------------------------------------------
st.subheader("Why LightGBM")

st.markdown(
    """
    Three algorithms were trained and evaluated on an identical 80/20 split
    of the same 943-row, 30-feature dataset, predicting `log1p(cost per sqft)`.

    *Note: the row below labeled HGB was originally mislabeled "Linear
    Regression" in an early notebook draft — the code that produced these
    numbers trains a `HistGradientBoostingRegressor`. Corrected here.*
    """
)

comparison_df = pd.DataFrame([
    {"Model": "HistGradientBoostingRegressor (HGB)", "R² (log scale)": 0.299, "MAE (₹/sqft)": 2080, "Median APE": "27.5%"},
    {"Model": "LightGBM  ✅ deployed", "R² (log scale)": 0.299, "MAE (₹/sqft)": 2059, "Median APE": "24.4%"},
    {"Model": "XGBoost", "R² (log scale)": 0.220, "MAE (₹/sqft)": 2173, "Median APE": "29.1%"},
])
st.dataframe(comparison_df, use_container_width=True, hide_index=True)

st.markdown(
    """
    **Why LightGBM, given R² is essentially tied with HGB?** Its MAE and
    Median APE are both better — meaning it handles outliers and non-linear
    feature interactions more effectively — without R² improving. That
    pattern matters: better error metrics with flat R² means LightGBM
    predicts *individual* projects more accurately without uncovering new
    signal in the data. The ~30% variance ceiling itself is a **data**
    constraint (finish quality, amenities, and micro-location aren't
    captured in TNRERA filings), not something any of the three algorithms
    could train its way past.
    """
)

st.divider()

# ---------------------------------------------------------------------------
# 2. Feature importance
# ---------------------------------------------------------------------------
st.subheader("What drives the prediction")

model = load_model()
try:
    importances = pd.DataFrame({
        "feature": model.feature_name_,
        "importance": model.feature_importances_,
    }).sort_values("importance", ascending=True).tail(15)

    fig_importance = px.bar(
        importances, x="importance", y="feature", orientation="h",
        title="Top 15 features by LightGBM split importance",
    )
    fig_importance.update_layout(height=500)
    st.plotly_chart(fig_importance, use_container_width=True)
    st.caption(
        "This is split-count importance (how often a feature is used to split), "
        "not permutation importance — it shows what the model relies on structurally, "
        "not necessarily what moves predictions most on unseen data."
    )
except AttributeError:
    st.warning("Could not read feature importances from the loaded model object.")

st.divider()

# ---------------------------------------------------------------------------
# 3. Project map
# ---------------------------------------------------------------------------
st.subheader("Where the training data comes from")

map_df = load_map_ready_data()

fig_map = px.scatter_mapbox(
    map_df,
    lat="Latitude",
    lon="Longitude",
    color="FE_Total_Project_Cost_per_Sqft",
    size_max=12,
    zoom=5.5,
    center={"lat": 11.0, "lon": 78.5},
    hover_name="Project_Name",
    hover_data={
        "Districts": True,
        "Type_of_Building": True,
        "FE_Total_Project_Cost_per_Sqft": ":,.0f",
        "Latitude": False,
        "Longitude": False,
    },
    color_continuous_scale="Viridis",
    labels={"FE_Total_Project_Cost_per_Sqft": "Cost per sqft (₹)"},
    mapbox_style="carto-positron",
    height=600,
)
fig_map.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0})
st.plotly_chart(fig_map, use_container_width=True)
