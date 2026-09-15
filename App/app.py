import streamlit as st

st.set_page_config(
    page_title="TNRERA AVM — Tamil Nadu Real Estate Valuation",
    page_icon="🏗️",
    layout="wide",
)

st.title("🏗️ Tamil Nadu Real Estate AVM")
st.caption("An automated valuation model built on 943 TNRERA-registered projects")

st.markdown(
    """
    This tool predicts construction cost per square foot for a real estate
    project in Tamil Nadu, using project characteristics — location, site
    extent, permitted FSI, dwelling units, and parking — as inputs.

    **Use the sidebar to navigate:**
    - **Price Predictor** — enter a hypothetical project's details and get a
      predicted cost/sqft, with the model's honest uncertainty band.
    - **Model Analysis** — see how the model was built: which of three
      algorithms was chosen and why, where the data comes from, and where
      its limits are.

    ---

    ### A note on what this model can and can't tell you

    The model explains roughly **30% of the variance** in project cost per
    square foot (R² ≈ 0.30 on a log scale). That's not a bug to be fixed —
    it reflects a real ceiling in what TNRERA filings record. Two projects
    a few hundred meters apart can carry very different price points for
    reasons the dataset simply doesn't capture: finish quality, amenities,
    brand premium, micro-location factors. Treat every prediction here as
    a **data-driven starting point**, not a valuation.
    """
)

st.info(
    "Built from Tamil Nadu RERA project registration filings. "
    "See the Model Analysis page for the full comparison of algorithms tried.",
    icon="ℹ️",
)
