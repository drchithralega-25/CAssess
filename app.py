import streamlit as st
import base64
from fpdf import FPDF
from io import BytesIO
import matplotlib.pyplot as plt
import seaborn as sns

st.set_page_config(page_title="B.COM CAssess", layout="centered")

# Set background using base64 encoded image of light blue sky with white clouds
cloud_bg = """
<style>
.stApp {
    background-image: url("https://i.ibb.co/qxnWx6X/cloud-bg.jpg");
    background-size: cover;
    background-attachment: fixed;
    background-repeat: no-repeat;
}
</style>
"""
st.markdown(cloud_bg, unsafe_allow_html=True)

# App Title
st.markdown("<h1 style='text-align: center; color: #0B3D91;'>B.COM CAssess</h1>", unsafe_allow_html=True)

# Sample slider-based questionnaire
st.subheader("B.COM CAssess")
name = st.text_input("Name")
gender = st.selectbox("Gender", ["Male", "Female", "Other"])

communication = st.slider("Rate your communication skills", 0, 10, 5)
logical_reasoning = st.slider("Rate your logical thinking ability", 0, 10, 5)
interest_commerce = st.slider("Interest in commerce and accounting", 0, 10, 5)
tech_comfort = st.slider("Comfort with using computers and technology", 0, 10, 5)
creativity = st.slider("Creativity & Innovation", 0, 10, 5)

responses = {
    "Communication": communication,
    "Logical Reasoning": logical_reasoning,
    "Interest in Commerce": interest_commerce,
    "Tech Comfort": tech_comfort,
    "Creativity": creativity
}

# Analyze score
score = sum(responses.values())
percentage = round((score / 50) * 100, 2)
fit = "Yes" if percentage >= 70 else "No"

# Generate recommendation
if percentage >= 70:
    recommendation_text = f"{name} appears to be a good fit for B.Com (CA). Their skills and interests align well with the curriculum and future career opportunities."
elif 50 <= percentage < 70:
    recommendation_text = f"{name} may find B.Com (CA) a bit challenging but manageable. However, they might shine more in courses like BBA or BCom General."
else:
    recommendation_text = f"{name} has potential but may be better suited for streams like BA, BBA, or BSc based on their interests and skill ratings."

# Display summary
st.subheader("Summary Report")
st.markdown(f"**Name:** {name}")
st.markdown(f"**Gender:** {gender}")
st.markdown(f"**Fit for B.Com (CA):** {fit}")
st.markdown(f"**Score:** {score}/50")
st.markdown(f"**Fit Percentage:** {percentage}%")
st.markdown(f"**Recommendation:** {recommendation_text}")

# Visual chart
st.subheader("Visual Analysis")
fig, ax = plt.subplots()
sns.barplot(x=list(responses.keys()), y=list(responses.values()), palette="Blues_d", ax=ax)
ax.set_ylim(0, 10)
ax.set_title("Skill Ratings")
st.pyplot(fig)

# PDF report generation
def generate_pdf_report(name, gender, responses, fit, recommendation_text, score, percentage):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt="B.COM CAssess - Evaluation Report", ln=True, align='C')
    pdf.ln(10)
    pdf.cell(200, 10, txt=f"Name: {name}", ln=True)
    pdf.cell(200, 10, txt=f"Gender: {gender}", ln=True)
    pdf.ln(5)
    pdf.cell(200, 10, txt="Ratings:", ln=True)
    for trait, value in responses.items():
        pdf.cell(200, 10, txt=f"{trait}: {value}/10", ln=True)
    pdf.ln(5)
    pdf.cell(200, 10, txt=f"Score: {score}/50", ln=True)
    pdf.cell(200, 10, txt=f"Fit Percentage: {percentage}%", ln=True)
    pdf.cell(200, 10, txt=f"Fit for B.Com (CA): {fit}", ln=True)
    pdf.ln(5)
    pdf.multi_cell(0, 10, txt=f"Recommendation: {recommendation_text}")

    buffer = BytesIO()
    pdf.output(buffer)
    return buffer

if st.button("Generate PDF Report"):
    pdf_buffer = generate_pdf_report(name, gender, responses, fit, recommendation_text, score, percentage)
    st.download_button(
        label="Download PDF Report",
        data=pdf_buffer,
        file_name=f"{name}_Evaluation_Report.pdf",
        mime="application/pdf"
    )
