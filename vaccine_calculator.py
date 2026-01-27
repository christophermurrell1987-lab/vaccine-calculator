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
# CONFIGURATION - HATCHERY FACTORS
# =============================================================================

# Egg to chick conversion factor (accounts for infertility, mortality, sexing)
EGG_TO_CHICK_FACTOR = 2.5  # 2.5 eggs injected per saleable chick

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
# VACCINE DATA
# =============================================================================

# INOVO VACCINES
INOVO_VACCINES = {
    "-- Select --": {"price_per_1000": 0.00, "notes": ""},
    "Nobilis Rismavac +CA126": {"price_per_1000": 18.26, "notes": "Marek's - £18.26/1000 doses"},
    "Nobilis Rismavac HIGH PFU": {"price_per_1000": 52.12, "notes": "Marek's High PFU - £52.12/1000 doses"},
    "Innovax ND-ILT": {"price_per_1000": 32.625, "notes": "Vector MD+ND+ILT - £65.25/2000 doses"},
    "Innovax ND-IBD": {"price_per_1000": 32.50, "notes": "Vector MD+ND+IBD - £65.00/2000 doses"},
    "Vectormune ND": {"price_per_1000": 24.94, "notes": "Vector MD+ND - £49.88/2000 doses"},
    "Transmune": {"price_per_1000": 12.63, "notes": "IBD Immune Complex - £25.26/2000 doses"},
}

# DAY OLD INJECTION VACCINES
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

# DAY OLD SPRAY VACCINES
DAY_OLD_SPRAY_VACCINES = {
    "-- Select --": {"price_per_1000": 0.00, "notes": ""},
    "IB 4/91": {"price_per_1000": 5.376, "notes": "IB Variant - £26.88/5000 doses"},
    "IB Ma5": {"price_per_1000": 2.868, "notes": "IB Massachusetts - £14.34/5000 doses"},
    "IB Primer": {"price_per_1000": 4.828, "notes": "IB Primer - £24.14/5000 doses"},
    "IBird": {"price_per_1000": 4.132, "notes": "IB - £20.66/5000 doses"},
    "Evalon": {"price_per_1000": 95.34, "notes": "Coccidiosis - avg £95.34/1000 doses"},
    "Paracox 8": {"price_per_1000": 102.44, "notes": "Coccidiosis - avg £102.44/1000 doses"},
}

# DISEASE PROTECTION MAPPING
# Maps vaccine names to the list of diseases they cover
VACCINE_PROTECTION = {
    "Nobilis Rismavac +CA126": ["Marek's Disease (Standard)"],
    "Nobilis Rismavac HIGH PFU": ["Marek's Disease (High Potency)"],
    "Innovax ND-ILT": ["Marek's Disease", "Newcastle Disease (ND)", "Inf. Laryngotracheitis (ILT)"],
    "Innovax ND-IBD": ["Marek's Disease", "Newcastle Disease (ND)", "Gumboro (IBD)"],
    "Vectormune ND": ["Marek's Disease", "Newcastle Disease (ND)"],
    "Transmune": ["Gumboro (IBD)"],
    "Reo": ["Reovirus (Viral Arthritis)"],
    "Lincocin": ["Bacterial Infections (Antibiotic Only)"],
    "IB 4/91": ["IB (Variant 4-91)"],
    "IB Ma5": ["IB (Classic Mass)"],
    "IB Primer": ["IB (Mass + Variant)"],
    "IBird": ["IB (Variant)"],
    "Evalon": ["Coccidiosis (Long Life)"],
    "Paracox 8": ["Coccidiosis (Standard)"]
}

# Vector vaccines list
VECTOR_VACCINES = ["Innovax ND-ILT", "Innovax ND-IBD", "Vectormune ND"]

# =============================================================================
# INPUT SECTION
# =============================================================================

col_left, col_right = st.columns([1, 1])

