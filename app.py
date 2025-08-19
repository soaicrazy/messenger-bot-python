import os, hmac, hashlib
from flask import Flask, request
import requests
from datetime import datetime
import random   # 👈 để chơi xúc xắc


app = Flask(__name__)

PAGE_ACCESS_TOKEN ="EAAU0Fisjh0cBPEbpiq9JpPgZCkTmNKykol1j2jYC5AdMoxlPi0RThvTjRUHWc4ZBx3pRbSz5d8wZCtsTd8GyAZADfGfWKUmCZBJnygZAVvjvH7VgqRBURsLTZC45TWGnIaD7cQ8FfPVfjBoBZALpQMOIlc7QJnGBDTswByTba30lxvGenx72PxifPbPBkzk1X5igoWCZBl8nGZBgZDZD"
VERIFY_TOKEN = "botchat123"
APP_SECRET = os.getenv("APP_SECRET")
# ✅ Verify webhook
@app.route("/webhook", methods=["GET"])
def verify():
    if request.args.get("hub.mode") == "subscribe" and request.args.get("hub.verify_token") == VERIFY_TOKEN:
        return request.args.get("hub.challenge"), 200
    return "Forbidden", 403

# ✅ Nhận message
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
                    handle_message(sender, text)   # ✅ gọi handle_message thay vì echo
                elif "postback" in event:
                    payload = event["postback"].get("payload")
                    if payload == "GET_STARTED":
                        send_message(sender, "Xin chào! Gõ 'menu' để bắt đầu.")
        return "OK", 200
    return "Not Found", 404

# ✅ Xử lý tin nhắn người dùng
def handle_message(sender, text):
    text_lower = text.strip().lower()

    # --- Các nhóm từ khóa ---
    greetings = ["hi", "hello", "xin chào", "chào", "helo", "hí"]
    bye_words = ["bye", "tạm biệt", "bái bai"]
    thanks_words = ["cảm ơn", "thank", "thanks"]
    ask_time = ["mấy giờ", "time", "giờ hiện tại"]
    ask_weather = ["thời tiết", "trời mưa không", "hôm nay thế nào"]
    ask_name = ["bạn tên gì", "tên gì", "who are you"]
    ask_contact = ["liên hệ", "contact", "hỗ trợ"]
    dice_keywords = ["xúc xắc", "dice", "tung xúc xắc"]

    # --- xử lý tin nhắn ---
    if any(word in text_lower for word in greetings):
        reply = "Xin chào bạn 👋"

    elif any(word in text_lower for word in ask_time):
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        reply = f"⏰ Bây giờ server là {now}."

    elif any(word in text_lower for word in dice_keywords):
        if "chơi" in text_lower or "2" in text_lower:
            user_dice = random.randint(1, 6)
            bot_dice = random.randint(1, 6)
            if user_dice > bot_dice:
                result = "🎉 Bạn thắng!"
            elif user_dice < bot_dice:
                result = "🤖 Bot thắng!"
            else:
                result = "😅 Hòa rồi!"
            reply = f"🎲 Bạn tung được {user_dice}\n🤖 Bot tung được {bot_dice}\n👉 {result}"
        else:
            dice = random.randint(1, 6)
            reply = f"🎲 Bạn tung được số {dice}"

    else:
        reply = f"Bạn vừa nói: {text}"

    send_message(sender, reply)

# ✅ Gửi message ra Messenger
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
