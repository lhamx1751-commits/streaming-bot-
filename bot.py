import logging, os
from telegram import Update, BotCommand
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes
from dotenv import load_dotenv
from database import init_db
from handlers.start import start_handler, welcome_handler
from handlers.netflix import netflix_callback
from handlers.disney import disney_callback
from handlers.youtube import youtube_callback
from handlers.menu import menu_callback
from handlers.pengingat import cek_pengingat
from handlers.conversation import (
    conv_tambah_netflix, conv_tambah_profil,
    conv_tambah_disney, conv_tambah_perangkat,
    conv_tambah_youtube, conv_tambah_member
)

load_dotenv()
logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s', level=logging.INFO)

BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID"))

async def setup_commands(app):
    await app.bot.set_my_commands([
        BotCommand("start", "🏠 Menu Utama"),
        BotCommand("batal", "❌ Batalkan proses"),
    ])
    await app.bot.set_my_short_description("Bot manajemen akun streaming Netflix, Disney+, YouTube Family")
    await app.bot.set_my_description(
        "👋 Halo! Saya Streaming Manager Bot\n\n"
        "Saya membantu kamu kelola pelanggan:\n"
        "🎬 Netflix Premium — per profil, expired berbeda\n"
        "🏰 Disney+ — kelola perangkat login\n"
        "📺 YouTube Family — kelola member\n\n"
        "Ketik /start untuk membuka menu utama."
    )

async def error_handler(update, context):
    logging.error("Error:", exc_info=context.error)

def main():
    init_db()
    app = Application.builder().token(BOT_TOKEN).post_init(setup_commands).build()

    # Conversation handlers
    app.add_handler(conv_tambah_netflix())
    app.add_handler(conv_tambah_profil())
    app.add_handler(conv_tambah_disney())
    app.add_handler(conv_tambah_perangkat())
    app.add_handler(conv_tambah_youtube())
    app.add_handler(conv_tambah_member())

    # Commands
    app.add_handler(CommandHandler("start", start_handler))

    # Callbacks
    app.add_handler(CallbackQueryHandler(start_handler, pattern="^start_menu$"))
    app.add_handler(CallbackQueryHandler(netflix_callback, pattern="^(menu_netflix|nf_)"))
    app.add_handler(CallbackQueryHandler(disney_callback, pattern="^(menu_disney|ds_)"))
    app.add_handler(CallbackQueryHandler(youtube_callback, pattern="^(menu_youtube|yt_)"))
    app.add_handler(CallbackQueryHandler(menu_callback, pattern="^menu_"))

    # Welcome message (tanpa /start)
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, welcome_handler))

    app.add_error_handler(error_handler)
    app.job_queue.run_repeating(cek_pengingat, interval=3600, first=10)

    logging.info("✅ Streaming Manager Bot aktif!")
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
