import os
import threading
from flask import Flask
from pyrogram import Client, filters

# 1. Render uchun kichik Web Server (Port xatoligini oldini oladi)
web_app = Flask(__name__)

@web_app.route('/')
def home():
    return "Userbot is running!"

def run_web():
    # Render avtomatik PORT o'zgaruvchisini beradi (aks holda 8080)
    port = int(os.environ.get("PORT", 8080))
    web_app.run(host="0.0.0.0", port=port)

# Web serverni alohida oqimda (thread) ishga tushiramiz
threading.Thread(target=run_web, daemon=True).start()

# 2. Pyrogram Userbot qismi
api_id = int(os.environ.get("API_ID"))
api_hash = os.environ.get("API_HASH")
session_string = os.environ.get("STRING_SESSION")

app = Client(
    "userbot",
    api_id=api_id,
    api_hash=api_hash,
    session_string=session_string
)

@app.on_message(filters.me & filters.command("ping", prefixes="."))
def ping_pong(_, message):
    message.edit_text("🏓 **Pong! Userbot muvaffaqiyatli ishlamoqda.**")

@app.on_message(filters.me & filters.command("alive", prefixes="."))
def alive_check(_, message):
    message.edit_text("✅ **Userbot 24/7 rejimida faol!**")

print("Userbot va Web Server ishga tushirildi...")
app.run()
