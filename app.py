import os, random, json
from flask import Flask, request
import requests
from datetime import datetime
from openai import OpenAI

# ============= CẤU HÌNH =============
app = Flask(__name__)

PAGE_ACCESS_TOKEN = "EAAU0Fisjh0cBPEbpiq9JpPgZCkTmNKykol1j2jYC5AdMoxlPi0RThvTjRUHWc4ZBx3pRbSz5d8wZCtsTd8GyAZADfGfWKUmCZBJnygZAVvjvH7VgqRBURsLTZC45TWGnIaD7cQ8FfPVfjBoBZALpQMOIlc7QJnGBDTswByTba30lxvGenx72PxifPbPBkzk1X5igoWCZBl8nGZBgZDZD"
VERIFY_TOKEN = "botchat123"
RESPONSES_FILE = "responses.json"

client = OpenAI(api_key="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")
sessions = {}

# ======================
# Load / Save học thêm
# ======================
if os.path.exists(RESPONSES_FILE):
    with open(RESPONSES_FILE, "r", encoding="utf-8") as f:
        responses = json.load(f)
else:
    responses = {}

def save_responses():
    with open(RESPONSES_FILE, "w", encoding="utf-8") as f:
        json.dump(responses, f, ensure_ascii=False, indent=2)

# ======================
# Hàm gọi ChatGPT
# ======================
def ask_gpt(prompt):
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",   # hoặc "gpt-4o-mini" cho nhanh + rẻ
            messages=[{"role": "user", "content": prompt}]
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"⚠️ Lỗi AI: {e}"

# ======================
# Verify webhook
# ======================
@app.route("/webhook", methods=["GET"])
def verify():
    if request.args.get("hub.mode") == "subscribe" and request.args.get("hub.verify_token") == VERIFY_TOKEN:
        return request.args.get("hub.challenge"), 200
    return "Forbidden", 403

# ======================
# Nhận message
# ======================
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
                    text_lower = text.lower()

                    greetings = ["hi", "hello", "xin chào", "chào"]
                    ask_time = ["mấy giờ", "time", "giờ", "thời gian"]
                    dice_keywords = ["xúc xắc", "dice", "lắc"]
                    game_keywords = ["nối từ", "chơi nối từ không", "chơi nối từ ko"]

                    # --- học thêm ---
                    if text_lower.startswith("học:"):
                        try:
                            parts = text.replace("học:", "", 1).split("=")
                            keyword, answer = parts[0].strip(), parts[1].strip()
                            responses[keyword.lower()] = answer
                            save_responses()
                            reply = f"👌 Đã học thêm từ mới: '{keyword}'"
                        except:
                            reply = "⚠️ Sai cú pháp, hãy nhắn: học: từ khóa = câu trả lời"

                    # --- xử lý tin nhắn ---
                    elif any(word in text_lower for word in greetings):
                        reply = "Xin chào bạn 👋"

                    elif any(word in text_lower for word in ask_time):
                        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        reply = f"⏰ Bây giờ là {now}."

                    # --- nối từ ---
                    elif any(word in text_lower for word in game_keywords):
                        sessions[sender] = {"mode": "noi_tu", "last_phrase": "bạn thân"}
                        reply = "🎮 Bắt đầu game nối từ 2 từ! Mình mở đầu: 'bạn thân'. Giờ tới lượt bạn!"
                    
                    elif sender in sessions and sessions[sender]["mode"] == "noi_tu":
                        if text_lower == "thoát":
                            del sessions[sender]
                            reply = "✅ Bạn đã thoát game. Giờ mình quay lại chat bình thường nhé!"
                        else:
                            last_phrase = sessions[sender]["last_phrase"]
                            new_phrase = text.strip().lower().split()
                    
                            if len(new_phrase) < 2:
                                reply = "⚠️ Bạn phải nhập ít nhất 2 từ (ví dụ: 'bạn thân')."
                            else:
                                last_word = last_phrase.split()[-1]
                                first_word = new_phrase[0]
                    
                                if first_word == last_word:
                                    user_phrase = " ".join(new_phrase)
                                    sessions[sender]["last_phrase"] = user_phrase
                                
                                    bot_phrase = f"{new_phrase[-1]} vui"
                                    sessions[sender]["last_phrase"] = bot_phrase
                                
                                    reply = f"✅ Chuẩn! Bạn nhập: '{user_phrase}'\n🤖 Mình nối tiếp: '{bot_phrase}'. Giờ tới lượt bạn!"
                                else:
                                    reply = f"❌ Sai rồi! Cụm từ bạn nhập không bắt đầu bằng '{last_word}'. Game kết thúc."
                                    del sessions[sender]

                    # --- xúc xắc ---
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

                    # --- keyword học được ---
                    else:
                        found = False
                        for key, value in responses.items():
                            if key in text_lower:
                                reply = value
                                found = True
                                break
                        if not found:
                            # Gọi AI nếu không khớp rule nào
                            reply = ask_gpt(text)

                    send_message(sender, reply)

                elif "postback" in event:
                    payload = event["postback"].get("payload")
                    if payload == "GET_STARTED":
                        send_message(sender, "Xin chào! Gõ 'menu' để bắt đầu.")
        return "OK", 200
    return "Not Found", 404

# ======================
# Gửi message ra Messenger
# ======================
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
