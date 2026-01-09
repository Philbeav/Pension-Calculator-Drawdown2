import streamlit as st
import pandas as pd
from datetime import date

# 1. Basic Page Setup (No complex CSS to prevent crashes)
st.set_page_config(page_title="Astute Retirement Mindset", layout="centered")

st.title("Astute Retirement Mindset")
st.header("Pension Drawdown Calculator")

# 2. Inputs (Range fixed: 1955 - 2010)
dob = st.date_input("Date of Birth", value=date(1975, 1, 1), 
                   min_value=date(1955, 1, 1), max_value=date(2010, 12, 31))

target_retire = st.date_input("Target Retirement Date", value=date(2035, 1, 1))

pot = st.slider("Current Pension Pot (£)", 0, 3500000, 500000, 5000)
contrib = st.slider("Annual Contribution (£)", 0, 100000, 10000, 500)
drawdown = st.slider("Monthly Withdrawal Goal (£)", 0, 20000, 3000, 100)

with st.expander("Growth & Inflation Settings"):
    cagr = st.number_input("Growth Rate (%)", value=5.0) / 100
    inf = st.number_input("Inflation + Debasement (%)", value=9.0) / 100

# 3. Simple Math Logic
today_yr = date.today().year
retire_yr = target_retire.year

# State Pension Age
spa_age = 67
if dob.year < 1960: spa_age = 66
elif dob.year >= 1977: spa_age = 68
spa_yr = dob.year + spa_age

# Accumulation
projected_pot = float(pot)
for _ in range(max(0, retire_yr - today_yr)):
    projected_pot = (projected_pot + contrib) * (1 + cagr)

# 4. Table Logic
results = []
current_bal = projected_pot
yearly_goal = drawdown * 12

for i in range(31):
    yr = retire_yr + i
    age = yr - dob.year
    
    # State Pension (Est. 4.5% annual rise)
    sp = 0.0
    if yr >= spa_yr:
        sp = 11973.0 * (1.045 ** (yr - today_yr))
    
    # Drawdown
    take = yearly_goal if current_bal >= yearly_goal else current_bal
    current_bal = (current_bal - take) * (1 + cagr)
    
    # Real Value
    real = (take + sp) / (1.045 ** (yr - today_yr))

    results.append({
        "Year": yr,
        "Age": int(age),
        "Pot Remaining": f"£{current_bal:,.0f}",
        "Private Pension": f"£{take:,.0f}",
        "State Pension": f"£{sp:,.0f}",
        "Total Income": f"£{take + sp:,.0f}",
        "Real Value": f"£{real:,.0f}"
    })

# 5. Display (Standard Table)
st.metric("Pot at Retirement", f"£{projected_pot:,.0f}")
st.table(pd.DataFrame(results))

st.info("Note: This is a simplified stable version. Figures are illustrative.")
