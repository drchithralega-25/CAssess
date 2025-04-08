import streamlit as st
import openai
import matplotlib.pyplot as plt
import pandas as pd
from fpdf import FPDF
import tempfile
import base64

# ------------------ Page Config ------------------
st.set_page_config(page_title="B.COM CAssess", layout="centered")

# ------------------ API Setup ------------------
openai.api_key = st.secrets["OPENROUTER_API_KEY"]
openai.api_base = "https://openrouter.ai/api/v1"

# ------------------ App UI ------------------
st.markdown(
    """
    <style>
    body {
        background: linear-gradient(to right, #fdfcfb, #e2d1c3);
    }
    .reportview-container .main .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }
    </style>
    """,
    unsafe_allow_html=True
)

st.title("📊 B.COM CAssess - Student Admission Evaluator")
st.write("Fill in the questionnaire to evaluate student's suitability for B.Com (CA)")

# ------------------ Form ------------------
with st.form("admission_form"):
    name = st.text_input("Student Name")
    age = st.number_input("Age", min_value=15, max_value=30)
    communication = st.slider("Communication Skills", 1, 10)
    interest_commerce = st.slider("Interest in Commerce/Accounting", 1, 10)
    tech_affinity = st.slider("Comfort with Computers/Technology", 1, 10)
    logical_reasoning = st.slider("Logical & Analytical Thinking", 1, 10)
    teamwork = st.slider("Teamwork & Collaboration", 1, 10)
    leadership = st.slider("Leadership/Initiative", 1, 10)
    motivation = st.slider("Motivation & Career Clarity", 1, 10)
    other_interest = st.text_input("Other Subject Interests (e.g., Arts, Science, Business Mgmt)")
    submitted = st.form_submit_button("Evaluate Student")

# ------------------ Processing ------------------
if submitted:
    st.success("Evaluation in progress...")

    # Prepare prompt for AI
    prompt = f"""
    Student Name: {name}
    Age: {age}
    Communication Skills: {communication}/10
    Commerce Interest: {interest_commerce}/10
    Technology Affinity: {tech_affinity}/10
    Logical Reasoning: {logical_reasoning}/10
    Teamwork: {teamwork}/10
    Leadership: {leadership}/10
    Motivation: {motivation}/10
    Other Interests: {other_interest}

    Based on the above, assess the student's:
    - Strengths
    - Weaknesses
    - Fit for B.Com (CA)
    - Suggest best-fit department if not suitable for B.Com(CA).
    Provide a short paragraph of recommendation.
    """

    try:
        response = openai.ChatCompletion.create(
            model="mistralai/mixtral-8x7b",
            messages=[{"role": "user", "content": prompt}]
        )
        analysis = response.choices[0].message.content
        st.markdown("### 🧠 AI-Based Assessment")
        st.write(analysis)

        # ------------------ Chart ------------------
        scores = {
            "Communication": communication,
            "Commerce Interest": interest_commerce,
            "Tech Affinity": tech_affinity,
            "Reasoning": logical_reasoning,
            "Teamwork": teamwork,
            "Leadership": leadership,
            "Motivation": motivation
        }
        df = pd.DataFrame(list(scores.items()), columns=["Skill", "Score"])

        st.markdown("### 📈 Skill Chart")
        fig, ax = plt.subplots()
        ax.barh(df["Skill"], df["Score"], color="#6a5acd")
        ax.set_xlim([0, 10])
        ax.set_xlabel("Score out of 10")
        st.pyplot(fig)

        # ------------------ PDF Report ------------------
        st.markdown("### 📄 Download Evaluation Report")

        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)
        pdf.cell(200, 10, txt="B.COM (CA) Admission Evaluation Report", ln=True, align='C')
        pdf.ln(10)
        pdf.cell(200, 10, txt=f"Student Name: {name}", ln=True)
        pdf.cell(200, 10, txt=f"Age: {age}", ln=True)

        for skill, score in scores.items():
            pdf.cell(200, 10, txt=f"{skill}: {score}/10", ln=True)

        pdf.ln(10)
        pdf.multi_cell(200, 10, txt=f"Assessment:\n{analysis}")

        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
            pdf.output(tmp.name)
            with open(tmp.name, "rb") as f:
                base64_pdf = base64.b64encode(f.read()).decode('utf-8')
                pdf_display = f'<a href="data:application/pdf;base64,{base64_pdf}" download="{name}_assessment.pdf">📥 Download PDF</a>'
                st.markdown(pdf_display, unsafe_allow_html=True)

    except Exception as e:
        st.error("❌ Error analyzing student. Please check API setup or quota.")
        st.error(str(e))
