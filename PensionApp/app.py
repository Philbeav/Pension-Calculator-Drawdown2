import streamlit as st
import pandas as pd
from datetime import date, timedelta

# --- PAGE CONFIGURATION ---
st.set_page_config(page_title="Astute Retirement Mindset", layout="centered")

# --- CUSTOM STYLING (Specific Background, Blue Titles, Bullet Points) ---
st.markdown(
    f"""
    <style>
    /* Main Background - Custom Hex #FFF0DB */
    .stApp {{
        background-color: #FFF0DB; 
    }}
    
    /* Content Container with Blue Border */
    .block-container {{
        border: 4px solid #00008B; 
        padding: 30px !important;
        background-color: #FFF0DB; 
        margin-top: 50px !important; 
        margin-bottom: 40px !important;
        border-radius: 10px;
        max-width: 850px !important;
    }}
    
    /* Dark Blue Headlines and Subheaders */
    h1, h2, h3, h4, h5, h6, .stSubheader {{
        color: #00008B !important;
        font-family: 'Helvetica', sans-serif;
    }}

    /* CSS TO HIDE THE INDEX COLUMN AND CENTER DATA */
    thead tr th:first-child {{ display:none; }}
    tbody tr th {{ display:none; }}
    
    .stTable td, .stTable th {{
        text-align: center !important;
        color: #333;
    }}
    
    thead tr th {{
        text-align: center !important;
    }}

    /* Input highlights in Yellow */
    div[data-baseweb="input"], div[data-baseweb="select"], div[data-baseweb="slider"] {{
        background-color: #FFFFE0 !important; 
    }}

    /* Hide default Streamlit header */
    header {{visibility: hidden;}}
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

years_to_retire = (target_retirement_date - date.today()).days / 365.25
pot_at_retirement = current_pot
if years_to_retire > 0:
    for _ in range(max(0, int(years_to_retire * 12))):
        pot_at_retirement = pot_at_retirement * (1 + cagr)**(1/12) + (annual_contribution / 12)

pot_after_ls = pot_at_retirement - lump_sum_amount

st.markdown("---")
col1, col2 = st.columns(2)
col1.metric("Tax Free Amount", f"£{lump_sum_amount:,.0f}")
col2.metric("Starting Pension Pot", f"£{pot_after_ls:,.0f}")

# 3. Drawdown Simulation
data_rows = []
balance = pot_after_ls
sim_date = target_retirement_date
base_sp_annual = 11973.0 

fixed_monthly_withdrawal = monthly_drawdown_goal 

for year in range(1, 31):
    annual_drawdown_this_year = 0
    annual_sp_this_year = 0
    current_age = calculate_age(dob, sim_date)
    
    for month in range(12):
        years_from_now = (sim_date - date.today()).days / 365.25
        projected_sp_monthly = (base_sp_annual * (1.045 ** years_from_now)) / 12
        
        if sim_date >= spa_date:
            if not state_pension_end_date or sim_date < state_pension_end_date:
                annual_sp_this_year += projected_sp_monthly
        
        if balance >= fixed_monthly_withdrawal:
            balance -= fixed_monthly_withdrawal
            annual_drawdown_this_year += fixed_monthly_withdrawal
        else:
            annual_drawdown_this_year += balance
            balance = 0
            
        balance *= (1 + cagr)**(1/12)
        sim_date += timedelta(days=30)

    combined = annual_drawdown_this_year + annual_sp_this_year
    total_years_from_now = year + years_to_retire
    real_val = combined / ((1 + (inflation + debasement)/2) ** total_years_from_now)

    data_rows.append({
        "Year": sim_date.year,
        "User Age": int(current_age),
        "Remaining Pot": f"£{balance:,.0f}",
        "Private Pension": f"£{annual_drawdown_this_year:,.0f}",
        "State Pension": f"£{annual_sp_this_year:,.0f}",
        "Combined": f"£{combined:,.0f}",
        "Real Value": f"£{real_val:,.0f}"