with col_left:
    st.subheader("📊 Volume & Machine Settings")
    
    num_chicks = st.number_input(
        "Number of chicks for order (saleable chicks)",
        min_value=0,
        max_value=10_000_000,
        value=100_000,
        step=1000,
    )
    
    inovo_multiplier = st.number_input(
        "In-ovo egg multiplier",
        min_value=1.0,
        max_value=5.0,
        value=2.5,
        step=0.1,
    )
    
    eggs_for_inovo = int(num_chicks * inovo_multiplier)
    
    monthly_egg_volume = st.number_input(
        "Monthly egg injection volume (for Inovo cost calc)",
        min_value=1,
        max_value=10_000_000,
        value=500_000,
        step=10000,
    )
    
    inovo_cost_per_egg = INOVO_MONTHLY_LEASE / monthly_egg_volume
    
    st.success(f"**Chicks:** {num_chicks:,} | **Eggs for in-ovo:** {eggs_for_inovo:,}")

with col_right:
    st.subheader("🔧 Treatments")
    
    beak_treatment = st.checkbox("Beak Treatment (Novatech IR)")
    toe_treatment = st.checkbox("Toe Treatment")
    
    if toe_treatment:
        st.warning("⚠️ Toe treatment cost not yet configured")

st.markdown("---")

# =============================================================================
# VACCINE SELECTION
# =============================================================================

st.subheader("💉 Vaccine Selection")

selected_vectors = []

col1, col2, col3 = st.columns(3)

# INOVO COLUMN
with col1:
    st.markdown("### 🥚 In-Ovo Vaccination")
    inovo_1 = st.selectbox("Inovo Vaccine 1", options=list(INOVO_VACCINES.keys()), key="inovo_1")
    inovo_2 = st.selectbox("Inovo Vaccine 2", options=list(INOVO_VACCINES.keys()), key="inovo_2")
    inovo_3 = st.selectbox("Inovo Vaccine 3", options=list(INOVO_VACCINES.keys()), key="inovo_3")
    
    # Track vectors
    for v in [inovo_1, inovo_2, inovo_3]:
        if v in VECTOR_VACCINES: selected_vectors.append(f"Inovo: {v}")

# DAY OLD INJECTION COLUMN
with col2:
    st.markdown("### 💉 Day-Old Injection")
    day_old_inj_1 = st.selectbox("Day Old Inj 1", options=list(DAY_OLD_INJECTION_VACCINES.keys()), key="do_1")
    day_old_inj_2 = st.selectbox("Day Old Inj 2", options=list(DAY_OLD_INJECTION_VACCINES.keys()), key="do_2")
    day_old_inj_3 = st.selectbox("Day Old Inj 3", options=list(DAY_OLD_INJECTION_VACCINES.keys()), key="do_3")
    
    # Track vectors
    for v in [day_old_inj_1, day_old_inj_2, day_old_inj_3]:
        if v in VECTOR_VACCINES: selected_vectors.append(f"Day Old: {v}")

# DAY OLD SPRAY COLUMN  
with col3:
    st.markdown("### 🌫️ Day-Old Spray")
    day_old_spray_1 = st.selectbox("Spray 1", options=list(DAY_OLD_SPRAY_VACCINES.keys()), key="sp_1")
    day_old_spray_2 = st.selectbox("Spray 2", options=list(DAY_OLD_SPRAY_VACCINES.keys()), key="sp_2")
    day_old_spray_3 = st.selectbox("Spray 3", options=list(DAY_OLD_SPRAY_VACCINES.keys()), key="sp_3")

# Vector warning
if len(selected_vectors) > 1:
    st.error(f"⚠️ **VECTOR CONFLICT!** Only ONE vector vaccine can be used. Selected: {', '.join(selected_vectors)}")

# Interference warning
all_selected = [inovo_1, inovo_2, inovo_3, day_old_inj_1, day_old_inj_2, day_old_inj_3]
has_ca126 = any("CA126" in vax for vax in all_selected)
has_innovax = any("Innovax" in vax for vax in all_selected)

if has_ca126 and has_innovax:
    st.warning("⚠️ **HVT INTERFERENCE:** CA126 may interfere with Innovax. Use Rismavac HIGH PFU instead.")

st.markdown("---")

# =============================================================================
# CALCULATIONS
# =============================================================================

# Multipliers
inovo_multiplier_doses = eggs_for_inovo / 1000
chick_multiplier_doses = num_chicks / 1000

