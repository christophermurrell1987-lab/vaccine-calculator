# Hatchery Vaccine Pricing Calculator
# Run with: streamlit run vaccine_calculator.py

import streamlit as st
import pandas as pd

# ============================================
# PAGE CONFIG
# ============================================
st.set_page_config(
    page_title="Hatchery Vaccine Pricing Calculator",
    page_icon="🐣",
    layout="wide",
)

# ============================================
# CONSTANTS
# ============================================

PLACEHOLDER = "-- Select --"

# Egg-to-chick conversion (accounts for infertility, mortality, sexing)
DEFAULT_EGG_TO_CHICK_FACTOR = 2.5

# Zoetis Inovo monthly lease (GBP)
INOVO_MONTHLY_LEASE = 6125.00

# Novatech Day-Old costs (USD → GBP)
USD_TO_GBP = 0.79
NOVATECH_CRADLE_COUNT = 0.00655 * USD_TO_GBP       # £0.00518 / chick
NOVATECH_ROLLER_INJECT = 0.00545 * USD_TO_GBP      # £0.00431 / chick
NOVATECH_NEEDLE_SANITATION = 0.00214 * USD_TO_GBP   # £0.00169 / chick
NOVATECH_BEAK_TREATMENT = 0.00987 * USD_TO_GBP      # £0.00780 / chick

# Combined per-chick injection cost (excluding beak)
NOVATECH_INJECTION_COST = (
    NOVATECH_CRADLE_COUNT + NOVATECH_ROLLER_INJECT + NOVATECH_NEEDLE_SANITATION
)

# ============================================
# VACCINE CATALOGUE (single source of truth)
# ============================================
# Each vaccine is defined once. The "categories" field controls which
# selection columns it appears in: "inovo", "day_old_inj", "spray".

