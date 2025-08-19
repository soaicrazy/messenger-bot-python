import os
import requests
from flask import Flask, request
from threading import Thread

app = Flask(__name__)

PAGE_ACCESS_TOKEN = os.getenv("PAGE_ACCESS_TOKEN")
VERIFY_TOKEN = os.getenv("VERIFY_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Gọi OpenAI API
def ask_openai(prompt):
    url = "https://api.openai.com/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "Content-Type": "application/json"
    }
    body = {
        "model": "gpt-3.5-turbo",
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.7
    }
    r = requests.post(url, headers=headers, json=body, timeout=20)
    if r.status_code == 200:
        return r.json()["choices"][0]["message"]["content"]
    else:
        print("Error OpenAI:", r.text)
        return "Xin lỗi, tôi không thể trả lời lúc này."

# Gửi message ra Messenger
def send_message(psid, text):
    url = "https://graph.facebook.com/v19.0/me/messages"
    params = {"access_token": PAGE_ACCESS_TOKEN}
    body = {"recipient": {"id": psid}, "message": {"text": text}}
    r = requests.post(url, params=params, json=body)
    if r.status_code != 200:
        print("Error:", r.text)

# Xử lý message async
def handle_message(sender, text):
    reply = ask_openai(text)
    send_message(sender, reply)

# Webhook verify (GET)
@app.route("/webhook", methods=["GET"])
def verify():
    token = request.args.get("hub.verify_token")
    challenge = request.args.get("hub.challenge")
    if token == VERIFY_TOKEN:
        return challenge
    return "Verification token mismatch", 403

# Webhook nhận tin nhắn (POST)
@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.get_json()
    if data.get("object") == "page":
        for entry in data.get("entry", []):
            for event in entry.get("messaging", []):
                sender = event.get("sender", {}).get("id")
                if "message" in event:
                    text = event["message"].get("text", "")
                    Thread(target=handle_message, args=(sender, text)).start()
        return "EVENT_RECEIVED", 200
    return "Not Found", 404
