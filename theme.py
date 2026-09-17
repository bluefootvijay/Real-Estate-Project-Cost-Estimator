"""
Shared design system for the Real Estate Project Cost Intelligence app.

Every page (About, The Model, Data Analysis) imports CSS / render_header /
render_footer from here instead of carrying its own copy of the same ~30
CSS rules. One shared source also means the Markdown blank-line/indentation
bug (see flatten()) only has one place to reappear, not three.

Nav routing: this app uses Streamlit's classic pages/ folder, where each
page gets a URL slug = its filename with the leading "N_" stripped
(underscores kept). pages/1_The_Model.py -> "The_Model". Plain <a href>
tags to those slugs are enough for navigation — no st.page_link needed —
which keeps the nav bar's exact HTML/CSS under our control.
"""

import base64
from pathlib import Path

ASSETS_DIR = Path(__file__).resolve().parent.parent / "assets"
MAP_IMAGE_PATH = ASSETS_DIR / "tn_map_blended.webp"

NAV_ITEMS = [
    ("THE MODEL", "The_Model"),
    ("DATA ANALYSIS", "Data_Analysis"),
    ("ABOUT", ""),
]


def flatten(html: str) -> str:
    """Strip per-line indentation and blank lines from an HTML/CSS block.

    Markdown (CommonMark, which Streamlit uses) ends raw-HTML-block parsing
    at the first blank line inside the block, and treats 4+ leading spaces
    on any line as a literal code block. Both silently break
    unsafe_allow_html content — this is the fix, applied once here so every
    page benefits.
    """
    return "\n".join(line.strip() for line in html.strip().splitlines() if line.strip())


CSS = flatten(
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
    section[data-testid="stSidebar"]{ display:none; }
    .stApp{ background:var(--paper); }
    .block-container{ max-width:1180px; padding-top:2.5rem; padding-bottom:2rem; }
    .rec-title{ font-family:'Fraunces', serif; font-weight:600; font-size:44px; letter-spacing:-0.5px; color:var(--ink); margin:0; }
    .rec-sub{ font-family:'Fraunces', serif; font-style:italic; font-weight:300; font-size:14px; color:var(--ink-soft); margin-top:4px; }
    .rec-nav{ text-align:right; }
    .rec-nav span{ font-family:'Inter', sans-serif; font-size:11px; font-weight:600; letter-spacing:1.2px; margin-left:28px; }
    .rec-nav a{ text-decoration:none; color:var(--ink-soft); }
    .rec-nav span.current a{ color:var(--ink); }
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
    .rec-section{ margin-bottom:56px; }
    .rec-section h2{ font-family:'Fraunces', serif; font-weight:600; font-size:24px; color:var(--ink); margin:0 0 18px; }
    .rec-caption{ font-family:'Inter', sans-serif; font-size:13.5px; line-height:1.75; color:var(--ink-soft); max-width:110ch; margin:14px 0 0; }
    .rec-page-title{ font-family:'Fraunces', serif; font-weight:500; font-style:italic; font-size:15px; color:var(--ink-soft); margin:0 0 32px; }
    </style>
    """
)


def render_header(current: str) -> str:
    """Header block: title, nav (linking to real page routes), and rule."""
    nav_html = "".join(
        f'<span class="{"current" if label == current else ""}"><a href="{slug}">{label}</a></span>'
        for label, slug in NAV_ITEMS
    )
    return flatten(
        f"""
        <div style="display:flex; justify-content:space-between; align-items:flex-end;">
        <div>
        <p class="rec-title">REAL ESTATE PROJECT COST INTELLIGENCE</p>
        <div class="rec-sub">Tamil Nadu, India</div>
        </div>
        <div class="rec-nav">{nav_html}</div>
        </div>
        <hr class="rec-rule">
        """
    )


def render_footer() -> str:
    return flatten(
        """
        <div class="rec-footer">
        <div>Real Estate Project Cost Intelligence — Built by Vijaykumar · <a href="https://github.com/bluefootvijay/Real-Estate-Project-Cost-Estimator">GitHub</a></div>
        <div>Data: Tamil Nadu RERA project registration filings</div>
        </div>
        """
    )


def map_image_b64() -> str | None:
    """Base64-encode the recolored district map once, for inline embedding."""
    if not MAP_IMAGE_PATH.exists():
        return None
    return base64.b64encode(MAP_IMAGE_PATH.read_bytes()).decode()


# Chart palette — hardcoded hex (not the CSS vars above) because Plotly
# renders to static SVG/canvas and can't read page CSS custom properties.
# Matches the light-mode --accent, plus a warm secondary for two-series
# comparisons, so charts read as part of the same system without leaning
# on blue for every series.
CHART_PRIMARY = "#3c5f8a"
CHART_SECONDARY = "#c17a3c"
CHART_INK = "#17160f"
CHART_INK_SOFT = "#5b5848"
CHART_PAPER = "#f6f2e9"