VACCINE_CATALOGUE = {
    "Nobilis Rismavac +CA126": {
        "price_per_1000": 16.92,
        "notes": "Marek's - £16.92/1000 doses",
        "categories": ["inovo", "day_old_inj"],
        "protection": ["Marek's Disease (Standard)"],
    },
    "Nobilis Rismavac HIGH PFU": {
        "price_per_1000": 45.09,
        "notes": "Marek's High PFU - £45.09/1000 doses",
        "categories": ["inovo", "day_old_inj"],
        "protection": ["Marek's Disease (High Potency)"],
    },
    "Innovax ND-ILT": {
        "price_per_1000": 33.83,
        "notes": "Vector MD+ND+ILT - £67.66/2000 doses",
        "categories": ["inovo", "day_old_inj"],
        "protection": ["Marek's Disease", "Newcastle Disease (ND)", "Inf. Laryngotracheitis (ILT)"],
        "is_vector": True,
    },
    "Innovax ND-IBD": {
        "price_per_1000": 33.475,
        "notes": "Vector MD+ND+IBD - £66.95/2000 doses",
        "categories": ["inovo", "day_old_inj"],
        "protection": ["Marek's Disease", "Newcastle Disease (ND)", "Gumboro (IBD)"],
        "is_vector": True,
    },
    "Innovax ILT-IBD": {
        "price_per_1000": 35.195,
        "notes": "Vector MD+ILT+IBD - £70.39/2000 doses",
        "categories": ["inovo", "day_old_inj"],
        "protection": ["Marek's Disease", "Inf. Laryngotracheitis (ILT)", "Gumboro (IBD)"],
        "is_vector": True,
    },
    "Vectormune ND": {
        "price_per_1000": 24.94,
        "notes": "Vector MD+ND - £49.88/2000 doses",
        "categories": ["inovo", "day_old_inj"],
        "protection": ["Marek's Disease", "Newcastle Disease (ND)"],
        "is_vector": True,
    },
    "Transmune": {
        "price_per_1000": 12.63,
        "notes": "IBD Immune Complex - £25.26/2000 doses",
        "categories": ["inovo", "day_old_inj"],
        "protection": ["Gumboro (IBD)"],
    },
    "Reo": {
        "price_per_1000": 22.37,
        "notes": "Reovirus - £22.37/1000 doses",
        "categories": ["day_old_inj"],
        "protection": ["Reovirus (Viral Arthritis)"],
    },
    "Lincocin": {
        "price_per_1000": 1.16,
        "notes": "Antibiotic - £23.11/100ml (20,000 doses)",
        "categories": ["day_old_inj"],
        "protection": ["Bacterial Infections (Antibiotic Only)"],
    },
    "IB 4/91": {
        "price_per_1000": 4.748,
        "notes": "IB Variant - £56.97/12x1000 doses",
        "categories": ["spray"],
        "protection": ["IB (Variant 4-91)"],
    },
    "IB Ma5": {
        "price_per_1000": 2.665,
        "notes": "IB Massachusetts - £31.98/12x1000 doses",
        "categories": ["spray"],
        "protection": ["IB (Classic Mass)"],
    },
    "IB Primer": {
        "price_per_1000": 4.828,
        "notes": "IB Primer - £24.14/5000 doses",
        "categories": ["spray"],
        "protection": ["IB (Mass + Variant)"],
    },
    "IBird": {
        "price_per_1000": 4.132,
        "notes": "IB - £20.66/5000 doses",
        "categories": ["spray"],
        "protection": ["IB (Variant)"],
    },
    "Evalon": {
        "price_per_1000": 95.34,
        "notes": "Coccidiosis - avg £95.34/1000 doses",
        "categories": ["spray"],
        "protection": ["Coccidiosis (5-Strain Core Protection)"],
    },
    "Paracox 8": {
        "price_per_1000": 102.44,
        "notes": "Coccidiosis - avg £102.44/1000 doses",
        "categories": ["spray"],
        "protection": ["Coccidiosis (8-Strain Broad Spectrum)"],
    },
    "Paracox 5": {
        "price_per_1000": 146.01,
        "notes": "Coccidiosis - £146.01/1000 doses",
        "categories": ["spray"],
        "protection": ["Coccidiosis (5-Strain Standard)"],
    },
}

# Disease categories for the coverage summary grid
DISEASE_CATEGORIES = {
    "Marek's Disease": {
        "diseases": ["Marek's Disease", "Marek's Disease (Standard)", "Marek's Disease (High Potency)"],
        "icon": "🛡️",
    },
    "Newcastle Disease": {
        "diseases": ["Newcastle Disease (ND)"],
        "icon": "🧬",
    },
    "Infectious Bronchitis": {
        "diseases": ["IB (Variant 4-91)", "IB (Classic Mass)", "IB (Mass + Variant)", "IB (Variant)"],
        "icon": "🌬️",
    },
    "Gumboro (IBD)": {
        "diseases": ["Gumboro (IBD)"],
        "icon": "✅",
    },
    "Inf. Laryngotracheitis": {
        "diseases": ["Inf. Laryngotracheitis (ILT)"],
        "icon": "🧬",
    },
    "Reovirus": {
        "diseases": ["Reovirus (Viral Arthritis)"],
        "icon": "✅",
    },
    "Coccidiosis": {
        "diseases": [
            "Coccidiosis (5-Strain Core Protection)",
            "Coccidiosis (8-Strain Broad Spectrum)",
            "Coccidiosis (5-Strain Standard)",
        ],
        "icon": "🦠",
    },
    "Bacterial": {
        "diseases": ["Bacterial Infections (Antibiotic Only)"],
        "icon": "💊",
    },
}

# Maximum vaccine slots per column
MAX_SLOTS = 4


# ============================================
# HELPER FUNCTIONS
# ============================================


def vaccines_for_category(category: str) -> list[str]:
    """Return vaccine names available for a given category, with placeholder first."""
    return [PLACEHOLDER] + [
        name for name, info in VACCINE_CATALOGUE.items() if category in info["categories"]
    ]


