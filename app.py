import os, threading, requests
from flask import Flask, request
from openai import OpenAI
import traceback

app = Flask(__name__)

PAGE_ACCESS_TOKEN ="EAAU0Fisjh0cBPEbpiq9JpPgZCkTmNKykol1j2jYC5AdMoxlPi0RThvTjRUHWc4ZBx3pRbSz5d8wZCtsTd8GyAZADfGfWKUmCZBJnygZAVvjvH7VgqRBURsLTZC45TWGnIaD7cQ8FfPVfjBoBZALpQMOIlc7QJnGBDTswByTba30lxvGenx72PxifPbPBkzk1X5igoWCZBl8nGZBgZDZD"
VERIFY_TOKEN = "botchat123"
APP_SECRET = os.getenv("APP_SECRET")
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Hàm gọi GPT
def ask_gpt(user_message):
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",   # model nhẹ
            messages=[
                {"role": "system", "content": "Bạn là một trợ lý AI thân thiện."},
                {"role": "user", "content": user_message}
            ],
            max_tokens=200
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print("GPT Error:", e)
        traceback.print_exc()
        return "Xin lỗi, tôi chưa thể trả lời lúc này."

# Verify webhook
@app.route("/webhook", methods=["GET"])
def verify():
    if request.args.get("hub.mode") == "subscribe" and request.args.get("hub.verify_token") == VERIFY_TOKEN:
        return request.args.get("hub.challenge"), 200
    return "Forbidden", 403

# Nhận message
@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.get_json()
    if data.get("object") == "page":
        for entry in data.get("entry", []):
            for event in entry.get("messaging", []):
                sender = event.get("sender", {}).get("id")
                if not sender:
                    continue
                if "message" in event:
                    text = event["message"].get("text", "")
                    threading.Thread(target=handle_message, args=(sender, text)).start()
                elif "postback" in event:
                    payload = event["postback"].get("payload")
                    if payload == "GET_STARTED":
                        threading.Thread(target=send_message, args=(sender, "Xin chào! Gõ 'menu' để bắt đầu.")).start()
        return "OK", 200
    return "Not Found", 404

def handle_message(sender, text):
    reply = ask_gpt(text)
    send_message(sender, reply)

# Gửi message ra Messenger
def send_message(psid, text):
    url = "https://graph.facebook.com/v19.0/me/messages"
    params = {"access_token": PAGE_ACCESS_TOKEN}
    body = {"recipient": {"id": psid}, "message": {"text": text}}
    r = requests.post(url, params=params, json=body)
    if r.status_code != 200:
        print("Error:", r.text)

if __name__ == "__main__":
    port = int(os.getenv("PORT", 3000))
    app.run(host="0.0.0.0", port=port)
