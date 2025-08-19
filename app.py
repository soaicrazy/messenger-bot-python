import os
import requests
from flask import Flask, request
import openai

app = Flask(__name__)

# Lấy biến môi trường từ Railway
PAGE_ACCESS_TOKEN = os.getenv("PAGE_ACCESS_TOKEN")
VERIFY_TOKEN = os.getenv("VERIFY_TOKEN")
openai.api_key = os.getenv("OPENAI_API_KEY")

@app.route("/webhook", methods=["GET", "POST"])
def webhook():
    if request.method == "GET":
        # Facebook webhook verification
        mode = request.args.get("hub.mode")
        token = request.args.get("hub.verify_token")
        challenge = request.args.get("hub.challenge")

        if mode == "subscribe" and token == VERIFY_TOKEN:
            return challenge, 200
        else:
            return "Verification failed", 403

    elif request.method == "POST":
        # Messenger event handling
        data = request.get_json()
        print(data)  # Debug log

        if "entry" in data:
            for entry in data["entry"]:
                if "messaging" in entry:
                    for message_event in entry["messaging"]:
                        if "message" in message_event:
                            sender_id = message_event["sender"]["id"]
                            user_message = message_event["message"].get("text")

                            if user_message:
                                reply = get_ai_response(user_message)
                                send_message(sender_id, reply)

        return "EVENT_RECEIVED", 200


def get_ai_response(user_message):
    try:
        response = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Bạn là một trợ lý thân thiện."},
                {"role": "user", "content": user_message}
            ]
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"⚠️ Lỗi AI: {str(e)}"


def send_message(recipient_id, message_text):
    headers = {
        "Content-Type": "application/json"
    }
    data = {
        "recipient": {"id": recipient_id},
        "message": {"text": message_text}
    }
    params = {"access_token": PAGE_ACCESS_TOKEN}
    requests.post("https://graph.facebook.com/v12.0/me/messages",
                  params=params, headers=headers, json=data)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
