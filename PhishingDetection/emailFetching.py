from flask import Flask, request, jsonify, redirect, session # type: ignore
from googleapiclient.discovery import build # type: ignore
from google_auth_oauthlib.flow import Flow # type: ignore
import google.auth.transport.requests # type: ignore
import os
import pickle
from google.auth.transport.requests import Request # type: ignore
import base64

app = Flask(__name__)

SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]
CLIENT_SECRET_FILE = "credentials.json"  # Download from Google Cloud Console

# Store user tokens
TOKEN_DIR = "tokens"
os.makedirs(TOKEN_DIR, exist_ok=True)

# Authenticate with Gmail OAuth
def authenticate_user(user_email):
    token_path = os.path.join(TOKEN_DIR, f"{user_email}.pickle")

    if os.path.exists(token_path):
        with open(token_path, "rb") as token:
            creds = pickle.load(token)
        return creds

    return None

# Route for user authentication
@app.route("/login")
def login():
    flow = Flow.from_client_secrets_file(CLIENT_SECRET_FILE, scopes=SCOPES, redirect_uri="http://localhost:5000/callback")
    auth_url, _ = flow.authorization_url(prompt="consent")
    return redirect(auth_url)

# Callback after user logs in
@app.route("/callback")
def callback():
    flow = Flow.from_client_secrets_file(CLIENT_SECRET_FILE, scopes=SCOPES, redirect_uri="http://localhost:5000/callback")
    flow.fetch_token(authorization_response=request.url)

    creds = flow.credentials
    service = build("gmail", "v1", credentials=creds)
    
    # Get user's email
    user_info = service.users().getProfile(userId="me").execute()
    user_email = user_info["emailAddress"]

    # Save credentials
    with open(os.path.join(TOKEN_DIR, f"{user_email}.pickle"), "wb") as token:
        pickle.dump(creds, token)

    # Fetch and print first 5 emails
    results = service.users().messages().list(userId="me", maxResults=5).execute()
    messages = results.get("messages", [])

    print("First 5 Emails:")
    for msg in messages:
        msg_data = service.users().messages().get(userId="me", id=msg["id"]).execute()
        headers = msg_data["payload"]["headers"]
        
        subject = next((h["value"] for h in headers if h["name"] == "Subject"), "No Subject")
        sender = next((h["value"] for h in headers if h["name"] == "From"), "Unknown Sender")
        print(f"From: {sender}, Subject: {subject}")

    return redirect("http://127.0.0.1:5500/index.html")

# Fetch emails for a specific user
@app.route("/fetch_emails", methods=["POST"])
def fetch_emails():
    data = request.get_json()
    user_email = data.get("email")

    creds = authenticate_user(user_email)
    if not creds:
        return jsonify({"error": "User not authenticated. Please log in first."}), 401

    service = build("gmail", "v1", credentials=creds)
    results = service.users().messages().list(userId="me", maxResults=5).execute()
    messages = results.get("messages", [])

    emails = []
    for msg in messages:
        msg_data = service.users().messages().get(userId="me", id=msg["id"]).execute()
        headers = msg_data["payload"]["headers"]
        
        subject = next((h["value"] for h in headers if h["name"] == "Subject"), "No Subject")
        sender = next((h["value"] for h in headers if h["name"] == "From"), "Unknown Sender")

        # Extract email body
        body = "No Body"
        if "payload" in msg_data:
            parts = msg_data["payload"].get("parts", [])
            if parts:
                for part in parts:
                    if part.get("mimeType") == "text/plain":  # Get plain text body
                        body = base64.urlsafe_b64decode(part["body"]["data"]).decode("utf-8", errors="ignore")
                        break
            elif "body" in msg_data["payload"] and "data" in msg_data["payload"]["body"]:
                body = base64.urlsafe_b64decode(msg_data["payload"]["body"]["data"]).decode("utf-8", errors="ignore")

        emails.append({
            "subject": subject,
            "from": sender,
            "body": body
        })

    return jsonify(emails)

if __name__ == "__main__":
    app.run(debug=True)
