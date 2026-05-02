import logging, os
from telegram import Update, BotCommand
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters
from dotenv import load_dotenv
from database import init_db
from handlers.start import start_handler, welcome_handler
from handlers.netflix import netflix_callback
from handlers.disney import disney_callback
from handlers.youtube import youtube_callback
from handlers.menu import menu_callback
from handlers.pengingat import cek_pengingat, kirim_laporan_pagi
from handlers.conversation import (
    conv_tambah_netflix, conv_tambah_profil, conv_edit_netflix,
    conv_edit_profil, conv_perp_netflix,
    conv_tambah_disney, conv_tambah_perangkat, conv_edit_disney,
    conv_edit_perangkat, conv_perp_disney,
    conv_tambah_youtube, conv_edit_youtube, conv_perp_youtube,
    conv_cari, conv_bulk_perangkat, conv_bulk_profil
)
import pytz

load_dotenv()
logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID"))
WIB = pytz.timezone("Asia/Jakarta")

async def setup_commands(app):
    await app.bot.set_my_commands([
        BotCommand("start", "🏠 Menu Utama"),
        BotCommand("cari", "🔍 Cari akun"),
        BotCommand("batal", "❌ Batalkan proses"),
    ])

async def error_handler(update, context):
    logger.error("Error:", exc_info=context.error)

def main():
    init_db()
    app = Application.builder().token(BOT_TOKEN).post_init(setup_commands).build()

    for conv in [
        conv_bulk_perangkat(), conv_bulk_profil(),
        conv_tambah_netflix(), conv_tambah_profil(),
        conv_edit_netflix(), conv_edit_profil(), conv_perp_netflix(),
        conv_tambah_disney(), conv_tambah_perangkat(),
        conv_edit_disney(), conv_edit_perangkat(), conv_perp_disney(),
        conv_tambah_youtube(), conv_edit_youtube(), conv_perp_youtube(),
        conv_cari(),
    ]:
        app.add_handler(conv)

    app.add_handler(CommandHandler("start", start_handler))
    app.add_handler(CallbackQueryHandler(start_handler, pattern="^start_menu$"))
    app.add_handler(CallbackQueryHandler(netflix_callback, pattern="^(menu_netflix|nf_)"))
    app.add_handler(CallbackQueryHandler(disney_callback, pattern="^(menu_disney|ds_)"))
    app.add_handler(CallbackQueryHandler(youtube_callback, pattern="^(menu_youtube|yt_)"))
    app.add_handler(CallbackQueryHandler(menu_callback, pattern="^menu_"))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, welcome_handler))
    app.add_error_handler(error_handler)

    app.job_queue.run_repeating(cek_pengingat, interval=3600, first=10)
    app.job_queue.run_daily(
        kirim_laporan_pagi,
        time=__import__('datetime').time(8, 0, 0, tzinfo=WIB)
    )

    logger.info("✅ Streaming Manager Bot v5 aktif!")
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
