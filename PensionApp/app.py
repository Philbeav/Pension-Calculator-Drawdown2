import streamlit as st
import pandas as pd
from datetime import date

# --- 1. PAGE CONFIGURATION ---
st.set_page_config(page_title="Astute Retirement Mindset", layout="centered")

# --- 2. ROBUST CSS STYLING ---
st.markdown(
    """
    <style>
    .stApp { background-color: #FFFFFF !important; }
    
    .block-container {
        background-color: #FFF0DB !important;
        border: 5px solid #00008B !important;
        padding: 40px !important;
        border-radius: 20px !important;
        margin-top: 50px !important;
        max-width: 900px !important;
    }

    h1, h2, h3, .stSubheader { color: #00008B !important; }
    
    /* Hide Table Index */
    thead tr th:first-child { display:none !important; }
    tbody tr th { display:none !important; }
    .stTable td { text-align: center !important; }

    div[data-baseweb="input"], div[data-baseweb="select"], div[data-baseweb="slider"] {
        background-color: #FFFFE0 !important; 
    }
    header {visibility: hidden;}
    </style>
    """,
    unsafe_allow_html=True
)

st.title("Astute Retirement Mindset")
st.subheader("Pension Drawdown Calculator")

# --- 3. INPUTS ---
# Range strictly set from 1955 to 2010
dob = st.date_input(
    "Date of Birth", 
    value=date(1975, 1, 1), 
    min_value=date(1955, 1, 1), 
    max_value=date(2010, 12, 31),
    format="DD/MM/YYYY"
)

target_retirement_date = st.date_input("Target Retirement Date", value=date(2035, 1, 1), format="DD/MM/YYYY")

current_pot = st.slider("Current Private Pension Pot (£)", 0, 3500000, 500000, step=5000)
st.write(f"**Selected Pot: £{current_pot:,}**")

annual_contribution = st.slider("Annual Contribution (£)", 0, 100000, 10000, step=500)
monthly_drawdown = st.slider("Desired Monthly Withdrawal (£)", 0, 20000, 3000, step=100)
