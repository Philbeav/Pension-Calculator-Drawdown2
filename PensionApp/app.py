import streamlit as st
import pandas as pd
from datetime import date

# --- 1. PAGE CONFIGURATION ---
st.set_page_config(page_title="Astute Retirement Mindset", layout="centered")

# --- 2. CSS STYLING ---
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
        margin-bottom: 50px !important;
        max-width: 800px !important;
    }

    h1, h2, h3, .stSubheader { color: #00008B !important; }
    
    .stTable td, .stTable th { text-align: center !important; }
    thead tr th:first-child { display:none !important; }
    tbody tr th { display:none !important; }
    
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
st.markdown("### 📋 Personal & Financial Details")

# Set range from 1955 to 2010
dob = st.date_input(
    "Date of Birth", 
    value=date(1975, 1, 1), 
    min_value=date(1955, 1, 1), 
    max_value=date(2010, 12, 31),
    format="DD/MM/YYYY"
)

target_retirement_date = st.date_input("Target Retirement Date", value=date(2035, 1, 1), format="DD/MM/YYYY")

current_pot = st.slider("Current Private Pension Pot (£)", 0, 3500000, 500000, step=5000)
st.markdown(f"**Selected Pot: £{current_pot:,}**")

annual_contribution = st.slider("Annual Contribution (£)", 0, 100000, 10000, step=500)
monthly_drawdown = st.slider("Desired Monthly Withdrawal (£)", 0, 20000, 3000, step=100)

st.info(f"Fixed Yearly Drawdown: £{monthly_drawdown * 12:,.0f}")

take_lump_sum = st.selectbox("Take 25% Tax-Free Lump Sum?", ["N", "Y"])
lump_sum_val = 0.0
if take_lump_sum == "Y":
    max_ls = min(current_pot * 0.25, 268275.0)
    lump_sum_val = st.number_input(f"Lump Sum Amount (Max £{max_ls:,.0f})", value=
