import streamlit as st
import matplotlib.pyplot as plt
import tempfile
from fpdf import FPDF
import base64
from io import BytesIO
import openai
import os

# Set Streamlit page config
st.set_page_config(page_title="B.COM CAssess", layout="centered")

# Title and intro
st.title("📘 B.COM CAssess")
st.markdown("""
Welcome to **B.COM CAssess** – your smart admission evaluator for the B.Com (CA) program.
Please answer a few questions to help us understand your strengths, weaknesses, and interests.
""")

# Student details
name = st.text_input("👤 Your Full Name")
gender = st.radio("🚻 Gender", ["Male", "Female", "Other"])

# Questionnaire sliders
st.subheader("🔍 B.COM CAssess")
q1 = st.slider("Interest in Commerce & Accounting", 0, 10, 5)
q2 = st.slider("Computer Application Skills", 0, 10, 5)
q3 = st.slider("Analytical Thinking", 0, 10, 5)
q4 = st.slider("Communication Skills", 0, 10, 5)
q5 = st.slider("Creativity / Presentation", 0, 10, 5)
q6 = st.slider("Leadership / Initiative Taking", 0, 10, 5)
q7 = st.slider("Interest in Math / Statistics", 0, 10, 5)
q8 = st.slider("Teamwork & Collaboration", 0, 10, 5)
q9 = st.slider("Interest in Business / Marketing", 0, 10, 5)
q10 = st.slider("Technical Adaptability", 0, 10, 5)

# Short answer
short_input = st.text_area("In a few words, describe your career goal.")

responses = {
    "Commerce": q1,
    "Computer": q2,
    "Analytical": q3,
    "Communication": q4,
    "Creativity": q5,
    "Leadership": q6,
    "Math": q7,
    "Teamwork": q8,
    "Business": q9,
    "Tech": q10
}

# Analyze
if st.button("📊 Analyze My Fit"):
    total = sum(responses.values())
    score = round((total / 100) * 100, 2)
    traits = sorted(responses.items(), key=lambda x: x[1], reverse=True)
    strengths = [k for k, v in traits[:3]]
    weaknesses = [k for k, v in traits[-3:]]

    fit = "Yes" if score >= 60 else "Maybe"
    suggested = "B.Com (CA)" if fit == "Yes" else ("BBA" if q4 > q1 else "BSc or BA")

    # Recommendation text
    recommendation_text = f"""
### 📌 Summary:
- **Fit Score:** {score}%
- **Strengths:** {', '.join(strengths)}
- **Weaknesses:** {', '.join(weaknesses)}
- **Suggested Course:** {suggested}

**Final Recommendation:** Based on your profile, you have a {'strong' if fit=='Yes' else 'moderate'} potential for B.Com (CA). You can succeed well if you strengthen your weaker areas. {"Alternatively, you may shine even brighter in " + suggested + " based on your interests." if fit=='Maybe' else "Keep pushing forward in your commerce and tech journey!"}
    """

    st.markdown(recommendation_text)

    # Bar chart
    st.subheader("📈 Your Skill Profile")
    fig, ax = plt.subplots()
    sns.barplot(x=list(responses.keys()), y=list(responses.values()), palette="Blues_d", ax=ax)
    plt.xticks(rotation=45)
    st.pyplot(fig)

    # PDF Report
    def generate_pdf_report(name, gender, responses, fit, recommendation_text, score, traits):
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", 'B', 16)
        pdf.cell(200, 10, txt="B.COM CAssess Report", ln=True, align='C')
        pdf.set_font("Arial", size=12)

        pdf.ln(10)
        pdf.cell(200, 10, txt=f"Name: {name}", ln=True)
        pdf.cell(200, 10, txt=f"Gender: {gender}", ln=True)
        pdf.cell(200, 10, txt=f"Fit Score: {score}%", ln=True)
        pdf.ln(5)
        pdf.cell(200, 10, txt=f"Strengths: {', '.join(strengths)}", ln=True)
        pdf.cell(200, 10, txt=f"Weaknesses: {', '.join(weaknesses)}", ln=True)
        pdf.ln(10)
        pdf.multi_cell(0, 10, txt="Recommendation:\n" + recommendation_text.replace("### ", ""))

        buffer = BytesIO()
        pdf.output(buffer)
        buffer.seek(0)
        b64 = base64.b64encode(buffer.read()).decode()
        href = f'<a href="data:application/octet-stream;base64,{b64}" download="BComCA_Report_{name}.pdf">📄 Download Your Report</a>'
        return href

    pdf_link = generate_pdf_report(name, gender, responses, fit, recommendation_text, score, traits)
    st.markdown(pdf_link, unsafe_allow_html=True)
