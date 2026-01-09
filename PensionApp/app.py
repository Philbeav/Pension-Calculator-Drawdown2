import streamlit as st
import pandas as pd
from datetime import date, timedelta

# --- PAGE CONFIGURATION ---
st.set_page_config(page_title="Astute Retirement Mindset", layout="centered")

# --- CUSTOM STYLING (Narrow Border, Parchment, UK Formatting) ---
st.markdown(
    """
    <style>
    /* Main Background */
    .stApp {
        background-color: #FDF5E6; /* Old Lace / Parchment */
    }
    
    /* Narrow Content Container with Blue Border */
    .block-container {
        border: 4px solid #00008B; /* Dark Blue Border */
        padding: 30px !important;
        background-color: #F5F5DC; /* Beige/Parchment */
        margin-top: 20px;
        margin-bottom: 20px;
        border-radius: 10px;
        max-width: 800px !important;
    }
    
    /* Center table headers and cells */
    th, td {
        text-align: center !important;
    }

    /* Input highlights in Yellow */
    div[data-baseweb="input"], div[data-baseweb="select"], div[data-baseweb="slider"] {
        background-color: #FFFFE0 !important; /* Light Yellow */
    }

    /* Mobile adjustments */
    @media (max-width: 600px) {
        .block-container {
            border-width: 2px;
            padding: 15px !important;
        }
    }
    </style>
    """,
    unsafe_allow_html=True
)

st.title("Astute Retirement Mindset")
st.subheader("Pension Drawdown Calculator")

# --- INPUT SECTION ---
st.markdown("### 📋 Personal & Financial Details")

# Date inputs set to UK format
dob = st.date_input("Date of Birth", value=date(1975, 1, 1), format="DD/MM/YYYY")
target_retirement_date = st.date_input("Target Retirement Date", value=date(2035, 1, 1), format="DD/MM/YYYY")

current_pot = st.slider("Current Private Pension Pot (£)", 0, 2000000, 500000, step=1000)
annual_contribution = st.slider("Annual Contribution (Pre-Retirement) (£)", 0, 100000, 10000, step=500)
monthly_drawdown_goal = st.slider("Desired Monthly Withdrawal (£)", 0, 20000, 3000, step=100)

# Display yearly equivalent
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

def calculate_age(birth, current):
    return current.year - birth.year - ((current.month, current.day) < (birth.month, birth.day))

# UK State Pension Age Logic
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

st.success(f"Starting Pot at Retirement: £{pot_after_ls:,.2f}")

# 3. Drawdown Simulation
data_rows = []
balance = pot_after_ls
sim_date = target_retirement_date
current_sp_annual = 11973.0 # 2025/26 Base

for year in range(1, 31):
    annual_drawdown_this_year = 0
    annual_sp_this_year = 0
    
    # Calculate age at the start of this simulation year
    current_age = calculate_age(dob, sim_date)
    
    # Monthly Loop
    for month in range(12):
        # State Pension Growth (Increases every year)
        projected_sp_monthly = (current_sp_annual * (1.045 ** ((sim_date - date.today()).days / 365.25))) / 12
        
        if sim_date >= spa_date:
            if not state_pension_end_date or sim_date < state_pension_end_date:
                annual_sp_this_year += projected_sp_monthly
        
        # Private Withdrawal (Inflation adjusted)
        monthly_withdrawal = monthly_drawdown_goal * ((1 + inflation) ** (year - 1))
        if balance >= monthly_withdrawal:
            balance -= monthly_withdrawal
            annual_drawdown_this_year += monthly_withdrawal
        else:
            annual_drawdown_this_year += balance
            balance = 0
            
        balance *= (1 + cagr)**(1/12)
        sim_date += timedelta(days=30)

    combined = annual_drawdown_this_year + annual_sp_this_year
    real_val = combined / ((1 + debasement) ** (year + years_to_retire))

    data_rows.append({
        "Year": sim_date.year,
        "User Age": int(current_age),
        "Remaining Pot": f"£{balance:,.0f}",
        "Private Pension": f"£{annual_drawdown_this_year:,.0f}",
        "State Pension": f"£{annual_sp_this_year:,.0f}",
        "Combined": f"£{combined:,.0f}",
        "Real Value": f"£{real_val:,.0f}"
    })

# --- DISPLAY TABLE ---
st.subheader("30-Year Projection")
df = pd.DataFrame(data_rows)
# Reordering columns as requested
df = df[["Year", "User Age", "Remaining Pot", "Private Pension", "State Pension", "Combined", "Real Value"]]
st.table(df)

# --- FOOTER ---
st.markdown("---")
st.markdown("""
**The model assumes that the users qualifies for the full state pension with the required national insurance contributions having been attained.** **All of these calculations are for illustrative purposes only and should not in any way be regarded as guaranteed or relied upon for financial decisions.** **Figures shown are gross amounts and should be modelled against your own personal tax liabilities.**
""")
