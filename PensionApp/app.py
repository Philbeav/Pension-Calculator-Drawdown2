import streamlit as st
import pandas as pd
from datetime import date

# 1. Page Config
st.set_page_config(page_title="Astute Retirement Mindset", layout="centered")

st.title("Astute Retirement Mindset")
st.subheader("Pension Drawdown Calculator")

# 2. Inputs (Range fixed: 1955 - 2010)
dob = st.date_input("Date of Birth", 
                   value=date(1975, 1, 1), 
                   min_value=date(1955, 1, 1), 
                   max_value=date(2010, 12, 31))

target_retire_date = st.date_input("Target Retirement Date", value=date(2035, 1, 1))

pot = st.slider("Current Pension Pot (£)", 0, 3500000, 500000, step=5000)
contrib = st.slider("Annual Contribution (£)", 0, 100000, 10000, step=500)
drawdown_monthly = st.slider("Monthly Withdrawal Goal (£)", 0, 20000, 3000, step=100)

with st.expander("Growth & Inflation Settings"):
    cagr = st.number_input("Annual Growth Rate (%)", value=5.0) / 100
    inflation = st.number_input("Inflation + Debasement (%)", value=9.0) / 100

# 3. Calculation Logic
today_yr = date.today().year
retire_yr = target_retire_date.year

# UK State Pension Age Logic
if dob.year < 1960: spa_age = 66
elif dob.year < 1977: spa_age = 67
else: spa_age = 68
spa_yr = dob.year + spa_age

# Accumulation Phase
projected_pot = float(pot)
for _ in range(max(0, retire_yr - today_yr)):
    projected_pot = (projected_pot + contrib) * (1 + cagr)

# 4. 30-Year Simulation
results = []
current_bal = projected_pot
yearly_drawdown = drawdown_monthly * 12

for i in range(31):
    yr = retire_yr + i
    # Accurate Age calculation
    age = yr - dob.year
    
    # State Pension (Est. 4.5% annual rise from today)
    sp = 0.0
    if yr >= spa_yr:
        sp = 11973.0 * (1.045 ** (yr - today_yr))
    
    # Drawdown Logic
    actual_drawdown = yearly_drawdown if current_bal >= yearly_drawdown else current_bal
    current_bal = (current_bal - actual_drawdown) * (1 + cagr)
    
    # Adjusted for Inflation (Real Value)
    real_val = (actual_drawdown + sp) / ((1 + (inflation/2)) ** (yr - today_yr))

    results.append({
        "Year": yr,
        "User Age": int(age),
        "Remaining Pot": f"£{current_bal:,.0f}",
        "Private Pension": f"£{actual_drawdown:,.0f}",
        "State Pension": f"£{sp:,.0f}",
        "Combined Total": f"£{actual_drawdown + sp:,.0f}",
        "Real Value": f"£{real_val:,.0f}"
    })

# 5. Display
st.divider()
st.metric("Estimated Pot at Retirement", f"£{projected_pot:,.0f}")
st.write("### 30-Year Projection")

# Standard table for maximum reliability
df = pd.DataFrame(results)
st.table(df)

st.divider()
st.info("Note: This is a stable version for testing. Figures are illustrative only.")
