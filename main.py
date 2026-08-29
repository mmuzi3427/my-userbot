import os
import re
import threading
from flask import Flask
from pyrogram import Client, filters
from pyrogram.types import Message

# 1. Flask (Render uchilmasligi uchun Web Server)
web_app = Flask(__name__)

@web_app.route('/')
def home():
    return "Bonus Userbot is running!"

def run_web():
    port = int(os.environ.get("PORT", 8080))
    web_app.run(host="0.0.0.0", port=port)

threading.Thread(target=run_web, daemon=True).start()

# 2. Pyrogram Sozlamalari
api_id = int(os.environ.get("API_ID"))
api_hash = os.environ.get("API_HASH")
session_string = os.environ.get("STRING_SESSION")

# ---------------- SOZLAMALAR ----------------
# Monitoring qilinadigan KANAL username yoki ID'si (masalan: "bonus_kanali" yoki -100123456789)
KANAL_USERNAME = "CheapSMM_News" 

# Bonus beradigan BOT username'si (masalan: "pul_ishlash_boti")
BOT_USERNAME = "CheapSMM_bot" 

# Lug'at: Matndagi meva nomi va tugmadagi mos emoji
FRUIT_MAP = {
    "qulupnay": "🍓",
    "olma": "🍏",
    "nok": "🍐",
    "banan": "🍌",
    "kivi": "🥝",
    "uzum": "🍇",
    "gilos": "🍒",
    "shaftoli": "🍑",
    "ananas": "🍍",
    "apelsin": "🍊",
    "limon": "🍋"
}
# --------------------------------------------

app = Client(
    "userbot",
    api_id=api_id,
    api_hash=api_hash,
    session_string=session_string
)

# 1-BOSQICH: Kanalga post kelishini kuzatish
@app.on_message(filters.chat(KANAL_USERNAME))
def check_channel_post(client: Client, message: Message):
    if message.text and "Bonus olish boshlandi" in message.text:
        print("🚀 Kanalda bonus posti topildi! Botga /start bonus yuborilmoqda...")
        client.send_message(BOT_USERNAME, "/start bonus")

# 2-BOSQICH: Botdan kelgan javob va tugmalarni qayta ishlash
@app.on_message(filters.chat(BOT_USERNAME))
def handle_bot_response(client: Client, message: Message):
    # Agar botda Inline (pastki) tugmalar bo'lsa va matn kelgan bo'lsa
    if message.reply_markup and message.text:
        text_lower = message.text.lower()
        
        # Qaysi meva so'ralganini lug'atdan izlaymiz
        target_emoji = None
        for fruit_name, emoji in FRUIT_MAP.items():
            if fruit_name in text_lower:
                target_emoji = emoji
                print(f"🎯 So'ralgan meva topildi: {fruit_name} -> {emoji}")
                break
        
        # Agar so'ralgan meva topilsa, tugmalar ichidan o'sha emojini qidiramiz
        if target_emoji:
            for row in message.reply_markup.inline_keyboard:
                for button in row:
                    # Tugma matnida mos emoji bor-yo'qligini tekshirish
                    if button.text and target_emoji in button.text:
                        print(f"✅ Tugma bosilmoqda: {button.text}")
                        # Tugmani bosish (Callback query yuborish)
                        try:
                            message.click(button.text)
                        except Exception as e:
                            print(f"❌ Tugmani bosishda xatolik: {e}")
                        return

# Oddiy tekshiruv komandasi
@app.on_message(filters.me & filters.command("ping", prefixes="."))
def ping_pong(_, message):
    message.edit_text("🏓 **Bonus Userbot faol va ishlamoqda!**")

print("Bonus Userbot ishga tushdi...")
app.run()
