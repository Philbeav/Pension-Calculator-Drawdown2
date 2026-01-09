import streamlit as st
import pandas as pd
from datetime import date

# 1. Page Config
st.set_page_config(page_title="Astute Retirement Mindset", layout="centered")

# 2. Minimum Styling (Only the essentials to prevent loading errors)
st.markdown("""
    <style>
    /* Basic background and text colors */
    .stApp { background-color: #FFF0DB; }
    h1, h2, h3, .stSubheader { color: #00008B !important; }
    
    /* Hide Table Index */
    thead tr th:first-child { display:none; }
    tbody tr th { display:none; }
    .stTable td { text-align: center !important; }
    </style>
    """, unsafe_allow_html=True)

st.title("Astute Retirement Mindset")
st.subheader("Pension Drawdown Calculator")

# 3. Inputs
dob = st.date_input("Date of Birth", value=date(1975, 1, 1), format="DD/MM/YYYY")
target_retirement_date = st.date_input("Target Retirement Date", value=date(2035, 1, 1), format="DD/MM/YYYY")

current_pot = st.slider("Current Private Pension Pot (£)", 0, 3500000, 500000, step=5000)
st.write(f"Selected: £{current_pot:,}")

annual_contribution = st.slider("Annual Contribution (£)", 0, 100000, 10000, step=500)
monthly_drawdown = st.slider("Desired Monthly Withdrawal (£)", 0, 20000, 3000, step=100)

take_lump_sum = st.selectbox("Take 25% Tax-Free Lump Sum?", ["N", "Y"])
lump_sum_val = 0.0
if take_lump_sum == "Y":
    max_ls = min(current_pot * 0.25, 268275.0)
    lump_sum_val = st.number_input(f"Lump Sum Amount (Max £{max_ls:,.0f})", value=max_ls)

# 4. Calculations
today_yr = date.today().year
retire_yr = target_retirement_date.year
growth = 0.05 # 5% Fixed for stability

# Accumulation
pot_at_retire = float(current_pot)
for _ in range(max(0, retire_yr - today_yr)):
    pot_at_retire = (pot_at_retire + annual_contribution) * (1 + growth)

balance = pot_at_retire - lump_sum_val
yearly_goal = monthly_drawdown * 12

# 5. Table Logic
data = []
for i in range(30):
    yr = retire_yr + i
    age = yr - dob.year
    
    # Simple drawdown logic
    payout = yearly_goal if balance >= yearly_goal else balance
    balance -= payout
    balance *= (1 + growth)
    
    data.append({
        "Year": yr,
        "Age": age,
        "Remaining Pot": f"£{balance:,.0f}",
        "Private Pension": f"£{payout:,.0f}",
        "Combined Income": f"£{payout:,.0f}"
    })

# 6. Display
st.metric("Starting Pension Pot", f"£{pot_at_retire - lump_sum_val:,.0f}")
st.table(pd.DataFrame(data))

st.markdown("---")
st.markdown("Disclaimer: For illustrative purposes only.")
