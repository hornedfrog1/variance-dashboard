import streamlit as st
import plotly.graph_objects as go
import pandas as pd

# ==========================================
# 1. APP CONFIGURATION & EYE CANDY (CSS)
# ==========================================
st.set_page_config(page_title="Cost Control Dashboard", layout="wide")

st.markdown("""
<style>
/* 1. Style the metric cards to look like raised 3D dashboard tiles */
div[data-testid="metric-container"] {
    background-color: #f8f9fa;
    border: 1px solid #e9ecef;
    padding: 5% 5% 5% 10%;
    border-radius: 10px;
    box-shadow: 3px 3px 10px rgba(0,0,0,0.08);
    border-left: 5px solid #4d1979; /* TCU Purple Accent */
}

/* 2. Make the Metric Labels bigger and bolder for the projector */
[data-testid="stMetricLabel"] {
    font-size: 1.15rem !important;
    font-weight: 700 !important;
    color: #333333;
}

/* 3. Make the main dollar amounts bolder */
[data-testid="stMetricValue"] {
    font-weight: 800 !important;
}

/* 4. Hide the clunky minus sign in the Favorable text but keep the green arrow */
[data-testid="stMetricDelta"] svg + div::first-letter {
    font-size: 0;
}
</style>
""", unsafe_allow_html=True)

st.title("Purple Anodized Aluminum Enclosures: AI Cost Controller")


# ==========================================
# 2. SIDEBAR: EDITABLE BASELINE STANDARDS
# ==========================================
st.sidebar.header("🎯 Set Standard Costs")

with st.sidebar.expander("⚙️ Edit Baseline Standards", expanded=False):
    SQ = st.number_input("Standard Material Qty (lbs)", value=20000, step=1000)
    SP = st.number_input("Standard Material Price ($/lb)", value=5.00, format="%.2f", step=0.10)
    SH = st.number_input("Standard Labor Hours", value=5000, step=500)
    SR = st.number_input("Standard Labor Rate ($/hr)", value=20.00, format="%.2f", step=0.50)

std_cost = (SQ * SP) + (SH * SR)
st.sidebar.markdown("---")


# ==========================================
# 3. SIDEBAR: ACTUAL RESULTS (WITH LIVE DELTAS)
# ==========================================
st.sidebar.header("🎛️ Actual Results")

def get_delta_html(actual, standard, is_currency=False):
    delta = actual - standard
    if delta == 0:
        return "<div style='text-align: right; color: gray; font-size: 0.85em; margin-top: -15px; margin-bottom: 15px;'>🎯 On Target</div>"
    color = "#d62728" if delta > 0 else "#2ca02c"
    sign = "+" if delta > 0 else ""
    formatted_delta = f"${delta:,.2f}" if is_currency else f"{delta:,.0f}"
    return f"<div style='text-align: right; color: {color}; font-weight: bold; font-size: 0.85em; margin-top: -15px; margin-bottom: 15px;'>{sign}{formatted_delta} vs Standard</div>"

st.sidebar.markdown("#### 📦 Materials")
AQ_slider = st.sidebar.slider("Actual Materials Used (lbs)", 15000, 30000, 22000, help=f"Standard Target: {SQ:,.0f} lbs")
st.sidebar.markdown(get_delta_html(AQ_slider, SQ), unsafe_allow_html=True)

AP = st.sidebar.slider("Actual Material Price ($/lb)", 3.00, 8.00, 4.80, help=f"Standard Target: ${SP:,.2f}")
st.sidebar.markdown(get_delta_html(AP, SP, True), unsafe_allow_html=True)

st.sidebar.markdown("#### 👷 Labor")
AH = st.sidebar.slider("Actual Labor Hours", 3000, 8000, 5500, help=f"Standard Target: {SH:,.0f} hours")
st.sidebar.markdown(get_delta_html(AH, SH), unsafe_allow_html=True)

AR = st.sidebar.slider("Actual Labor Rate ($/hr)", 15.00, 30.00, 21.00, help=f"Standard Target: ${SR:,.2f}")
st.sidebar.markdown(get_delta_html(AR, SR, True), unsafe_allow_html=True)


# ==========================================
# 4. SIDEBAR: LIVE QR CODE & GAMIFICATION
# ==========================================
st.sidebar.markdown("---")
st.sidebar.header("📱 Scan to Play Live!")
app_url = "https://variance-dashboard-fyajytibd3ibqjrrlxykwf.streamlit.app/" 
qr_url = f"https://api.qrserver.com/v1/create-qr-code/?size=200x200&data={app_url}"
st.sidebar.image(qr_url, use_container_width=True)

