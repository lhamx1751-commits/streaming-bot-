from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from database import yt_all, yt_get, yt_delete
from utils import sisa_hari, format_tgl, status_icon

async def youtube_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data

    if data == "menu_youtube":
        await list_youtube(update, "aktif")
    elif data == "yt_list_aktif":
        await list_youtube(update, "aktif")
    elif data == "yt_list_expired":
        await list_youtube(update, "expired")
    elif data == "yt_list_semua":
        await list_youtube(update, None)
    elif data.startswith("yt_detail_"):
        await detail_youtube(update, int(data[10:]))
    elif data.startswith("yt_hapus_konfirm_"):
        yid = int(data[17:])
        y = yt_get(yid)
        kb = [[
            InlineKeyboardButton("✅ Ya, Hapus", callback_data=f"yt_hapus_{yid}"),
            InlineKeyboardButton("❌ Batal", callback_data=f"yt_detail_{yid}"),
        ]]
        await query.edit_message_text(
            f"⚠️ *Yakin hapus akun YouTube ini?*\n\n📧 {y['email']}",
            parse_mode='Markdown', reply_markup=InlineKeyboardMarkup(kb)
        )
    elif data.startswith("yt_hapus_"):
        yid = int(data[9:])
        y = yt_get(yid)
        yt_delete(yid)
        kb = [[InlineKeyboardButton("« Menu Utama", callback_data="start_menu")]]
        await query.edit_message_text(f"✅ Akun *{y['email']}* berhasil dihapus.", parse_mode='Markdown', reply_markup=InlineKeyboardMarkup(kb))

async def list_youtube(update, status):
    query = update.callback_query
    list_y = yt_all(status)
    label = "Aktif" if status == "aktif" else "Expired" if status == "expired" else "Semua"

    teks = f"📺 *YouTube — {label}* ({len(list_y)} akun)\n━━━━━━━━━━━━━━━━━━━━\n\n"
    kb = []

    if not list_y:
        teks += "❌ Tidak ada akun."
    else:
        for y in list_y:
            sisa = sisa_hari(y['expired'])
            icon = status_icon(sisa)
            teks += f"{icon} `{y['email']}` — {sisa}hr\n"
            kb.append([InlineKeyboardButton(f"📺 {y['email']}", callback_data=f"yt_detail_{y['id']}")])

    kb.append([
        InlineKeyboardButton("🟢 Aktif", callback_data="yt_list_aktif"),
        InlineKeyboardButton("🔴 Expired", callback_data="yt_list_expired"),
        InlineKeyboardButton("📋 Semua", callback_data="yt_list_semua"),
    ])
    kb.append([
        InlineKeyboardButton("➕ Tambah", callback_data="tambah_youtube"),
        InlineKeyboardButton("« Menu", callback_data="start_menu"),
    ])
    await query.edit_message_text(teks, parse_mode='Markdown', reply_markup=InlineKeyboardMarkup(kb))

async def detail_youtube(update, yid):
    query = update.callback_query
    y = yt_get(yid)
    if not y:
        await query.edit_message_text("❌ Data tidak ditemukan.")
        return

    sisa = sisa_hari(y['expired'])
    icon = status_icon(sisa)

    teks = (
        f"📺 *Detail Akun YouTube Family*\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"📧 *Email    :* `{y['email']}`\n"
        f"🔑 *Password :* `{y['password'] or '-'}`\n"
        f"⏰ *Expired  :* {format_tgl(y['expired'])}\n"
        f"{icon} *Sisa     :* {sisa} hari\n"
        f"📝 *Catatan  :* {y['catatan'] or '-'}\n"
    )

    kb = [
        [
            InlineKeyboardButton("✏️ Edit", callback_data=f"edit_yt_{yid}"),
            InlineKeyboardButton("🔄 Perpanjang", callback_data=f"perp_yt_{yid}"),
        ],
        [
            InlineKeyboardButton("🗑️ Hapus", callback_data=f"yt_hapus_konfirm_{yid}"),
            InlineKeyboardButton("« Kembali", callback_data="menu_youtube"),
        ],
    ]
    await query.edit_message_text(teks, parse_mode='Markdown', reply_markup=InlineKeyboardMarkup(kb))
