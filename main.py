import os
import random
import asyncio
import threading
import logging
from collections import deque
from flask import Flask, render_template_string
from pyrogram import Client, filters, compose
from pyrogram.types import Message

# ---------------- 1. LOGLARNI VEB-SAHIFADA KO'RSATISH TIZIMI ----------------
# Oxirgi 100 ta log satrini xotirada saqlash uchun deque
log_buffer = deque(maxlen=100)

class WebLogHandler(logging.Handler):
    def emit(self, record):
        log_entry = self.format(record)
        log_buffer.append(log_entry)

# Standart logging va print xabarlarini tutib olish
web_handler = WebLogHandler()
web_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s', datefmt='%H:%M:%S'))

logger = logging.getLogger()
logger.setLevel(logging.INFO)
logger.addHandler(web_handler)

# Print xabarlarini ham log bo'lib tushishi uchun funksiya
def log_print(text):
    print(text)
    logger.info(text)

# 2. Flask Web Server
web_app = Flask(__name__)

# Bosh sahifa
@web_app.route('/')
def home():
    return "Multi-Account Bonus Userbot faol! Loglarni ko'rish uchun <a href='/logs'>/logs</a> sahifasiga o'ting."

# Loglarni ko'rsatuvchi jonli sahifa
HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Userbot Loglari</title>
    <meta http-equiv="refresh" content="3"> <!-- Har 3 soniyada avto-yangilanish -->
    <style>
        body { background-color: #1e1e1e; color: #00ff00; font-family: monospace; padding: 20px; }
        h2 { color: #ffffff; }
        .log-box { background: #000; border: 1px solid #333; padding: 15px; border-radius: 5px; height: 80vh; overflow-y: auto; }
        .log-line { border-bottom: 1px solid #222; padding: 3px 0; white-space: pre-wrap; }
        .error { color: #ff5555; }
        .success { color: #55ff55; }
    </style>
</head>
<body>
    <h2>📋 Userbot Jonli Loglari (Auto-refresh)</h2>
    <div class="log-box">
        {% for log in logs %}
            <div class="log-line {% if '❌' in log or 'ERROR' in log %}error{% elif '✅' in log %}success{% endif %}">{{ log }}</div>
        {% endfor %}
    </div>
</body>
</html>
"""

@web_app.route('/logs')
def show_logs():
    return render_template_string(HTML_TEMPLATE, logs=list(log_buffer))

def run_web():
    port = int(os.environ.get("PORT", 8080))
    web_app.run(host="0.0.0.0", port=port)

threading.Thread(target=run_web, daemon=True).start()

# ---------------- 3. ASOSIY USERBOT SOZLAMALARI ----------------
api_id = int(os.environ.get("API_ID"))
api_hash = os.environ.get("API_HASH")

KANAL_USERNAME = "CheapSMM_News" 
BOT_USERNAME = "CheapSMM_bot" 

bonus_ol = True
saqlangan_son = 4

FRUIT_MAP = {
    "qulupnay": "🍓", "olma": "🍏", "nok": "🍐", "banan": "🍌",
    "kivi": "🥝", "uzum": "🍇", "gilos": "🍒", "shaftoli": "🍑",
    "ananas": "🍍", "apelsin": "🍊", "limon": "🍋"
}

sessions = []
for key, val in os.environ.items():
    if key.startswith("STRING_SESSION"):
        sessions.append(val)

if not sessions:
    raise ValueError("❌ Hech qanday STRING_SESSION topilmadi!")

clients = []
for i, s_str in enumerate(sessions):
    c = Client(f"userbot_{i+1}", api_id=api_id, api_hash=api_hash, session_string=s_str)
    clients.append(c)

# ---------------- 4. HANDLERLAR (ASYNC) ----------------

def register_handlers(app: Client):
    
    # 1-BOSQICH: Kanalga post kelishini kuzatish (Tezkor va xavfsiz)
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

            # Kutilishni 0.7 soniyaga tushiramiz (0s, 0.7s, 1.4s, 2.1s)
            delay = acc_index * 0.7
            log_print(f"🚀 [{client.name}] Post topildi! {delay:.1f}s kutilmoqda...")
            
            await asyncio.sleep(delay)
            
            try:
                await client.read_chat_history(message.chat.id)
            except Exception:
                pass
                
            try:
                await client.send_message(BOT_USERNAME, "/start bonus")
                log_print(f"✅ [{client.name}] Botga /start bonus yuborildi!")
            except Exception as e:
                log_print(f"❌ [{client.name}] Xabar yuborishda xatolik: {e}")

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
                    log_print(f"🎯 [{client.name}] So'ralgan meva: {fruit_name} -> {emoji}")
                    break
            
            if target_emoji:
                for row in message.reply_markup.inline_keyboard:
                    for button in row:
                        if button.text and target_emoji in button.text:
                            # 0.2 - 0.8 soniya kichik tasodifiy kutilish
                            base_wait = random.uniform(0.2, 0.8)
                            log_print(f"⏳ [{client.name}] {base_wait:.1f}s kutilmoqda...")
                            await asyncio.sleep(base_wait)
                            
                            log_print(f"✅ [{client.name}] Tugma bosilmoqda: {button.text}")
                            try:
                                # timeout-ni olib tashlaymiz va callback-ni to'g'ridan-to'g'ri yuboramiz
                                await message.click(button.text, timeout=30)
                                log_print(f"🎉 [{client.name}] Tugma muvaffaqiyatli bosildi!")
                            except Exception as e:
                                log_print(f"❌ [{client.name}] Tugmani bosishda xatolik: {e}")
                            return


    # 3-BOSQICH: Boshqaruv komandalari
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

# Handlerlarni barcha akkauntlarga ulash
for cl in clients:
    register_handlers(cl)

# 5. Klientlarni ishga tushirish
if __name__ == "__main__":
    log_print(f"🚀 Jami {len(clients)} ta akkaunt ishga tushirilmoqda...")
    compose(clients)
