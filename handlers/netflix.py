from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from database import nf_all, nf_get, nf_delete, profil_all, profil_get, profil_delete
from utils import sisa_hari, format_tgl, status_icon

async def netflix_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data

    if data == "menu_netflix": await list_netflix(update, "aktif")
    elif data == "nf_list_aktif": await list_netflix(update, "aktif")
    elif data == "nf_list_expired": await list_netflix(update, "expired")
    elif data == "nf_list_semua": await list_netflix(update, None)
    elif data.startswith("nf_detail_"): await detail_netflix(update, int(data[10:]))
    elif data.startswith("nf_profil_"): await kelola_profil(update, int(data[10:]))
    elif data.startswith("nf_hapus_konfirm_"):
        nid = int(data[17:])
        n = nf_get(nid)
        kb = [[
            InlineKeyboardButton("✅ Ya, Hapus", callback_data=f"nf_hapus_{nid}"),
            InlineKeyboardButton("❌ Batal", callback_data=f"nf_detail_{nid}"),
        ]]
        await query.edit_message_text(
            f"⚠️ *Yakin hapus akun ini?*\n\n📧 {n['email']}\n_Semua profil ikut terhapus!_",
            parse_mode='Markdown', reply_markup=InlineKeyboardMarkup(kb)
        )
    elif data.startswith("nf_hapus_"):
        nid = int(data[9:])
        n = nf_get(nid)
        nf_delete(nid)
        kb = [[InlineKeyboardButton("« Menu Utama", callback_data="start_menu")]]
        await query.edit_message_text(f"✅ Akun *{n['email']}* berhasil dihapus.", parse_mode='Markdown', reply_markup=InlineKeyboardMarkup(kb))
    elif data.startswith("nf_hapus_profil_konfirm_"):
        pid = int(data[24:])
        p = profil_get(pid)
        kb = [[
            InlineKeyboardButton("✅ Ya, Hapus", callback_data=f"nf_hapus_profil_{pid}"),
            InlineKeyboardButton("❌ Batal", callback_data=f"nf_profil_{p['netflix_id']}"),
        ]]
        await query.edit_message_text(f"⚠️ *Yakin hapus profil {p['nama']}?*", parse_mode='Markdown', reply_markup=InlineKeyboardMarkup(kb))
    elif data.startswith("nf_hapus_profil_"):
        pid = int(data[16:])
        p = profil_get(pid)
        nid = p['netflix_id']
        profil_delete(pid)
        await kelola_profil(update, nid)

async def list_netflix(update, status):
    query = update.callback_query
    list_n = nf_all(status)
    label = "Aktif" if status == "aktif" else "Expired" if status == "expired" else "Semua"

    teks = f"🎬 *Netflix — {label}* ({len(list_n)} akun)\n━━━━━━━━━━━━━━━━━━━━\n\n"
    kb = []

    if not list_n:
        teks += "❌ Belum ada akun Netflix."
    else:
        for n in list_n:
            profil = profil_all(n['id'])
            aktif = sum(1 for p in profil if sisa_hari(p.get('expired','')) >= 0)
            expired = len(profil) - aktif
            icon = "🟢" if expired == 0 else "🟡" if aktif > 0 else "🔴"
            teks += f"{icon} `{n['email']}`\n   👥 {aktif} aktif · {expired} expired\n\n"
            kb.append([InlineKeyboardButton(f"🎬 {n['email']}", callback_data=f"nf_detail_{n['id']}")])

    kb.append([
        InlineKeyboardButton("🟢 Aktif", callback_data="nf_list_aktif"),
        InlineKeyboardButton("🔴 Expired", callback_data="nf_list_expired"),
        InlineKeyboardButton("📋 Semua", callback_data="nf_list_semua"),
    ])
    kb.append([
        InlineKeyboardButton("➕ Tambah Akun", callback_data="tambah_netflix"),
        InlineKeyboardButton("« Menu", callback_data="start_menu"),
    ])
    await query.edit_message_text(teks, parse_mode='Markdown', reply_markup=InlineKeyboardMarkup(kb))

async def detail_netflix(update, nid):
    query = update.callback_query
    n = nf_get(nid)
    if not n:
        await query.edit_message_text("❌ Data tidak ditemukan.")
        return

    profil = profil_all(nid)
    teks = (
        f"🎬 *Detail Akun Netflix*\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"📧 *Email      :* `{n['email']}`\n"
        f"🔑 *Password   :* `{n['password'] or '-'}`\n"
        f"📅 *Ubah PW    :* {n['tgl_ubah_pw'] or '-'}\n"
        f"💳 *Metode     :* {n['metode_bayar'] or '-'}\n"
        f"📝 *Catatan    :* {n['catatan'] or '-'}\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"👥 *Profil ({len(profil)}/5):*\n\n"
    )

    for p in profil:
        sisa = sisa_hari(p.get('expired',''))
        icon = status_icon(sisa)
        expired_str = f"{format_tgl(p['expired'])} *({sisa} hr)*" if p.get('expired') else "✅ Aktif"
        teks += f"{icon} *{p['nomor']}. {p['nama']}*\n"
        teks += f"   📌 PIN: `{p['pin'] or '-'}` · ⏰ {expired_str}\n\n"

    kb = [
        [InlineKeyboardButton("👥 Kelola Profil", callback_data=f"nf_profil_{nid}")],
        [
            InlineKeyboardButton("✏️ Edit", callback_data=f"edit_nf_{nid}"),
            InlineKeyboardButton("🔄 Perpanjang", callback_data=f"perp_nf_{nid}"),
        ],
        [
            InlineKeyboardButton("🗑️ Hapus Akun", callback_data=f"nf_hapus_konfirm_{nid}"),
            InlineKeyboardButton("« Kembali", callback_data="menu_netflix"),
        ],
    ]
    await query.edit_message_text(teks, parse_mode='Markdown', reply_markup=InlineKeyboardMarkup(kb))

async def kelola_profil(update, nid):
    query = update.callback_query
    n = nf_get(nid)
    profil = profil_all(nid)

    teks = (
        f"👥 *Kelola Profil Netflix*\n"
        f"📧 {n['email']}\n"
        f"━━━━━━━━━━━━━━━━━━━━\n\n"
    )

    kb = []
    for p in profil:
        sisa = sisa_hari(p.get('expired',''))
        icon = status_icon(sisa)
        expired_str = f"{format_tgl(p['expired'])} ({sisa}hr)" if p.get('expired') else "Aktif"
        teks += f"{icon} *{p['nomor']}. {p['nama']}* | PIN: `{p['pin'] or '-'}`\n   ⏰ {expired_str}\n\n"
        kb.append([
            InlineKeyboardButton(f"✏️ Edit {p['nomor']}. {p['nama']}", callback_data=f"edit_profil_{p['id']}"),
            InlineKeyboardButton("🗑️", callback_data=f"nf_hapus_profil_konfirm_{p['id']}"),
        ])

    slot_tersisa = 5 - len(profil)
    if slot_tersisa > 0:
        kb.append([
            InlineKeyboardButton("➕ Tambah 1 Profil", callback_data=f"tambah_profil_{nid}"),
            InlineKeyboardButton("📋 Bulk Tambah", callback_data=f"bulk_profil_{nid}"),
        ])
    kb.append([InlineKeyboardButton("« Kembali", callback_data=f"nf_detail_{nid}")])

    await query.edit_message_text(teks or "Belum ada profil.", parse_mode='Markdown', reply_markup=InlineKeyboardMarkup(kb))
