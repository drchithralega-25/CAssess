import streamlit as st
from fpdf import FPDF
from typing import Dict
import matplotlib.pyplot as plt
import base64
from io import BytesIO

# Set page config early
st.set_page_config(page_title="B.COM CAssess", layout="centered")

# --- Function to generate PDF report ---
def generate_pdf_report(name: str, gender: str, responses: Dict[str, str], analysis: str, recommendation: str, score: int, traits: Dict[str, int]):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)

    pdf.cell(200, 10, txt="Student Evaluation Report", ln=True, align='C')
    pdf.ln(10)

    pdf.cell(200, 10, txt=f"Name: {name}", ln=True)
    pdf.cell(200, 10, txt=f"Gender: {gender}", ln=True)
    pdf.ln(5)

    for question, answer in responses.items():
        pdf.multi_cell(0, 10, txt=f"{question}\nAnswer: {answer}")
        pdf.ln(1)

    pdf.ln(5)
    pdf.cell(200, 10, txt="Personal Traits (0-10):", ln=True)
    for trait, val in traits.items():
        pdf.cell(200, 10, txt=f"{trait}: {val}/10", ln=True)

    pdf.ln(5)
    pdf.multi_cell(0, 10, txt="Evaluation Summary:")
    pdf.multi_cell(0, 10, txt=analysis)
    pdf.ln(2)
    pdf.multi_cell(0, 10, txt=f"Final Recommendation: {recommendation}")
    pdf.multi_cell(0, 10, txt=f"Score to fit in BCom (CA): {score}%")

    buffer = BytesIO()
    pdf.output(buffer, dest='S').encode('latin1')
    buffer.seek(0)
    b64 = base64.b64encode(buffer.read()).decode()
    href = f'<a href="data:application/octet-stream;base64,{b64}" download="student_evaluation_report.pdf">Download PDF Report</a>'
    return href

# --- Title and Form ---
st.title("B.COM CAssess - Admission Evaluator")
st.markdown("""
<style>
body {
    background-color: #f8f9fa;
}
</style>
""", unsafe_allow_html=True)

st.markdown("#### Fill the following to evaluate your suitability for B.Com (CA)")

with st.form("student_form"):
    name = st.text_input("Name")
    gender = st.selectbox("Gender", ["Boy", "Girl", "Other"])
    age = st.number_input("Age", min_value=15, max_value=25)

    q1 = st.text_area("1. Why do you want to join B.Com (CA)?")
    q2 = st.text_area("2. What are your favorite school subjects and why?")
    q3 = st.text_area("3. How do you rate your computer skills (e.g., MS Office, programming)?")
    q4 = st.text_area("4. How comfortable are you with accounting and numbers?")
    q5 = st.text_area("5. What are your hobbies or extracurricular interests?")

    st.markdown("#### Rate your qualities (0 - Poor, 10 - Excellent)")
    communication = st.slider("Communication Skills", 0, 10, 5)
    problem_solving = st.slider("Problem Solving Skills", 0, 10, 5)
    teamwork = st.slider("Teamwork & Collaboration", 0, 10, 5)
    leadership = st.slider("Leadership", 0, 10, 5)
    tech_comfort = st.slider("Tech Comfort Level", 0, 10, 5)

    submitted = st.form_submit_button("Evaluate")

if submitted:
    responses = {
        "Why do you want to join B.Com (CA)?": q1,
        "Favorite subjects": q2,
        "Computer skills": q3,
        "Comfort with accounting": q4,
        "Hobbies": q5
    }

    traits = {
        "Communication Skills": communication,
        "Problem Solving": problem_solving,
        "Teamwork": teamwork,
        "Leadership": leadership,
        "Tech Comfort": tech_comfort
    }

    # Basic rule-based analysis
    score = 0
    if "account" in q1.lower() or "computer" in q1.lower(): score += 20
    if any(sub in q2.lower() for sub in ["commerce", "computer", "math"]): score += 20
    if any(s in q3.lower() for s in ["good", "excellent", "proficient"]): score += 20
    if any(s in q4.lower() for s in ["very", "comfortable", "easy"]): score += 20
    if any(h in q5.lower() for h in ["coding", "chess", "finance", "typing"]): score += 20

    avg_traits = sum(traits.values()) / len(traits)
    score = min(score + int(avg_traits * 2), 100)

    # Result Summary
    if score >= 80:
        fit = "✅ Strong fit for B.Com (CA)."
        stream_suggestion = "B.Com (CA)"
    elif score >= 60:
        fit = "⚠️ Moderate fit. May consider B.Com General, BBA, or BCA."
        stream_suggestion = "B.Com / BBA / BCA"
    else:
        fit = "❌ Not a suitable fit for B.Com (CA). You may explore BA, BSc, or Humanities."
        stream_suggestion = "BA / BSc / Humanities"

    summary = f"""
Name: {name}
Gender: {gender}
Score: {score}%

{fit}
Recommended Stream: {stream_suggestion}
"""

    st.success("Evaluation Completed")
    st.markdown("### Summary:")
    st.markdown(summary.replace("\n", "\n\n"))

    recommendation_text = f"Based on the student's answers and rated qualities, {name} exhibits a {fit.lower()} The overall score of {score}% reflects their academic and personality alignment with the B.Com (CA) program. If not B.Com (CA), {stream_suggestion} would be more suitable."

    # Generate and offer PDF download
    pdf_link = generate_pdf_report(name, gender, responses, fit, recommendation_text, score, traits)
    st.markdown(pdf_link, unsafe_allow_html=True)

    # Chart for visual feedback
    fig, ax = plt.subplots()
    ax.barh(["Suitability Score"], [score], color="#4CAF50" if score >= 80 else ("#FFC107" if score >= 60 else "#F44336"))
    ax.set_xlim(0, 100)
    ax.set_title("B.Com (CA) Suitability Score")
    st.pyplot(fig)
