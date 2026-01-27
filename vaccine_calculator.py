import streamlit as st

# Page configuration
st.set_page_config(
    page_title="Hatchery Vaccine Pricing Calculator",
    page_icon="🐣",
    layout="wide"
)

# Title
st.title("🐣 Hatchery Vaccine Pricing Calculator")
st.markdown("---")

# =============================================================================
# CONFIGURATION - MACHINE COSTS
# =============================================================================

# Zoetis Inovo monthly lease cost (GBP)
INOVO_MONTHLY_LEASE = 6125.00

# Novatech Day Old costs (converted from USD to GBP at ~0.79)
USD_TO_GBP = 0.79
NOVATECH_CRADLE_COUNT = 0.00655 * USD_TO_GBP      # £0.00518 per chick
NOVATECH_ROLLER_INJECT = 0.00545 * USD_TO_GBP     # £0.00431 per chick  
NOVATECH_NEEDLE_SANITATION = 0.00214 * USD_TO_GBP # £0.00169 per chick
NOVATECH_BEAK_TREATMENT = 0.00987 * USD_TO_GBP    # £0.00780 per chick

# Total Novatech injection cost per chick (without beak)
NOVATECH_INJECTION_COST = NOVATECH_CRADLE_COUNT + NOVATECH_ROLLER_INJECT + NOVATECH_NEEDLE_SANITATION

# =============================================================================
# VACCINE DATA - Prices per dose (normalised to per 1000 where needed)
# Format: {"Vaccine Name": (price, doses_per_pack, notes)}
# =============================================================================

# INOVO VACCINES - Can be injected in-ovo at day 18
INOVO_VACCINES = {
    "-- Select --": {"price_per_1000": 0.00, "notes": ""},
    "Nobilis Rismavac +CA126": {"price_per_1000": 18.26, "notes": "Marek's - £18.26/1000 doses"},
    "Nobilis Rismavac HIGH PFU": {"price_per_1000": 52.12, "notes": "Marek's High PFU - £52.12/1000 doses"},
    "Innovax ND-ILT": {"price_per_1000": 32.625, "notes": "Vector MD+ND+ILT - £65.25/2000 doses"},
    "Innovax ND-IBD": {"price_per_1000": 32.50, "notes": "Vector MD+ND+IBD - £65.00/2000 doses"},
    "Vectormune ND": {"price_per_1000": 24.94, "notes": "Vector MD+ND - £49.88/2000 doses"},
    "Transmune": {"price_per_1000": 12.63, "notes": "IBD Immune Complex - £25.26/2000 doses"},
}

# DAY OLD INJECTION VACCINES - Subcutaneous injection at hatch
DAY_OLD_INJECTION_VACCINES = {
    "-- Select --": {"price_per_1000": 0.00, "notes": ""},
    "Nobilis Rismavac +CA126": {"price_per_1000": 18.26, "notes": "Marek's - £18.26/1000 doses"},
    "Nobilis Rismavac HIGH PFU": {"price_per_1000": 52.12, "notes": "Marek's High PFU - £52.12/1000 doses"},
    "Innovax ND-ILT": {"price_per_1000": 32.625, "notes": "Vector MD+ND+ILT - £65.25/2000 doses"},
    "Innovax ND-IBD": {"price_per_1000": 32.50, "notes": "Vector MD+ND+IBD - £65.00/2000 doses"},
    "Vectormune ND": {"price_per_1000": 24.94, "notes": "Vector MD+ND - £49.88/2000 doses"},
    "Transmune": {"price_per_1000": 12.63, "notes": "IBD Immune Complex - £25.26/2000 doses"},
    "Reo": {"price_per_1000": 22.37, "notes": "Reovirus - £22.37/1000 doses"},
    "Lincocin": {"price_per_1000": 1.16, "notes": "Antibiotic - £23.11/100ml (20,000 doses)"},
}

# DAY OLD SPRAY VACCINES - Coarse spray at hatch
DAY_OLD_SPRAY_VACCINES = {
    "-- Select --": {"price_per_1000": 0.00, "notes": ""},
    "IB 4/91": {"price_per_1000": 5.376, "notes": "IB Variant - £26.88/5000 doses"},
    "IB Ma5": {"price_per_1000": 2.868, "notes": "IB Massachusetts - £14.34/5000 doses"},
    "IB Primer": {"price_per_1000": 4.828, "notes": "IB Primer - £24.14/5000 doses"},
    "IBird": {"price_per_1000": 4.132, "notes": "IB - £20.66/5000 doses"},
    "Evalon (1000 dose)": {"price_per_1000": 98.77, "notes": "Coccidiosis - £98.77/1000 doses"},
    "Evalon (5000 dose)": {"price_per_1000": 91.902, "notes": "Coccidiosis - £459.51/5000 doses"},
    "Paracox 8 (1000 dose)": {"price_per_1000": 112.75, "notes": "Coccidiosis - £112.75/1000 doses"},
    "Paracox 8 (5000 dose)": {"price_per_1000": 92.138, "notes": "Coccidiosis - £460.69/5000 doses"},
}

