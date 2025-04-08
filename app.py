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
st.write("Answer the questions to evaluate the student's suitability for B.Com (CA)")

# ------------------ Form ------------------
with st.form("admission_form"):
    name = st.text_input("Student Name")
    age = st.number_input("Age", min_value=15, max_value=30)
    email = st.text_input("Email ID")
    phone = st.text_input("Phone Number")
    school = st.text_input("School Name")

    communication = st.slider("Communication Skills", 1, 10)
    interest_commerce = st.slider("Interest in Commerce/Accounting", 1, 10)
    tech_affinity = st.slider("Comfort with Computers/Technology", 1, 10)
    logical_reasoning = st.slider("Logical & Analytical Thinking", 1, 10)
    teamwork = st.slider("Teamwork & Collaboration", 1, 10)
    leadership = st.slider("Leadership/Initiative", 1, 10)
    motivation = st.slider("Motivation & Career Clarity", 1, 10)
    other_interest = st.text_input("Other Subject Interests (e.g., Arts, Science, Business Mgmt)")

    # Additional text-based questions
    why_commerce = st.text_area("Why are you interested in Commerce/Computer Applications?")
    future_goal = st.text_area("What is your career goal?")
    strength_self = st.text_area("What do you think is your biggest strength?")
    weakness_self = st.text_area("What do you think is your biggest weakness?")

    submitted = st.form_submit_button("Evaluate Student")

# ------------------ Processing ------------------
if submitted:
    st.success("Evaluation in progress...")

    # Prepare prompt for AI
    prompt = f"""
    A student provided the following responses:

    Name: {name}
    Age: {age}
    Email: {email}
    Phone: {phone}
    School: {school}

    Communication Skills: {communication}/10
    Interest in Commerce: {interest_commerce}/10
    Technology Affinity: {tech_affinity}/10
    Logical Reasoning: {logical_reasoning}/10
    Teamwork: {teamwork}/10
    Leadership: {leadership}/10
    Motivation: {motivation}/10
    Other Interests: {other_interest}

    Written Answers:
    - Why Commerce/CA: {why_commerce}
    - Career Goal: {future_goal}
    - Self Strength: {strength_self}
    - Self Weakness: {weakness_self}

    Based on the above data, analyze:
    1. Student's strengths
    2. Student's weaknesses
    3. Whether the student is a good fit for B.Com (CA)
    4. If not suitable for B.Com (CA), suggest the best-suited stream (like BBA, BA, BSc etc.)
    5. Give a final recommendation in paragraph form.
    """

    try:
        response = openai.ChatCompletion.create(
            model="mistralai/mixtral-8x7b",
            messages=[{"role": "user", "content": prompt}]
        )
        analysis = response.choices[0].message.content

        # ------------------ Summary Score ------------------
        score_total = communication + interest_commerce + tech_affinity + logical_reasoning + teamwork + leadership + motivation
        score_out_of = 70
        percentage_score = round((score_total / score_out_of) * 100, 2)

        st.markdown("### 🧠 AI-Based Assessment")
        st.write(analysis)

        st.markdown("### ⭐ Summary")
        if percentage_score >= 75:
            summary = f"{name} has a strong overall score of {percentage_score}%, indicating a good fit for the B.Com (CA) program."
        elif 60 <= percentage_score < 75:
            summary = f"{name} has a moderate score of {percentage_score}%. B.Com (CA) could be suitable with additional guidance, but exploring related fields like BBA or BSc (CS) might also be beneficial."
        else:
            summary = f"{name} scored {percentage_score}%, which suggests B.Com (CA) may not be the best fit. Alternatives such as BBA, BA, or BSc could align better with their strengths."

        st.markdown(summary)

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
        pdf.cell(200, 10, txt=f"Email: {email}", ln=True)
        pdf.cell(200, 10, txt=f"Phone: {phone}", ln=True)
        pdf.cell(200, 10, txt=f"School: {school}", ln=True)

        for skill, score in scores.items():
            pdf.cell(200, 10, txt=f"{skill}: {score}/10", ln=True)

        pdf.cell(200, 10, txt=f"Summary Score: {percentage_score}%", ln=True)
        pdf.multi_cell(200, 10, txt=f"Summary: {summary}")

        pdf.ln(5)
        pdf.cell(200, 10, txt="Written Responses:", ln=True)
        pdf.multi_cell(200, 10, txt=f"Why BCom(CA): {why_commerce}\nCareer Goal: {future_goal}\nStrength: {strength_self}\nWeakness: {weakness_self}\n")

        pdf.ln(5)
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
