import streamlit as st
import pandas as pd
from datetime import date

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

dob = st.date_input("Date of Birth", value=date(1975, 1, 1), format="DD/MM/YYYY")
target_retirement_date = st.date_input("Target Retirement Date", value=date(2035, 1, 1), format="DD/MM/YYYY")

current_pot = st.slider("Current Private Pension Pot (£)", 0, 3500000, 500000, step=5000, format="£%d")
st.markdown(f"**Current Pot Selected: £{current_pot:,}**")

annual_contribution = st.slider("Annual Contribution (Pre-Retirement) (£)", 0, 100000, 10000, step=500, format="£%d")
st.markdown(f"**Annual Contribution Selected: £{annual_contribution:,}**")

monthly_drawdown_goal = st.slider("Desired Monthly Withdrawal (£)", 0, 20000, 3000, step=100, format="£%d")
st.markdown(f"**Monthly Withdrawal Selected: £{monthly_drawdown_goal:,}**")

st.info(f"Calculated Fixed Yearly Drawdown: £{monthly_drawdown_goal * 12:,.0f}")

take_lump_sum = st.selectbox("Take 25% Tax-Free Lump Sum?", ["N", "Y"])
lump_sum_val = 0.0
if take_lump_sum == "Y":
    max_ls = min(current_pot * 0.25, 268275.0)
    lump_sum_val = st.number_input(f"Lump Sum Amount (Max £{max_ls:,.0f})", value=max_ls, min_value=0.0)

state_pension_end_date = st.date_input("Date UK State Pension expected to end (Optional)", value=None, format="DD/MM/YYYY")

with st.expander("Growth & Inflation Settings"):
    cagr = st.number_input("Pension Pot CAGR (%)", value=5.0) / 100
    inflation = st.number_input("Expected Inflation Rate (%)", value=4.0) / 100
    debasement = st.number_input("Currency Debasement Rate (%)", value=5.0) / 100

# --- CALCULATIONS ---

# 1. Accumulation Phase
today = date.today()
years_to_retirement = (target_retirement_date.year - today.year)
pot_at_retirement = float(current_pot)

for _ in range(max(0, years_to_retirement)):
    pot_at_retirement = (pot_at_retirement + annual_contribution) * (1 + cagr)

# 2. Retirement Setup
balance = pot_at_retirement - lump_sum_val
start_year = target_retirement_date.year
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

# 3. Drawdown Simulation
data_rows = []
base_sp_annual = 11973.0 
yearly_drawdown = float(monthly_drawdown_goal * 12)

for i in range(30):
    current_year = start_year + i
    current_age = start_age + i
    
    # State Pension Logic
    sp_this_year = 0.0
    if current_year >= spa_year:
        # Check if user has passed their optional end date
        if state_pension_end_date is None or current_year < state_pension_end_date.year:
            # 4.5% Triple Lock estimation
            years_from_now = current_year - today.year
            sp_this_year = base_sp_annual * (1.045 ** max(0, years_from_now))
    
    # Private Pension Logic
    private_p_this_year = 0.0
    if balance >= yearly_drawdown:
        balance -= yearly_drawdown
        private_p_this_year = yearly_drawdown
    else:
        private_p_this_year = balance
        balance = 0
    
    # Pot Growth
    balance *= (1 + cagr)
    
    # Combined & Real Value
    combined = private_p_this_year + sp_this_year
    years_ahead = current_year - today.year
    real_val = combined / ((1 + (inflation
