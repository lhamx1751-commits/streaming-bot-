from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from database import *
from utils import sisa_hari, format_tgl, status_icon, format_rp


async def disney_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data

    if data == "menu_disney":
        await tampil_list_disney(update)
    elif data.startswith("ds_detail_"):
        await tampil_detail_disney(update, int(data[10:]))
    elif data.startswith("ds_perangkat_"):
        await tampil_perangkat(update, int(data[13:]))
    elif data.startswith("ds_hapus_perangkat_"):
        rid = int(data[19:])
        p = perangkat_get_all.__module__
        from database import get_conn
        conn = get_conn()
        c = conn.cursor()
        c.execute("SELECT disney_id FROM disney_perangkat WHERE id=?", (rid,))
        row = c.fetchone()
        conn.close()
        did = row['disney_id'] if row else 0
        perangkat_hapus(rid)
        kb = [[InlineKeyboardButton("« Kembali", callback_data=f"ds_perangkat_{did}")]]
        await query.edit_message_text("✅ Perangkat berhasil dihapus.", reply_markup=InlineKeyboardMarkup(kb))
    elif data.startswith("ds_hapus_konfirm_"):
        did = int(data[17:])
        d = disney_get(did)
        kb = [[
            InlineKeyboardButton("✅ Ya, Hapus", callback_data=f"ds_hapus_{did}"),
            InlineKeyboardButton("❌ Batal", callback_data=f"ds_detail_{did}"),
        ]]
        await query.edit_message_text(
            f"⚠️ *Yakin hapus akun Disney+ ini?*\n\n📧 {d['email']}",
            parse_mode='Markdown', reply_markup=InlineKeyboardMarkup(kb)
        )
    elif data.startswith("ds_hapus_"):
        did = int(data[9:])
        disney_hapus(did)
        kb = [[InlineKeyboardButton("« Menu Utama", callback_data="start_menu")]]
        await query.edit_message_text("✅ Akun Disney+ berhasil dihapus.", reply_markup=InlineKeyboardMarkup(kb))


async def tampil_list_disney(update):
    query = update.callback_query
    list_d = disney_get_all()

    if not list_d:
        kb = [
            [InlineKeyboardButton("➕ Tambah Akun Disney+", callback_data="tambah_disney")],
            [InlineKeyboardButton("« Menu Utama", callback_data="start_menu")],
        ]
        await query.edit_message_text(
            "🏰 *Disney+*\n\n❌ Belum ada akun Disney+.",
            parse_mode='Markdown', reply_markup=InlineKeyboardMarkup(kb)
        )
        return

    teks = f"🏰 *Daftar Akun Disney+* ({len(list_d)} akun)\n━━━━━━━━━━━━━━━━━━━━\n\n"
    kb = []
    for d in list_d:
        sisa = sisa_hari(d['expired_langganan'])
        icon = status_icon(sisa)
        perangkat = perangkat_get_all(d['id'])
        teks += f"{icon} `{d['email']}` — {len(perangkat)} perangkat ({sisa}hr)\n"
        kb.append([InlineKeyboardButton(f"🏰 {d['email']}", callback_data=f"ds_detail_{d['id']}")])

    kb.append([InlineKeyboardButton("➕ Tambah Akun", callback_data="tambah_disney")])
    kb.append([InlineKeyboardButton("« Menu Utama", callback_data="start_menu")])
    await query.edit_message_text(teks, parse_mode='Markdown', reply_markup=InlineKeyboardMarkup(kb))


async def tampil_detail_disney(update, did):
    query = update.callback_query
    d = disney_get(did)
    if not d:
        await query.edit_message_text("❌ Data tidak ditemukan.")
        return

    perangkat_list = perangkat_get_all(did)
    sisa = sisa_hari(d['expired_langganan'])
    icon = status_icon(sisa)

    teks = (
        f"🏰 *Detail Akun Disney+*\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"📱 *No HP      :* {d['no_hp'] or '-'}\n"
        f"📧 *Email      :* `{d['email']}`\n"
        f"🔑 *Password   :* `{d['password'] or '-'}`\n"
        f"⏰ *Expired    :* {format_tgl(d['expired_langganan'])}\n"
        f"{icon} *Sisa       :* {sisa} hari\n"
        f"💰 *Harga      :* {format_rp(d['harga'])}\n"
        f"📝 *Catatan    :* {d['catatan'] or '-'}\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"📱 *Perangkat Login ({len(perangkat_list)}):*\n\n"
    )

    for i, p in enumerate(perangkat_list, 1):
        teks += (
            f"  {i}. 📱 *{p['nama_perangkat']}*\n"
            f"     👤 {p['nama_pelanggan'] or '-'} | 📞 {p['no_hp'] or '-'}\n"
            f"     📅 {p['tanggal_login'] or '-'}\n\n"
        )

    kb = [
        [InlineKeyboardButton("📱 Kelola Perangkat", callback_data=f"ds_perangkat_{did}")],
        [
            InlineKeyboardButton("🗑️ Hapus Akun", callback_data=f"ds_hapus_konfirm_{did}"),
            InlineKeyboardButton("« Kembali", callback_data="menu_disney"),
        ],
    ]
    await query.edit_message_text(teks, parse_mode='Markdown', reply_markup=InlineKeyboardMarkup(kb))


async def tampil_perangkat(update, did):
    query = update.callback_query
    d = disney_get(did)
    perangkat_list = perangkat_get_all(did)

    teks = (
        f"📱 *Kelola Perangkat Disney+*\n"
        f"📧 {d['email']}\n"
        f"━━━━━━━━━━━━━━━━━━━━\n\n"
    )

    kb = []
    for p in perangkat_list:
        teks += f"📱 *{p['nama_perangkat']}* — {p['nama_pelanggan'] or '-'}\n"
        kb.append([InlineKeyboardButton(
            f"🗑️ Hapus {p['nama_perangkat']}",
            callback_data=f"ds_hapus_perangkat_{p['id']}"
        )])

    kb.append([InlineKeyboardButton("➕ Tambah Perangkat", callback_data=f"tambah_perangkat_{did}")])
    kb.append([InlineKeyboardButton("« Kembali", callback_data=f"ds_detail_{did}")])

    await query.edit_message_text(
        teks or "Belum ada perangkat.",
        parse_mode='Markdown',
        reply_markup=InlineKeyboardMarkup(kb)
    )