st.sidebar.markdown("---")
st.sidebar.header("Alumni Audit Challenge")
chaos_mode = st.sidebar.checkbox("Enable Production Chaos")

if chaos_mode:
    AQ = AQ_slider + 3000 
else:
    AQ = AQ_slider


# ==========================================
# 5. CORE MATH & FORMULA GLOSSARY
# ==========================================
dm_price_var = AQ * (AP - SP)
dm_qty_var = SP * (AQ - SQ)
dl_rate_var = AH * (AR - SR)
dl_eff_var = SR * (AH - SH)

total_actual = (AQ * AP) + (AH * AR)
net_variance = total_actual - std_cost

with st.expander("📚 Formula Glossary: What do these letters mean?"):
    glos1, glos2 = st.columns(2)
    with glos1:
        st.markdown("""
        **Direct Materials (DM)**
        * **AQ (Actual Quantity):** The total physical raw materials used on the floor.
        * **AP (Actual Price):** The real-world price paid per unit of material.
        * **SQ (Standard Quantity):** The budgeted material allowance for this production run.
        * **SP (Standard Price):** The target purchase price per unit of material.
        """)
    with glos2:
        st.markdown("""
        **Direct Labor (DL)**
        * **AH (Actual Hours):** The total physical hours your team worked on the floor.
        * **AR (Actual Rate):** The real-world hourly wage paid to the workers.
        * **SH (Standard Hours):** The budgeted time allowance for this production run.
        * **SR (Standard Rate):** The target hourly wage for the workforce.
        """)
st.markdown("---")


# ==========================================
# 6. METRICS WITH LIVE DYNAMIC TUTOR
# ==========================================
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("DM Price Var", f"${abs(dm_price_var):,.2f}", f"{'-' if dm_price_var <= 0 else ''}Favorable" if dm_price_var <= 0 else "Unfavorable", delta_color="inverse")
    with st.expander("📘 What is this?"):
        st.markdown("**Formula:** `AQ x (AP - SP)`")
        st.markdown("**Meaning:** The financial impact of the raw aluminum's purchase price.")
        st.markdown("---")
        if AP < SP:
            st.success(f"**Live Analysis:** You paid ${SP - AP:.2f} less per pound than the ${SP:.2f} standard. This saved money, creating a Favorable variance.")
        elif AP > SP:
            st.error(f"**Live Analysis:** You paid ${AP - SP:.2f} more per pound than the ${SP:.2f} standard. This overpayment creates an Unfavorable variance.")
        else:
            st.info(f"**Live Analysis:** You paid exactly the standard ${SP:.2f} rate. No variance.")

with col2:
    st.metric("DM Qty Var", f"${abs(dm_qty_var):,.2f}", f"{'-' if dm_qty_var <= 0 else ''}Favorable" if dm_qty_var <= 0 else "Unfavorable", delta_color="inverse")
    with st.expander("📘 What is this?"):
        st.markdown("**Formula:** `SP x (AQ - SQ)`")
        st.markdown("**Meaning:** The financial impact of scrap, waste, or over-usage on the floor.")
        st.markdown("---")
        if AQ < SQ:
            st.success(f"**Live Analysis:** You used {SQ - AQ:,} fewer pounds than the {SQ:,.0f} lb standard allowance. Excellent material efficiency!")
        elif AQ > SQ:
            st.error(f"**Live Analysis:** You used {AQ - SQ:,} more pounds than the {SQ:,.0f} lb standard allowance. This excess waste drives costs up.")
        else:
            st.info(f"**Live Analysis:** You used exactly the standard {SQ:,.0f} lbs. No variance.")

with col3:
    st.metric("DL Rate Var", f"${abs(dl_rate_var):,.2f}", f"{'-' if dl_rate_var <= 0 else ''}Favorable" if dl_rate_var <= 0 else "Unfavorable", delta_color="inverse")
    with st.expander("📘 What is this?"):
        st.markdown("**Formula:** `AH x (AR - SR)`")
        st.markdown("**Meaning:** The financial impact of paying workers more or less than expected.")
        st.markdown("---")
        if AR < SR:
            st.success(f"**Live Analysis:** You paid ${SR - AR:.2f} less per hour than the ${SR:.2f} standard rate. This creates a Favorable variance.")
        elif AR > SR:
            st.error(f"**Live Analysis:** You paid ${AR - SR:.2f} more per hour than the ${SR:.2f} standard. Did you authorize emergency overtime?")
        else:
            st.info(f"**Live Analysis:** You paid exactly the standard ${SR:.2f} rate. No variance.")

