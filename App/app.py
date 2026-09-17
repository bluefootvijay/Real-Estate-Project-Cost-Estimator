"""
About page — Real Estate Project Cost Intelligence (Tamil Nadu, India)

This is the site's root page. It's the "About" page in the nav (positioning
statement + project framing) — the Price Predictor lives at pages/1_The_Model.py
and the EDA charts live at pages/2_Data_Analysis.py.
"""

import sys
from pathlib import Path

import streamlit as st

sys.path.append(str(Path(__file__).resolve().parent))

from utils.data_loader import load_historical_data
from utils.theme import CSS, map_image_b64, render_footer, render_header

MODEL_R2 = 0.30
MEDIAN_APE = 0.244

st.set_page_config(
    page_title="Real Estate Project Cost Intelligence — Tamil Nadu, India",
    page_icon="🗺️",
    layout="wide",
)


def _flatten(html: str) -> str:
    return "\n".join(line.strip() for line in html.strip().splitlines() if line.strip())


df = load_historical_data()
total_filings = len(df)
total_districts = df["Districts"].nunique()

map_b64 = map_image_b64()
if map_b64 is None:
    st.warning("Map asset not found — place tn_map_blended.webp in App/assets/.")
map_img_tag = (
    f'<img src="data:image/webp;base64,{map_b64}" alt="Tamil Nadu district road network">'
    if map_b64
    else ""
)

BODY = _flatten(
    f"""
    <div class="rec-positioning">
    <div class="who">ARCHITECT<br>DATA SCIENTIST</div>
    <p>Years of practicing architecture mean State Development Regulations, High Rise Building/Non High Rise Building tiers, and FSI rules aren't reference material — they're fluent. That's the lens this portfolio brings to spatial data science, GIS &amp; urban analytics, and AVM work.</p>
    </div>
    <div class="rec-content">
    <div class="rec-copy">
    <p>Tamil Nadu's registered real estate market spans {total_districts} districts under RERA disclosure, from dense urban Chennai filings to smaller district-level developments across the state.</p>
    <p>This project parses every RERA project registration filed between <strong>2024 and 2026</strong>, cross-referencing <strong>TNCDBR-2019</strong> bylaw ceilings — FSI, Parking — against what developers actually built and declared.</p>
    <p>Use it to understand where project cost per sqft clusters, where the model's confidence holds, and where the data simply runs out — TNRERA filings don't capture finish quality, materials, or amenities: the details that separate a luxury project from a budget one at the same coordinates.</p>
    </div>
    <div class="rec-map">{map_img_tag}</div>
    <div class="rec-stats">
    <div class="stat"><div class="num">{total_filings}</div><div class="cap">RERA FILINGS PARSED</div></div>
    <div class="stat"><div class="num">{total_districts}</div><div class="cap">DISTRICTS COVERED</div></div>
    <div class="stat"><div class="num">{MODEL_R2:.2f}</div><div class="cap">MODEL R² SCORE</div></div>
    <div class="stat"><div class="num">{MEDIAN_APE:.0%}</div><div class="cap">MEDIAN ABSOLUTE % ERROR</div></div>
    </div>
    </div>
    """
)

st.markdown(CSS + render_header("ABOUT") + BODY + render_footer(), unsafe_allow_html=True)
