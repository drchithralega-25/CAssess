import streamlit as st
import os
import re
from fpdf import FPDF
import base64
import matplotlib.pyplot as plt
import openai
from openai import OpenAIError

# Load API key
openai_api_key = os.getenv("OPENAI_API_KEY")
openai.api_key = openai_api_key

# Set background image
def set_bg_from_url():
    page_bg_img = f'''
    <style>
    .stApp {{
        background-image: url("https://images.unsplash.com/photo-1571260899304-425eee4c7efc?ixlib=rb-4.0.3&auto=format&fit=crop&w=1950&q=80");
        background-size: cover;
        background-position: center;
        background-repeat: no-repeat;
        background-attachment: fixed;
    }}
    .stMarkdown, .stTextInput, .stTextArea, .stButton, .stForm {{
        background-color: rgba(255, 255, 255, 0.85);
        border-radius: 10px;
        padding: 10px;
    }}
    </style>
    '''
    st.markdown(page_bg_img, unsafe_allow_html=True)

set_bg_from_url()

st.set_page_config(page_title="B.Com CA Admission Evaluator", layout="centered")

st.title("🎓 B.Com (CA) Student Fit & Assessment Tool")
st.markdown("This tool evaluates student responses, gives a detailed report, and shows a bar chart of key strengths.")

# --- Student Form ---
with st.form("student_form"):
    name = st.text_input("👤 Student Name")
    q1 = st.text_area("1️⃣ Why have you chosen B.Com (CA)?")
    q2 = st.text_area("2️⃣ Favorite subjects and why?")
    q3 = st.text_area("3️⃣ Describe a time you had difficulty understanding a concept.")
    q4 = st.text_area("4️⃣ Your comfort level with technology?")
    q5 = st.text_area("5️⃣ Career goals after B.Com (CA)?")
    submitted = st.form_submit_button("🔍 Evaluate")

# --- AI Evaluation Prompt ---
def generate_prompt(name, answers):
    return f"""
A student named {name} has applied for B.Com (CA). Analyze their answers and return:

1. A detailed evaluation report including:
   - Strengths
   - Weaknesses
   - Fit for B.Com (CA)
   - Suggest a better stream if not fit

2. A score (out of 10) for the following:
   [Scores]
   - Subject Interest:
   - Tech Comfort:
   - Communication:
   - Adaptability:
   - B.Com(CA) Fit:

Answers:
1. {answers[0]}
2. {answers[1]}
3. {answers[2]}
4. {answers[3]}
5. {answers[4]}
"""

# --- Extract Scores from AI Response ---
def extract_scores(text):
    try:
        pattern = r"(?i)subject interest:\s*(\d+).*?tech comfort:\s*(\d+).*?communication:\s*(\d+).*?adaptability:\s*(\d+).*?b\.?com\(ca\)? fit:\s*(\d+)"
        match = re.search(pattern, text, re.DOTALL)
        if match:
            return {
                "Subject Interest": int(match.group(1)),
                "Tech Comfort": int(match.group(2)),
                "Communication": int(match.group(3)),
                "Adaptability": int(match.group(4)),
                "B.Com(CA) Fit": int(match.group(5))
            }
    except Exception:
        pass
    return None

# --- AI Call ---
def analyze_student(name, answers):
    prompt = generate_prompt(name, answers)
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}]
        )
        return response.choices[0].message.content
    except OpenAIError as e:
        st.error(f"OpenAI Error: {e}")
        return None

# --- PDF Generator ---
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

# --- Plot Chart ---
def plot_scores(score_dict):
    fig, ax = plt.subplots()
    categories = list(score_dict.keys())
    scores = list(score_dict.values())
    colors = ['#4c72b0', '#55a868', '#c44e52', '#8172b2', '#ccb974']
    ax.barh(categories, scores, color=colors)
    ax.set_xlim(0, 10)
    ax.set_xlabel("Score (out of 10)")
    ax.set_title("Student Evaluation Chart")
    st.pyplot(fig)

# --- Final Evaluation ---
if submitted:
    if not name or not all([q1, q2, q3, q4, q5]):
        st.warning("⚠️ Please fill in all fields.")
    else:
        st.subheader("📊 Evaluation in Progress")
        with st.spinner("Analyzing responses..."):
            answers = [q1, q2, q3, q4, q5]
            result = analyze_student(name, answers)

            if result:
                st.success("✅ Evaluation Complete")

                # Extract and show report
                report_text = result.strip()
                st.markdown(f"### 🧾 Report for {name}")
                st.markdown(report_text)

                # Extract and plot scores
                scores = extract_scores(report_text)
                if scores:
                    st.markdown("### 📈 Evaluation Summary")
                    plot_scores(scores)
                else:
                    st.warning("⚠️ Could not extract scores from the AI response.")

                # Download PDF
                pdf_bytes = generate_pdf(name, report_text)
                b64 = base64.b64encode(pdf_bytes).decode()
                href = f'<a href="data:application/octet-stream;base64,{b64}" download="{name}_Report.pdf">📥 Download PDF Report</a>'
                st.markdown(href, unsafe_allow_html=True)
