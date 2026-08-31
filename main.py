import os
import time
import random
import threading
from flask import Flask
from pyrogram import Client, filters
from pyrogram.types import Message

# 1. Web Server (Render to'xtab qolmasligi uchun)
web_app = Flask(__name__)

@web_app.route('/')
def home():
    return "Multi-Account Bonus Userbot is running!"

def run_web():
    port = int(os.environ.get("PORT", 8080))
    web_app.run(host="0.0.0.0", port=port)

threading.Thread(target=run_web, daemon=True).start()

# 2. Asosiy Sozlamalar va O'zgaruvchilar
api_id = int(os.environ.get("API_ID"))
api_hash = os.environ.get("API_HASH")

KANAL_USERNAME = "CheapSMM_News" 
BOT_USERNAME = "CheapSMM_bot" 

bonus_ol = True
saqlangan_son = 4

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

# 3. Seanslarni yuklash (Render Environment Variables'dan)
# STRING_SESSION_1, STRING_SESSION_2, STRING_SESSION_3 va h.k.
sessions = []
for key, val in os.environ.items():
    if key.startswith("STRING_SESSION"):
        sessions.append(val)

if not sessions:
    raise ValueError("❌ Hetch qanday STRING_SESSION topilmadi!")

# 4. Klientlarni (Mijozlarni) yaratish
clients = []
for i, s_str in enumerate(sessions):
    # Birinchi akkaunt (i == 0) asosiy boshqaruvchi akkaunt bo'ladi
    c = Client(f"userbot_{i+1}", api_id=api_id, api_hash=api_hash, session_string=s_str)
    clients.append(c)

# ---------------- HANDLERLAR (MANTIQ) ----------------

def register_handlers(app: Client, is_main_account: bool):
    
    # 1-BOSQICH: Kanalga post kelishini kuzatish
    @app.on_message(filters.chat(KANAL_USERNAME))
    def check_channel_post(client: Client, message: Message):
        global bonus_ol
        if not bonus_ol:
            return
            
        if message.text and "Bonus olish boshlandi" in message.text:
            print(f"🚀 [{client.name}] Kanalda bonus posti topildi! /start bonus yuborilmoqda...")
            try:
                client.read_chat_history(message.chat.id)
            except Exception:
                pass
            client.send_message(BOT_USERNAME, "/start bonus")

    # 2-BOSQICH: Botdan kelgan javob va tugmalarni qayta ishlash
    @app.on_message(filters.chat(BOT_USERNAME))
    def handle_bot_response(client: Client, message: Message):
        global bonus_ol, saqlangan_son
        if not bonus_ol:
            return

        try:
            client.read_chat_history(message.chat.id)
        except Exception:
            pass

        if message.reply_markup and message.text:
            text_lower = message.text.lower()
            
            target_emoji = None
            for fruit_name, emoji in FRUIT_MAP.items():
                if fruit_name in text_lower:
                    target_emoji = emoji
                    print(f"🎯 [{client.name}] So'ralgan meva: {fruit_name} -> {emoji}")
                    break
            
            if target_emoji:
                for row in message.reply_markup.inline_keyboard:
                    for button in row:
                        if button.text and target_emoji in button.text:
                            # Kutish vaqtini dinamik ravishda har safar tasodifiy hisoblash
                            wait_time = random.randint(1, saqlangan_son) if saqlangan_son >= 1 else 1
                            print(f"⏳ [{client.name}] {wait_time} soniya kutilmoqda...")
                            time.sleep(wait_time)
                            
                            print(f"✅ [{client.name}] Tugma bosilmoqda: {button.text}")
                            try:
                                message.click(button.text)
                            except Exception as e:
                                print(f"❌ [{client.name}] Tugmani bosishda xatolik: {e}")
                            return

    # 3-BOSQICH: Boshqaruv komandalari (Faqat ASOSIY akkaunt uchun ishlaydi)
    if is_main_account:
        @app.on_message(filters.me & filters.command("ping", prefixes="."))
        def ping_pong(_, message: Message):
            message.edit_text(f"🏓 **Bonus Userbot faol!**\n👥 Faol akkauntlar soni: `{len(clients)}` ta")

        @app.on_message(filters.me & filters.command("on", prefixes="."))
        def turn_on(_, message: Message):
            global bonus_ol
            if not bonus_ol:
                bonus_ol = True
                message.edit_text("✅ Barcha akkauntlarda bonus olish yoqildi!")
            else:
                message.edit_text("✅ Allaqachon yoqilgan!")

        @app.on_message(filters.me & filters.command("off", prefixes="."))
        def turn_off(_, message: Message):
            global bonus_ol
            if bonus_ol:
                bonus_ol = False
                message.edit_text("❌ Barcha akkauntlarda bonus olish to'xtatildi!")
            else:
                message.edit_text("❌ Allaqachon o'chirilgan!")

        @app.on_message(filters.me & filters.command("son", prefixes="."))
        def save_number(_, message: Message):
            global saqlangan_son
            if len(message.command) > 1 and message.command[1].isdigit():
                saqlangan_son = int(message.command[1])
                message.edit_text(f"✅ **Maksimal kutish vaqti saqlandi:** `{saqlangan_son}` soniya")
            else:
                message.edit_text("⚠️ **Format:** `.son 5` ko'rinishida yuboring.")

# Har bir akkauntga handlerlarni biriktirish
for i, cl in enumerate(clients):
    is_main = (i == 0) # Birinchi akkaunt asosiy hisoblanadi
    register_handlers(cl, is_main)

# 5. Barcha klientlarni parallel ishga tushirish
print(f"Jami {len(clients)} ta akkaunt ishga tushirilmoqda...")

async def main():
    for cl in clients:
        await cl.start()
    print("🚀 Barcha akkauntlar muvaffaqiyatli ulashdi va ishlamoqda!")
    # Dasturni to'xtatmasdan ushlab turish
    import asyncio
    await asyncio.Event().wait()

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
