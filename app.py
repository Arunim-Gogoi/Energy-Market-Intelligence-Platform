import streamlit as st
import pandas as pd
import plotly.express as px
from dotenv import load_dotenv
from data_loader import load_energy_data
from rag_utils import build_index, answer_question

load_dotenv()

st.set_page_config(page_title="Energy Market Intelligence", layout="wide", page_icon="⚡")

st.markdown(
    """
    <style>
    .stApp { background-color: #0a1929; color: #e0f7fa; }
    h1, h2, h3 { color: #00e5ff; }
    </style>
    """,
    unsafe_allow_html=True,
)

st.title("⚡ Energy Market Intelligence Platform")
st.caption(
    "Analyst-style dashboard: oil, renewables & demand trends, "
    "plus a RAG assistant over energy market reports."
)

df = load_energy_data()

countries = sorted(df["country"].dropna().unique())
default_idx = countries.index("India") if "India" in countries else 0
country = st.sidebar.selectbox("Country", countries, index=default_idx)
year_min, year_max = int(df.year.min()), int(df.year.max())
year_range = st.sidebar.slider("Year range", year_min, year_max, (2000, year_max))

sub = df[(df.country == country) & (df.year.between(*year_range))].sort_values("year")

col1, col2 = st.columns(2)

with col1:
    st.subheader("Oil production (TWh)")
    st.plotly_chart(px.line(sub, x="year", y="oil_production"), use_container_width=True)

with col2:
    st.subheader("Renewables share of electricity (%)")
    st.plotly_chart(px.line(sub, x="year", y="renewables_share_elec"), use_container_width=True)

st.subheader("Primary energy consumption mix (latest available year)")
sources = ["coal_consumption", "oil_consumption", "gas_consumption",
           "renewables_consumption", "nuclear_consumption"]
present = [s for s in sources if s in sub.columns]
mix = sub.dropna(subset=present, how="all")
if not mix.empty:
    latest = mix[mix.year == mix.year.max()]
    melt = latest.melt(id_vars="year", value_vars=present, var_name="source", value_name="TWh").dropna()
    if not melt.empty:
        st.plotly_chart(px.bar(melt, x="source", y="TWh"), use_container_width=True)
    else:
        st.caption("No consumption-mix data for the latest year in range.")
else:
    st.caption("No consumption-mix data available for this country/range.")

st.subheader("📊 Auto-generated insight")

def first_last(colname):
    """First and last non-null (year, value) pair for a column within the current range."""
    valid = sub.dropna(subset=[colname])
    if len(valid) < 2:
        return None
    return valid.iloc[0], valid.iloc[-1]

def pct_change(a, b):
    if pd.isna(a) or pd.isna(b) or a == 0:
        return None
    return round((b - a) / a * 100, 1)

oil_pair = first_last("oil_production")
if oil_pair:
    o_first, o_last = oil_pair
    oil_chg = pct_change(o_first["oil_production"], o_last["oil_production"])
    oil_txt = (
        f"{country}'s oil production changed by **{oil_chg}%** "
        f"between {int(o_first.year)} and {int(o_last.year)}"
        if oil_chg is not None
        else f"oil production data for {country} doesn't support a clean % change in this range"
    )
else:
    oil_txt = f"no oil production data for {country} in this range"

ren_pair = first_last("renewables_share_elec")
if ren_pair:
    r_first, r_last = ren_pair
    ren_txt = (
        f"Renewables' share of electricity moved from {r_first['renewables_share_elec']:.1f}% "
        f"({int(r_first.year)}) to {r_last['renewables_share_elec']:.1f}% ({int(r_last.year)})."
    )
else:
    ren_txt = "No renewables-share data available for this range."

st.write(f"{oil_txt.capitalize()}. {ren_txt}")

st.subheader("🔎 Ask the Energy Market Assistant (RAG)")
st.caption("Answers are grounded in the reports in /docs — swap in real ones anytime.")

if "index" not in st.session_state:
    with st.spinner("Building knowledge index..."):
        st.session_state.index = build_index("docs")

q = st.text_input("e.g. 'What's driving renewable capacity growth right now?'")
if q:
    with st.spinner("Thinking..."):
        answer, used_sources = answer_question(q, st.session_state.index)
    st.write(answer)
    if used_sources:
        with st.expander("Sources"):
            for s in used_sources:
                st.write(f"- {s}")
