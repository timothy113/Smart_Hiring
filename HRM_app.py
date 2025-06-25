
# ------------- IMPORT REQUIRED RIBRARIES ---------------
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

# ----------------- EMAIL CONFIG -------------------
EMAIL_ADDRESS = "hrmatchbot@gmail.com"        
EMAIL_PASSWORD = "xbwbwwmbqnmuvxjp"                   

# ----------------- HELPER FUNCTIONS -------------------

def send_email(to_email, subject, body):
    """Send interview invitation to selected candidates."""
    msg = MIMEMultipart()
    msg['From'] = EMAIL_ADDRESS
    msg['To'] = to_email
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))

    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
            smtp.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
            smtp.send_message(msg)
        return True
    except Exception as e:
        print(f"Failed to send email to {to_email}: {e}")
        return False

def extract_contact(text, fallback_name):
    """Extract email, phone, and name from resume text."""
    email_match = re.search(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+", text)
    phone_match = re.search(r"(\+?\d{2,4})?[\s.-]?\(?\d{2,4}\)?[\s.-]?\d{3,4}[\s.-]?\d{3,4}", text)
    email = email_match.group(0) if email_match else "Not found"
    phone = phone_match.group(0) if phone_match else "Not found"
    return email, phone, fallback_name

# ------------------ STREAMLIT APP --------------------

st.set_page_config(page_title="Smart Hiring Made Easy", layout="wide")
st.title("Upload Resumes. Get Top Candidates. Send Interview Emails Automatically")

# Load model only once
@st.cache_resource
def load_model():
    return SentenceTransformer('all-MiniLM-L6-v2')

model = load_model()

# Upload ZIP and Paste Job Description
zip_file = st.file_uploader("Upload a ZIP file with resumes (PDFs)", type="zip")
job_desc = st.text_area("Paste Job Description")

if zip_file and job_desc:
    with tempfile.TemporaryDirectory() as tmpdir:
        # Save and extract ZIP
        zip_path = os.path.join(tmpdir, "resumes.zip")
        with open(zip_path, "wb") as f:
            f.write(zip_file.read())
        with zipfile.ZipFile(zip_path, "r") as zip_ref:
            zip_ref.extractall(tmpdir)

        # Prepare embeddings
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

        # Create DataFrame and sort by best match
        df = pd.DataFrame(resume_data).sort_values(by="Match (%)", ascending=False)

        st.success("Resumes ranked by relevance!")
        st.dataframe(df)

        # Select Top-N Matches
        top_n = st.slider("Select how many top candidates to invite:", min_value=1, max_value=len(df), value=min(3, len(df)))
        top_matches = df.head(top_n)

        # Download CSV for top matches
        st.subheader("Export Top Candidates")
        csv = top_matches.to_csv(index=False).encode("utf-8")
        st.download_button("Download Top Matches CSV", data=csv, file_name="top_matches.csv", mime="text/csv")

        # Send emails to top matches
        if st.button(f"Send Interview Invites to Top {top_n} Candidates"):
            sent = 0
            for _, row in top_matches.iterrows():
                if row["Email"] != "Not found":
                    if send_email(row["Email"], "Interview Invitation", row["Interview Message"]):
                        sent += 1
            st.success(f"{sent} email(s) sent successfully.")
