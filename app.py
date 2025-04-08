
import streamlit as st
import openai
import os
from fpdf import FPDF
import base64

# Load API key from Streamlit secrets
openai.api_key = os.getenv("OPENAI_API_KEY")

st.set_page_config(page_title="B.Com CA Admission Evaluator", layout="centered")

# --- Styling ---
st.markdown("""
    <style>
    body {
        background-color: #f2f4f8;
    }
    .main {
        background-color: white;
        padding: 2rem;
        border-radius: 10px;
        box-shadow: 0 4px 10px rgba(0,0,0,0.1);
    }
    h1, h2, h3 {
        color: #003366;
    }
    .stButton>button {
        background-color: #3366cc;
        color: white;
        font-weight: bold;
    }
    </style>
""", unsafe_allow_html=True)

st.title("🎓 B.Com (CA) Student Fit & Assessment Tool")
st.markdown("""
This tool analyzes student responses to evaluate their **strengths**, **weaknesses**, and **fit for B.Com (CA)**. 
If not suitable, it suggests an alternative stream that might better match their interests and skills.
""")

# --- Student Input Form ---
with st.form("student_form"):
    name = st.text_input("👤 Student Name")
    q1 = st.text_area("1️⃣ Why have you chosen to apply for the B.Com (CA) program?")
    q2 = st.text_area("2️⃣ What subjects did you enjoy the most in your higher secondary studies, and why?")
    q3 = st.text_area("3️⃣ Describe a time you had difficulty understanding a concept. How did you overcome it?")
    q4 = st.text_area("4️⃣ What is your level of comfort with using computers and technology in academics?")
    q5 = st.text_area("5️⃣ What kind of career or job role are you interested in after completing B.Com (CA)?")
    submitted = st.form_submit_button("🔍 Evaluate Student")

# --- AI Evaluation Logic ---
def analyze_student_fit(name, answers):
    prompt = f"""
    You are an expert admission advisor. A student named {name} has provided the following answers while applying to a B.Com (Computer Applications) program:

    1. Why B.Com (CA)?\n{answers[0]}
    2. Favorite subjects?\n{answers[1]}
    3. Academic challenge?\n{answers[2]}
    4. Tech comfort level?\n{answers[3]}
    5. Career interest?\n{answers[4]}

    Please analyze the student's:
    - Strengths
    - Weaknesses
    - Fit for B.Com (CA)
    - If not fit, suggest a better department (e.g., BBA, B.Sc, BA, etc.) and why.
    Provide a detailed evaluation in a friendly and insightful tone.
    """
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "user", "content": prompt}
        ]
    )
    return response['choices'][0]['message']['content']

# --- PDF Generation ---
def generate_pdf(student_name, report_text):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 16)
    pdf.cell(200, 10, f"Student Evaluation Report: {student_name}", ln=True, align='C')
    pdf.ln(10)
    pdf.set_font("Arial", size=12)
    for line in report_text.split('\n'):
        pdf.multi_cell(0, 10, line)
    return pdf.output(dest='S').encode('latin-1')

if submitted:
    st.subheader("📊 AI-Powered Student Evaluation Report")
    with st.spinner("Analyzing student responses..."):
        report = analyze_student_fit(name, [q1, q2, q3, q4, q5])
        st.success("Evaluation complete!")
        st.markdown(f"""
        ### 🧾 Report for {name}
        {report}
        """)

        # Generate PDF
        pdf_bytes = generate_pdf(name, report)
        b64_pdf = base64.b64encode(pdf_bytes).decode('utf-8')
        href = f'<a href="data:application/octet-stream;base64,{b64_pdf}" download="{name}_Evaluation_Report.pdf">📥 Download PDF Report</a>'
        st.markdown(href, unsafe_allow_html=True)
