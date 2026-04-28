import streamlit as st
import plotly.graph_objects as go
import streamlit.components.v1 as components
from textwrap import dedent


# ==========================================
# 1. APP CONFIGURATION & EYE CANDY (CSS)
# ==========================================
st.set_page_config(page_title="Cost Control Dashboard", layout="wide")

st.markdown(
    """
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
""",
    unsafe_allow_html=True,
)


# ==========================================
# 2. HELPERS
# ==========================================
def fmt_currency(value: float) -> str:
    return f"${abs(value):,.2f}"


def variance_label(value: float) -> str:
    if value < 0:
        return "F"
    if value > 0:
        return "U"
    return "0"


def variance_word(value: float) -> str:
    if value < 0:
        return "Favorable"
    if value > 0:
        return "Unfavorable"
    return "No Variance"


def variance_display(value: float) -> str:
    label = variance_label(value)
    if label == "0":
        return "$0.00"
    return f"{fmt_currency(value)} ({label})"


def get_delta_html(actual, standard, is_currency=False):
    delta = actual - standard
    if delta == 0:
        return "<div style='text-align: right; color: gray; font-size: 0.85em; margin-top: -15px; margin-bottom: 15px;'>🎯 On Target</div>"
    color = "#d62728" if delta > 0 else "#2ca02c"
    sign = "+" if delta > 0 else ""
    formatted_delta = f"${delta:,.2f}" if is_currency else f"{delta:,.0f}"
    return (
        f"<div style='text-align: right; color: {color}; font-weight: bold; "
        f"font-size: 0.85em; margin-top: -15px; margin-bottom: 15px;'>{sign}{formatted_delta} vs Standard</div>"
    )


def copy_button(text: str, button_label: str, key: str) -> None:
    safe_text = (
        text.replace("\\", "\\\\")
        .replace("`", "\\`")
        .replace("${", "\\${")
    )
    html = f"""
    <div style="margin: 0.25rem 0 0.75rem 0;">
        <button id="btn-{key}" style="
            background-color:#4F8BF9;
            color:white;
            border:none;
            padding:0.5rem 0.9rem;
            border-radius:0.5rem;
            cursor:pointer;
            font-size:0.95rem;
        ">{button_label}</button>
        <span id="msg-{key}" style="margin-left:0.5rem;font-size:0.9rem;color:#2e7d32;"></span>
    </div>
    <script>
        const button = document.getElementById("btn-{key}");
        const message = document.getElementById("msg-{key}");
        const text = `{safe_text}`;
        button.addEventListener("click", async () => {{
            try {{
                await navigator.clipboard.writeText(text);
                message.textContent = "Copied to clipboard";
                setTimeout(() => {{ message.textContent = ""; }}, 2000);
            }} catch (err) {{
                message.textContent = "Copy failed. Select the prompt and copy manually.";
            }}
        }});
    </script>
    """
    components.html(html, height=55)


# ==========================================
# 3. SIDEBAR: NAVIGATION
# ==========================================
page = st.sidebar.radio(
    "Navigate",
    ["Variance Dashboard", "How you can make this or something similar!", "Glossary"],
)

st.title("Purple Anodized Aluminum Enclosures: AI Cost Controller")


# ==========================================
# 4. SIDEBAR: EDITABLE BASELINE STANDARDS
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
# 5. SIDEBAR: ACTUAL RESULTS (WITH LIVE DELTAS)
# ==========================================
st.sidebar.header("🎛️ Actual Results")

st.sidebar.markdown("#### 📦 Materials")
AQ_slider = st.sidebar.slider(
    "Actual Materials Used (lbs)",
    15000,
    30000,
    22000,
    help=f"Standard Target: {SQ:,.0f} lbs",
)
st.sidebar.markdown(get_delta_html(AQ_slider, SQ), unsafe_allow_html=True)

AP = st.sidebar.slider(
    "Actual Material Price ($/lb)",
    3.00,
    8.00,
    4.80,
    help=f"Standard Target: ${SP:,.2f}",
)
st.sidebar.markdown(get_delta_html(AP, SP, True), unsafe_allow_html=True)

