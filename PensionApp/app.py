import streamlit as st
import pandas as pd
from datetime import date, timedelta

# --- PAGE CONFIGURATION ---
st.set_page_config(page_title="Astute Retirement Mindset", layout="centered")

# --- CUSTOM STYLING (Parchment, Centered Table, Mobile Friendly) ---
st.markdown(
    """
    <style>
    /* Parchment Background and Blue Border */
    .stApp {
        background-color: #F5F5DC; 
        border: 10px solid #00008B;
        padding: 10px;
    }
    
    /* Center table headers and cells */
    th, td {
        text-align: center !important;
    }

    /* Soften the input fields */
    div[data-baseweb="input"], div[data-baseweb="select"], div[data-baseweb="slider"] {
        background-color: #FFF9E3 !important;
        border-radius: 5px;
    }

    /* Mobile responsiveness for headers */
    @media (max-width: 600px) {
        h1 { font-size: 1.5rem !important; }
        .stApp { border: 5px solid #00008B; }
    }
    </style>
    """,
    unsafe_allow_html=True
)

st.title("Astute Retirement Mindset")
st.subheader("Pension Drawdown Calculator")

# --- INPUT SECTION ---
st.markdown("### 📋 Personal & Financial Details")

dob = st.date_input("Date of Birth", value=date(1975, 1, 1))
target_retirement_date = st.date_input("Target Retirement Date", value=date(2035, 1, 1))

current_pot = st.slider("Current Private Pension Pot (£)", 0, 2000000, 500000, step=1000)
annual_contribution = st.slider("Annual Contribution (Pre-Retirement) (£)", 0, 100000, 10000, step=500)
monthly_drawdown_goal = st.slider("Desired Monthly Withdrawal (£)", 0, 20000, 3000, step=100)
st.info(f"Yearly Drawdown: £{monthly_drawdown_goal * 12:,.0f}")

take_lump_sum = st.selectbox("Take 25% Tax-Free Lump Sum?", ["N", "Y"])
lump_sum_amount = 0.0
if take_lump_sum == "Y":
    max_ls = min(current_pot * 0.25, 268275.0)
    lump_sum_amount = st.number_input(f"Lump Sum Amount (Max £{max_ls:,.0f})", value=max_ls)

state_pension_end_date = st.date_input("Date UK State Pension expected to end (Optional)", value=None)

# --- ADVANCED SETTINGS ---
with st.expander("Growth & Inflation Settings"):
    cagr = st.number_input("Pension Pot CAGR (%)", value=5.0) / 100
    inflation = st.number_input("Expected Inflation Rate (%)", value=4.0) / 100
    debasement = st.number_input("Currency Debasement Rate (%)", value=5.0) / 100

# --- CALCULATIONS ---

# 1. Age & State Pension Timing
def calculate_age(birth, current):
    return current.year - birth.year - ((current.month, current.day) < (birth.month, birth.day))

# UK State Pension Age Logic
if dob.year < 1960: spa_age = 66
elif dob.year < 1977: spa_age = 67
else: spa_age = 68
spa_date = date(dob.year + spa_age, dob.month, dob.day)

# 2. Accumulation Phase (Until Retirement)
years_to_retire = (target_retirement_date - date.today()).days / 365.25
pot_at_retirement = current_pot
if years_to_retire > 0:
    for _ in range(int(years_to_retire * 12)):
        pot_at_retirement = pot_at_retirement * (1 + cagr)**(1/12) + (annual_contribution / 12)

# 3. Lump Sum
pot_after_ls = pot_at_retirement - lump_sum_amount

st.success(f"Starting Pot at Retirement: £{pot_after_ls:,.2f}")

# 4. Drawdown Simulation (30 Years)
data_rows = []
balance = pot_after_ls
sim_date = target_retirement_date
current_sp_annual = 11973.0 # 2025/26 Base

for year in range(1, 31):
    annual_drawdown_this_year = 0
    annual_sp_this_year = 0
    
    # Yearly Age (Calculated at start of the simulation year)
    current_age = calculate_age(dob, sim_date)
    
    for month in range(12):
        # State Pension Growth (Increases every year)
        projected_sp_monthly = (current_sp_annual * (1.045 ** ((sim_date - date.today()).days / 365.25))) / 12
        
        # Check Eligibility
        if sim_date >= spa_date:
            if not state_pension_end_date or sim_date < state_pension_end_date:
                annual_sp_this_year += projected_sp_monthly
        
        # Private Withdrawal (Adjusted for inflation each year)
        monthly_withdrawal = monthly_drawdown_goal * ((1 + inflation) ** (year - 1))
        if balance >= monthly_withdrawal:
            balance -= monthly_withdrawal
            annual_drawdown_this_year += monthly_withdrawal
        else:
            annual_drawdown_this_year += balance
            balance = 0
            
        # Pot Growth
        balance *= (1 + cagr)**(1/12)
        sim_date += timedelta(days=30)

    combined = annual_drawdown_this_year + annual_sp_this_year
    real_val = combined / ((1 + debasement) ** (year + years_to_retire))

    data_rows.append({
        "Year": sim_date.year,
        "User Age": current_age,
        "Remaining Pot": f"£{balance:,.0f}",
        "Private Pension": f"£{annual_drawdown_this_year:,.0f}",
        "State Pension": f"£{annual_sp_this_year:,.0f}",
        "Combined": f"£{combined:,.0f}",
        "Real Value": f"£{real_val:,.0f}"
    })

# --- DISPLAY TABLE ---
df = pd.DataFrame(data_rows)
st.table(df)

# --- FOOTER ---
st.markdown("---")
st.markdown("""
**The model assumes that the users qualifies for the full state pension with the required national insurance contributions having been attained.** **All of these calculations are for illustrative purposes only and should not in any way be regarded as guaranteed or relied upon for financial decisions.** **Figures shown are gross amounts and should be modelled against your own personal tax liabilities.**
""")
