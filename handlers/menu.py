from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from database import get_backup_text, nf_all, ds_all, yt_all, profil_all, perangkat_all
from utils import sisa_hari, status_icon, format_tgl

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
        await query.edit_message_text("➕ *Tambah Akun Baru*\n\nPilih layanan:", parse_mode='Markdown', reply_markup=InlineKeyboardMarkup(kb))

    elif data == "menu_stats":
        from database import get_stats
        stats = get_stats()
        teks = (
            f"📊 *Statistik Lengkap*\n"
            f"━━━━━━━━━━━━━━━━━━━━\n\n"
            f"🎬 *Netflix Premium*\n"
            f"   📦 Akun Aktif : {stats['netflix']}\n"
            f"   👥 Total Profil: {stats['profil']}\n\n"
            f"🏰 *Disney+*\n"
            f"   📦 Akun Aktif  : {stats['disney']}\n"
            f"   📱 Total Perangkat: {stats['perangkat']}\n\n"
            f"📺 *YouTube Family*\n"
            f"   📦 Akun Aktif : {stats['youtube']}\n"
            f"━━━━━━━━━━━━━━━━━━━━"
        )
        kb = [[InlineKeyboardButton("« Menu Utama", callback_data="start_menu")]]
        await query.edit_message_text(teks, parse_mode='Markdown', reply_markup=InlineKeyboardMarkup(kb))

    elif data == "menu_expired":
        await tampil_expired(update)

    elif data == "menu_backup":
        await tampil_backup(update)

    elif data == "menu_cari":
        await query.edit_message_text(
            "🔍 *Cari Akun*\n\nGunakan perintah:\n/cari [keyword]\n\nContoh:\n/cari kedaipremium\n/cari 08571",
            parse_mode='Markdown'
        )

async def tampil_expired(update):
    query = update.callback_query
    teks = "⚠️ *Akun Akan Expired (7 hari)*\n━━━━━━━━━━━━━━━━━━━━\n\n"
    ada = False

    for n in nf_all():
        for p in profil_all(n['id']):
            if not p['expired']: continue
            sisa = sisa_hari(p['expired'])
            if 0 <= sisa <= 7:
                ada = True
                icon = status_icon(sisa)
                teks += f"{icon} 🎬 *{p['nama']}* (Profil {p['nomor']})\n"
                teks += f"   📧 {n['email']}\n"
                teks += f"   ⏰ {format_tgl(p['expired'])} — {sisa} hari lagi\n\n"

    for d in ds_all():
        sisa = sisa_hari(d['expired_langganan'])
        if 0 <= sisa <= 7:
            ada = True
            icon = status_icon(sisa)
            teks += f"{icon} 🏰 *Disney+* — {d['email']}\n"
            teks += f"   ⏰ {format_tgl(d['expired_langganan'])} — {sisa} hari lagi\n\n"
        for p in perangkat_all(d['id']):
            if not p['expired']: continue
            sisa = sisa_hari(p['expired'])
            if 0 <= sisa <= 7:
                ada = True
                icon = status_icon(sisa)
                teks += f"{icon} 📱 *{p['nama']}* (Disney perangkat)\n"
                teks += f"   📧 {d['email']}\n"
                teks += f"   ⏰ {format_tgl(p['expired'])} — {sisa} hari lagi\n\n"

    for y in yt_all():
        sisa = sisa_hari(y['expired'])
        if 0 <= sisa <= 7:
            ada = True
            icon = status_icon(sisa)
            teks += f"{icon} 📺 *YouTube* — {y['email']}\n"
            teks += f"   ⏰ {format_tgl(y['expired'])} — {sisa} hari lagi\n\n"

    if not ada:
        teks += "✅ Tidak ada akun yang akan expired dalam 7 hari!"

    kb = [[InlineKeyboardButton("« Menu Utama", callback_data="start_menu")]]
    await query.edit_message_text(teks, parse_mode='Markdown', reply_markup=InlineKeyboardMarkup(kb))

async def tampil_backup(update):
    query = update.callback_query
    teks = get_backup_text()
    kb = [[InlineKeyboardButton("« Menu Utama", callback_data="start_menu")]]
    # Split kalau teks terlalu panjang
    if len(teks) > 4000:
        parts = [teks[i:i+4000] for i in range(0, len(teks), 4000)]
        for part in parts[:-1]:
            await query.message.reply_text(part, parse_mode='Markdown')
        await query.message.reply_text(parts[-1], parse_mode='Markdown', reply_markup=InlineKeyboardMarkup(kb))
    else:
        await query.edit_message_text(teks, parse_mode='Markdown', reply_markup=InlineKeyboardMarkup(kb))
