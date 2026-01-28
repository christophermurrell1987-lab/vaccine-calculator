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
    "Evalon": ["Coccidiosis (5-Strain Core Protection)"],
    "Paracox 8": ["Coccidiosis (8-Strain Broad Spectrum)"]
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
    inovo_1_double = st.checkbox("2x Dose", key="inovo_1_dd", disabled=(inovo_1 == "-- Select --"))
    
    inovo_2 = st.selectbox("Inovo Vaccine 2", options=list(INOVO_VACCINES.keys()), key="inovo_2")
    inovo_2_double = st.checkbox("2x Dose", key="inovo_2_dd", disabled=(inovo_2 == "-- Select --"))
    
    inovo_3 = st.selectbox("Inovo Vaccine 3", options=list(INOVO_VACCINES.keys()), key="inovo_3")
    inovo_3_double = st.checkbox("2x Dose", key="inovo_3_dd", disabled=(inovo_3 == "-- Select --"))
    
    inovo_4 = st.selectbox("Inovo Vaccine 4", options=list(INOVO_VACCINES.keys()), key="inovo_4")
    inovo_4_double = st.checkbox("2x Dose", key="inovo_4_dd", disabled=(inovo_4 == "-- Select --"))
    
    # Track vectors
    for v in [inovo_1, inovo_2, inovo_3, inovo_4]:
        if v in VECTOR_VACCINES: selected_vectors.append(f"Inovo: {v}")

# DAY OLD INJECTION COLUMN
with col2:
    st.markdown("### 💉 Day-Old Injection")
    
    day_old_inj_1 = st.selectbox("Day Old Inj 1", options=list(DAY_OLD_INJECTION_VACCINES.keys()), key="do_1")
    do_1_double = st.checkbox("2x Dose", key="do_1_dd", disabled=(day_old_inj_1 == "-- Select --"))
    
    day_old_inj_2 = st.selectbox("Day Old Inj 2", options=list(DAY_OLD_INJECTION_VACCINES.keys()), key="do_2")
    do_2_double = st.checkbox("2x Dose", key="do_2_dd", disabled=(day_old_inj_2 == "-- Select --"))
    
    day_old_inj_3 = st.selectbox("Day Old Inj 3", options=list(DAY_OLD_INJECTION_VACCINES.keys()), key="do_3")
    do_3_double = st.checkbox("2x Dose", key="do_3_dd", disabled=(day_old_inj_3 == "-- Select --"))
    
    day_old_inj_4 = st.selectbox("Day Old Inj 4", options=list(DAY_OLD_INJECTION_VACCINES.keys()), key="do_4")
    do_4_double = st.checkbox("2x Dose", key="do_4_dd", disabled=(day_old_inj_4 == "-- Select --"))
    
    # Track vectors
    for v in [day_old_inj_1, day_old_inj_2, day_old_inj_3, day_old_inj_4]:
        if v in VECTOR_VACCINES: selected_vectors.append(f"Day Old: {v}")

# DAY OLD SPRAY COLUMN  
with col3:
    st.markdown("### 🌫️ Day-Old Spray")
    day_old_spray_1 = st.selectbox("Spray 1", options=list(DAY_OLD_SPRAY_VACCINES.keys()), key="sp_1")
    day_old_spray_2 = st.selectbox("Spray 2", options=list(DAY_OLD_SPRAY_VACCINES.keys()), key="sp_2")
    day_old_spray_3 = st.selectbox("Spray 3", options=list(DAY_OLD_SPRAY_VACCINES.keys()), key="sp_3")
    day_old_spray_4 = st.selectbox("Spray 4", options=list(DAY_OLD_SPRAY_VACCINES.keys()), key="sp_4")

# Vector warning
if len(selected_vectors) > 1:
    st.error(f"⚠️ **VECTOR CONFLICT!** Only ONE vector vaccine can be used. Selected: {', '.join(selected_vectors)}")

# Interference warning
all_selected = [inovo_1, inovo_2, inovo_3, inovo_4, day_old_inj_1, day_old_inj_2, day_old_inj_3, day_old_inj_4]
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

