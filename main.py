import os
import random
import asyncio
import threading
from flask import Flask
from pyrogram import Client, filters, compose
from pyrogram.types import Message

# 1. Web Server (Render to'xtab qolmasligi uchun)
web_app = Flask(__name__)

@web_app.route('/')
def home():
    return "Multi-Account Bonus Userbot (Async) is running!"

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
sessions = []
for key, val in os.environ.items():
    if key.startswith("STRING_SESSION"):
        sessions.append(val)

if not sessions:
    raise ValueError("❌ Hech qanday STRING_SESSION topilmadi!")

# 4. Klientlarni (Mijozlarni) yaratish
clients = []
for i, s_str in enumerate(sessions):
    c = Client(f"userbot_{i+1}", api_id=api_id, api_hash=api_hash, session_string=s_str)
    clients.append(c)

# ---------------- HANDLERLAR (ASYNC MANTIQ) ----------------

def register_handlers(app: Client):
    
    # 1-BOSQICH: Kanalga post kelishini kuzatish
    @app.on_message(filters.chat(KANAL_USERNAME))
    async def check_channel_post(client: Client, message: Message):
        global bonus_ol
        if not bonus_ol:
            return
            
        if message.text and "Bonus olish boshlandi" in message.text:
            try:
                acc_index = int(client.name.split("_")[1]) - 1
            except Exception:
                acc_index = 0

            # Har bir akkaunt uchun ketma-ket 2.5 soniya farq bilan so'rov yuborish
            delay = acc_index * 2.5
            print(f"🚀 [{client.name}] Post topildi! {delay}s kutilmoqda...")
            
            await asyncio.sleep(delay)
            
            try:
                await client.read_chat_history(message.chat.id)
            except Exception:
                pass
                
            try:
                await client.send_message(BOT_USERNAME, "/start bonus")
                print(f"✅ [{client.name}] Botga /start bonus yuborildi!")
            except Exception as e:
                print(f"❌ [{client.name}] Xabar yuborishda xatolik: {e}")

    # 2-BOSQICH: Botdan kelgan javob va tugmalarni qayta ishlash
    @app.on_message(filters.chat(BOT_USERNAME))
    async def handle_bot_response(client: Client, message: Message):
        global bonus_ol, saqlangan_son
        if not bonus_ol:
            return

        try:
            await client.read_chat_history(message.chat.id)
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
                            base_wait = random.randint(1, saqlangan_son) if saqlangan_son >= 1 else 1
                            print(f"⏳ [{client.name}] {base_wait} soniya kutilmoqda...")
                            await asyncio.sleep(base_wait)
                            
                            print(f"✅ [{client.name}] Tugma bosilmoqda: {button.text}")
                            try:
                                await message.click(button.text)
                            except Exception as e:
                                print(f"❌ [{client.name}] Tugmani bosishda xatolik: {e}")
                            return

    # 3-BOSQICH: Boshqaruv komandalari (Barcha akkauntlarda ishlaydi)
    @app.on_message(filters.me & filters.command("ping", prefixes="."))
    async def ping_pong(_, message: Message):
        await message.edit_text(f"🏓 **Bonus Userbot faol!**\n👥 Jami ulangan akkauntlar: `{len(clients)}` ta")

    @app.on_message(filters.me & filters.command("on", prefixes="."))
    async def turn_on(_, message: Message):
        global bonus_ol
        if not bonus_ol:
            bonus_ol = True
            await message.edit_text("✅ Barcha akkauntlarda bonus olish yoqildi!")
        else:
            await message.edit_text("✅ Allaqachon yoqilgan!")

    @app.on_message(filters.me & filters.command("off", prefixes="."))
    async def turn_off(_, message: Message):
        global bonus_ol
        if bonus_ol:
            bonus_ol = False
            await message.edit_text("❌ Barcha akkauntlarda bonus olish to'xtatildi!")
        else:
            await message.edit_text("❌ Allaqachon o'chirilgan!")

    @app.on_message(filters.me & filters.command("son", prefixes="."))
    async def save_number(_, message: Message):
        global saqlangan_son
        if len(message.command) > 1 and message.command[1].isdigit():
            saqlangan_son = int(message.command[1])
            await message.edit_text(f"✅ **Maksimal kutish vaqti saqlandi:** `{saqlangan_son}` soniya")
        else:
            await message.edit_text("⚠️ **Format:** `.son 5` ko'rinishida yuboring.")

# Handlerlarni barcha akkauntlarga biriktirish
for cl in clients:
    register_handlers(cl)

# 5. Klientlarni ishga tushirish
if __name__ == "__main__":
    print(f"🚀 Jami {len(clients)} ta akkaunt ishga tushirilmoqda...")
    compose(clients)
