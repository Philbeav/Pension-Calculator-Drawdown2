import streamlit as st
import pandas as pd
from datetime import date, timedelta

# --- PAGE CONFIGURATION ---
st.set_page_config(page_title="Astute Retirement Mindset", layout="centered")

# --- CUSTOM STYLING (Dark Blue Titles, Cream Background, Centered Table) ---
st.markdown(
    """
    <style>
    /* Main Background - Cream */
    .stApp {
        background-color: #FFFDD0; 
    }
    
    /* Content Container with Blue Border */
    .block-container {
        border: 4px solid #00008B; 
        padding: 30px !important;
        background-color: #FFFDD0; 
        margin-top: 50px !important; 
        margin-bottom: 40px !important;
        border-radius: 10px;
        max-width: 850px !important;
    }
    
    /* Dark Blue Headlines and Subheaders */
    h1, h2, h3, h4, h5, h6, .stSubheader {
        color: #00008B !important;
        font-family: 'Helvetica', sans-serif;
    }

    /* CSS TO HIDE THE INDEX COLUMN AND CENTER DATA */
    /* This targets the first column (the index) and hides it */
    thead tr th:first-child { display:none; }
    tbody tr th { display:none; }
    
    /* Center all remaining headers and cells */
    .stTable td, .stTable th {
        text-align: center !important;
        color: #333;
    }

    /* Input highlights in Yellow */
    div[data-baseweb="input"], div[data-baseweb="select"], div[data-baseweb="slider"] {
        background-color: #FFFFE0 !important; 
    }

    /* Hide default Streamlit header */
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

current_pot = st.slider("Current Private Pension Pot (£)", 0, 2000000, 500000, step=1000)
annual_contribution = st.slider("Annual Contribution (Pre-Retirement) (£)", 0, 100000, 10000, step=500)
monthly_drawdown_goal = st.slider("Desired Monthly Withdrawal (£)", 0, 20000, 3000, step=100)

st.info(f"Fixed Yearly Drawdown: £{monthly_drawdown_goal * 12:,.0f}")

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

def calculate_age(birth, current):
    return current.year - birth.year - ((current.month, current.day) < (birth.month, birth.day))

if dob.year < 1960: spa_age = 66
elif dob.year < 1977: spa_age = 67
else: spa_age = 68
spa_date = date(dob.year + spa_age, dob.month, dob.day)

# 1. Accumulation Phase
years_to_retire = (target_retirement_date - date.today()).days / 365.25
pot_at_retirement = current_pot
if years_to_retire > 0:
    for _ in range(max(0, int(years_to_retire * 12))):
        pot_at_retirement = pot_at_retirement * (1 + cagr)**(1/12) + (annual_contribution / 12)

# 2. Lump Sum
pot_after_ls = pot_at_retirement - lump_sum_amount

st.markdown("---")
col1, col2 = st.columns(2)
col1.metric("Tax Free Amount", f