def calc_vaccine_cost(
    vax_name: str, dose_multiplier: float, is_double: bool = False
) -> float:
    """Calculate cost for a vaccine selection. Returns 0 for placeholder."""
    if vax_name == PLACEHOLDER:
        return 0.0
    base = VACCINE_CATALOGUE[vax_name]["price_per_1000"] * dose_multiplier
    return base * 2 if is_double else base


def render_vaccine_slots(
    label: str,
    category: str,
    num_slots: int,
    allow_double_dose: bool = True,
) -> list[tuple[str, bool]]:
    """Render selectboxes (and optional 2x checkboxes) for a vaccine column.
    Returns list of (vaccine_name, is_double) tuples."""
    options = vaccines_for_category(category)
    selections: list[tuple[str, bool]] = []
    st.markdown(f"### {label}")
    for i in range(1, num_slots + 1):
        vax = st.selectbox(
            f"Vaccine {i}",
            options=options,
            key=f"{category}_{i}",
            label_visibility="collapsed" if i > 1 else "visible",
        )
        is_double = False
        if allow_double_dose:
            is_double = st.checkbox(
                "2x Dose",
                key=f"{category}_{i}_dd",
                disabled=(vax == PLACEHOLDER),
            )
        selections.append((vax, is_double))
    return selections


# ============================================
# HEADER
# ============================================
st.title("🐣 Hatchery Vaccine Pricing Calculator")

# ============================================
# INPUT SECTION
# ============================================

col_left, col_right = st.columns(2)

with col_left:
    st.subheader("📊 Volume & Machine Settings")
    num_chicks = st.number_input(
        "Saleable chicks in this order",
        min_value=0,
        max_value=10_000_000,
        value=100_000,
        step=1000,
    )
    inovo_multiplier = st.number_input(
        "In-ovo egg multiplier",
        min_value=1.0,
        max_value=5.0,
        value=DEFAULT_EGG_TO_CHICK_FACTOR,
        step=0.1,
        help="How many eggs are injected per saleable chick (accounts for infertility, mortality, sexing).",
    )
    eggs_for_inovo = int(num_chicks * inovo_multiplier)

    monthly_egg_volume = st.number_input(
        "Monthly egg injection volume (for Inovo lease allocation)",
        min_value=1,
        max_value=10_000_000,
        value=500_000,
        step=10_000,
    )
    inovo_cost_per_egg = INOVO_MONTHLY_LEASE / monthly_egg_volume

    st.info(f"**{num_chicks:,}** chicks  ·  **{eggs_for_inovo:,}** eggs for in-ovo")

with col_right:
    st.subheader("🔧 Additional Treatments")
    beak_treatment = st.checkbox("Beak Treatment (Novatech IR)")
    toe_treatment = st.checkbox("Toe Treatment")
    if toe_treatment:
        st.warning("Toe treatment cost not yet configured — will show as £0.")

st.markdown("---")

# ============================================
# VACCINE SELECTION
# ============================================

st.subheader("💉 Vaccine Selection")

col_inovo, col_day_old, col_spray = st.columns(3)

with col_inovo:
    inovo_selections = render_vaccine_slots(
        "🥚 In-Ovo", "inovo", MAX_SLOTS, allow_double_dose=True
    )

with col_day_old:
    day_old_selections = render_vaccine_slots(
        "💉 Day-Old Injection", "day_old_inj", MAX_SLOTS, allow_double_dose=True
    )

with col_spray:
    spray_selections = render_vaccine_slots(
        "🌫️ Day-Old Spray", "spray", MAX_SLOTS, allow_double_dose=False
    )

# ============================================
# WARNINGS (vectors, interference, duplicates)
# ============================================

