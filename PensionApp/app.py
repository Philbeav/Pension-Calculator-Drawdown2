import streamlit as st
import pandas as pd
from datetime import date

# --- 1. PAGE CONFIGURATION ---
st.set_page_config(page_title="Astute Retirement Mindset", layout="centered")

# --- 2. THE STABLE STYLING ---
st.markdown(
    """
    <style>
    /* Make the whole page background white */
    .stApp { background-color: #FFFFFF !important; }
    
    /* Create a custom container for the app content */
    .custom-container {
        border: 4px solid #00008B; 
        padding: 40px;
        background-color: #FFF0DB; 
        border-radius: 15px;
        color: #333333;
        margin-bottom: 20px;
    }
    
    /* Dark Blue Titles */
    .blue-text { color: #00008B !important; font-weight: bold; }
    h1, h2, h3, .stSubheader { color: #00008B !important; }

    /* Centering Table and Hiding Index Column */
    table { width: 100%; border-collapse: collapse; }
    th { background-color: #FFFFE0 !important; text-align: center !important; color: #00008B !important; }
    td { text-align: center !important; }
    
    /* Hide the index column in st.table */
    thead tr th:first-child { display:none; }
    tbody tr th { display:none; }

    /* Force yellow background for inputs */
    div[data-baseweb="input"], div[data-baseweb="select"], div[data-baseweb="slider"] {
        background-color: #FFFFE0 !important; 
    }
    header {visibility: hidden;}
    </style>
    """,
    unsafe_allow_html=True
)

# Start of the blue-bordered cream box
st.markdown('<div class="custom-container">', unsafe_allow_html=True)

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
    max_ls = min(current_pot * 0.25, 268275.0)
    lump_sum_val = st.number_input(f"Lump Sum Amount (Max £{max_ls:,.0f})", value=max_ls, min_value=0.0)

state_pension_end_