# Vector vaccines list (only ONE can be selected across all categories)
VECTOR_VACCINES = ["Innovax ND-ILT", "Innovax ND-IBD", "Vectormune ND"]

# =============================================================================
# INPUT SECTION
# =============================================================================

col_left, col_right = st.columns([1, 1])

with col_left:
    st.subheader("📊 Volume & Machine Settings")
    
    num_chicks = st.number_input(
        "Number of eggs/chicks to vaccinate",
        min_value=0,
        max_value=10_000_000,
        value=100_000,
        step=1000,
        help="Enter the total number for this batch"
    )
    
    monthly_egg_volume = st.number_input(
        "Monthly egg injection volume (for Inovo cost calculation)",
        min_value=1,
        max_value=10_000_000,
        value=500_000,
        step=10000,
        help="Used to calculate per-egg Inovo machine lease cost"
    )
    
    # Calculate Inovo cost per egg based on monthly volume
    inovo_cost_per_egg = INOVO_MONTHLY_LEASE / monthly_egg_volume
    
    st.info(f"**Inovo machine cost:** £{inovo_cost_per_egg:.5f}/egg (based on £{INOVO_MONTHLY_LEASE:,.0f}/month ÷ {monthly_egg_volume:,} eggs)")
    st.info(f"**Novatech injection cost:** £{NOVATECH_INJECTION_COST:.5f}/chick")

with col_right:
    st.subheader("🔧 Treatments")
    
    beak_treatment = st.checkbox(
        "☑️ Beak Treatment (Novatech IR)",
        help=f"Adds £{NOVATECH_BEAK_TREATMENT:.5f} per chick"
    )
    
    toe_treatment = st.checkbox(
        "☑️ Toe Treatment",
        help="Cost TBC - speak to boss"
    )
    
    if toe_treatment:
        st.warning("⚠️ Toe treatment selected - cost not yet configured")

st.markdown("---")

# =============================================================================
# VACCINE SELECTION
# =============================================================================

st.subheader("💉 Vaccine Selection")

# Track selected vector vaccines
selected_vectors = []

col1, col2, col3 = st.columns(3)

# INOVO COLUMN
with col1:
    st.markdown("### 🥚 In-Ovo Vaccination")
    st.caption("Injected at day 18 of incubation")
    
    inovo_1 = st.selectbox(
        "Inovo Vaccine 1",
        options=list(INOVO_VACCINES.keys()),
        key="inovo_1",
        help=INOVO_VACCINES.get(st.session_state.get("inovo_1", "-- Select --"), {}).get("notes", "")
    )
    
    inovo_2 = st.selectbox(
        "Inovo Vaccine 2", 
        options=list(INOVO_VACCINES.keys()),
        key="inovo_2"
    )
    
    # Track vectors
    if inovo_1 in VECTOR_VACCINES:
        selected_vectors.append(f"Inovo 1: {inovo_1}")
    if inovo_2 in VECTOR_VACCINES:
        selected_vectors.append(f"Inovo 2: {inovo_2}")

# DAY OLD INJECTION COLUMN
with col2:
    st.markdown("### 💉 Day-Old Injection")
    st.caption("Subcutaneous at hatch (Novatech)")
    
    day_old_inj_1 = st.selectbox(
        "Day Old Injection 1",
        options=list(DAY_OLD_INJECTION_VACCINES.keys()),
        key="day_old_inj_1"
    )
    
    day_old_inj_2 = st.selectbox(
        "Day Old Injection 2",
        options=list(DAY_OLD_INJECTION_VACCINES.keys()),
        key="day_old_inj_2"
    )
    
    # Track vectors
    if day_old_inj_1 in VECTOR_VACCINES:
        selected_vectors.append(f"Day Old Inj 1: {day_old_inj_1}")
    if day_old_inj_2 in VECTOR_VACCINES:
        selected_vectors.append(f"Day Old Inj 2: {day_old_inj_2}")

