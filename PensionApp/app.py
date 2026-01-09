import streamlit as st
import pandas as pd
from datetime import date, timedelta

# --- PAGE CONFIGURATION ---
st.set_page_config(page_title="Astute Retirement Mindset", layout="centered")

# --- CUSTOM STYLING (Fixed Top Border & Refined Layout) ---
st.markdown(
    """
    <style>
    /* Main Background */
    .stApp {
        background-color: #FDF5E6; /* Old Lace / Parchment */
    }
    
    /* Narrow Content Container with Blue Border */
    /* Added margin-top to ensure the top border isn't cut off */
    .block-container {
        border: 4px solid #00008B; 
        padding: 30px !important;
        background-color: #F5F5DC; 
        margin-top: 40px !important; 
        margin-bottom: 40px !important;
        border-radius: 10px;
        max-width: 800px !important;
    }
    
    /* Center table headers and cells */
    th, td {
        text-align: center !important;
    }

    /* Input highlights in Yellow */
    div[data-baseweb="input"], div[data-baseweb="select"], div[data-baseweb="slider"] {
        background-color: #FFFFE0 !important; 
    }

    /* Remove the default streamlit header padding to help border visibility */
    header {visibility: hidden;}
    </style>
    """,
    unsafe_allow_html=True
)

st.title("Astute Retirement Mindset")
st.subheader("Pension Drawdown Calculator")

# --- INPUT SECTION ---
st.markdown("### 📋 Personal & Financial Details")

# Date of Birth with expanded range: 1955 to 2000
dob = st.date_input(
    "Date of Birth", 
    value=date(1975, 1, 1), 
    min_value=date(1955, 1, 1), 
    max_value=date(2000, 12, 31),
    format="DD/MM/YYYY"
)

target_retirement_date = st.date_input("Target Retirement Date", value=date(2035, 1, 1), format="DD/MM/YYYY")

current_pot = st.slider("Current Private Pension Pot (£)", 0, 2000000, 500000, step=1000)
annual_contribution = st.slider("Annual Contribution (Pre-Retirement) (£)", 0, 100000, 10000, step=500)
monthly_drawdown_goal = st.slider("Desired Monthly Withdrawal (£)", 0, 20000, 3000, step=100)

st.info(f"Yearly Drawdown: £{monthly_drawdown_goal * 12:,.0f}")

take_lump_sum = st.selectbox("Take 25% Tax-Free Lump Sum?", ["N", "Y"])
lump_sum_amount = 0.0
if take_lump_sum == "Y":
    max_ls = min(current_pot * 0.25, 268275.0)
    lump_sum_amount = st.number_input(f"Lump Sum Amount (Max £{max_ls:,.0f})", value=max_ls)

state_pension_end_date = st.date_input("Date UK State Pension expected to end (Optional)", value=None, format="DD/MM/YYYY")

# --- ADVANCED SETTINGS ---
with st.expander("Growth & Inflation Settings"):
    cagr = st.number_input("Pension Pot CAGR (%)", value=5.0) / 100
    inflation = st.number_input("Expected Inflation Rate (%)", value=4.0) / 100
    debasement = st.number_input("Currency Debasement Rate (%)", value=5.0) / 100

# --- CALCULATIONS ---
