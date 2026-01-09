import streamlit as st
import pandas as pd
from datetime import date, timedelta
import math

# --- PAGE CONFIGURATION & STYLING ---
st.set_page_config(page_title="Astute Retirement Mindset", layout="wide")

# Custom CSS for Cream Background, Dark Blue Border, and Yellow Inputs
st.markdown(
    """
    <style>
    /* Main Background and Border */
    .stApp {
        background-color: #FDFDD0; /* Cream */
        border: 15px solid #00008B; /* Dark Blue */
        padding: 20px;
    }
    
    /* Highlight Inputs in Yellow */
    div[data-baseweb="input"] {
        background-color: #FFFACD !important; /* LemonChiffon */
        border: 1px solid #ccc;
    }
    div[data-baseweb="select"] {
        background-color: #FFFACD !important;
    }
    div[data-baseweb="slider"] {
        /* Sliders are complex to style fully via CSS injection, 
           but the track background is handled by theme usually. */
    }
    
    /* Headers */
    h1, h2, h3 {
        color: #00008B;
        font-family: 'Helvetica', sans-serif;
    }
    
    /* Metric styling */
    div[data-testid="stMetricValue"] {
        color: #00008B;
    }
    </style>
    """,
    unsafe_allow_html=True
)

st.title("Astute Retirement Mindset")
st.subheader("Pension Drawdown Calculator")
st.markdown("---")

# --- SIDEBAR / INPUTS SECTION ---
# We use columns to create a clean layout
col_input_1, col_input_2 = st.columns(2)

with col_input_1:
    st.markdown("### Personal Details")
    dob = st.date_input("Date of birth", value=date(1975, 1, 1))
    
    # Target Retirement Date
    target_retirement_date = st.date_input("Target date for retirement", value=date(2035, 1, 1))
    
    # State Pension End Date (Optional)
    state_pension_end_date = st.date_input(
        "Date UK state pension expected to end (Optional)", 
        value=None, 
        min_value=date.today()
    )

with col_input_2:
    st.markdown("### Financial Assumptions")
    # Sliders as requested for specific fields
    current_pot = st.slider("Current private pension pot size (£)", 0, 2000000, 500000, step=1000)
    
    annual_contribution = st.slider(
        "Annual contribution to pot (pre-retirement) (£)", 
        0, 100000, 10000, step=500
    )
    
    monthly_drawdown = st.slider(
        "Desired Monthly Pension Withdrawal (£)", 
        0, 20000, 3000, step=100
    )
    st.caption(f"**Yearly Equivalent:** £{monthly_drawdown * 12:,.0f}")

st.markdown("---")

# Additional Configuration (Expanders to keep UI clean but accessible)
with st.expander("Advanced Settings & Growth Rates", expanded=True):
    col_adv1, col_adv2, col_adv3 = st.columns(3)
    
    with col_adv1:
        cagr = st.number_input("Pension Pot CAGR (%)", value=5.0, step=0.1) / 100
        inflation = st.number_input("Expected Inflation Rate (%)", value=4.0, step=0.1) / 100
    
    with col_adv2:
        debasement = st.number_input("Currency Debasement Rate (%)", value=5.0, step=0.1) / 100
        state_pension_growth = 0.045 # Fixed assumption per prompt
        
    with col_adv3:
        take_lump_sum = st.selectbox("Take Tax-Free Lump Sum?", ["N", "Y"])
        lump_sum_amount = 0.0
        if take_lump_sum == "Y":
            max_lump_sum = min(current_pot * 0.25, 268275.0)
            lump_sum_amount = st.number_input(
                f"Lump Sum Amount (£) (Max £{max_lump_sum:,.0f})", 
                value=min(50000.0, max_lump_sum),
                max_value=max_lump_sum
            )

# --- CALCULATION LOGIC ---

# 1. Constants & State Pension Rules (2025/26 Figures)
# Full New State Pension: £230.25/week -> £11,973/year
current_sp_annual = 11973.0 
sp_growth_rate = 0.045

# Determine State Pension Age (SPA) roughly based on DOB
# < 1960: 66, 1960-1977: 67, > 1977: 68
birth_year = dob.year
if birth_year < 1960:
    spa = 66
elif birth_year < 1977:
    spa = 67
else:
    spa = 68

spa_date = date(dob.year + spa, dob.month, dob.day)

# 2. Pre-Retirement Growth Phase
# Calculate months until retirement
days_to_retire = (target_retirement_date - date.today()).days
years_to_retire = days_to_retire / 365.25

# Grow current pot until retirement date
# Formula: Future Value of Pot + Future Value of Contributions
# Monthly compounding for precision
months_to_retire = int(years_to_retire * 12)
pot_at_retirement = current_pot

