from fastapi import FastAPI, HTTPException
import requests
import smtplib
from email.mime.text import MIMEText
import os

app = FastAPI()

# Langflow API URL (Replace with your deployed Langflow URL)
LANGFLOW_URL = os.getenv("LANGFLOW_URL", "http://localhost:7860")

@app.post("/analyze")
async def analyze_healthcare_data(data: dict):
    try:
        # Send input data to Langflow
        response = requests.post(f"{LANGFLOW_URL}/api/v1/chain", json=data)
        response.raise_for_status()  # Raise exception for HTTP errors
        result = response.json()
        
        # Extract relevant details
        severity = result.get("severity", "unknown")
        doctor_email = result.get("doctor_email")

        # If the condition is severe, send an email to the doctor
        if severity == "severe" and doctor_email:
            send_email(doctor_email, data["patient_email"], result["disease"])

        return {
            "severity": severity,
            "remedies": result.get("remedies", "No data available"),
            "medications": result.get("medications", "No data available"),
            "doctor": result.get("doctor"),
            "doctor_email": doctor_email
        }
    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=500, detail=f"Langflow API error: {str(e)}")

# Email Function
def send_email(doctor_email, patient_email, disease):
    try:
        msg = MIMEText(f"A patient with {disease} needs consultation. Contact: {patient_email}")
        msg["Subject"] = "Urgent Patient Consultation"
        msg["From"] = os.getenv("EMAIL_SENDER", "your-email@example.com")
        msg["To"] = doctor_email

        with smtplib.SMTP(os.getenv("SMTP_SERVER", "smtp.example.com"), 587) as server:
            server.starttls()
            server.login(os.getenv("EMAIL_SENDER"), os.getenv("EMAIL_PASSWORD"))
            server.sendmail(os.getenv("EMAIL_SENDER"), doctor_email, msg.as_string())

        print(f"Email sent to {doctor_email}")
    except Exception as e:
        print(f"Email sending failed: {str(e)}")