# DAY OLD SPRAY COLUMN  
with col3:
    st.markdown("### 🌫️ Day-Old Spray")
    st.caption("Coarse spray at hatch (no machine cost)")
    
    day_old_spray_1 = st.selectbox(
        "Day Old Spray 1",
        options=list(DAY_OLD_SPRAY_VACCINES.keys()),
        key="day_old_spray_1"
    )
    
    day_old_spray_2 = st.selectbox(
        "Day Old Spray 2",
        options=list(DAY_OLD_SPRAY_VACCINES.keys()),
        key="day_old_spray_2"
    )

# Vector warning
if len(selected_vectors) > 1:
    st.error(f"⚠️ **VECTOR CONFLICT!** Only ONE vector vaccine can be used. You have selected: {', '.join(selected_vectors)}")

st.markdown("---")

# =============================================================================
# CALCULATIONS
# =============================================================================

multiplier = num_chicks / 1000

# Vaccine costs
inovo_1_vaccine_cost = INOVO_VACCINES[inovo_1]["price_per_1000"] * multiplier
inovo_2_vaccine_cost = INOVO_VACCINES[inovo_2]["price_per_1000"] * multiplier

day_old_inj_1_vaccine_cost = DAY_OLD_INJECTION_VACCINES[day_old_inj_1]["price_per_1000"] * multiplier
day_old_inj_2_vaccine_cost = DAY_OLD_INJECTION_VACCINES[day_old_inj_2]["price_per_1000"] * multiplier

day_old_spray_1_vaccine_cost = DAY_OLD_SPRAY_VACCINES[day_old_spray_1]["price_per_1000"] * multiplier
day_old_spray_2_vaccine_cost = DAY_OLD_SPRAY_VACCINES[day_old_spray_2]["price_per_1000"] * multiplier

# Machine/application costs
# Inovo machine cost applies if ANY inovo vaccine selected
inovo_selected = inovo_1 != "-- Select --" or inovo_2 != "-- Select --"
inovo_machine_cost = (inovo_cost_per_egg * num_chicks) if inovo_selected else 0

# Novatech machine cost applies if ANY day old injection vaccine selected
day_old_inj_selected = day_old_inj_1 != "-- Select --" or day_old_inj_2 != "-- Select --"
novatech_machine_cost = (NOVATECH_INJECTION_COST * num_chicks) if day_old_inj_selected else 0

# Beak treatment cost
beak_cost = (NOVATECH_BEAK_TREATMENT * num_chicks) if beak_treatment else 0

# Toe treatment cost (TBC)
toe_cost = 0  # Cost not yet defined

# Spray has no machine cost
spray_machine_cost = 0

# Totals by category
total_inovo_vaccines = inovo_1_vaccine_cost + inovo_2_vaccine_cost
total_day_old_inj_vaccines = day_old_inj_1_vaccine_cost + day_old_inj_2_vaccine_cost
total_spray_vaccines = day_old_spray_1_vaccine_cost + day_old_spray_2_vaccine_cost

total_vaccines = total_inovo_vaccines + total_day_old_inj_vaccines + total_spray_vaccines
total_machine_costs = inovo_machine_cost + novatech_machine_cost
total_treatments = beak_cost + toe_cost

grand_total = total_vaccines + total_machine_costs + total_treatments

# Cost per chick
cost_per_chick = grand_total / num_chicks if num_chicks > 0 else 0

# =============================================================================
# RESULTS SECTION
# =============================================================================

st.subheader("💰 Cost Breakdown")

res_col1, res_col2, res_col3 = st.columns(3)

with res_col1:
    st.markdown("**🥚 In-Ovo**")
    if inovo_1 != "-- Select --":
        st.write(f"• {inovo_1}: £{inovo_1_vaccine_cost:,.2f}")
    if inovo_2 != "-- Select --":
        st.write(f"• {inovo_2}: £{inovo_2_vaccine_cost:,.2f}")
    if inovo_selected:
        st.write(f"• Machine lease: £{inovo_machine_cost:,.2f}")
    st.write(f"**Subtotal: £{total_inovo_vaccines + inovo_machine_cost:,.2f}**")

