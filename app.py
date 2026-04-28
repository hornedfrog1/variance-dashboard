import streamlit as st

import plotly.graph_objects as go

import streamlit.components.v1 as components

from textwrap import dedent

st.set_page_config(

    page_title="DM and DL Variance Visualizer",

    page_icon="📊",

    layout="wide",

)

UNITS_PRODUCED = 10_000

PRODUCT_NAME = "Purple Anodized Aluminum Enclosures"

SQ = 20_000

SP = 5.00

SH = 5_000

SR = 20.00

TOTAL_STANDARD_COST = 200_000.00

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

def render_dashboard() -> None:

    st.title("Direct Materials and Direct Labor Variance Visualizer")

    st.subheader(f"Scenario: {UNITS_PRODUCED:,} units of {PRODUCT_NAME}")

    st.success(

        "Want to see how to build this? Open the sidebar and click 'How you can make this or something similar!'"

    )

    col_a, col_b = st.columns(2)

    with col_a:

        st.markdown("### Standard Cost Assumptions")

        st.write(f"**Standard Material Quantity (SQ):** {SQ:,} lbs")

        st.write(f"**Standard Material Price (SP):** ${SP:,.2f} per lb")

        st.write(f"**Standard Labor Hours (SH):** {SH:,} hours")

        st.write(f"**Standard Labor Rate (SR):** ${SR:,.2f} per hour")

        st.write(f"**Total Standard Cost:** ${TOTAL_STANDARD_COST:,.2f}")

    with col_b:

        st.markdown("### Actual Cost Snapshot")

        st.write(f"**Actual DM Cost:** ${actual_dm_cost:,.2f}")

        st.write(f"**Actual DL Cost:** ${actual_dl_cost:,.2f}")

        st.write(f"**Total Actual Cost:** ${actual_total_cost:,.2f}")

        st.write(f"**Total Variance:** {variance_display(total_variance)}")

    labels = [

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

            orientation="v",

            measure=measure,

            x=labels,

            y=values,

            text=text_values,

            textposition="outside",

            connector={"line": {"color": "rgba(120,120,120,0.5)"}},

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

    st.markdown("### Variance Metrics")

    m1, m2, m3, m4 = st.columns(4)

    m1.metric(

        label=f"DM Price Variance ({variance_label(dm_price_variance)})",

        value=fmt_currency(dm_price_variance),

        delta=variance_word(dm_price_variance),

    )

    m2.metric(

        label=f"DM Quantity Variance ({variance_label(dm_quantity_variance)})",

        value=fmt_currency(dm_quantity_variance),

        delta=variance_word(dm_quantity_variance),

    )

    m3.metric(

        label=f"DL Rate Variance ({variance_label(dl_rate_variance)})",

        value=fmt_currency(dl_rate_variance),

        delta=variance_word(dl_rate_variance),

    )

    m4.metric(

        label=f"DL Efficiency Variance ({variance_label(dl_efficiency_variance)})",

        value=fmt_currency(dl_efficiency_variance),

        delta=variance_word(dl_efficiency_variance),

    )

    st.markdown("### Calculation Detail")

    st.table(

        [

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

    )

    st.caption(

        "Negative variances are Favorable because they reduce cost versus standard. Positive variances are Unfavorable because they increase cost versus standard."

    )

def render_how_to_page() -> None:

    st.title("How you can make this or something similar!")

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

    s1.success(

        "1. Copy a prompt\n\nStart with the app prompt, deployment prompt, or customization prompt."

    )

    s2.success(

        "2. Paste into ChatGPT\n\nAsk ChatGPT to generate the code or instructions for you."

    )

    s3.success(

        "3. Run and share\n\nTest locally, deploy it online, and share the link with others."

    )

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

    with st.expander("Even more ideas to improve the experience"):

        st.markdown(

            """

            - Add a short challenge asking attendees to modify the app after the session.

            - Add a notes section that explains what operational events might cause each variance.

            - Add a downloadable one-page summary for participants.

            - Add a presenter mode section with talking points for the live demo.

            - Add a QR code image directly in the app once the final public URL is live.

            """

        )

def render_glossary() -> None:

    st.title("Glossary")

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

page = st.sidebar.radio(

    "Navigate",

    ["Variance Dashboard", "How you can make this or something similar!", "Glossary"],

)

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

dm_price_variance = AQ * (AP - SP)

dm_quantity_variance = SP * (AQ - SQ)

dl_rate_variance = AH * (AR - SR)

dl_efficiency_variance = SR * (AH - SH)

total_variance = (

    dm_price_variance

    + dm_quantity_variance

    + dl_rate_variance

    + dl_efficiency_variance

)

actual_total_cost = TOTAL_STANDARD_COST + total_variance

actual_dm_cost = AQ * AP

actual_dl_cost = AH * AR

if page == "Variance Dashboard":

    render_dashboard()

elif page == "How you can make this or something similar!":

    render_how_to_page()

else:

    render_glossary()