# Function to get cost with double dose support
def get_cost(vax_name, category_dict, mult, is_double=False):
    if vax_name == "-- Select --": return 0
    base_cost = category_dict[vax_name]["price_per_1000"] * mult
    return base_cost * 2 if is_double else base_cost

# Inovo vaccine costs (with double dose multipliers)
inovo_costs = [
    get_cost(inovo_1, INOVO_VACCINES, inovo_multiplier_doses, inovo_1_double),
    get_cost(inovo_2, INOVO_VACCINES, inovo_multiplier_doses, inovo_2_double),
    get_cost(inovo_3, INOVO_VACCINES, inovo_multiplier_doses, inovo_3_double),
    get_cost(inovo_4, INOVO_VACCINES, inovo_multiplier_doses, inovo_4_double),
]
total_inovo_vaccines = sum(inovo_costs)

# Day old injection costs (with double dose multipliers)
do_inj_costs = [
    get_cost(day_old_inj_1, DAY_OLD_INJECTION_VACCINES, chick_multiplier_doses, do_1_double),
    get_cost(day_old_inj_2, DAY_OLD_INJECTION_VACCINES, chick_multiplier_doses, do_2_double),
    get_cost(day_old_inj_3, DAY_OLD_INJECTION_VACCINES, chick_multiplier_doses, do_3_double),
    get_cost(day_old_inj_4, DAY_OLD_INJECTION_VACCINES, chick_multiplier_doses, do_4_double),
]
total_day_old_inj_vaccines = sum(do_inj_costs)

# Spray costs (no double dose for spray)
total_spray_vaccines = sum([get_cost(v, DAY_OLD_SPRAY_VACCINES, chick_multiplier_doses) for v in [day_old_spray_1, day_old_spray_2, day_old_spray_3, day_old_spray_4]])

# Machine Costs
inovo_selected = any(v != "-- Select --" for v in [inovo_1, inovo_2, inovo_3, inovo_4])
inovo_machine_cost = (inovo_cost_per_egg * eggs_for_inovo) if inovo_selected else 0

day_old_inj_selected = any(v != "-- Select --" for v in [day_old_inj_1, day_old_inj_2, day_old_inj_3, day_old_inj_4])
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
# 🛡️ PROTECTION SUMMARY
# =============================================================================

st.subheader("🛡️ Protection Summary")

# Build a dict of disease -> list of vaccines providing it
all_selected_vaccines = [
    ("Inovo", inovo_1), ("Inovo", inovo_2), ("Inovo", inovo_3), ("Inovo", inovo_4),
    ("Day Old Inj", day_old_inj_1), ("Day Old Inj", day_old_inj_2), ("Day Old Inj", day_old_inj_3), ("Day Old Inj", day_old_inj_4),
    ("Spray", day_old_spray_1), ("Spray", day_old_spray_2), ("Spray", day_old_spray_3), ("Spray", day_old_spray_4)
]

disease_to_vaccines = {}
for method, vax in all_selected_vaccines:
    if vax in VACCINE_PROTECTION:
        for disease in VACCINE_PROTECTION[vax]:
            if disease not in disease_to_vaccines:
                disease_to_vaccines[disease] = []
            disease_to_vaccines[disease].append(f"{vax} ({method})")

# Define disease categories for logical grouping
DISEASE_CATEGORIES = {
    "Marek's Disease": ["Marek's Disease", "Marek's Disease (Standard)", "Marek's Disease (High Potency)"],
    "Newcastle Disease": ["Newcastle Disease (ND)"],
    "Infectious Bronchitis": ["IB (Variant 4-91)", "IB (Classic Mass)", "IB (Mass + Variant)", "IB (Variant)"],
    "Gumboro (IBD)": ["Gumboro (IBD)"],
    "Inf. Laryngotracheitis": ["Inf. Laryngotracheitis (ILT)"],
    "Reovirus": ["Reovirus (Viral Arthritis)"],
    "Coccidiosis": ["Coccidiosis (5-Strain Core Protection)", "Coccidiosis (8-Strain Broad Spectrum)"],
    "Bacterial": ["Bacterial Infections (Antibiotic Only)"],
}

