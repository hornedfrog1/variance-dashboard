import streamlit as st
import plotly.graph_objects as go
import pandas as pd

# 1. App Configuration
st.set_page_config(page_title="Cost Control Dashboard", layout="wide")
st.title("Purple Anodized Aluminum Enclosures: AI Cost Controller")

# 2. Standard Costs (The Baseline)
SQ = 20000
SP = 5.00
SH = 5000
SR = 20.00
std_cost = (SQ * SP) + (SH * SR)

# 3. Sidebar Inputs (The Levers)
st.sidebar.header("Actual Results (February)")
AQ_slider = st.sidebar.slider("Actual Materials Used (lbs)", 15000, 30000, 22000)
AP = st.sidebar.slider("Actual Material Price ($/lb)", 3.00, 8.00, 4.80)
AH = st.sidebar.slider("Actual Labor Hours", 3000, 8000, 5500)
AR = st.sidebar.slider("Actual Labor Rate ($/hr)", 15.00, 30.00, 21.00)

# 4. Gamification: The Alumni Audit Challenge
st.sidebar.markdown("---")
st.sidebar.header("Alumni Audit Challenge")
chaos_mode = st.sidebar.checkbox("Enable Production Chaos")

# Injecting the "Phantom Scrap" if Chaos is enabled
if chaos_mode:
    # This silently adds 3,000 lbs of material usage ($15,000 variance) 
    # that won't show up on the user's slider!
    AQ = AQ_slider + 3000 
else:
    AQ = AQ_slider

# 5. Variance Calculations
dm_price_var = AQ * (AP - SP)
dm_qty_var = SP * (AQ - SQ)
dl_rate_var = AH * (AR - SR)
dl_eff_var = SR * (AH - SH)

total_actual = (AQ * AP) + (AH * AR)
net_variance = total_actual - std_cost

# 6. Layout: Metrics Row
col1, col2, col3, col4 = st.columns(4)
col1.metric("DM Price Variance", f"${abs(dm_price_var):,.2f}", "Unfavorable" if dm_price_var > 0 else "Favorable", delta_color="inverse")
col2.metric("DM Qty Variance", f"${abs(dm_qty_var):,.2f}", "Unfavorable" if dm_qty_var > 0 else "Favorable", delta_color="inverse")
col3.metric("DL Rate Variance", f"${abs(dl_rate_var):,.2f}", "Unfavorable" if dl_rate_var > 0 else "Favorable", delta_color="inverse")
col4.metric("DL Eff Variance", f"${abs(dl_eff_var):,.2f}", "Unfavorable" if dl_eff_var > 0 else "Favorable", delta_color="inverse")

# 7. Visualization: Plotly Waterfall Chart
fig = go.Figure(go.Waterfall(
    name = "Cost Bridge", orientation = "v",
    measure = ["absolute", "relative", "relative", "relative", "relative", "total"],
    x = ["Standard Cost", "DM Price Var", "DM Qty Var", "DL Rate Var", "DL Eff Var", "Actual Cost"],
    textposition = "outside",
    text = [f"${std_cost/1000}k", f"${dm_price_var/1000}k", f"${dm_qty_var/1000}k", f"${dl_rate_var/1000}k", f"${dl_eff_var/1000}k", f"${total_actual/1000}k"],
    y = [std_cost, dm_price_var, dm_qty_var, dl_rate_var, dl_eff_var, total_actual],
    connector = {"line":{"color":"rgb(63, 63, 63)"}},
    decreasing = {"marker":{"color":"#2ca02c"}},  # Green for Favorable
    increasing = {"marker":{"color":"#d62728"}},  # Red for Unfavorable
    totals = {"marker":{"color":"#1f77b4"}}       # Blue for Totals
))
fig.update_layout(title="Cost Bridge: Standard to Actual", showlegend=False, height=500)
st.plotly_chart(fig, use_container_width=True)

# 8. Dynamic AI Narrative & What-If Optimizer
st.markdown("### 🤖 AI Controller Analysis")
if net_variance > 0:
    st.error(f"**Warning: Operating at a Net Deficit of ${net_variance:,.2f}.**")
    
    # AI determines the worst offender dynamically
    variances = {"Materials Price": dm_price_var, "Materials Quantity": dm_qty_var, "Labor Rate": dl_rate_var, "Labor Efficiency": dl_eff_var}
    worst_name = max(variances, key=variances.get)
    worst_val = variances[worst_name]
    
    st.write(f"The primary driver of this deficit is an unfavorable **{worst_name} Variance** of ${worst_val:,.2f}.")
    
    # What-If Optimizer Logic
    hours_to_cut = net_variance / SR
    st.info(f"**Recovery Optimizer:** To offset this ${net_variance:,.2f} deficit strictly through labor efficiency, the floor manager must reduce production time by **{hours_to_cut:,.1f} hours** from the current actuals.")
else:
    st.success(f"**Success: Operating at a Net Surplus of ${abs(net_variance):,.2f}.**")
    st.write("Production is currently operating under or at standard cost. Maintain current material sourcing and labor scheduling.")
    
# Trigger the Audit Alert if Chaos is on
if chaos_mode:
    st.warning("⚠️ **AUDIT ALERT:** The 'Enable Production Chaos' toggle is active. A $15,000 phantom material cost has been secretly injected into the math. The sliders no longer match the waterfall output. Can you find the leak?")
