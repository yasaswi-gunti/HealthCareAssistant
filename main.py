from fastapi import FastAPI, HTTPException
import requests
import os

app = FastAPI()

# Langflow API URL (Replace with your deployed Langflow URL)
LANGFLOW_URL = os.getenv("LANGFLOW_URL", "http://localhost:7860")

@app.post("/analyze")
async def analyze_healthcare_data(data: dict):
    try:
        # Send input data to Langflow
        response = requests.post(f"{LANGFLOW_URL}", json=data)
        response.raise_for_status()  # Raise exception for HTTP errors
        result = response.json()
        
        # Extract relevant details
        severity = result.get("severity", "unknown")

        return {
            "severity": severity,
            "remedies": result.get("remedies", "No data available"),
            "medications": result.get("medications", "No data available"),
            "doctor": result.get("doctor"),
            "doctor_email": result.get("doctor_email")
        }
    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=500, detail=f"Langflow API error: {str(e)}")