all_selections: list[tuple[str, str, bool]] = []  # (name, method_label, is_double)
for vax, dbl in inovo_selections:
    all_selections.append((vax, "Inovo", dbl))
for vax, dbl in day_old_selections:
    all_selections.append((vax, "Day Old Inj", dbl))
for vax, dbl in spray_selections:
    all_selections.append((vax, "Spray", dbl))

active_selections = [(n, m, d) for n, m, d in all_selections if n != PLACEHOLDER]

# Vector conflict
selected_vectors = [
    f"{m}: {n}"
    for n, m, _ in active_selections
    if VACCINE_CATALOGUE.get(n, {}).get("is_vector", False)
]
if len(selected_vectors) > 1:
    st.error(
        f"⚠️ **VECTOR CONFLICT!** Only one vector vaccine can be used. "
        f"Currently selected: {', '.join(selected_vectors)}"
    )

# HVT interference
active_names = [n for n, _, _ in active_selections]
has_ca126 = any("CA126" in n for n in active_names)
has_innovax = any("Innovax" in n for n in active_names)
if has_ca126 and has_innovax:
    st.warning(
        "⚠️ **HVT INTERFERENCE:** CA126 may interfere with Innovax. "
        "Consider Rismavac HIGH PFU instead."
    )

st.markdown("---")

# ============================================
# COST CALCULATIONS
# ============================================

inovo_dose_mult = eggs_for_inovo / 1000
chick_dose_mult = num_chicks / 1000

# --- Vaccine costs ---
inovo_line_items: list[tuple[str, float]] = []
for vax, is_double in inovo_selections:
    cost = calc_vaccine_cost(vax, inovo_dose_mult, is_double)
    if cost > 0:
        label = f"Inovo: {vax}" + (" (2x Dose)" if is_double else "")
        inovo_line_items.append((label, cost))

day_old_line_items: list[tuple[str, float]] = []
for vax, is_double in day_old_selections:
    cost = calc_vaccine_cost(vax, chick_dose_mult, is_double)
    if cost > 0:
        label = f"Day Old Inj: {vax}" + (" (2x Dose)" if is_double else "")
        day_old_line_items.append((label, cost))

spray_line_items: list[tuple[str, float]] = []
for vax, _ in spray_selections:
    cost = calc_vaccine_cost(vax, chick_dose_mult, False)
    if cost > 0:
        spray_line_items.append((f"Spray: {vax}", cost))

total_inovo_vaccines = sum(c for _, c in inovo_line_items)
total_day_old_vaccines = sum(c for _, c in day_old_line_items)
total_spray_vaccines = sum(c for _, c in spray_line_items)
total_vaccines = total_inovo_vaccines + total_day_old_vaccines + total_spray_vaccines

# --- Machine costs ---
inovo_selected = any(v != PLACEHOLDER for v, _ in inovo_selections)
inovo_machine_cost = (inovo_cost_per_egg * eggs_for_inovo) if inovo_selected else 0.0

day_old_inj_selected = any(v != PLACEHOLDER for v, _ in day_old_selections)
# If ANY day-old vaccine is double-dosed, the machine must make two full passes
# through all chicks (cradle count + roller inject + needle sanitation × 2).
any_double_dose = any(dbl for _, dbl in day_old_selections)
novatech_passes = 2 if (day_old_inj_selected and any_double_dose) else 1
novatech_machine_cost = (
    NOVATECH_INJECTION_COST * num_chicks * novatech_passes
) if day_old_inj_selected else 0.0

beak_cost = NOVATECH_BEAK_TREATMENT * num_chicks if beak_treatment else 0.0
toe_cost = 0.0

total_machine = inovo_machine_cost + novatech_machine_cost + beak_cost + toe_cost
grand_total = total_vaccines + total_machine
cost_per_chick = grand_total / num_chicks if num_chicks > 0 else 0.0

# ============================================
# RESULTS — Key Metrics
# ============================================

