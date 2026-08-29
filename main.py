import os
from pyrogram import Client, filters

# Render'dagi muhit o'zgaruvchilaridan (Environment Variables) ma'lumotlarni olish
api_id = int(os.environ.get("API_ID"))
api_hash = os.environ.get("API_HASH")
session_string = os.environ.get("STRING_SESSION")

app = Client(
    "userbot",
    api_id=api_id,
    api_hash=api_hash,
    session_string=session_string
)

# `.ping` deb yozganingizda ishlaydi
@app.on_message(filters.me & filters.command("ping", prefixes="."))
def ping_pong(_, message):
    message.edit_text("🏓 **Pong! Userbot muvaffaqiyatli ishlamoqda.**")

# `.alive` deb yozganingizda ma'lumot beradi
@app.on_message(filters.me & filters.command("alive", prefixes="."))
def alive_check(_, message):
    message.edit_text("✅ **Userbot va 24/7 rejimida faol!**")

print("Userbot ishga tushirildi...")
app.run()