# Function to get cost
def get_cost(vax_name, category_dict, mult):
    if vax_name == "-- Select --": return 0
    return category_dict[vax_name]["price_per_1000"] * mult

# Totals
total_inovo_vaccines = sum([get_cost(v, INOVO_VACCINES, inovo_multiplier_doses) for v in [inovo_1, inovo_2, inovo_3]])
total_day_old_inj_vaccines = sum([get_cost(v, DAY_OLD_INJECTION_VACCINES, chick_multiplier_doses) for v in [day_old_inj_1, day_old_inj_2, day_old_inj_3]])
total_spray_vaccines = sum([get_cost(v, DAY_OLD_SPRAY_VACCINES, chick_multiplier_doses) for v in [day_old_spray_1, day_old_spray_2, day_old_spray_3]])

# Machine Costs
inovo_selected = any(v != "-- Select --" for v in [inovo_1, inovo_2, inovo_3])
inovo_machine_cost = (inovo_cost_per_egg * eggs_for_inovo) if inovo_selected else 0

day_old_inj_selected = any(v != "-- Select --" for v in [day_old_inj_1, day_old_inj_2, day_old_inj_3])
novatech_machine_cost = (NOVATECH_INJECTION_COST * num_chicks) if day_old_inj_selected else 0

beak_cost = (NOVATECH_BEAK_TREATMENT * num_chicks) if beak_treatment else 0
toe_cost = 0

grand_total = total_inovo_vaccines + total_day_old_inj_vaccines + total_spray_vaccines + inovo_machine_cost + novatech_machine_cost + beak_cost + toe_cost
cost_per_chick = grand_total / num_chicks if num_chicks > 0 else 0

# =============================================================================
# RESULTS DISPLAY
# =============================================================================

# Grand total display
total_col1, total_col2, total_col3 = st.columns(3)
with total_col1:
    st.metric("Total Vaccine Cost", f"£{total_inovo_vaccines + total_day_old_inj_vaccines + total_spray_vaccines:,.2f}")
with total_col2:
    st.metric("Total Machine/App Cost", f"£{inovo_machine_cost + novatech_machine_cost + beak_cost + toe_cost:,.2f}")
with total_col3:
    st.metric("Grand Total", f"£{grand_total:,.2f}", delta=f"£{cost_per_chick:.4f} per chick")

st.markdown("---")

# =============================================================================
# 🛡️ PROTECTION SUMMARY (NEW SECTION)
# =============================================================================

st.subheader("🛡️ Protection Summary")
st.caption("Based on selected vaccines, the flock will have protection against:")

# Collect all diseases from all selected vaccines
diseases_covered = set()
all_selected_vaccines = [inovo_1, inovo_2, inovo_3, day_old_inj_1, day_old_inj_2, day_old_inj_3, day_old_spray_1, day_old_spray_2, day_old_spray_3]

for vax in all_selected_vaccines:
    if vax in VACCINE_PROTECTION:
        for disease in VACCINE_PROTECTION[vax]:
            diseases_covered.add(disease)

if diseases_covered:
    # Organize into columns for cleaner look
    prot_cols = st.columns(4)
    sorted_diseases = sorted(list(diseases_covered))
    
    for i, disease in enumerate(sorted_diseases):
        col_index = i % 4
        with prot_cols[col_index]:
            if "Marek's" in disease:
                st.success(f"**{disease}**")
            elif "Newcastle" in disease or "ND" in disease:
                st.info(f"**{disease}**")
            elif "IB" in disease or "Bronchitis" in disease:
                st.warning(f"**{disease}**")
            else:
                st.write(f"✅ **{disease}**")
else:
    st.info("No vaccines selected yet.")

# =============================================================================
# DETAILED BREAKDOWN
# =============================================================================

with st.expander("📋 Click for Detailed Cost Breakdown"):
    st.write("Detailed line-by-line costs...")
    # (Reusing previous logic for brevity in display, but calculations remain same)
    if inovo_selected: st.write(f"Inovo Machine: £{inovo_machine_cost:,.2f}")
    if day_old_inj_selected: st.write(f"Novatech Machine: £{novatech_machine_cost:,.2f}")
    st.write(f"**Total Cost per Chick: £{cost_per_chick:.5f}**")