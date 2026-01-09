import streamlit as st
import pandas as pd
from datetime import date, timedelta

# --- PAGE CONFIGURATION ---
st.set_page_config(page_title="Astute Retirement Mindset", layout="centered")

# --- CUSTOM STYLING ---
st.markdown(
    """
    <style>
    .stApp { background-color: #FFFFFF !important; }
    
    .block-container {
        border: 4px solid #00008B; 
        padding: 40px !important;
        background-color: #FFF0DB !important; 
        margin-top: 50px !important; 
        margin-bottom: 50px !important;
        border-radius: 15px;
        max-width: 800px !important;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
    }
    
    h1, h2, h3, h4, h5, h6, .stSubheader { color: #00008B !important; }

    /* Center and format table */
    thead tr th:first-child { display:none; }
    tbody tr th { display:none; }
    .stTable td, .stTable th { text-align: center !important; }

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

# --- INPUT SECTION ---
st.markdown("### 📋 Personal & Financial Details")

dob = st.date_input(
    "Date of Birth", 
    value=date(1975, 1, 1), 
    min_value=date(1955, 1, 1), 
    max_value=date(2000, 12, 31),
    format="DD/MM/YYYY"
)

target_retirement_date = st.date_input("Target Retirement Date", value=date(2035, 1, 1), format="DD/MM/YYYY")

current_pot = st.slider("Current Private Pension Pot (£)", 0, 3500000, 500000, step=5000, format="£%d")
st.markdown(f"**Current Pot Selected: £{current_pot:,}**")

annual_contribution = st.slider("Annual Contribution (Pre-Retirement) (£)", 0, 100000, 10000, step=500, format="£%d")
st.markdown(f"**Annual Contribution Selected: £{annual_contribution:,}**")

monthly_drawdown_goal = st.slider("Desired Monthly Withdrawal (£)", 0, 20000, 3000, step=100, format="£%d")
st.markdown(f"**Monthly Withdrawal Selected: £{monthly_drawdown_goal:,}**")

st.info(f"Calculated Fixed Yearly Drawdown: £{monthly_drawdown_goal * 12:,.0f}")

take_lump_sum = st.selectbox("Take 25% Tax-Free Lump Sum?", ["N", "Y"])
lump_sum_amount = 0.0
if take_lump_sum == "Y":
    max_ls = min(current_pot * 0.25, 268275.0)
    lump_sum_amount = st.number_input(f"Lump Sum Amount (Max £{max_ls:,.0f})", value=max_ls, min_value=0.0, max_value=max_ls)

state_pension_end_date = st.date_input("Date UK State Pension expected to end (Optional)", value=None, format="DD/MM/YYYY")

with st.expander("Growth & Inflation Settings"):
    cagr = st.number_input("Pension Pot CAGR (%)", value=5.0) / 100
    inflation = st.number_input("Expected Inflation Rate (%)", value=4.0) / 100
    debasement = st.number_input("Currency Debasement Rate (%)", value=5.0) / 100

# --- CALCULATIONS ---

def calculate_age(birth, current):
    return current.year - birth.year - ((current.month, current.day) < (birth.month, birth.day))

# UK State Pension Age Logic
if dob.year < 1960: spa_age = 66
elif dob.year < 1977: spa_age = 67
else: spa_age =