met1, met2, met3 = st.columns(3)
with met1:
    st.metric("Total Vaccine Cost", f"£{total_vaccines:,.2f}")
with met2:
    st.metric("Total Machine / Application Cost", f"£{total_machine:,.2f}")
with met3:
    st.metric(
        "Grand Total",
        f"£{grand_total:,.2f}",
        delta=f"£{cost_per_chick:.4f} per chick",
    )

st.markdown("---")

# ============================================
# PROTECTION SUMMARY
# ============================================

st.subheader("🛡️ Protection Summary")

# Build disease → vaccines mapping from active selections
disease_to_vaccines: dict[str, list[str]] = {}
for name, method, _ in active_selections:
    for disease in VACCINE_CATALOGUE.get(name, {}).get("protection", []):
        disease_to_vaccines.setdefault(disease, []).append(f"{name} ({method})")

if disease_to_vaccines:
    table_rows = []
    for category, info in DISEASE_CATEGORIES.items():
        for disease in info["diseases"]:
            if disease in disease_to_vaccines:
                table_rows.append(
                    {
                        "Category": f"{info['icon']} {category}",
                        "Disease Protection": disease,
                        "Provided By": ", ".join(disease_to_vaccines[disease]),
                    }
                )

    if table_rows:
        st.dataframe(
            pd.DataFrame(table_rows),
            column_config={
                "Category": st.column_config.TextColumn("Category", width="medium"),
                "Disease Protection": st.column_config.TextColumn("Disease Protection", width="large"),
                "Provided By": st.column_config.TextColumn("Vaccine (Method)", width="large"),
            },
            hide_index=True,
            use_container_width=True,
        )

        # Coverage chips — fixed 4-column grid to avoid narrow wrapping
        categories_covered = list(dict.fromkeys(r["Category"] for r in table_rows))
        cols_per_row = min(len(categories_covered), 4)
        for row_start in range(0, len(categories_covered), cols_per_row):
            row_cats = categories_covered[row_start : row_start + cols_per_row]
            cols = st.columns(cols_per_row)
            for i, cat in enumerate(row_cats):
                with cols[i]:
                    count = sum(1 for r in table_rows if r["Category"] == cat)
                    st.caption(f"**{cat}** — {count} protection{'s' if count > 1 else ''}")
    else:
        st.info("No vaccines selected yet.")
else:
    st.info("Select vaccines above to see disease coverage.")

st.markdown("---")

# ============================================
# DETAILED BREAKDOWN (as a proper table)
# ============================================

with st.expander("📋 Detailed Cost Breakdown"):
    all_line_items: list[tuple[str, float]] = []
    all_line_items.extend(inovo_line_items)
    if inovo_selected:
        all_line_items.append(("Inovo Machine Lease (allocated)", inovo_machine_cost))
    all_line_items.extend(day_old_line_items)
    if day_old_inj_selected:
        passes_note = f" (×{novatech_passes} pass{'es' if novatech_passes > 1 else ''})"
        all_line_items.append((f"Novatech Machine Costs{passes_note}", novatech_machine_cost))
    all_line_items.extend(spray_line_items)
    if beak_treatment:
        all_line_items.append(("Beak Treatment (Novatech IR)", beak_cost))
    if toe_treatment:
        all_line_items.append(("Toe Treatment", toe_cost))

    if all_line_items:
        breakdown_df = pd.DataFrame(
            [
                {
                    "Item": name,
                    "Total Cost (£)": round(cost, 2),
                    "Per Chick (£)": round(cost / num_chicks, 5) if num_chicks > 0 else 0,
                }
                for name, cost in all_line_items
            ]
        )
        st.dataframe(breakdown_df, hide_index=True, use_container_width=True)
        st.markdown(f"**Grand Total: £{grand_total:,.2f}  ·  £{cost_per_chick:.5f} per chick**")
    else:
        st.info("No items to show — select vaccines above.")
