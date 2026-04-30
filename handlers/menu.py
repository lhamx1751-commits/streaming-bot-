from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from database import get_statistik, netflix_get_all, disney_get_all, yt_get_all
from database import profil_get_all, perangkat_get_all, member_get_all
from utils import sisa_hari, format_tgl, status_icon

async def menu_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data

    if data == "menu_tambah":
        kb = [
            [InlineKeyboardButton("🎬 Tambah Akun Netflix", callback_data="tambah_netflix")],
            [InlineKeyboardButton("🏰 Tambah Akun Disney+", callback_data="tambah_disney")],
            [InlineKeyboardButton("📺 Tambah Akun YouTube", callback_data="tambah_youtube")],
            [InlineKeyboardButton("« Kembali", callback_data="start_menu")],
        ]
        await query.edit_message_text(
            "➕ *Tambah Akun Baru*\n\nPilih layanan:",
            parse_mode='Markdown', reply_markup=InlineKeyboardMarkup(kb)
        )

    elif data == "menu_statistik":
        stats = get_statistik()
        teks = (
            f"📊 *Statistik Lengkap*\n"
            f"━━━━━━━━━━━━━━━━━━━━\n\n"
            f"🎬 *Netflix Premium*\n"
            f"   📦 Akun: {stats['netflix']}\n"
            f"   👥 Profil Aktif: {stats['profil']}\n\n"
            f"🏰 *Disney+*\n"
            f"   📦 Akun: {stats['disney']}\n"
            f"   📱 Perangkat: {stats['perangkat']}\n\n"
            f"📺 *YouTube Family*\n"
            f"   📦 Akun: {stats['youtube']}\n"
            f"   👥 Member: {stats['member']}\n"
            f"━━━━━━━━━━━━━━━━━━━━"
        )
        kb = [[InlineKeyboardButton("« Menu Utama", callback_data="start_menu")]]
        await query.edit_message_text(teks, parse_mode='Markdown', reply_markup=InlineKeyboardMarkup(kb))

    elif data == "menu_expired":
        await tampil_expired(update)


async def tampil_expired(update):
    query = update.callback_query
    teks = "⚠️ *Akun Akan Expired*\n━━━━━━━━━━━━━━━━━━━━\n\n"
    ada = False

    for n in netflix_get_all():
        for p in profil_get_all(n['id']):
            sisa = sisa_hari(p['expired'])
            if 0 <= sisa <= 7:
                ada = True
                icon = status_icon(sisa)
                teks += f"{icon} 🎬 *Profil {p['nomor_profil']}* — {p['nama_pelanggan'] or '-'}\n"
                teks += f"   📧 {n['email']} | ⏰ {sisa} hari lagi\n\n"

    for d in disney_get_all():
        sisa = sisa_hari(d['expired_langganan'])
        if 0 <= sisa <= 7:
            ada = True
            icon = status_icon(sisa)
            teks += f"{icon} 🏰 *Disney+* — {d['email']}\n"
            teks += f"   ⏰ {sisa} hari lagi\n\n"

    for y in yt_get_all():
        sisa = sisa_hari(y['expired_langganan'])
        if 0 <= sisa <= 7:
            ada = True
            icon = status_icon(sisa)
            teks += f"{icon} 📺 *YouTube* — {y['email_akun']}\n"
            teks += f"   ⏰ {sisa} hari lagi\n\n"

    if not ada:
        teks += "✅ Tidak ada akun yang akan expired dalam 7 hari!"

    kb = [[InlineKeyboardButton("« Menu Utama", callback_data="start_menu")]]
    await query.edit_message_text(teks, parse_mode='Markdown', reply_markup=InlineKeyboardMarkup(kb))
    
