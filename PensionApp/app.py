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

# Precise Age Function
def get_age(birth_date, current_date):
    return current_date.year - birth_date.year - ((current_date.month, current_date.day) < (birth_date.month, birth_date.day))

today = date.today()
retire_yr = target_retirement_date.year
retire_age = get_age(dob, target_retirement_date)

# State Pension Age Logic
if dob.year < 1960: spa_age = 66
elif dob.year < 1977: spa_age = 67
else: spa_age = 68
# State pension starts on the actual birthday of that age
spa_date = date(dob.year + spa_age, dob.month, dob.day)

# Accumulation (Approx years between now and retirement)
years_to_grow = max(0, retire_yr - today.year)
pot_at_retire = float(current_pot)
for _ in range(years_to_grow):
    pot_at_retire = (pot_at_retire + annual_contribution) * (1 + cagr)

balance = pot_at_retire - lump_sum_val
yearly_goal = float(monthly_drawdown * 12)
base_sp_annual = 11973.0

data = []
for i in range(30):
    current_sim_date = date(target_retirement_date.year + i, target_retirement_date.month, target_retirement_date.day)
    curr_yr = current_sim_date.year
    curr_age = get_age(dob, current_sim_date)
    
    # State Pension Logic (Comparing dates, not just years)
    sp_val = 0.0
    if current_sim_date >= spa_date:
        if state_pension_end_date is None or current_sim_date < state_pension_end_date:
            years_diff = curr_yr - today.year
            sp_val = base_sp_annual * (1.045 ** max(0, years_diff))
    
    # Private Pension
    payout = yearly_goal if balance >= yearly_goal else balance
    balance -= payout
    balance *= (1 + cagr)
    
    combined = payout + sp_val
    total_inf = (inflation + debasement) / 2
    real_val = combined / ((1 + total_inf) ** max(1, (curr_yr - today.year)))

    data.append({
        "Year": curr_yr,
        "User Age": int(curr_age),
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
