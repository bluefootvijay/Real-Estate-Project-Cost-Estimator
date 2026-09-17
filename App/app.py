"""
Home page — Real Estate Project Cost Intelligence (Tamil Nadu, India)

Renders the editorial mockup design (serif headline, muted-blue accent,
landscape positioning banner, three-column content row, footer) using
CSS injected via st.markdown(unsafe_allow_html=True).

IMPORTANT — a Streamlit/Markdown gotcha that broke the first version of
this file: CommonMark (the markdown dialect Streamlit uses) treats a
blank line INSIDE a raw HTML block as the end of that block — everything
after gets parsed as normal markdown text instead of HTML, and 4+ spaces
of leading indentation on any line triggers a literal code block too.
Since this file's HTML/CSS strings live inside an indented function body,
both traps are easy to hit by accident. `_flatten()` below strips all
per-line indentation and blank lines before anything is handed to
st.markdown, and the whole page is built as ONE markdown call so there is
only a single place this can go wrong.

Real numbers (row count, district count) are pulled live from
utils.data_loader so this page can never drift from the actual dataset.
The model's R² and median APE are fixed evaluation results from
04_TNRERA_MODELLING.ipynb — not derivable from the raw CSV at runtime —
so they're set as constants, matching MEDIAN_APE on the Price Predictor page.
"""

import base64
import sys
from pathlib import Path

import streamlit as st

sys.path.append(str(Path(__file__).resolve().parent))

from utils.data_loader import load_historical_data

MODEL_R2 = 0.30
MEDIAN_APE = 0.244

ASSETS_DIR = Path(__file__).resolve().parent / "assets"
MAP_IMAGE_PATH = ASSETS_DIR / "tn_map_blended.webp"

st.set_page_config(
    page_title="Real Estate Project Cost Intelligence — Tamil Nadu, India",
    page_icon="🗺️",
    layout="wide",
)


def _flatten(html: str) -> str:
    """Strip per-line indentation and blank lines from an HTML/CSS block.

    Prevents Markdown from (a) treating indented lines as a literal code
    block, and (b) ending raw-HTML-block parsing early at a blank line —
    both of which silently break unsafe_allow_html content. See module
    docstring.
    """
    return "\n".join(line.strip() for line in html.strip().splitlines() if line.strip())


@st.cache_data
def _map_image_b64() -> str | None:
    """Base64-encode the recolored district map once, for inline embedding."""
    if not MAP_IMAGE_PATH.exists():
        return None
    return base64.b64encode(MAP_IMAGE_PATH.read_bytes()).decode()


df = load_historical_data()
total_filings = len(df)
total_districts = df["Districts"].nunique()

map_b64 = _map_image_b64()
if map_b64 is None:
    st.warning(
        f"Map asset not found at {MAP_IMAGE_PATH}. "
        "Place tn_map_blended.webp in the App/assets/ folder — see README."
    )
map_img_tag = (
    f'<img src="data:image/webp;base64,{map_b64}" alt="Tamil Nadu district road network">'
    if map_b64
    else ""
)

CSS = _flatten(
    """
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,300;9..144,500;9..144,600&family=Inter:wght@400;500;600&display=swap" rel="stylesheet">
    <style>
    :root{
    --paper:#f6f2e9; --ink:#17160f; --ink-soft:#5b5848; --accent:#3c5f8a; --line:#c9c2ae;
    }
    @media (prefers-color-scheme: dark){
    :root:not([data-theme="light"]){
    --paper:#15140f; --ink:#f2efe4; --ink-soft:#a9a48d; --line:#3a3728; --accent:#7fa3d1;
    }
    }
    #MainMenu, header[data-testid="stHeader"], footer{ visibility:hidden; height:0; }
    .stApp{ background:var(--paper); }
    .block-container{ max-width:1180px; padding-top:2.5rem; padding-bottom:2rem; }
    .rec-title{ font-family:'Fraunces', serif; font-weight:600; font-size:44px; letter-spacing:-0.5px; color:var(--ink); margin:0; }
    .rec-sub{ font-family:'Fraunces', serif; font-style:italic; font-weight:300; font-size:14px; color:var(--ink-soft); margin-top:4px; }
    .rec-nav{ text-align:right; }
    .rec-nav span{ font-family:'Inter', sans-serif; font-size:11px; font-weight:600; letter-spacing:1.2px; color:var(--ink-soft); margin-left:28px; }
    .rec-nav span.current{ color:var(--ink); }
    .rec-rule{ height:2px; background:var(--accent); border:none; margin:22px 0 40px; }
    .rec-positioning{ display:flex; align-items:center; gap:32px; padding:20px 26px; margin-bottom:40px; border-left:3px solid var(--accent); background:rgba(60,95,138,0.055); }
    .rec-positioning .who{ flex:0 0 auto; font-family:'Inter', sans-serif; font-size:10.5px; font-weight:600; letter-spacing:0.8px; line-height:1.6; color:var(--accent); white-space:nowrap; }
    .rec-positioning p{ flex:1 1 auto; font-family:'Fraunces', serif; font-style:italic; font-weight:300; font-size:15.5px; line-height:1.6; color:var(--ink); margin:0; }
    .rec-content{ display:grid; grid-template-columns:1fr 1.3fr 0.9fr; gap:40px; align-items:start; }
    .rec-copy p{ font-family:'Inter', sans-serif; font-size:14px; line-height:1.75; color:var(--ink-soft); margin:0 0 16px; }
    .rec-copy strong{ color:var(--ink); font-weight:600; }
    .rec-map{ display:flex; justify-content:center; }
    .rec-map img{ width:100%; max-width:380px; opacity:0.94; }
    .rec-stats{ display:flex; flex-direction:column; align-items:flex-end; text-align:right; gap:26px; }
    .rec-stats .num{ font-family:'Fraunces', serif; font-weight:500; font-size:34px; line-height:1; color:var(--accent); }
    .rec-stats .cap{ font-family:'Inter', sans-serif; font-size:10.5px; letter-spacing:0.8px; color:var(--ink-soft); margin-top:4px; }
    .rec-footer{ margin-top:80px; padding-top:20px; border-top:1px solid var(--line); display:flex; flex-direction:column; align-items:flex-end; text-align:right; gap:4px; font-family:'Inter', sans-serif; font-size:11px; color:var(--ink-soft); }
    .rec-footer a{ color:var(--ink-soft); }
    </style>
    """
)

BODY = _flatten(
    f"""
    <div style="display:flex; justify-content:space-between; align-items:flex-end;">
    <div>
    <p class="rec-title">REAL ESTATE PROJECT COST INTELLIGENCE</p>
    <div class="rec-sub">Tamil Nadu, India</div>
    </div>
    <div class="rec-nav">
    <span class="current">THE MODEL</span>
    <span>DATA ANALYSIS</span>
    <span>ABOUT</span>
    </div>
    </div>
    <hr class="rec-rule">
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
    <div class="rec-footer">
    <div>Real Estate Project Cost Intelligence — Built by Vijaykumar · <a href="https://github.com/bluefootvijay/Real-Estate-Project-Cost-Estimator">GitHub</a></div>
    <div>Data: Tamil Nadu RERA project registration filings</div>
    </div>
    """
)

st.markdown(CSS + BODY, unsafe_allow_html=True)
