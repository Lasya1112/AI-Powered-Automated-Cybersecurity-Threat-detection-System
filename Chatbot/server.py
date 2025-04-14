import os
import requests
import time
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Azure OpenAI API credentials
AZURE_API_KEY = os.getenv("AZURE_API_KEY")
AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
AZURE_OPENAI_DEPLOYMENT = os.getenv("AZURE_OPENAI_DEPLOYMENT")

app = FastAPI()

# Enable CORS for frontend interaction
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow requests from any origin (change for production)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class UserMessage(BaseModel):
    message: str

@app.get("/")
def root():
    return {"message": "Welcome to the Cybercrime Chatbot API. Use /chat to interact with the chatbot."}

@app.get("/chat")
def chat_example():
    return {"message": "Use a POST request with a JSON body to chat with the bot."}


@app.post("/chat")
def cybercrime_chatbot(user_message: UserMessage):
    if not AZURE_API_KEY or not AZURE_OPENAI_ENDPOINT or not AZURE_OPENAI_DEPLOYMENT:
        return {"error": "Missing API credentials. Check your .env file."}

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {AZURE_API_KEY}",
    }

    payload = {
        "model": AZURE_OPENAI_DEPLOYMENT,
        "messages": [
            {"role": "system", "content": "You are a chatbot that strictly educates children about cybercrime, cybersecurity, and related topics. If a user asks about unrelated topics, respond with: 'I only have knowledge about cybersecurity and cybercrime.'"},
            {"role": "user", "content": user_message.message}
        ]
    }

    for attempt in range(5):  # Retry up to 5 times
        response = requests.post(AZURE_OPENAI_ENDPOINT, json=payload, headers=headers)

        if response.status_code == 200:
            return {"response": response.json().get("choices", [{}])[0].get("message", {}).get("content", "").strip()}
        elif response.status_code == 429:
            retry_after = int(response.headers.get("Retry-After", 20))  # Default to 20 sec if not provided
            print(f"Rate limit exceeded. Retrying in {retry_after} seconds...")
            time.sleep(retry_after)
        else:
            return {"error": f"Error: {response.status_code} - {response.text}"}

    return {"error": "Error: Failed after multiple retries"}