if disease_to_vaccines:
    # Build table data
    table_rows = []
    
    for category, diseases in DISEASE_CATEGORIES.items():
        for disease in diseases:
            if disease in disease_to_vaccines:
                vaccines = disease_to_vaccines[disease]
                table_rows.append({
                    "Category": category,
                    "Protection": disease,
                    "Provided By": ", ".join(vaccines)
                })
    
    if table_rows:
        import pandas as pd
        df = pd.DataFrame(table_rows)
        
        # Style the dataframe
        st.dataframe(
            df,
            column_config={
                "Category": st.column_config.TextColumn("Category", width="medium"),
                "Protection": st.column_config.TextColumn("Disease Protection", width="large"),
                "Provided By": st.column_config.TextColumn("Vaccine (Method)", width="large"),
            },
            hide_index=True,
            use_container_width=True
        )
        
        # Quick visual summary underneath
        st.markdown("---")
        st.caption("**Coverage Summary**")
        
        # Count unique categories covered
        categories_covered = set(row["Category"] for row in table_rows)
        
        summary_cols = st.columns(len(categories_covered))
        for i, cat in enumerate(categories_covered):
            with summary_cols[i]:
                count = len([r for r in table_rows if r["Category"] == cat])
                if "Marek" in cat:
                    st.markdown(f"🛡️ **{cat}** ({count})")
                elif "Newcastle" in cat or "Laryngo" in cat:
                    st.markdown(f"🧬 **{cat}**")
                elif "Bronchitis" in cat:
                    st.markdown(f"🌬️ **{cat}** ({count})")
                elif "Cocci" in cat:
                    st.markdown(f"🦠 **{cat}**")
                else:
                    st.markdown(f"✅ **{cat}**")
    else:
        st.info("No vaccines selected yet.")
else:
    st.info("No vaccines selected yet.")

# =============================================================================
# DETAILED BREAKDOWN
# =============================================================================

with st.expander("📋 Click for Detailed Cost Breakdown"):
    st.write("Detailed line-by-line costs...")
    
    breakdown_data = []
    
    # INOVO
    inovo_vaccines_list = [
        (inovo_1, inovo_1_double),
        (inovo_2, inovo_2_double),
        (inovo_3, inovo_3_double),
        (inovo_4, inovo_4_double),
    ]
    for vax, is_double in inovo_vaccines_list:
        if vax != "-- Select --":
            cost = INOVO_VACCINES[vax]["price_per_1000"] * inovo_multiplier_doses
            if is_double:
                cost *= 2
            label = f"Inovo: {vax}" + (" (2x DOSE)" if is_double else "")
            breakdown_data.append((label, cost))
    if inovo_selected:
        breakdown_data.append(("Inovo Machine Lease", inovo_machine_cost))

    # DAY OLD INJ
    do_vaccines_list = [
        (day_old_inj_1, do_1_double),
        (day_old_inj_2, do_2_double),
        (day_old_inj_3, do_3_double),
        (day_old_inj_4, do_4_double),
    ]
    for vax, is_double in do_vaccines_list:
        if vax != "-- Select --":
            cost = DAY_OLD_INJECTION_VACCINES[vax]["price_per_1000"] * chick_multiplier_doses
            if is_double:
                cost *= 2
            label = f"Day Old Inj: {vax}" + (" (2x DOSE)" if is_double else "")
            breakdown_data.append((label, cost))
    if day_old_inj_selected:
        breakdown_data.append(("Novatech Machine Costs", novatech_machine_cost))
    
    # SPRAY
    for vax in [day_old_spray_1, day_old_spray_2, day_old_spray_3, day_old_spray_4]:
        if vax != "-- Select --":
            cost = DAY_OLD_SPRAY_VACCINES[vax]["price_per_1000"] * chick_multiplier_doses
            breakdown_data.append((f"Spray: {vax}", cost))
        
    # TREATMENTS
    if beak_treatment:
        breakdown_data.append(("Beak Treatment", beak_cost))

    # DISPLAY
    for name, cost in breakdown_data:
        per_chick = cost / num_chicks if num_chicks > 0 else 0
        st.write(f"• **{name}**: £{cost:,.2f} (£{per_chick:.5f}/chick)")
    
    st.markdown("---")
    st.write(f"**Total Cost per Chick: £{cost_per_chick:.5f}**")
