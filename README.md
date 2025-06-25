#Smart Hiring Made Easy - Resume Matcher & Auto Interview Email Inviter

**Smart Hiring** is a simple web app that helps recruiters and HR teams quickly find the best candidates by matching resumes to job descriptions and automatically sending interview invitations.


 **Try it live:** https://smarthiring-qtapcdysjkmq4rjq6zegws.streamlit.app/

---

## What the App Does

- Upload a ZIP file with multiple PDF resumes  
- Paste a job description  
- App reads all resumes and compares them with the job  
- Candidates are scored and ranked based on best match  
- You can export top matches to CSV  
- Send personalized email invitations directly from the app  

---

## How It Works (in simple terms)

- Uses **NLP (Natural Language Processing)** to understand the job description and resumes  
- Compares them using **cosine similarity** to find how well each resume matches  
- Uses **regex** to extract contact details like email and phone number  
- Sends email invites via **Gmail SMTP** (secure login with App Password)  

---

## Features

| Feature               | Description                                    |
|-----------------------|------------------------------------------------|
| Resume Matching       | Compares each resume with the job using AI     |
| Email Invitations     | Automatically sends interview invites          |
| Zip Upload Support    | Upload many resumes at once                    |
| Export CSV            | Download top matches as CSV                    |
| AI-Powered Matching   | Uses pre-trained model (`MiniLM`)              |
| Secure Email Login    | No need to hardcode your password              |

---

## How to Use (Step-by-Step)

1. Visit the app: (https://smarthiring-qtapcdysjkmq4rjq6zegws.streamlit.app/)
2. Upload a ZIP file of PDF resumes  
3. Paste your job description in the box  
4. Wait a few seconds for matching  
5. Select how many top candidates to invite  
6. Enter your Gmail and App Password on the sidebar  
7. Click to send interview invitations automatically  
8. Export top candidates as a CSV if needed  

---

## NOTE

- You must have **2-Step Verification** enabled on your Gmail account  
- Create a **Gmail App Password** for this app to send emails securely  
- How to create an App Password (https://support.google.com/accounts/answer/185833)

---

## Tech Stack

- `Python`
- `Streamlit` – Web interface
- `Sentence Transformers` – Semantic similarity
- `PyMuPDF` – PDF reading
- `smtplib` & `email.mime` – Sending emails
- `re (regex)` – Extracting email and phone numbers

---

## Author

**Timothy Mbilinya**  
Aspiring LLMOps Engineer & AI Developer  
🇲🇼 Malawi  
- GitHub: [https://github.com/timothy113](https://github.com/timothy113)  
- LinkedIn: [Timothy Mbilinya](https://www.linkedin.com/in/timothy-mbilinya)

---

## Contributions

Pull requests are welcome. If you find a bug or want to suggest improvements, please create an issue.
