import streamlit as st
import pandas as pd
from datetime import date

# --- 1. PAGE CONFIGURATION ---
st.set_page_config(page_title="Astute Retirement Mindset", layout="centered")

# --- 2. FAILSAFE CUSTOM STYLING ---
st.markdown(
    """
    <style>
    /* Main background White */
    .stApp { background-color: #FFFFFF !important; }
    
    /* App Box Cream with Blue Border */
    [data-testid="stVerticalBlock"] > div:has(div.stTitle) {
        border: 4px solid #00008B; 
        padding: 40px !important;
        background-color: #FFF0DB !important; 
        border-radius: 15px;
    }
    
    /* Dark Blue Titles */
    h1, h2, h3, h4, h5, h6, .stSubheader { color: #00008B !important; }

    /* Centering Table and Hiding Index Column (0,1,2...) */
    [data-testid="stTable"] td, [data-testid="stTable"] th {
        text-align: center !important;
    }
    [data-testid="stTable"] thead tr th:first-child { display:none; }
    [data-testid="stTable"] tbody tr th { display:none; }

    /* Input background color */
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

# --- 3. INPUT SECTION ---
st.markdown("### 📋 Personal & Financial Details")

dob = st.date_input("Date of Birth", value=date(1975, 1, 1), format="DD/MM/YYYY")
target_retirement_date = st.date_input("Target Retirement Date", value=date(2035, 1, 1), format="DD/MM/YYYY")

current_pot = st.slider("Current Private Pension Pot (£)", 0, 3500000, 500000, step=5000)
st.markdown(f"**Current Pot Selected: £{current_pot:,}**")

annual_contribution = st.slider("Annual Contribution (Pre-Retirement) (£)", 0, 100000, 10000, step=500)
st.markdown(f"**Annual Contribution Selected: £{annual_contribution:,}**")

monthly_drawdown_goal = st.slider("Desired Monthly Withdrawal (£)", 0, 20000, 3000, step=100)
st.markdown(f"**Monthly Withdrawal Selected: £{monthly_drawdown_goal:,}**")

st.info(f"Calculated Fixed Yearly Drawdown: £{monthly_drawdown_goal * 12:,.0f}")

take_lump_sum = st.selectbox("Take 25% Tax-Free Lump Sum?", ["N", "Y"])
lump_sum_val = 0.0
if take_lump_sum == "Y":
    # Cap tax-free lump sum at UK standard max
    max_ls = min(current_pot * 0.25, 268275.0)
    lump_sum_val = st.number_input(f"Lump Sum Amount (Max £{max_ls:,.0f})", value=max_ls, min_value=0.0)

state_pension_end_date = st.date_input("Date UK State Pension expected to end (Optional)", value=None, format="DD/MM/YYYY")

with st.expander("Growth & Inflation Settings"):
    cagr = st.number_input("Pension Pot CAGR (%)", value=5.0) / 100
    inflation = st.number_input("Expected Inflation Rate (%)", value=4.0) / 100
    debasement = st.number_input("Currency Debasement Rate (%)", value=5.0) / 100

# --- 4. CALCULATIONS ---

# 4a. Accumulation Phase
today_year = date.today().year
start_year = target_retirement_date.year
years_to_grow = start_year - today_year

pot_at_retirement = float(current_pot)
for _ in range(max(0, years_to_grow)):
    pot_at_retirement = (pot_at_retirement + annual_contribution) * (1 + cagr)

# 4b. Retirement Setup
balance = pot_at_retirement - lump_sum_val
start_age = start_year - dob.year

# UK State Pension Age Logic
if dob.year < 1960: spa_age = 66
elif dob.year < 1977: spa_age = 67
else: spa_age = 68
spa_year = dob.year + spa_age

st.markdown("---")
col1, col2 = st.columns(2)
col1.metric("Tax Free Amount", f"£{lump_sum_val:,.0f}")
col2.metric("Starting Pension Pot", f"£{balance:,.0f}")

# 4