with res_col2:
    st.markdown("**💉 Day-Old Injection**")
    if day_old_inj_1 != "-- Select --":
        st.write(f"• {day_old_inj_1}: £{day_old_inj_1_vaccine_cost:,.2f}")
    if day_old_inj_2 != "-- Select --":
        st.write(f"• {day_old_inj_2}: £{day_old_inj_2_vaccine_cost:,.2f}")
    if day_old_inj_selected:
        st.write(f"• Novatech (cradle/inject/sanit): £{novatech_machine_cost:,.2f}")
    if beak_treatment:
        st.write(f"• Beak treatment: £{beak_cost:,.2f}")
    if toe_treatment:
        st.write(f"• Toe treatment: £{toe_cost:,.2f} (TBC)")
    st.write(f"**Subtotal: £{total_day_old_inj_vaccines + novatech_machine_cost + beak_cost + toe_cost:,.2f}**")

with res_col3:
    st.markdown("**🌫️ Day-Old Spray**")
    if day_old_spray_1 != "-- Select --":
        st.write(f"• {day_old_spray_1}: £{day_old_spray_1_vaccine_cost:,.2f}")
    if day_old_spray_2 != "-- Select --":
        st.write(f"• {day_old_spray_2}: £{day_old_spray_2_vaccine_cost:,.2f}")
    st.write("• Application: Free")
    st.write(f"**Subtotal: £{total_spray_vaccines:,.2f}**")

st.markdown("---")

# Grand total display
total_col1, total_col2, total_col3 = st.columns(3)

with total_col1:
    st.metric(
        label="Total Vaccine Cost",
        value=f"£{total_vaccines:,.2f}"
    )

with total_col2:
    st.metric(
        label="Total Machine/Application Cost", 
        value=f"£{total_machine_costs + total_treatments:,.2f}"
    )

with total_col3:
    st.metric(
        label="Grand Total",
        value=f"£{grand_total:,.2f}",
        delta=f"£{cost_per_chick:.4f} per chick"
    )

# =============================================================================
# DETAILED BREAKDOWN TABLE
# =============================================================================

st.markdown("---")
with st.expander("📋 Detailed Cost Per Chick Breakdown"):
    st.markdown("### Per-Chick Cost Analysis")
    
    breakdown_data = []
    
    if inovo_1 != "-- Select --":
        breakdown_data.append(("Inovo: " + inovo_1, INOVO_VACCINES[inovo_1]["price_per_1000"] / 1000))
    if inovo_2 != "-- Select --":
        breakdown_data.append(("Inovo: " + inovo_2, INOVO_VACCINES[inovo_2]["price_per_1000"] / 1000))
    if inovo_selected:
        breakdown_data.append(("Inovo Machine Lease", inovo_cost_per_egg))
        
    if day_old_inj_1 != "-- Select --":
        breakdown_data.append(("Day Old Inj: " + day_old_inj_1, DAY_OLD_INJECTION_VACCINES[day_old_inj_1]["price_per_1000"] / 1000))
    if day_old_inj_2 != "-- Select --":
        breakdown_data.append(("Day Old Inj: " + day_old_inj_2, DAY_OLD_INJECTION_VACCINES[day_old_inj_2]["price_per_1000"] / 1000))
    if day_old_inj_selected:
        breakdown_data.append(("Novatech Cradle Count", NOVATECH_CRADLE_COUNT))
        breakdown_data.append(("Novatech Roller Inject", NOVATECH_ROLLER_INJECT))
        breakdown_data.append(("Novatech Needle Sanitation", NOVATECH_NEEDLE_SANITATION))
    if beak_treatment:
        breakdown_data.append(("Beak Treatment", NOVATECH_BEAK_TREATMENT))
        
    if day_old_spray_1 != "-- Select --":
        breakdown_data.append(("Spray: " + day_old_spray_1, DAY_OLD_SPRAY_VACCINES[day_old_spray_1]["price_per_1000"] / 1000))
    if day_old_spray_2 != "-- Select --":
        breakdown_data.append(("Spray: " + day_old_spray_2, DAY_OLD_SPRAY_VACCINES[day_old_spray_2]["price_per_1000"] / 1000))
    
    if breakdown_data:
        for item, cost in breakdown_data:
            st.write(f"• {item}: £{cost:.5f}")
        st.write(f"**Total per chick: £{cost_per_chick:.5f}**")
    else:
        st.write("No vaccines selected")

# =============================================================================
# FOOTER
# =============================================================================

st.markdown("---")
st.caption("""
**Notes:**
- Inovo machine cost based on Zoetis lease (£6,125/month) divided by monthly egg volume
- Novatech costs converted from USD at rate of 0.79
- Vector vaccines (Innovax ND-ILT, Innovax ND-IBD, Vectormune ND) - only ONE can be used
- Spray application has no machine cost
- Toe treatment cost TBC
""")
