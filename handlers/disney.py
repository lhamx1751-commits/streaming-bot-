from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from database import ds_all, ds_get, ds_delete, perangkat_all, perangkat_get, perangkat_delete
from utils import sisa_hari, format_tgl, status_icon

async def disney_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data

    if data == "menu_disney":
        await list_disney(update, "aktif")
    elif data == "ds_list_aktif":
        await list_disney(update, "aktif")
    elif data == "ds_list_expired":
        await list_disney(update, "expired")
    elif data == "ds_list_semua":
        await list_disney(update, None)
    elif data.startswith("ds_detail_"):
        await detail_disney(update, int(data[10:]))
    elif data.startswith("ds_perangkat_"):
        await kelola_perangkat(update, int(data[13:]))
    elif data.startswith("ds_hapus_konfirm_"):
        did = int(data[17:])
        d = ds_get(did)
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
        d = ds_get(did)
        ds_delete(did)
        kb = [[InlineKeyboardButton("« Menu Utama", callback_data="start_menu")]]
        await query.edit_message_text(f"✅ Akun *{d['email']}* berhasil dihapus.", parse_mode='Markdown', reply_markup=InlineKeyboardMarkup(kb))
    elif data.startswith("ds_hapus_perangkat_konfirm_"):
        rid = int(data[27:])
        p = perangkat_get(rid)
        kb = [[
            InlineKeyboardButton("✅ Ya, Hapus", callback_data=f"ds_hapus_perangkat_{rid}"),
            InlineKeyboardButton("❌ Batal", callback_data=f"ds_perangkat_{p['disney_id']}"),
        ]]
        await query.edit_message_text(
            f"⚠️ *Yakin hapus perangkat ini?*\n\n📱 {p['nama']}",
            parse_mode='Markdown', reply_markup=InlineKeyboardMarkup(kb)
        )
    elif data.startswith("ds_hapus_perangkat_"):
        rid = int(data[19:])
        p = perangkat_get(rid)
        did = p['disney_id']
        perangkat_delete(rid)
        await kelola_perangkat(update, did)

async def list_disney(update, status):
    query = update.callback_query
    list_d = ds_all(status)
    label = "Aktif" if status == "aktif" else "Expired" if status == "expired" else "Semua"

    teks = f"🏰 *Disney+ — {label}* ({len(list_d)} akun)\n━━━━━━━━━━━━━━━━━━━━\n\n"
    kb = []

    if not list_d:
        teks += "❌ Tidak ada akun."
    else:
        for d in list_d:
            sisa = sisa_hari(d['expired_langganan'])
            icon = status_icon(sisa)
            pg = perangkat_all(d['id'])
            teks += f"{icon} `{d['email']}` — {len(pg)} perangkat ({sisa}hr)\n"
            kb.append([InlineKeyboardButton(f"🏰 {d['email']}", callback_data=f"ds_detail_{d['id']}")])

    kb.append([
        InlineKeyboardButton("🟢 Aktif", callback_data="ds_list_aktif"),
        InlineKeyboardButton("🔴 Expired", callback_data="ds_list_expired"),
        InlineKeyboardButton("📋 Semua", callback_data="ds_list_semua"),
    ])
    kb.append([
        InlineKeyboardButton("➕ Tambah", callback_data="tambah_disney"),
        InlineKeyboardButton("« Menu", callback_data="start_menu"),
    ])
    await query.edit_message_text(teks, parse_mode='Markdown', reply_markup=InlineKeyboardMarkup(kb))

async def detail_disney(update, did):
    query = update.callback_query
    d = ds_get(did)
    if not d:
        await query.edit_message_text("❌ Data tidak ditemukan.")
        return

    pg_list = perangkat_all(did)
    sisa = sisa_hari(d['expired_langganan'])
    icon = status_icon(sisa)

    teks = (
        f"🏰 *Detail Akun Disney+*\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"📦 *Paket    :* {d['nama_paket']}\n"
        f"📱 *No HP    :* {d['no_hp'] or '-'}\n"
        f"📧 *Email    :* `{d['email']}`\n"
        f"🔑 *Password :* `{d['password'] or '-'}`\n"
        f"⏰ *Expired  :* {format_tgl(d['expired_langganan'])}\n"
        f"{icon} *Sisa     :* {sisa} hari\n"
        f"📝 *Catatan  :* {d['catatan'] or '-'}\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"📱 *Perangkat ({len(pg_list)}/5):*\n\n"
    )

    for i, p in enumerate(pg_list, 1):
        sisa_p = sisa_hari(p['expired']) if p['expired'] else 999
        icon_p = status_icon(sisa_p)
        teks += f"{icon_p} *{i}. {p['nama']}*\n"
        teks += f"   ⏰ {format_tgl(p['expired']) if p['expired'] else '-'} ({sisa_p}hr)\n\n"

    kb = [
        [InlineKeyboardButton("📱 Kelola Perangkat", callback_data=f"ds_perangkat_{did}")],
        [
            InlineKeyboardButton("✏️ Edit Akun", callback_data=f"edit_ds_{did}"),
            InlineKeyboardButton("🔄 Perpanjang", callback_data=f"perp_ds_{did}"),
        ],
        [
            InlineKeyboardButton("🗑️ Hapus", callback_data=f"ds_hapus_konfirm_{did}"),
            InlineKeyboardButton("« Kembali", callback_data="menu_disney"),
        ],
    ]
    await query.edit_message_text(teks, parse_mode='Markdown', reply_markup=InlineKeyboardMarkup(kb))

async def kelola_perangkat(update, did):
    query = update.callback_query
    d = ds_get(did)
    pg_list = perangkat_all(did)

    teks = (
        f"📱 *Kelola Perangkat Disney+*\n"
        f"📧 {d['email']}\n"
        f"━━━━━━━━━━━━━━━━━━━━\n\n"
    )

    kb = []
    for p in pg_list:
        sisa = sisa_hari(p['expired']) if p['expired'] else 999
        icon = status_icon(sisa)
        teks += f"{icon} *{p['nama']}* | {format_tgl(p['expired']) if p['expired'] else '-'}\n"
        kb.append([
            InlineKeyboardButton(f"✏️ Edit {p['nama']}", callback_data=f"edit_perangkat_{p['id']}"),
            InlineKeyboardButton("🗑️ Hapus", callback_data=f"ds_hapus_perangkat_konfirm_{p['id']}"),
        ])

    if len(pg_list) < 5:
        kb.append([InlineKeyboardButton("➕ Tambah 1", callback_data=f"tambah_perangkat_{did}"), InlineKeyboardButton("📋 Bulk Tambah", callback_data=f"bulk_perangkat_{did}")])
    kb.append([InlineKeyboardButton("« Kembali", callback_data=f"ds_detail_{did}")])

    await query.edit_message_text(teks or "Belum ada perangkat.", parse_mode='Markdown', reply_markup=InlineKeyboardMarkup(kb))
