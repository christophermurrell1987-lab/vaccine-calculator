import streamlit as st

# Page configuration
st.set_page_config(
    page_title="Hatchery Vaccine Pricing Calculator",
    page_icon="🐣",
    layout="centered"
)

# Title
st.title("🐣 Vaccine Pricing Calculator")
st.markdown("---")

# =============================================================================
# VACCINE DATA - EDIT THESE LISTS
# Format: {"Vaccine Name": price_per_1000_doses}
# =============================================================================

INOVO_VACCINES = {
    "Select vaccine...": 0.00,
    "Vaccine A (Inovo)": 12.50,
    "Vaccine B (Inovo)": 15.75,
    "Vaccine C (Inovo)": 18.00,
    # Add more vaccines here
}

DAY_OLD_VACCINES = {
    "Select vaccine...": 0.00,
    "Vaccine X (Day Old)": 8.25,
    "Vaccine Y (Day Old)": 11.50,
    "Vaccine Z (Day Old)": 14.00,
    # Add more vaccines here
}

# =============================================================================
# INPUT SECTION
# =============================================================================

# Number of chicks/eggs
st.subheader("📊 Volume")
num_chicks = st.number_input(
    "Number of eggs/chicks to vaccinate",
    min_value=0,
    max_value=10_000_000,
    value=100_000,
    step=1000,
    help="Enter the total number for this batch"
)

st.markdown("---")

# Inovo vaccines section
st.subheader("💉 In-Ovo Vaccination")
col1, col2 = st.columns(2)

with col1:
    inovo_1 = st.selectbox(
        "Inovo Vaccine 1",
        options=list(INOVO_VACCINES.keys()),
        key="inovo_1"
    )

with col2:
    inovo_2 = st.selectbox(
        "Inovo Vaccine 2",
        options=list(INOVO_VACCINES.keys()),
        key="inovo_2"
    )

st.markdown("---")

# Day Old vaccines section
st.subheader("🐥 Day-Old Vaccination")
col3, col4 = st.columns(2)

with col3:
    day_old_1 = st.selectbox(
        "Day Old Vaccine 1",
        options=list(DAY_OLD_VACCINES.keys()),
        key="day_old_1"
    )

with col4:
    day_old_2 = st.selectbox(
        "Day Old Vaccine 2",
        options=list(DAY_OLD_VACCINES.keys()),
        key="day_old_2"
    )

st.markdown("---")

# =============================================================================
# CALCULATIONS
# =============================================================================

# Get prices (price per 1000 doses)
inovo_1_price = INOVO_VACCINES[inovo_1]
inovo_2_price = INOVO_VACCINES[inovo_2]
day_old_1_price = DAY_OLD_VACCINES[day_old_1]
day_old_2_price = DAY_OLD_VACCINES[day_old_2]

# Calculate costs (prices are per 1000, so divide quantity by 1000)
multiplier = num_chicks / 1000

inovo_1_cost = inovo_1_price * multiplier
inovo_2_cost = inovo_2_price * multiplier
day_old_1_cost = day_old_1_price * multiplier
day_old_2_cost = day_old_2_price * multiplier

total_inovo = inovo_1_cost + inovo_2_cost
total_day_old = day_old_1_cost + day_old_2_cost
grand_total = total_inovo + total_day_old

# Cost per chick
cost_per_chick = grand_total / num_chicks if num_chicks > 0 else 0

# =============================================================================
# RESULTS SECTION
# =============================================================================

st.subheader("💰 Cost Breakdown")

# Results in columns
res_col1, res_col2 = st.columns(2)

with res_col1:
    st.markdown("**In-Ovo Vaccines**")
    if inovo_1 != "Select vaccine...":
        st.write(f"• {inovo_1}: £{inovo_1_cost:,.2f}")
    if inovo_2 != "Select vaccine...":
        st.write(f"• {inovo_2}: £{inovo_2_cost:,.2f}")
    st.write(f"**Subtotal: £{total_inovo:,.2f}**")

with res_col2:
    st.markdown("**Day-Old Vaccines**")
    if day_old_1 != "Select vaccine...":
        st.write(f"• {day_old_1}: £{day_old_1_cost:,.2f}")
    if day_old_2 != "Select vaccine...":
        st.write(f"• {day_old_2}: £{day_old_2_cost:,.2f}")
    st.write(f"**Subtotal: £{total_day_old:,.2f}**")

st.markdown("---")

# Grand total display
total_col1, total_col2 = st.columns(2)

with total_col1:
    st.metric(
        label="Grand Total",
        value=f"£{grand_total:,.2f}"
    )

with total_col2:
    st.metric(
        label="Cost per Chick",
        value=f"£{cost_per_chick:.4f}"
    )

# =============================================================================
# FOOTER
# =============================================================================

st.markdown("---")
st.caption("Prices are per 1,000 doses. Edit the INOVO_VACCINES and DAY_OLD_VACCINES dictionaries to update vaccine options and pricing.")
