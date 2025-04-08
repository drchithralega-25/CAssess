import streamlit as st
import matplotlib.pyplot as plt
from io import BytesIO
from fpdf import FPDF
import base64

st.set_page_config(page_title="B.COM CAssess", layout="centered")

# Function to analyze responses and recommend

def analyze_responses(name, gender, responses):
    strengths = []
    weaknesses = []
    total_score = 0
    traits = []

    for question, score in responses.items():
        total_score += score
        if score >= 7:
            strengths.append(question)
        elif score <= 4:
            weaknesses.append(question)
        traits.append(f"{question}: {score}/10")

    percentage = (total_score / (len(responses) * 10)) * 100

    if percentage >= 70:
        fit = "Yes"
        recommendation = f"{name} is a strong candidate for B.Com (CA) with a score of {percentage:.2f}%. The responses indicate good potential in key areas like {', '.join(strengths[:2])}."
    elif 50 <= percentage < 70:
        fit = "Moderate"
        recommendation = f"{name} shows a moderate fit for B.Com (CA) with a score of {percentage:.2f}%. With improvement in areas like {', '.join(weaknesses[:2])}, they could thrive in this program. Alternatively, they may also consider BBA or B.Com General."
    else:
        fit = "No"
        recommendation = f"{name} scored {percentage:.2f}%, indicating that other streams like BBA, BA, or B.Sc might be a better fit currently. Areas like {', '.join(weaknesses[:2])} need further development."

    summary = f"\nStrengths: {', '.join(strengths) if strengths else 'None'}\nWeaknesses: {', '.join(weaknesses) if weaknesses else 'None'}\n\nFinal Recommendation: {recommendation}"
    return fit, recommendation, summary, percentage, traits

# Function to generate PDF report

def generate_pdf_report(name, gender, responses, fit, recommendation_text, score, traits):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)

    pdf.cell(200, 10, txt=f"B.COM CAssess - Student Evaluation Report", ln=True, align='C')
    pdf.ln(10)
    pdf.cell(200, 10, txt=f"Name: {name}", ln=True)
    pdf.cell(200, 10, txt=f"Gender: {gender}", ln=True)
    pdf.ln(10)

    for trait in traits:
        pdf.multi_cell(200, 10, txt=trait)

    pdf.ln(5)
    pdf.cell(200, 10, txt=f"Fit for B.Com (CA): {fit}", ln=True)
    pdf.multi_cell(200, 10, txt=f"Final Recommendation: {recommendation_text}")

    buffer = BytesIO()
    pdf.output(buffer)
    buffer.seek(0)
    b64_pdf = base64.b64encode(buffer.read()).decode('utf-8')
    pdf_link = f'<a href="data:application/pdf;base64,{b64_pdf}" download="BCom_CA_Report.pdf">Download PDF Report</a>'
    return pdf_link

# Main App
st.title("B.COM CAssess")

name = st.text_input("Enter your name")
gender = st.selectbox("Select your gender", ["Male", "Female", "Other"])

st.markdown("### Rate the following from 1 to 10")
questions = [
    "Interest in Computer Applications",
    "Mathematical Ability",
    "Communication Skills",
    "Leadership Qualities",
    "Teamwork",
    "Problem Solving",
    "Creativity",
    "Adaptability"
]

responses = {}
for q in questions:
    responses[q] = st.slider(q, 1, 10, 5)

if st.button("Evaluate"):
    fit, recommendation_text, summary, score, traits = analyze_responses(name, gender, responses)

    st.subheader("Result Summary")
    st.markdown(f"**Score to fit in B.Com (CA):** {score:.2f}%")
    st.markdown(summary)

    pdf_link = generate_pdf_report(name, gender, responses, fit, recommendation_text, score, traits)
    st.markdown(pdf_link, unsafe_allow_html=True)

    st.subheader("Visual Analysis")
    fig, ax = plt.subplots()
    ax.barh(list(responses.keys()), list(responses.values()), color='skyblue')
    ax.set_xlabel('Score (out of 10)')
    ax.set_title('Student Self Assessment')
    st.pyplot(fig)
