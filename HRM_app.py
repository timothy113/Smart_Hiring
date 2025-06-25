# -------------------- IMPORT REQUIRED LIBRARIES --------------------
import os
import fitz  # PyMuPDF for PDF reading
import zipfile
import tempfile
import streamlit as st
import pandas as pd
from sentence_transformers import SentenceTransformer, util
import re
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# -------------------- PAGE CONFIG------------------
st.set_page_config(page_title="Smart Hiring | Resume Matcher", layout="wide")

# -------------------- APP TITLE --------------------
st.markdown("""
    <h1 style='font-size: 36px; text-align: center;'>Smart Hiring Made Easy</h1>
    <p style='text-align: center; font-size: 20px;'>Upload Resumes ➤ Instantly Match Candidates ➤ Send Interview Emails automatically</p>
    <hr>
""", unsafe_allow_html=True)

# -------------------- EMAIL SETTINGS IN SIDEBAR --------------------
st.sidebar.header("Email Settings (For Sending Invitations)")
email_user = st.sidebar.text_input("Sender Gmail Address", placeholder="e.g. example@gmail.com")
email_pass = st.sidebar.text_input("Gmail App Password", type="password")
st.sidebar.info("You need a Gmail App Password to send emails. [Learn how](https://support.google.com/accounts/answer/185833).")

# -------------------- LOAD EMBEDDING MODEL --------------------
@st.cache_resource
def load_model():
    return SentenceTransformer('all-MiniLM-L6-v2')

model = load_model()

# -------------------- FILE UPLOAD + JOB DESCRIPTION --------------------
zip_file = st.file_uploader("Upload ZIP File with Resumes (PDF only)", type="zip")
job_desc = st.text_area("Paste the Job Description Below", height=200)

# -------------------- EMAIL SENDER FUNCTION --------------------
def send_email(to_email, subject, body, sender_email, sender_password):
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = to_email
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))

    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
            smtp.login(sender_email, sender_password)
            smtp.send_message(msg)
        return True
    except Exception as e:
        print(f"Failed to send email to {to_email}: {e}")
        return False

# -------------------- CONTACT INFO EXTRACTOR --------------------
def extract_contact(text, fallback_name):
    email_match = re.search(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+", text)
    phone_match = re.search(r"(\+?\d{2,4})?[\s.-]?\(?\d{2,4}\)?[\s.-]?\d{3,4}[\s.-]?\d{3,4}", text)
    email = email_match.group(0) if email_match else "Not found"
    phone = phone_match.group(0) if phone_match else "Not found"
    return email, phone, fallback_name

# -------------------- MAIN LOGIC --------------------
if zip_file and job_desc:
    with tempfile.TemporaryDirectory() as tmpdir:
        zip_path = os.path.join(tmpdir, "resumes.zip")
        with open(zip_path, "wb") as f:
            f.write(zip_file.read())
        with zipfile.ZipFile(zip_path, "r") as zip_ref:
            zip_ref.extractall(tmpdir)

        job_embedding = model.encode(job_desc, convert_to_tensor=True)
        resume_data = []

        for file in os.listdir(tmpdir):
            if file.endswith(".pdf"):
                pdf_path = os.path.join(tmpdir, file)
                with fitz.open(pdf_path) as doc:
                    text = ""
                    for page in doc:
                        text += page.get_text()

                name = os.path.splitext(file)[0]
                email, phone, extracted_name = extract_contact(text, name)
                resume_embedding = model.encode(text, convert_to_tensor=True)
                similarity = util.cos_sim(job_embedding, resume_embedding).item()
                match_percent = round(similarity * 100, 2)

                invite_msg = f"""Dear {extracted_name},

Congratulations! Based on your strong alignment with our job description, we are pleased to invite you to the next stage of the hiring process.

Please await further instructions regarding the interview.

Best regards,  
Recruitment Team
"""

                resume_data.append({
                    "Name": extracted_name,
                    "Email": email,
                    "Phone": phone,
                    "Match (%)": match_percent,
                    "Interview Message": invite_msg
                })

        df = pd.DataFrame(resume_data).sort_values(by="Match (%)", ascending=False)

        st.success("Resumes matched and ranked successfully!")
        st.dataframe(df)

        # Top-N candidates to invite
        top_n = st.slider("Select number of top candidates to invite:", 1, len(df), min(3, len(df)))
        top_matches = df.head(top_n)

        # Download Top Matches CSV
        st.subheader("Download Top Candidates")
        csv = top_matches.to_csv(index=False).encode("utf-8")
        st.download_button("Download CSV", data=csv, file_name="top_matches.csv", mime="text/csv")

        # Send Emails Button
        if st.button(f"Send Invitations to Top {top_n} Candidates"):
            if not email_user or not email_pass:
                st.error("Please enter your Gmail and App Password in the sidebar.")
            else:
                sent = 0
                for _, row in top_matches.iterrows():
                    if row["Email"] != "Not found":
                        if send_email(row["Email"], "Interview Invitation", row["Interview Message"], email_user, email_pass):
                            sent += 1
                st.success(f"{sent} email(s) sent successfully.")