st.sidebar.markdown("#### 👷 Labor")
AH = st.sidebar.slider(
    "Actual Labor Hours",
    3000,
    8000,
    5500,
    help=f"Standard Target: {SH:,.0f} hours",
)
st.sidebar.markdown(get_delta_html(AH, SH), unsafe_allow_html=True)

AR = st.sidebar.slider(
    "Actual Labor Rate ($/hr)",
    15.00,
    30.00,
    21.00,
    help=f"Standard Target: ${SR:,.2f}",
)
st.sidebar.markdown(get_delta_html(AR, SR, True), unsafe_allow_html=True)


# ==========================================
# 6. SIDEBAR: LIVE QR CODE & GAMIFICATION
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
# 7. CORE MATH
# ==========================================
dm_price_var = AQ * (AP - SP)
dm_qty_var = SP * (AQ - SQ)
dl_rate_var = AH * (AR - SR)
dl_eff_var = SR * (AH - SH)

total_actual = (AQ * AP) + (AH * AR)
net_variance = total_actual - std_cost


# ==========================================
# 8. PAGE: VARIANCE DASHBOARD
# ==========================================
def render_dashboard():
    with st.expander("📚 Formula Glossary: What do these letters mean?"):
        glos1, glos2 = st.columns(2)
        with glos1:
            st.markdown(
                """
                **Direct Materials (DM)**
                * **AQ (Actual Quantity):** The total physical raw materials used on the floor.
                * **AP (Actual Price):** The real-world price paid per unit of material.
                * **SQ (Standard Quantity):** The budgeted material allowance for this production run.
                * **SP (Standard Price):** The target purchase price per unit of material.
                """
            )
        with glos2:
            st.markdown(
                """
                **Direct Labor (DL)**
                * **AH (Actual Hours):** The total physical hours your team worked on the floor.
                * **AR (Actual Rate):** The real-world hourly wage paid to the workers.
                * **SH (Standard Hours):** The budgeted time allowance for this production run.
                * **SR (Standard Rate):** The target hourly wage for the workforce.
                """
            )

    st.markdown("---")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            "DM Price Var",
            f"${abs(dm_price_var):,.2f}",
            f"{'-' if dm_price_var <= 0 else ''}Favorable" if dm_price_var <= 0 else "Unfavorable",
            delta_color="inverse",
        )
        with st.expander("📘 What is this?"):
            st.markdown("**Formula:** `AQ x (AP - SP)`")
            st.markdown("**Meaning:** The financial impact of the raw aluminum's purchase price.")
            st.markdown("---")
            if AP < SP:
                st.success(
                    f"**Live Analysis:** You paid ${SP - AP:.2f} less per pound than the ${SP:.2f} standard. This saved money, creating a Favorable variance."
                )
            elif AP > SP:
                st.error(
                    f"**Live Analysis:** You paid ${AP - SP:.2f} more per pound than the ${SP:.2f} standard. This overpayment creates an Unfavorable variance."
                )
            else:
                st.info(f"**Live Analysis:** You paid exactly the standard ${SP:.2f} rate. No variance.")

    with col2:
        st.metric(
            "DM Qty Var",
            f"${abs(dm_qty_var):,.2f}",
            f"{'-' if dm_qty_var <= 0 else ''}Favorable" if dm_qty_var <= 0 else "Unfavorable",
            delta_color="inverse",
        )
        with st.expander("📘 What is this?"):
            st.markdown("**Formula:** `SP x (AQ - SQ)`")
            st.markdown("**Meaning:** The financial impact of scrap, waste, or over-usage on the floor.")
            st.markdown("---")
            if AQ < SQ:
                st.success(
                    f"**Live Analysis:** You used {SQ - AQ:,} fewer pounds than the {SQ:,.0f} lb standard allowance. Excellent material efficiency!"
                )
            elif AQ > SQ:
                st.error(
                    f"**Live Analysis:** You used {AQ - SQ:,} more pounds than the {SQ:,.0f} lb standard allowance. This excess waste drives costs up."
                )
            else:
                st.info(f"**Live Analysis:** You used exactly the standard {SQ:,.0f} lbs. No variance.")

    with col3:
        st.metric(
            "DL Rate Var",
            f"${abs(dl_rate_var):,.2f}",
            f"{'-' if dl_rate_var <= 0 else ''}Favorable" if dl_rate_var <= 0 else "Unfavorable",
            delta_color="inverse",
        )
        with st.expander("📘 What is this?"):
            st.markdown("**Formula:** `AH x (AR - SR)`")
            st.markdown("**Meaning:** The financial impact of paying workers more or less than expected.")
            st.markdown("---")
            if AR < SR:
                st.success(
                    f"**Live Analysis:** You paid ${SR - AR:.2f} less per hour than the ${SR:.2f} standard rate. This creates a Favorable variance."
                )
            elif AR > SR:
                st.error(
                    f"**Live Analysis:** You paid ${AR - SR:.2f} more per hour than the ${SR:.2f} standard. Did you authorize emergency overtime?"
                )
            else:
                st.info(f"**Live Analysis:** You paid exactly the standard ${SR:.2f} rate. No variance.")

    with col4:
        st.metric(
            "DL Eff Var",
            f"${abs(dl_eff_var):,.2f}",
            f"{'-' if dl_eff_var <= 0 else ''}Favorable" if dl_eff_var <= 0 else "Unfavorable",
            delta_color="inverse",
        )
        with st.expander("📘 What is this?"):
            st.markdown("**Formula:** `SR x (AH - SH)`")
            st.markdown("**Meaning:** The financial impact of manufacturing taking longer than planned.")
            st.markdown("---")
            if AH < SH:
                st.success(
                    f"**Live Analysis:** You finished production using {SH - AH:,} fewer hours than the {SH:,.0f} hour standard. Highly efficient labor!"
                )
            elif AH > SH:
                st.error(
                    f"**Live Analysis:** Production took {AH - SH:,} hours longer than the {SH:,.0f} hour standard. Machine jams or slow line speeds are costing you money."
                )
            else:
                st.info(f"**Live Analysis:** Production took exactly the standard {SH:,.0f} hours. No variance.")

    chart_text = [f"${v/1000:,.1f}k" for v in [std_cost, dm_price_var, dm_qty_var, dl_rate_var, dl_eff_var, total_actual]]

    fig = go.Figure(
        go.Waterfall(
            name="Cost Bridge",
            orientation="v",
            measure=["absolute", "relative", "relative", "relative", "relative", "total"],
            x=["Standard Cost", "DM Price Var", "DM Qty Var", "DL Rate Var", "DL Eff Var", "Actual Cost"],
            textposition="outside",
            text=chart_text,
            textfont={"size": 16, "family": "Arial Black"},
            y=[std_cost, dm_price_var, dm_qty_var, dl_rate_var, dl_eff_var, total_actual],
            connector={"line": {"color": "rgb(63, 63, 63)", "width": 2}},
            decreasing={"marker": {"color": "#2ca02c"}},
            increasing={"marker": {"color": "#d62728"}},
            totals={"marker": {"color": "#4d1979"}},
        )
    )

    fig.update_layout(
        title={"text": "Cost Bridge: Standard to Actual", "font": {"size": 24}},
        showlegend=False,
        height=550,
        font=dict(size=14, color="black"),
        margin=dict(t=80),
    )
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("### 🤖 AI Controller Analysis")
    if net_variance > 0:
        st.error(f"**Warning: Operating at a Net Deficit of ${net_variance:,.2f}.**")
        variances = {
            "Materials Price": dm_price_var,
            "Materials Quantity": dm_qty_var,
            "Labor Rate": dl_rate_var,
            "Labor Efficiency": dl_eff_var,
        }
        worst_name = max(variances, key=variances.get)
        worst_val = variances[worst_name]
        st.write(f"The primary driver of this deficit is an unfavorable **{worst_name} Variance** of ${worst_val:,.2f}.")
        hours_to_cut = net_variance / SR
        st.info(
            f"**Recovery Optimizer:** To offset this ${net_variance:,.2f} deficit strictly through labor efficiency, the floor manager must reduce production time by **{hours_to_cut:,.1f} hours** from the current actuals."
        )
    else:
        st.success(f"**Success: Operating at a Net Surplus of ${abs(net_variance):,.2f}.**")
        st.write("Production is currently operating under or at standard cost. Great job!")
        st.balloons()

    if chaos_mode:
        st.warning(
            "⚠️ **AUDIT ALERT:** The 'Enable Production Chaos' toggle is active. A $15,000 phantom material cost has been secretly injected into the math. The sliders no longer match the waterfall output. Can you find the leak?"
        )
        with st.expander("🔍 Reveal the Leak (Show Solution)"):
            st.markdown("**The Culprit:** Unrecorded Material Scrap / Theft")
            st.markdown(
                f"The UI slider shows you only used **{AQ_slider:,.0f} lbs** of material. However, the system silently processed **{AQ:,.0f} lbs** into the final math."
            )
            st.markdown(
                "This hidden **3,000 lb discrepancy** (valued at the standard \\$5.00/lb rate) perfectly explains the mysterious **\\$15,000 Unfavorable Quantity Variance** that doesn't match the inputs. This is why you must always audit the underlying data pipeline, not just the front-end dashboard!"
            )


