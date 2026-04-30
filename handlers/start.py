from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from database import get_statistik
from utils import cek_admin
import os

ADMIN_ID = int(os.getenv("ADMIN_ID", "0"))

WELCOME_TEXT = """👋 Halo! Saya *Streaming Manager Bot*

Saya membantu kamu kelola pelanggan:
🎬 Netflix Premium
🏰 Disney+
📺 YouTube Family

Ketik /start untuk membuka menu utama."""

async def start_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user

    if not cek_admin(user.id):
        msg = "⛔ *Akses Ditolak*\nBot ini hanya untuk admin."
        if update.callback_query:
            await update.callback_query.answer()
            await update.callback_query.edit_message_text(msg, parse_mode='Markdown')
        else:
            await update.message.reply_text(msg, parse_mode='Markdown')
        return

    stats = get_statistik()

    teks = (
        f"╔══════════════════════╗\n"
        f"       📊 *STREAMING MANAGER*\n"
        f"╚══════════════════════╝\n\n"
        f"👋 Selamat datang, *{user.first_name}*!\n\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"📦 *Ringkasan Akun:*\n"
        f"🎬 Netflix  : *{stats['netflix']}* akun ({stats['profil']} profil aktif)\n"
        f"🏰 Disney+  : *{stats['disney']}* akun ({stats['perangkat']} perangkat)\n"
        f"📺 YouTube  : *{stats['youtube']}* akun ({stats['member']} member)\n"
        f"━━━━━━━━━━━━━━━━━━━━\n\n"
        f"🔽 *Pilih menu di bawah:*"
    )

    keyboard = [
        [
            InlineKeyboardButton("🎬 Netflix", callback_data="menu_netflix"),
            InlineKeyboardButton("🏰 Disney+", callback_data="menu_disney"),
            InlineKeyboardButton("📺 YouTube", callback_data="menu_youtube"),
        ],
        [
            InlineKeyboardButton("➕ Tambah Akun", callback_data="menu_tambah"),
        ],
        [
            InlineKeyboardButton("📊 Statistik", callback_data="menu_statistik"),
            InlineKeyboardButton("⚠️ Akan Expired", callback_data="menu_expired"),
        ],
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)

    if update.callback_query:
        await update.callback_query.answer()
        await update.callback_query.edit_message_text(teks, parse_mode='Markdown', reply_markup=reply_markup)
    else:
        await update.message.reply_text(teks, parse_mode='Markdown', reply_markup=reply_markup)


async def welcome_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Muncul saat user pertama kali buka bot (tanpa /start)"""
    text = update.message.text.lower() if update.message.text else ""
    if text in ["start", "halo", "hi", "hello", "mulai"]:
        await start_handler(update, context)
