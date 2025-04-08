import streamlit as st
import matplotlib.pyplot as plt
import tempfile
from fpdf import FPDF
import random
import os

st.set_page_config(page_title="B.COM CAssess", layout="centered")
st.markdown("""
    <style>
        body {
            background-color: #fefefe;
        }
    </style>
""", unsafe_allow_html=True)

def analyze_responses(responses):
    traits = {
        "Analytical Thinking": responses[0],
        "Communication Skills": responses[1],
        "Tech Comfort": responses[2],
        "Business Acumen": responses[3],
        "Teamwork": responses[4],
        "Interest in Programming": responses[5]
    }
    strengths = [k for k, v in traits.items() if v >= 7]
    weaknesses = [k for k, v in traits.items() if v <= 4]

    score = sum(responses) / len(responses)
    fit = score >= 6.5

    if fit:
        recommendation_text = "You are a strong fit for B.Com (CA). Your skills and interests align well with the demands of the course."
    elif 5 <= score < 6.5:
        recommendation_text = "You can still consider B.Com (CA), but you may find better growth in courses like BBA or BSc Computer Science."
    else:
        recommendation_text = "You can shine brighter in fields such as BBA, BA (English), or BSc Psychology, based on your strengths."

    return strengths, weaknesses, fit, recommendation_text, round(score * 10, 2), traits

def generate_pdf_report(name, gender, responses, fit, recommendation_text, score, traits):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)

    pdf.cell(200, 10, txt=f"Student Assessment Report", ln=True, align='C')
    pdf.ln(10)
    pdf.cell(200, 10, txt=f"Name: {name}", ln=True)
    pdf.cell(200, 10, txt=f"Gender: {gender}", ln=True)
    pdf.ln(10)
    pdf.multi_cell(200, 10, txt=f"Scores:")
    for key, value in traits.items():
        pdf.cell(200, 10, txt=f"{key}: {value}/10", ln=True)

    pdf.ln(5)
    pdf.cell(200, 10, txt=f"Overall Fit Score: {score}%", ln=True)
    pdf.ln(5)
    pdf.multi_cell(200, 10, txt=f"Recommendation: {recommendation_text}")

    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        pdf.output(tmp.name)
        return tmp.name

st.title("B.COM (CA) Admission Strength Analyzer")
st.markdown("### Enter Student Details")

name = st.text_input("Student Name")
gender = st.selectbox("Gender", ["Boy", "Girl", "Prefer not to say"])

st.markdown("### Rate the following from 0 (Poor) to 10 (Excellent)")
q1 = st.slider("1. Problem Solving / Analytical Thinking", 0, 10, 5)
q2 = st.slider("2. Communication Skills", 0, 10, 5)
q3 = st.slider("3. Comfort with Technology", 0, 10, 5)
q4 = st.slider("4. Interest in Business Studies", 0, 10, 5)
q5 = st.slider("5. Team Collaboration / Leadership", 0, 10, 5)
q6 = st.slider("6. Interest in Programming / Coding", 0, 10, 5)

responses = [q1, q2, q3, q4, q5, q6]

if st.button("Evaluate Student"):
    strengths, weaknesses, fit, recommendation_text, score, traits = analyze_responses(responses)

    st.subheader("Evaluation Summary")
    st.markdown(f"**Fit Score**: {score}%")

    st.markdown("---")
    st.markdown("### Strengths")
    st.write(", ".join(strengths) if strengths else "No major strengths identified.")

    st.markdown("### Weaknesses")
    st.write(", ".join(weaknesses) if weaknesses else "No significant weaknesses.")

    st.markdown("### Final Recommendation")
    st.info(recommendation_text)

    st.markdown("### Fit Score Chart")
    fig, ax = plt.subplots()
    ax.barh(list(traits.keys()), list(traits.values()), color="skyblue")
    ax.set_xlim([0, 10])
    st.pyplot(fig)

    st.markdown("---")
    pdf_path = generate_pdf_report(name, gender, responses, fit, recommendation_text, score, traits)
    with open(pdf_path, "rb") as f:
        st.download_button("Download PDF Report", f, file_name=f"{name}_BComCA_Report.pdf")
