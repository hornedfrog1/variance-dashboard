import streamlit as st
import plotly.graph_objects as go

# Page setup
st.set_page_config(
    page_title="DM and DL Variance Visualizer",
    page_icon="📊",
    layout="wide",
)

# Scenario constants
UNITS_PRODUCED = 10_000
PRODUCT_NAME = "Purple Anodized Aluminum Enclosures"
SQ = 20_000  # Standard Material Quantity (lbs)
SP = 5.00    # Standard Material Price ($/lb)
SH = 5_000   # Standard Labor Hours
SR = 20.00   # Standard Labor Rate ($/hr)
TOTAL_STANDARD_COST = 200_000.00


def fmt_currency(value: float) -> str:
    return f"${abs(value):,.2f}"


def variance_label(value: float) -> str:
    return "F" if value < 0 else "U" if value > 0 else "None"


def variance_display(value: float) -> str:
    label = variance_label(value)
    if label == "None":
        return "$0.00"
    return f"{fmt_currency(value)} ({label})"


# Sidebar inputs
st.sidebar.header("Actuals Input")
AQ = st.sidebar.slider(
    "Actual Materials Used (AQ) - lbs",
    min_value=15_000,
    max_value=30_000,
    value=22_000,
    step=100,
)
AP = st.sidebar.slider(
    "Actual Material Price (AP) - $/lb",
    min_value=3.00,
    max_value=8.00,
    value=4.80,
    step=0.01,
)
AH = st.sidebar.slider(
    "Actual Labor Hours (AH)",
    min_value=3_000,
    max_value=8_000,
    value=5_500,
    step=50,
)
AR = st.sidebar.slider(
    "Actual Labor Rate (AR) - $/hr",
    min_value=15.00,
    max_value=30.00,
    value=21.00,
    step=0.01,
)

# Calculations
actual_dm_cost = AQ * AP
actual_dl_cost = AH * AR
actual_total_cost = actual_dm_cost + actual_dl_cost

# Variances: favorable = negative, unfavorable = positive
# DM Price Variance: AQ × (AP − SP)
dm_price_variance = AQ * (AP - SP)
# DM Quantity Variance: SP × (AQ − SQ)
dm_quantity_variance = SP * (AQ - SQ)
# DL Rate Variance: AH × (AR − SR)
dl_rate_variance = AH * (AR - SR)
# DL Efficiency Variance: SR × (AH − SH)
dl_efficiency_variance = SR * (AH - SH)

total_variance = (
    dm_price_variance
    + dm_quantity_variance
    + dl_rate_variance
    + dl_efficiency_variance
)

# Main content
st.title("Direct Materials and Direct Labor Variance Visualizer")
st.subheader(f"Scenario: {UNITS_PRODUCED:,} units of {PRODUCT_NAME}")

left, right = st.columns([1.1, 1.2])
with left:
    st.markdown("### Standards")
    st.write(f"**Standard Material Quantity (SQ):** {SQ:,} lbs")
    st.write(f"**Standard Material Price (SP):** ${SP:,.2f} per lb")
    st.write(f"**Standard Labor Hours (SH):** {SH:,} hours")
    st.write(f"**Standard Labor Rate (SR):** ${SR:,.2f} per hour")
    st.write(f"**Total Standard Cost:** ${TOTAL_STANDARD_COST:,.2f}")

with right:
    st.markdown("### Actual Cost Snapshot")
    st.write(f"**Actual DM Cost:** ${actual_dm_cost:,.2f}")
    st.write(f"**Actual DL Cost:** ${actual_dl_cost:,.2f}")
    st.write(f"**Total Actual Cost (from actual inputs):** ${actual_total_cost:,.2f}")
    st.write(f"**Total Variance vs Standard:** {variance_display(total_variance)}")

# Waterfall chart
x_labels = [
    "Standard Cost",
    "DM Price Var",
    "DM Quantity Var",
    "DL Rate Var",
    "DL Efficiency Var",
    "Actual Cost",
]

measure = ["total", "relative", "relative", "relative", "relative", "total"]
values = [
    TOTAL_STANDARD_COST,
    dm_price_variance,
    dm_quantity_variance,
    dl_rate_variance,
    dl_efficiency_variance,
    actual_total_cost,
]

text_values = [
    f"${TOTAL_STANDARD_COST:,.2f}",
    variance_display(dm_price_variance),
    variance_display(dm_quantity_variance),
    variance_display(dl_rate_variance),
    variance_display(dl_efficiency_variance),
    f"${actual_total_cost:,.2f}",
]

fig = go.Figure(
    go.Waterfall(
        name="Cost Bridge",
        orientation="v",
        measure=measure,
        x=x_labels,
        y=values,
        text=text_values,
        textposition="outside",
        connector={"line": {"color": "rgba(120,120,120,0.6)"}},
        increasing={"marker": {"color": "red"}},
        decreasing={"marker": {"color": "green"}},
        totals={"marker": {"color": "steelblue"}},
    )
)

fig.update_layout(
    title="Standard Cost to Actual Cost Waterfall",
    showlegend=False,
    height=550,
    yaxis_title="Cost ($)",
    margin=dict(l=20, r=20, t=60, b=20),
)

st.plotly_chart(fig, use_container_width=True)

# Metrics
st.markdown("### Variance Metrics")
col1, col2, col3, col4 = st.columns(4)

col1.metric(
    label=f"DM Price Variance ({variance_label(dm_price_variance)})",
    value=fmt_currency(dm_price_variance),
    delta=f"{'Favorable' if dm_price_variance < 0 else 'Unfavorable' if dm_price_variance > 0 else 'No Variance'}",
)
col2.metric(
    label=f"DM Quantity Variance ({variance_label(dm_quantity_variance)})",
    value=fmt_currency(dm_quantity_variance),
    delta=f"{'Favorable' if dm_quantity_variance < 0 else 'Unfavorable' if dm_quantity_variance > 0 else 'No Variance'}",
)
col3.metric(
    label=f"DL Rate Variance ({variance_label(dl_rate_variance)})",
    value=fmt_currency(dl_rate_variance),
    delta=f"{'Favorable' if dl_rate_variance < 0 else 'Unfavorable' if dl_rate_variance > 0 else 'No Variance'}",
)
col4.metric(
    label=f"DL Efficiency Variance ({variance_label(dl_efficiency_variance)})",
    value=fmt_currency(dl_efficiency_variance),
    delta=f"{'Favorable' if dl_efficiency_variance < 0 else 'Unfavorable' if dl_efficiency_variance > 0 else 'No Variance'}",
)

# Optional detail table
st.markdown("### Calculation Detail")
rows = [
    {
        "Variance": "DM Price Variance",
        "Formula": "AQ × (AP − SP)",
        "Amount": variance_display(dm_price_variance),
    },
    {
        "Variance": "DM Quantity Variance",
        "Formula": "SP × (AQ − SQ)",
        "Amount": variance_display(dm_quantity_variance),
    },
    {
        "Variance": "DL Rate Variance",
        "Formula": "AH × (AR − SR)",
        "Amount": variance_display(dl_rate_variance),
    },
    {
        "Variance": "DL Efficiency Variance",
        "Formula": "SR × (AH − SH)",
        "Amount": variance_display(dl_efficiency_variance),
    },
    {
        "Variance": "Total Variance",
        "Formula": "Sum of all four variances",
        "Amount": variance_display(total_variance),
    },
]

st.table(rows)

st.caption(
    "Interpretation: Negative variances are Favorable because they reduce cost versus standard. "
    "Positive variances are Unfavorable because they increase cost versus standard."
)
