import streamlit as st
import plotly.graph_objects as go
import pandas as pd

# 1. App Configuration
st.set_page_config(page_title="Cost Control Dashboard", layout="wide")

# --- CUSTOM CSS FOR EYE CANDY (TCU THEME) ---
st.markdown("""
<style>
/* Style the metric cards to look like raised 3D dashboard tiles */
div[data-testid="metric-container"] {
    background-color: #f8f9fa;
    border: 1px solid #e9ecef;
    padding: 5% 5% 5% 10%;
    border-radius: 10px;
    box-shadow: 3px 3px 10px rgba(0,0,0,0.08);
    border-left: 5px solid #4d1979; /* TCU Purple Accent */
}
</style>
""", unsafe_allow_html=True)
# --------------------------------------------

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

# --- LIVE QR CODE SECTION ---
st.sidebar.markdown("---")
st.sidebar.header("📱 Scan to Play Live!")

# Your actual live Streamlit URL
app_url = "https://variance-dashboard-fyajytibd3ibqjrrlxykwf.streamlit.app/" 

# This calls a free API to instantly generate the QR code image
qr_url = f"https://api.qrserver.com/v1/create-qr-code/?size=200x200&data={app_url}"
st.sidebar.image(qr_url, use_container_width=True)
# ---------------------------

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

# 6. Layout: Metrics Row (WITH DYNAMIC LIVE ANALYSIS)
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("DM Price Var", f"${abs(dm_price_var):,.2f}", f"{'-' if dm_price_var <= 0 else ''}Favorable" if dm_price_var <= 0 else "Unfavorable", delta_color="inverse")
    with st.expander("📘 What is this?"):
        st.markdown("**Formula:** `AQ x (AP - SP)`")
        st.markdown("**Meaning:** The financial impact of the raw aluminum's purchase price.")
        st.markdown("---")
        if AP < SP:
            st.success(f"**Live Analysis:** You paid ${SP - AP:.2f} less per pound than the $5.00 standard. This saved money, creating a Favorable variance.")
        elif AP > SP:
            st.error(f"**Live Analysis:** You paid ${AP - SP:.2f} more per pound than the $5.00 standard. This overpayment creates an Unfavorable variance.")
        else:
            st.info("**Live Analysis:** You paid exactly the standard $5.00 rate. No variance.")

with col2:
    st.metric("DM Qty Var", f"${abs(dm_qty_var):,.2f}", f"{'-' if dm_qty_var <= 0 else ''}Favorable" if dm_qty_var <= 0 else "Unfavorable", delta_color="inverse")
    with st.expander("📘 What is this?"):
        st.markdown("**Formula:** `SP x (AQ - SQ)`")
        st.markdown("**Meaning:** The financial impact of scrap, waste, or over-usage on the floor.")
        st.markdown("---")
        if AQ < SQ:
            st.success(f"**Live Analysis:** You used {SQ - AQ:,} fewer pounds than the 20,000 lb standard allowance. Excellent material efficiency!")
        elif AQ > SQ:
            st.error(f"**Live Analysis:** You used {AQ - SQ:,} more pounds than the 20,000 lb standard allowance. This excess waste drives costs up.")
        else:
            st.info("**Live Analysis:** You used exactly the standard 20,000 lbs. No variance.")

with col3:
    st.metric("DL Rate Var", f"${abs(dl_rate_var):,.2f}", f"{'-' if dl_rate_var <= 0 else ''}Favorable" if dl_rate_var <= 0 else "Unfavorable", delta_color="inverse")
    with st.expander("📘 What is this?"):
        st.markdown("**Formula:** `AH x (AR - SR)`")
        st.markdown("**Meaning:** The financial impact of paying workers more or less than expected.")
        st.markdown("---")
        if AR < SR:
            st.success(f"**Live Analysis:** You paid ${SR - AR:.2f} less per hour than the $20.00 standard rate. This creates a Favorable variance.")
        elif AR > SR:
            st.error(f"**Live Analysis:** You paid ${AR - SR:.2f} more per hour than the $20.00 standard. Did you authorize emergency overtime?")
        else:
            st.info("**Live Analysis:** You paid exactly the standard $20.00 rate. No variance.")

with col4:
    st.metric("DL Eff Var", f"${abs(dl_eff_var):,.2f}", f"{'-' if dl_eff_var <= 0 else ''}Favorable" if dl_eff_var <= 0 else "Unfavorable", delta_color="inverse")
    with st.expander("📘 What is this?"):
        st.markdown("**Formula:** `SR x (AH - SH)`")
        st.markdown("**Meaning:** The financial impact of manufacturing taking longer than planned.")
        st.markdown("---")
        if AH < SH:
            st.success(f"**Live Analysis:** You finished production using {SH - AH:,} fewer hours than the 5,000 hour standard. Highly efficient labor!")
        elif AH > SH:
            st.error(f"**Live Analysis:** Production took {AH - SH:,} hours longer than the 5,000 hour standard. Machine jams or slow line speeds are costing you money.")
        else:
            st.info("**Live Analysis:** Production took exactly the standard 5,000 hours. No variance.")

# 7. Visualization: Plotly Waterfall Chart (FIXED FLOATING POINT)
# This loops through the values and formats them perfectly to 1 decimal place
chart_text = [f"${v/1000:,.1f}k" for v in [std_cost, dm_price_var, dm_qty_var, dl_rate_var, dl_eff_var, total_actual]]

fig = go.Figure(go.Waterfall(
    name = "Cost Bridge", orientation = "v",
    measure = ["absolute", "relative", "relative", "relative", "relative", "total"],
    x = ["Standard Cost", "DM Price Var", "DM Qty Var", "DL Rate Var", "DL Eff Var", "Actual Cost"],
    textposition = "outside",
    text = chart_text, # Using the cleanly formatted text
    y = [std_cost, dm_price_var, dm_qty_var, dl_rate_var, dl_eff_var, total_actual],
    connector = {"line":{"color":"rgb(63, 63, 63)"}},
    decreasing = {"marker":{"color":"#2ca02c"}},  # Green for Favorable
    increasing = {"marker":{"color":"#d62728"}},  # Red for Unfavorable
    totals = {"marker":{"color":"#4d1979"}}       # Changed final bar to TCU Purple
))
fig.update_layout(title="Cost Bridge: Standard to Actual", showlegend=False, height=500)
st.plotly_chart(fig, use_container_width=True)

# 8. Dynamic AI Narrative & What-If Optimizer (WITH ANIMATION)
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
    st.write("Production is currently operating under or at standard cost. Great job!")
    
    # THE EYE CANDY ANIMATION TRIGGER
    st.balloons() 
    
# Trigger the Audit Alert if Chaos is on
if chaos_mode:
    st.warning("⚠️ **AUDIT ALERT:** The 'Enable Production Chaos' toggle is active. A $15,000 phantom material cost has been secretly injected into the math. The sliders no longer match the waterfall output. Can you find the leak?")
