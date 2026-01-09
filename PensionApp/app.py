import streamlit as st
import pandas as pd
from datetime import date

# --- 1. PAGE CONFIGURATION ---
st.set_page_config(page_title="Astute Retirement Mindset", layout="centered")

# --- 2. THE FINAL CSS FIX ---
st.markdown(
    """
    <style>
    /* 1. Page Background White */
    .stApp {
        background-color: #FFFFFF !important;
    }
    
    /* 2. Target the main content area for the Cream Box & Blue Border */
    .block-container {
        background-color: #FFF0DB !important;
        border: 5px solid #00008B !important;
        padding: 40px !important;
        border-radius: 20px !important;
        margin-top: 50px !important;
        margin-bottom: 50px !important;
        max-width: 800px !important;
    }

    /* 3. Headers & Text */
    h1, h2, h3, .stSubheader { color: #00008B !important; }
    
    /* 4. Table Formatting: Center and Hide Index */
    .stTable td, .stTable th { text-align: center !important; }
    thead tr th:first-child { display:none !important; }
    tbody tr th { display:none !important; }
    
    /* 5. Input Highlights in Yellow */
    div[data-baseweb="input"], div[data-baseweb="select"], div[data-baseweb="slider"] {
        background-color: #FFFFE0 !important; 
    }
    
    /* Hide Streamlit default header */
    header {visibility: hidden;}
    </style>
    """,
    unsafe_allow_html=True
)

# --- 3. APP CONTENT ---
st.title("Astute Retirement Mindset")
st.subheader("Pension Drawdown Calculator")

st.markdown("### 📋 Personal & Financial Details")

dob = st.date_input("Date of Birth", value=date(1975, 1, 1), format="DD/MM/YYYY")
target_retirement_date = st.date_input("Target Retirement Date", value=date(2035, 1, 1), format="DD/MM/YYYY")

current_pot = st.slider("Current Private Pension Pot (£)", 0, 3500000, 500000, step=5000)
st.markdown(f"**Current Pot Selected: £{current_pot:,}**")

annual_contribution = st.slider("Annual Contribution (£)", 0, 100000, 10000, step=500)
monthly_drawdown = st.slider("Desired Monthly Withdrawal (£)", 0, 20000, 3000, step=100)

st.info(f"Fixed Yearly Drawdown: £{monthly_drawdown * 12:,.0f}")

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

# --- 4. CALCULATION LOGIC ---
today_yr = date.today().year
retire_yr = target_retirement_date.year
start_age = retire_yr - dob.year

if dob.year < 1960: spa_age = 66
elif dob.year < 1977: spa_age = 67
else: spa_age = 68
spa_year = dob.year + spa_age

# Accumulation
pot_at_retire = float(current_pot)
for _ in range(max(0, retire_yr - today_yr)):
    pot_at_retire = (pot_at_retire + annual_contribution) * (1 + cagr)

balance = pot_at_retire - lump_sum_val
yearly_goal = float(monthly_drawdown * 12)
base_sp_annual = 11973.0

data = []
for i in range(30):
    yr = retire_yr + i
    age = start_age + i
    
    sp_val = 0.0
    if yr >= spa_year:
        if state_pension_end_date is None or yr < state_pension_end_date.year:
            sp_val = base_sp_annual * (1.045 ** max(0, yr - today_yr))
    
    payout = yearly_goal if balance >= yearly_goal else balance
    balance -= payout
    balance *= (1 + cagr)
    
    combined = payout + sp_val
    real_val = combined / ((1 + (inflation + debasement)/2) ** max(1, (yr - today_yr)))

    data.append({
        "Year": yr,
        "User Age": int(age),
        "Remaining Pot": f"£{balance:,.0f}",
        "Private Pension": f"£{payout:,.0f}",
        "State Pension": f"£{sp_val:,.0f}",
        "Combined": f"£{combined:,.0f}",
        "Real Value": f"£{real_val:,.0f}"
    })

# --- 5. RESULTS ---
st.markdown("---")
st.metric("Starting Pension Pot (After Lump Sum)", f"£{pot_at_retire - lump_sum_val:,.0f}")
st.subheader("30-Year Projection")
st.table(pd.DataFrame(data))

st.markdown("---")
st.markdown("""
**Notes:**
* The model assumes that the users qualifies for the full state pension with the required national insurance contributions having been attained.
* All of these calculations are for illustrative purposes only and should not in any way be regarded as guaranteed or relied upon for financial decisions.
* Figures shown are gross amounts and should be modelled against your own personal tax liabilities.
""")
