import sys
from pathlib import Path

import streamlit as st

sys.path.append(str(Path(__file__).resolve().parent.parent))

from utils.data_loader import get_district_centroids, load_model
from utils.feature_engineering import (
    BUILDING_TYPE_OPTIONS,
    KNOWN_DISTRICTS,
    USAGE_OPTIONS,
    build_feature_row,
    predict_cost_per_sqft,
)

# Median APE of the deployed model (LightGBM, from the notebook's final
# comparison table) — used to show an honest uncertainty band alongside
# every prediction, not just a bare number.
MEDIAN_APE = 0.244

st.set_page_config(page_title="Price Predictor", page_icon="💰", layout="wide")
st.title("💰 Price Predictor")
st.caption("Enter a project's details to get a predicted construction cost per sqft")

model = load_model()
centroids = get_district_centroids()

col_left, col_right = st.columns([1, 1])

with col_left:
    with st.form("prediction_form"):
        st.subheader("Location")
        district = st.selectbox("District", KNOWN_DISTRICTS, index=KNOWN_DISTRICTS.index("Chennai"))

        default_lat, default_lon = centroids.get(district, (13.0827, 80.2707))
        lat_col, lon_col = st.columns(2)
        latitude = lat_col.number_input("Latitude", value=float(default_lat), format="%.6f")
        longitude = lon_col.number_input("Longitude", value=float(default_lon), format="%.6f")
        st.caption(f"Defaulted to the median coordinates of {district}'s projects — adjust if you know the exact site.")

        st.subheader("Project type")
        usage = st.selectbox("Usage", USAGE_OPTIONS)
        building_type = st.selectbox("Type of Building", BUILDING_TYPE_OPTIONS)

        st.subheader("Site & built area")
        site_extent_sqm = st.number_input("Site Extent (Sqm)", min_value=0.0, value=1500.0, step=50.0)
        fsi_lig = st.number_input("FSI — LIG Residential (Sqm)", min_value=0.0, value=0.0, step=50.0,
                                   help="Low-Income-Group residential FSI area, if applicable. Most projects report 0.")
        fsi_other_res = st.number_input("FSI — Other Residential (Sqm)", min_value=0.0, value=2800.0, step=50.0)
        fsi_commercial = st.number_input("FSI — Commercial (Sqm)", min_value=0.0, value=0.0, step=50.0)
        total_dwelling_units = st.number_input("Total Dwelling Units", min_value=1.0, value=30.0, step=1.0)

        st.subheader("Parking")
        p_col1, p_col2, p_col3 = st.columns(3)
        covered_parking = p_col1.number_input("Covered", min_value=0.0, value=20.0, step=1.0)
        open_parking = p_col2.number_input("Open", min_value=0.0, value=4.0, step=1.0)
        visitor_parking = p_col3.number_input("Visitor", min_value=0.0, value=2.0, step=1.0)

        submitted = st.form_submit_button("Predict cost per sqft", use_container_width=True)

with col_right:
    st.subheader("Prediction")

    if not submitted:
        st.info("Fill in the form and click **Predict cost per sqft** to see a result.")
    else:
        feature_row = build_feature_row(
            district=district, latitude=latitude, longitude=longitude,
            usage=usage, building_type=building_type,
            site_extent_sqm=site_extent_sqm,
            fsi_lig_residential=fsi_lig, fsi_other_residential=fsi_other_res,
            fsi_commercial=fsi_commercial, total_dwelling_units=total_dwelling_units,
            covered_parking=covered_parking, open_parking=open_parking,
            visitor_parking=visitor_parking,
        )

        predicted = predict_cost_per_sqft(model, feature_row)
        low = predicted * (1 - MEDIAN_APE)
        high = predicted * (1 + MEDIAN_APE)

        st.metric("Predicted cost per sqft", f"₹{predicted:,.0f}")
        st.caption(
            f"Typical error band (± median APE of {MEDIAN_APE:.0%}): "
            f"₹{low:,.0f} – ₹{high:,.0f} per sqft. "
            "This is the honest range, not a display rounding — half of the model's "
            "predictions miss by more than this on held-out data."
        )

        fe_total_fsi_area_sqft = float(feature_row["FE_Total_FSI_Area_Sqft"].iloc[0])
        estimated_total_cost = predicted * fe_total_fsi_area_sqft
        st.metric("Estimated total construction cost", f"₹{estimated_total_cost:,.0f}")
        st.caption(f"= predicted cost/sqft × {fe_total_fsi_area_sqft:,.0f} sqft total FSI area")

        fe_fsi = float(feature_row["FE_FSI"].iloc[0])
        if fe_fsi > 10:
            st.warning(
                f"Computed FSI ({fe_fsi:.2f}) is unusually high relative to the training "
                "data. Double-check site extent and FSI area inputs — the model was not "
                "trained on many examples in this range."
            )
        if district not in centroids:
            st.warning(f"{district} has very few training examples — treat this prediction with extra caution.")

        with st.expander("See the full feature row sent to the model"):
            st.dataframe(feature_row.T.rename(columns={0: "value"}))
