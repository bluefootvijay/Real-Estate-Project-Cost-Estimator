"""
Data Analysis page — three EDA views rebuilt from the live dataset.

Corresponds to slides 3 ("The Data: TNRERA Project Filings"), 4 ("What's
Being Built"), and 5 ("Where the Money Moves") of the EDA portfolio deck —
selected and requested by name. Charts are recomputed from the actual
historical CSV each run (cached via load_historical_data), not embedded
slide images, so the numbers can't drift from the real data and the
styling matches the rest of the site instead of matplotlib's defaults.

Note: the original deck's slide 3 cites 1,030 raw PDF-parsed filings; the
modelling dataset used everywhere else in this app (and shown here) is the
943-row cleaned version, so the filing count below will differ from the
deck on purpose.
"""

import sys
from pathlib import Path

import plotly.graph_objects as go
import streamlit as st

sys.path.append(str(Path(__file__).resolve().parent.parent))

from utils.data_loader import load_historical_data
from utils.theme import CHART_INK, CHART_PRIMARY, CHART_SECONDARY, CSS, render_footer, render_header

st.set_page_config(page_title="Data Analysis — Real Estate Cost Intelligence", page_icon="📊", layout="wide")

st.markdown(CSS + render_header("DATA ANALYSIS"), unsafe_allow_html=True)
st.markdown(
    '<p class="rec-page-title">Three views into the underlying TNRERA dataset — '
    'filing volume, what gets built, and where project cost concentrates.</p>',
    unsafe_allow_html=True,
)

df = load_historical_data()
COST_COL = "FE_Total_Project_Cost_per_Sqft"


def _style(fig, height=380, showlegend=False):
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Inter, sans-serif", color="#5b5848", size=12),
        margin=dict(l=10, r=10, t=40, b=10),
        height=height,
        showlegend=showlegend,
    )
    fig.update_xaxes(showgrid=True, gridcolor="#e4ddce", zeroline=False)
    fig.update_yaxes(showgrid=False, zeroline=False)
    return fig


# ------------------------------------------------------------------
# Section 1 — The Data: TNRERA Project Filings
# ------------------------------------------------------------------
st.markdown('<div class="rec-section"><h2>The Data: TNRERA Project Filings</h2></div>', unsafe_allow_html=True)
c1, c2 = st.columns(2)

with c1:
    top_districts = df["Districts"].value_counts().head(10).sort_values()
    fig = go.Figure(go.Bar(x=top_districts.values, y=top_districts.index, orientation="h", marker_color=CHART_PRIMARY))
    fig.update_layout(title="Top 10 districts by filing count")
    st.plotly_chart(_style(fig), use_container_width=True)

with c2:
    missing_pct = (df.isna().mean() * 100).sort_values(ascending=False)
    missing_pct = missing_pct[missing_pct > 0].head(10).sort_values()
    if len(missing_pct):
        fig = go.Figure(go.Bar(x=missing_pct.values, y=missing_pct.index, orientation="h", marker_color=CHART_SECONDARY))
        fig.update_layout(title="Missingness by column (%)")
        st.plotly_chart(_style(fig), use_container_width=True)
    else:
        st.caption("No missing values in the modelling dataset — gaps were resolved upstream.")

top3 = df["Districts"].value_counts().head(3)
st.markdown(
    f'<p class="rec-caption">{len(df)} TNRERA filings in the modelling dataset. '
    f'{top3.index[0]}, {top3.index[1]}, and {top3.index[2]} account for the bulk of registrations. '
    "Cost and site fields are essentially complete; a handful of ancillary FSI and "
    "unit-count fields have real gaps — flagged and handled explicitly rather than "
    "silently dropped or imputed blind.</p>",
    unsafe_allow_html=True,
)

# ------------------------------------------------------------------
# Section 2 — What's Being Built
# ------------------------------------------------------------------
st.markdown('<div class="rec-section"><h2>What\'s Being Built</h2></div>', unsafe_allow_html=True)
c1, c2 = st.columns(2)