# ==========================================
# 9. PAGE: HOW TO MAKE THIS
# ==========================================
def render_how_to_page():
    st.markdown(
        """
        <div style="padding:1rem 1.25rem;border-radius:0.75rem;background:linear-gradient(90deg, #eef4ff 0%, #f8fbff 100%);border:1px solid #d7e6ff;margin-bottom:1rem;">
            <h2 style="margin:0 0 0.35rem 0;">Build your own app in minutes</h2>
            <p style="margin:0 0 0.75rem 0;font-size:1rem;">
                Use the prompts below to create an interactive business dashboard with ChatGPT, then deploy it and share it with your audience.
            </p>
            <p style="margin:0;font-size:0.95rem;"><strong>Best for event participants:</strong> copy a prompt, paste it into ChatGPT, and follow the steps.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    cta1, cta2, cta3 = st.columns(3)
    cta1.metric("Step 1", "Copy a prompt")
    cta2.metric("Step 2", "Paste into ChatGPT")
    cta3.metric("Step 3", "Run and share")

    st.markdown("### Choose your path")
    p1, p2, p3 = st.columns(3)
    p1.markdown(
        """
        <div style="padding:1rem;border:1px solid #e6e6e6;border-radius:0.75rem;height:100%;background:#fafafa;">
            <h4 style="margin-top:0;">I want to build the app</h4>
            <p>Start with Prompt 1 to generate the full Streamlit dashboard code.</p>
            <p><strong>Best for:</strong> people who want a working app quickly.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    p2.markdown(
        """
        <div style="padding:1rem;border:1px solid #e6e6e6;border-radius:0.75rem;height:100%;background:#fafafa;">
            <h4 style="margin-top:0;">I want to deploy and share it</h4>
            <p>Use Prompt 2 to get step-by-step instructions for publishing the app online.</p>
            <p><strong>Best for:</strong> people who want a live link for an event or team.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    p3.markdown(
        """
        <div style="padding:1rem;border:1px solid #e6e6e6;border-radius:0.75rem;height:100%;background:#fafafa;">
            <h4 style="margin-top:0;">I want to customize it</h4>
            <p>Use Prompt 3 to adapt the app for your own company, brand, or use case.</p>
            <p><strong>Best for:</strong> people who want to make the example their own.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.write(
        "This page gives participants ready-to-use prompts they can paste into ChatGPT to build, deploy, and share an accounting dashboard like this one."
    )

    st.markdown("### 1) Prompt to create the actual app code")
    st.caption("Copy this into ChatGPT to generate the Streamlit app code.")
    build_prompt = dedent(
        """
        Act as an expert Python developer and managerial accountant.

        Create a complete, single-file Python Streamlit application for a live presentation that analyzes manufacturing cost variances.

        Scenario:
        - Product: Purple Anodized Aluminum Enclosures
        - Units produced: 10,000
        - Standard Material Quantity (SQ): 20,000 lbs
        - Standard Material Price (SP): $5.00 per lb
        - Standard Labor Hours (SH): 5,000 hours
        - Standard Labor Rate (SR): $20.00 per hour
        - Total Standard Cost: $200,000

        Requirements:
        - Add sidebar sliders for AQ, AP, AH, and AR
        - Calculate DM Price Variance = AQ x (AP - SP)
        - Calculate DM Quantity Variance = SP x (AQ - SQ)
        - Calculate DL Rate Variance = AH x (AR - SR)
        - Calculate DL Efficiency Variance = SR x (AH - SH)
        - Label each variance as Favorable if negative and Unfavorable if positive
        - Create a Plotly waterfall chart that starts with Standard Cost and ends with Actual Cost
        - Show metric cards for the four variances
        - Add a second page explaining how the app was created and how someone could build a similar one
        - Keep the code polished, presentation-ready, and in one Python file

        Return only the final Python code.
        """
    ).strip()
    st.code(build_prompt, language="text")
    copy_button(build_prompt, "Copy Prompt 1: App Code", "prompt1")

    st.markdown("### 2) Prompt to deploy and share what you create")
    st.caption("Copy this into ChatGPT to get beginner-friendly deployment and sharing instructions.")
    deploy_prompt = dedent(
        """
        Act as a beginner-friendly technical coach.

        I created a single-file Streamlit app in Python and I want to deploy it and share it with event participants.

        Give me a clear, step-by-step guide that includes:
        - How to save the code into a .py file
        - How to install Streamlit and Plotly
        - How to run the app locally
        - How to create a requirements.txt file
        - How to upload the project to GitHub
        - How to deploy it using Streamlit Community Cloud
        - How to test the public link before sharing it
        - How to send the link to attendees
        - Common setup mistakes and how to fix them

        Use exact terminal commands and explain everything for a non-technical audience.
        """
    ).strip()
    st.code(deploy_prompt, language="text")
    copy_button(deploy_prompt, "Copy Prompt 2: Deploy and Share", "prompt2")

    st.markdown("### 3) Prompt to customize it for your own use case")
    st.caption("Copy this into ChatGPT to personalize the app for your own company, case study, or audience.")
    customize_prompt = dedent(
        """
        Act as an expert Streamlit developer, UX designer, and business analyst.

        I already have a Streamlit app that visualizes manufacturing cost variances. Help me customize it for my own organization.

        Please update the app so I can:
        - Change the product name and business scenario
        - Update the standard cost assumptions
        - Add my company colors and logo
        - Rewrite the explanatory text for a non-technical audience
        - Add one new feature such as overhead variance analysis, CSV upload, PDF export, or a commentary box explaining what caused the variances

        Keep the code in one Python file and return the full updated code.
        """
    ).strip()
    st.code(customize_prompt, language="text")
    copy_button(customize_prompt, "Copy Prompt 3: Customize", "prompt3")

    st.markdown("### Three simple steps")
    s1, s2, s3 = st.columns(3)
    s1.success("1. Copy a prompt\n\nStart with the app prompt, deployment prompt, or customization prompt.")
    s2.success("2. Paste into ChatGPT\n\nAsk ChatGPT to generate the code or instructions for you.")
    s3.success("3. Run and share\n\nTest locally, deploy it online, and share the link with others.")

    st.markdown("### What these tools are doing")
    g1, g2, g3 = st.columns(3)
    g1.info("**Streamlit** turns Python into a simple interactive web app.")
    g2.info("**Plotly** creates the interactive waterfall chart and visual storytelling.")
    g3.info("**ChatGPT** helps generate, explain, refine, and troubleshoot the app quickly.")

    st.markdown("### Make it easy for participants")
    c1, c2, c3 = st.columns(3)
    c1.info("Copy Prompt 1 into ChatGPT to generate the app code.")
    c2.info("Copy Prompt 2 into ChatGPT to get deployment and sharing instructions.")
    c3.info("Use Prompt 3 to personalize the app for your own company or case study.")

    st.markdown("### Try this next")
    t1, t2, t3 = st.columns(3)
    t1.warning("Add a company logo, event title, or brand colors.")
    t2.warning("Expand the app to include overhead or sales variances.")
    t3.warning("Add CSV upload so people can test their own numbers.")

    st.markdown("### Presenter notes")
    with st.expander("Open presenter notes"):
        st.markdown(
            """
            **Suggested talk track for the live demo**

            - This dashboard shows how actual results compare against standard manufacturing costs.
            - The sliders let us change materials and labor actuals in real time.
            - The waterfall chart tells the cost story visually, starting at standard cost and stepping through each variance.
            - The second page shows that this kind of app is not magic: attendees can build something similar themselves with well-structured prompts.
            - The goal is not only to show the analysis, but to show how quickly a useful business tool can be created and shared.
            """
        )

    st.markdown("### Quick start resources")
    st.code(
        "pip install streamlit plotly\npython3 -m streamlit run app.py",
        language="bash",
    )
    st.code(
        "streamlit\nplotly",
        language="text",
    )
    st.caption("Save the second code block as requirements.txt before deploying.")

    st.markdown("### Event tip: share with a QR code")
    st.write(
        "Once the app is deployed, generate a QR code for the public link and place it on your final presentation slide so attendees can open it instantly on their phones."
    )


# ==========================================
# 10. PAGE: GLOSSARY
# ==========================================
def render_glossary():
    st.markdown("### Glossary")
    st.write(
        "This page explains the core accounting and app terms used in the dashboard so participants can follow along more easily."
    )

    st.markdown("### Accounting terms")
    g1, g2 = st.columns(2)

    with g1:
        with st.expander("Standard Cost"):
            st.write(
                "The expected cost of producing a product under normal conditions. In this app, standard cost is the benchmark used to compare actual results."
            )
        with st.expander("Actual Cost"):
            st.write(
                "The real cost incurred based on actual materials used, prices paid, labor hours worked, and wage rates."
            )
        with st.expander("Variance"):
            st.write(
                "The difference between a standard amount and an actual amount. Variances help explain where performance differed from plan."
            )
        with st.expander("Favorable (F)"):
            st.write(
                "A variance that lowers cost compared with standard. In this app, a negative variance amount is treated as favorable."
            )
        with st.expander("Unfavorable (U)"):
            st.write(
                "A variance that increases cost compared with standard. In this app, a positive variance amount is treated as unfavorable."
            )
        with st.expander("Direct Materials"):
            st.write(
                "Raw materials that can be directly traced to the finished product, such as aluminum used to make the enclosure."
            )

    with g2:
        with st.expander("Direct Labor"):
            st.write(
                "The labor cost of employees who directly work on producing the product."
            )
        with st.expander("DM Price Variance"):
            st.write(
                "The cost impact of paying a different price per unit of material than expected. Formula: AQ x (AP - SP)."
            )
        with st.expander("DM Quantity Variance"):
            st.write(
                "The cost impact of using more or fewer materials than the standard allowed for actual output. Formula: SP x (AQ - SQ)."
            )
        with st.expander("DL Rate Variance"):
            st.write(
                "The cost impact of paying a different labor rate per hour than expected. Formula: AH x (AR - SR)."
            )
        with st.expander("DL Efficiency Variance"):
            st.write(
                "The cost impact of using more or fewer labor hours than the standard allowed for actual output. Formula: SR x (AH - SH)."
            )
        with st.expander("Waterfall Chart"):
            st.write(
                "A visual that starts with a base value, then shows how each positive or negative step changes the total. Here it shows how standard cost becomes actual cost."
            )

    st.markdown("### App-building terms")
    a1, a2 = st.columns(2)

    with a1:
        with st.expander("Streamlit"):
            st.write(
                "A Python framework used to turn data analysis code into a simple interactive web app."
            )
        with st.expander("Plotly"):
            st.write(
                "A visualization library used here to create the interactive waterfall chart."
            )
        with st.expander("Prompt"):
            st.write(
                "A clear instruction given to ChatGPT to generate code, explanations, or deployment steps."
            )

    with a2:
        with st.expander("Deploy"):
            st.write(
                "To publish the app online so other people can access it through a web link."
            )
        with st.expander("requirements.txt"):
            st.write(
                "A text file listing the Python packages needed to run the app, such as streamlit and plotly."
            )
        with st.expander("GitHub"):
            st.write(
                "A platform used to store and share code, and often used as the source for deploying an app."
            )

    st.info("Tip: If you are new to either accounting or app development, start here before using the prompt page.")


# ==========================================
# 11. ROUTER
# ==========================================
if page == "Variance Dashboard":
    render_dashboard()
elif page == "How you can make this or something similar!":
    render_how_to_page()
else:
    render_glossary()