with col4:
    st.metric("DL Eff Var", f"${abs(dl_eff_var):,.2f}", f"{'-' if dl_eff_var <= 0 else ''}Favorable" if dl_eff_var <= 0 else "Unfavorable", delta_color="inverse")
    with st.expander("📘 What is this?"):
        st.markdown("**Formula:** `SR x (AH - SH)`")
        st.markdown("**Meaning:** The financial impact of manufacturing taking longer than planned.")
        st.markdown("---")
        if AH < SH:
            st.success(f"**Live Analysis:** You finished production using {SH - AH:,} fewer hours than the {SH:,.0f} hour standard. Highly efficient labor!")
        elif AH > SH:
            st.error(f"**Live Analysis:** Production took {AH - SH:,} hours longer than the {SH:,.0f} hour standard. Machine jams or slow line speeds are costing you money.")
        else:
            st.info(f"**Live Analysis:** Production took exactly the standard {SH:,.0f} hours. No variance.")


# ==========================================
# 7. VISUALIZATION: PLOTLY WATERFALL CHART
# ==========================================
chart_text = [f"${v/1000:,.1f}k" for v in [std_cost, dm_price_var, dm_qty_var, dl_rate_var, dl_eff_var, total_actual]]

fig = go.Figure(go.Waterfall(
    name = "Cost Bridge", orientation = "v",
    measure = ["absolute", "relative", "relative", "relative", "relative", "total"],
    x = ["Standard Cost", "DM Price Var", "DM Qty Var", "DL Rate Var", "DL Eff Var", "Actual Cost"],
    textposition = "outside",
    text = chart_text,
    textfont = {"size": 16, "family": "Arial Black"}, 
    y = [std_cost, dm_price_var, dm_qty_var, dl_rate_var, dl_eff_var, total_actual],
    connector = {"line":{"color":"rgb(63, 63, 63)", "width": 2}},
    decreasing = {"marker":{"color":"#2ca02c"}},  
    increasing = {"marker":{"color":"#d62728"}},  
    totals = {"marker":{"color":"#4d1979"}}       
))

fig.update_layout(
    title={"text": "Cost Bridge: Standard to Actual", "font": {"size": 24}}, 
    showlegend=False, 
    height=550, 
    font=dict(size=14, color="black"), 
    margin=dict(t=80) 
)
st.plotly_chart(fig, use_container_width=True)


# ==========================================
# 8. DYNAMIC AI CONTROLLER NARRATIVE
# ==========================================
st.markdown("### 🤖 AI Controller Analysis")
if net_variance > 0:
    st.error(f"**Warning: Operating at a Net Deficit of ${net_variance:,.2f}.**")
    variances = {"Materials Price": dm_price_var, "Materials Quantity": dm_qty_var, "Labor Rate": dl_rate_var, "Labor Efficiency": dl_eff_var}
    worst_name = max(variances, key=variances.get)
    worst_val = variances[worst_name]
    st.write(f"The primary driver of this deficit is an unfavorable **{worst_name} Variance** of ${worst_val:,.2f}.")
    hours_to_cut = net_variance / SR
    st.info(f"**Recovery Optimizer:** To offset this ${net_variance:,.2f} deficit strictly through labor efficiency, the floor manager must reduce production time by **{hours_to_cut:,.1f} hours** from the current actuals.")
else:
    st.success(f"**Success: Operating at a Net Surplus of ${abs(net_variance):,.2f}.**")
    st.write("Production is currently operating under or at standard cost. Great job!")
    st.balloons() 
    
if chaos_mode:
    st.warning("⚠️ **AUDIT ALERT:** The 'Enable Production Chaos' toggle is active. A $15,000 phantom material cost has been secretly injected into the math. The sliders no longer match the waterfall output. Can you find the leak?")
    with st.expander("🔍 Reveal the Leak (Show Solution)"):
        st.markdown("**The Culprit:** Unrecorded Material Scrap / Theft")
        st.markdown(f"The UI slider shows you only used **{AQ_slider:,.0f} lbs** of material. However, the system silently processed **{AQ:,.0f} lbs** into the final math.")
        st.markdown("This hidden **3,000 lb discrepancy** (valued at the standard \\$5.00/lb rate) perfectly explains the mysterious **\\$15,000 Unfavorable Quantity Variance** that doesn't match the inputs. This is why you must always audit the underlying data pipeline, not just the front-end dashboard!")