if months_to_retire > 0:
    monthly_rate = (1 + cagr)**(1/12) - 1
    for _ in range(months_to_retire):
        pot_at_retirement = pot_at_retirement * (1 + monthly_rate) + (annual_contribution / 12)

# 3. Lump Sum Deduction
initial_tax_free = 0.0
if take_lump_sum == "Y":
    # Recalculate cap based on pot at retirement? 
    # Usually cap is fixed, but 25% is based on pot value at crystallization.
    # We will use the fixed cap of £268,275 or 25% of the crystallised pot.
    max_ls_at_retire = min(pot_at_retirement * 0.25, 268275.0)
    # If user input was higher than the future allowance, cap it. 
    # If user entered a fixed amount, we try to honor it up to the limit.
    if lump_sum_amount > max_ls_at_retire:
        initial_tax_free = max_ls_at_retire
    else:
        initial_tax_free = lump_sum_amount
    
    pot_after_lump = pot_at_retirement - initial_tax_free
else:
    pot_after_lump = pot_at_retirement

# Display Lump Sum & Starting Pot
st.markdown("### Retirement Summary")
col_res1, col_res2 = st.columns(2)
col_res1.metric("Tax Free Lump Sum", f"£{initial_tax_free:,.2f}")
col_res2.metric("Starting Pension Pot (Post-Lump Sum)", f"£{pot_after_lump:,.2f}")


# 4. Drawdown Simulation (30 Years)
data_rows = []
sim_balance = pot_after_lump
current_monthly_drawdown = monthly_drawdown
# Calculate State Pension amount at moment of retirement (it grows while we wait)
# SP grows from NOW until the year it is claimed.
years_until_spa = (spa_date - date.today()).days / 365.25
projected_sp_at_spa = current_sp_annual * ((1 + sp_growth_rate) ** years_until_spa)

# Simulation Loop
sim_date = target_retirement_date
user_age = sim_date.year - dob.year

for year in range(1, 31):
    
    total_pension_drawn_this_year = 0
    total_state_pension_this_year = 0
    
    # Process 12 months
    for month in range(12):
        # 1. Withdraw at START of month
        withdrawal = current_monthly_drawdown
        if sim_balance >= withdrawal:
            sim_balance -= withdrawal
            total_pension_drawn_this_year += withdrawal
        else:
            # Pot runs out
            total_pension_drawn_this_year += sim_balance
            sim_balance = 0
            
        # 2. Add State Pension if eligible
        # Check if current sim_date is >= SPA Date and < End Date (if set)
        is_eligible_sp = sim_date >= spa_date
        if state_pension_end_date and sim_date >= state_pension_end_date:
            is_eligible_sp = False
            
        if is_eligible_sp:
            monthly_sp = projected_sp_at_spa / 12
            total_state_pension_this_year += monthly_sp
            # State pension is income, not added to pot, but shown in table
        
        # 3. Growth on remaining balance (Compounding)
        monthly_growth = (1 + cagr)**(1/12) - 1
        sim_balance = sim_balance * (1 + monthly_growth)
        
        # Move time forward 1 month
        sim_date += timedelta(days=30) # Approx
    
    # End of Year Calculations
    combined_income = total_pension_drawn_this_year + total_state_pension_this_year
    
    # Debasement Calculation (Real Value of Combined Income)
    # Real Value = Nominal / (1 + Debasement)^n
    # n is years since TODAY (not retirement start), as debasement starts now
    years_since_start = (sim_date.year - date.today().year)
    real_value = combined_income / ((1 + debasement) ** years_since_start)
    
    data_rows.append({
        "Date": sim_date.strftime("%Y"),
        "User Age": int(sim_date.year - dob.year),
        "Private Pension Drawdown": f"£{total_pension_drawn_this_year:,.0f}",
        "State Pension": f"£{total_state_pension_this_year:,.0f}",
        "Combined Annual Amount": f"£{combined_income:,.0f}",
        "Debasement Real Value": f"£{real_value:,.0f}",
        "Remaining Pot Balance": f"£{sim_balance:,.0f}" # Added for clarity, though not strictly requested, it's vital context
    })
    
    # Adjust figures for next year
    current_monthly_drawdown *= (1 + inflation)
    projected_sp_at_spa *= (1 + sp_growth_rate) 

# --- RESULTS TABLE ---
st.subheader("30-Year Projection")
df = pd.DataFrame(data_rows)
st.dataframe(df, use_container_width=True)


# --- FOOTER / DISCLAIMERS ---
st.markdown("---")
st.markdown("""
**Notes:**
* **The model assumes that the user qualifies for the full state pension with the required national insurance contributions having been attained.**
* **All of these calculations are for illustrative purposes only and should not in any way be regarded as guaranteed or relied upon for financial decisions.**
* **Figures shown are gross amounts and should be modelled against your own personal tax liabilities.**
""")