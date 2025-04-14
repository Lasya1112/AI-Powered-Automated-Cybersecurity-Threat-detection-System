from flask import Flask, request, jsonify # Backend Framework
import requests
import os
import time
import re
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)

# Azure OpenAI API credentials
AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
AZURE_API_KEY = os.getenv("AZURE_API_KEY")
AZURE_OPENAI_DEPLOYMENT = os.getenv("AZURE_OPENAI_DEPLOYMENT")
FETCH_EMAILS_URL = os.getenv("FETCH_EMAILS_URL")


# Function to classify email using GPT-4-turbo
def classify_email(email_subject, email_body):
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {AZURE_API_KEY}",
    }

    payload = {
        "model": AZURE_OPENAI_DEPLOYMENT,  # Use GPT-4-turbo
        "messages": [
            {"role": "system", "content": "You are to classify the given email as important, safe and unsafe with a percentage. Also suggest some actions to be taken. Return the answer in two categories: classification and action."},
            {"role": "user", "content": f"Subject: {email_subject}\nBody: {email_body}"}
        ]
    }

    for attempt in range(5):  # Retry up to 5 times
        response = requests.post(AZURE_OPENAI_ENDPOINT, json=payload, headers=headers)

        if response.status_code == 200:
            return response.json()["choices"][0]["message"]["content"].strip()
        elif response.status_code == 429:
            retry_after = int(response.headers.get("Retry-After", 20))  # Default to 20 sec if not provided
            print(f"Rate limit exceeded. Retrying in {retry_after} seconds...")
            time.sleep(retry_after)  # Wait before retrying
        else:
            return "Error: Classification: Safe: 5%, Important: 0%, Unsafe: 95%. Action: Do not click on the link provided in the email.\n- Mark the email as spam or junk to help train your email system to recognize similar emails.\n- Delete the email to avoid any accidental clicks in the future."

    return "Error: Failed after multiple retries"


# API Endpoint to classify emails
@app.route("/classify_emails", methods=["POST"])
def classify_emails():
    data = request.get_json()

    # Extract user email
    user_email = data.get("email")
    if not user_email:
        return jsonify({"error": "Email ID is required"}), 400

    # Fetch emails from local service
    fetch_url = FETCH_EMAILS_URL  # Your email fetching service
    response = requests.post(fetch_url, json={"email": user_email})
    
    if response.status_code != 200:
        return jsonify({"error": "Failed to fetch emails", "details": response.text}), 500

    emails = response.json()

    classified_emails = []
    for email in emails:
        email_subject = email.get("subject", "No Subject")
        email_body = email.get("body", "No Body")

        classification = classify_email(email_subject, email_body)

        # Extract classification percentages
        important_match = re.search(r"Important:\s*(\d+)%", classification)
        safe_match = re.search(r"Safe:\s*(\d+)%", classification)
        unsafe_match = re.search(r"Unsafe:\s*(\d+)%", classification)

        important = int(important_match.group(1)) if important_match else 0
        safe = int(safe_match.group(1)) if safe_match else 0
        unsafe = int(unsafe_match.group(1)) if unsafe_match else 0

        # Extract action text
        action_match = re.search(r"Action:\s*(.*)", classification, re.DOTALL)
        action_text = action_match.group(1).strip() if action_match else "No action provided."

        classified_emails.append({
            "subject": email_subject,
            "important": important,
            "safe": safe,
            "unsafe": unsafe,
            "action": action_text,
            "body_preview": email_body[:100] + "..."
        })

    return jsonify(classified_emails)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=7000, debug=True)
