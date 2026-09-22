import pandas as pd
import streamlit as st

OWID_URL = "https://raw.githubusercontent.com/owid/energy-data/master/owid-energy-data.csv"


@st.cache_data(show_spinner="Loading OWID energy dataset...")
def load_energy_data() -> pd.DataFrame:
    """Free, no-auth global energy dataset: oil/gas/coal/renewables/demand by country & year."""
    return pd.read_csv(OWID_URL)