with c1:
    usage_counts = df["Usage"].value_counts().sort_values()
    fig = go.Figure(go.Bar(x=usage_counts.values, y=usage_counts.index, orientation="h", marker_color=CHART_SECONDARY))
    fig.update_layout(title="Building usage count")
    st.plotly_chart(_style(fig), use_container_width=True)

with c2:
    type_counts = df["Type_of_Building"].value_counts().sort_values()
    fig = go.Figure(go.Bar(x=type_counts.values, y=type_counts.index, orientation="h", marker_color=CHART_PRIMARY))
    fig.update_layout(title="Type of building")
    st.plotly_chart(_style(fig), use_container_width=True)

nhrb_n = int((df["Type_of_Building"] == "Non-High Rise Building (NHRB)").sum())
hrb_n = int((df["Type_of_Building"] == "High Rise Building (HRB)").sum())
ratio_text = f"roughly {nhrb_n / hrb_n:.1f} to 1" if hrb_n else "overwhelmingly"
st.markdown(
    f'<p class="rec-caption">Residential dominates the filing pool, with commercial and '
    "mixed-development projects a much smaller share. By building form, Non-High Rise "
    f"(NHRB) construction outnumbers High Rise (HRB) {ratio_text} — this market is still "
    "overwhelmingly low- and mid-rise, with high-rises concentrated in a smaller, denser "
    "segment. That split matters downstream since HRB and NHRB projects are governed by "
    "different FSI rules.</p>",
    unsafe_allow_html=True,
)

# ------------------------------------------------------------------
# Section 3 — Where the Money Moves
# ------------------------------------------------------------------
st.markdown('<div class="rec-section"><h2>Where the Money Moves</h2></div>', unsafe_allow_html=True)
c1, c2 = st.columns([1, 1.3])

with c1:
    for building_type, color in [
        ("Non-High Rise Building (NHRB)", CHART_PRIMARY),
        ("High Rise Building (HRB)", CHART_SECONDARY),
    ]:
        subset = df.loc[df["Type_of_Building"] == building_type, COST_COL].dropna()
        subset = subset[subset > 0]
        if not len(subset):
            continue
        fig = go.Figure(go.Histogram(x=subset, marker_color=color, opacity=0.85))
        fig.update_xaxes(type="log", title="Cost per sqft (₹)")
        fig.add_vline(x=subset.mean(), line_dash="dot", line_color=CHART_INK,
                       annotation_text=f"Mean ₹{subset.mean():,.0f}", annotation_font_size=10)
        fig.update_layout(title=f"{building_type}  (n={len(subset)})")
        st.plotly_chart(_style(fig, height=220), use_container_width=True)

with c2:
    district_counts = df["Districts"].value_counts()
    eligible = district_counts[district_counts >= 5].index
    plot_df = df[df["Districts"].isin(eligible) & df[COST_COL].notna() & (df[COST_COL] > 0)]

    fig = go.Figure()
    for building_type, color in [
        ("High Rise Building (HRB)", CHART_PRIMARY),
        ("Non-High Rise Building (NHRB)", CHART_SECONDARY),
    ]:
        sub = plot_df[plot_df["Type_of_Building"] == building_type]
        fig.add_trace(go.Box(x=sub["Districts"], y=sub[COST_COL], name=building_type, marker_color=color))
    fig.update_yaxes(type="log", title="Cost per sqft (₹)")
    fig.update_layout(title="Cost per sqft by district, split by building type (n≥5)", boxmode="group")
    fig.update_layout(legend=dict(orientation="h", y=-0.22))
    st.plotly_chart(_style(fig, height=460, showlegend=True), use_container_width=True)

st.markdown(
    '<p class="rec-caption">Total project cost per sqft varies sharply by district and '
    "building type. Chennai carries the widest spread — and the extreme outliers — while "
    "smaller districts cluster tighter around lower medians. Building type shifts the "
    "distribution too: NHRB and HRB projects in the same district don't price the same.</p>",
    unsafe_allow_html=True,
)

st.markdown(render_footer(), unsafe_allow_html=True)
