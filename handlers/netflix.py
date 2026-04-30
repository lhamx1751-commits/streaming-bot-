from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from database import *
from utils import sisa_hari, format_tgl, status_icon, format_rp


async def netflix_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data

    if data == "menu_netflix":
        await tampil_list_netflix(update)
    elif data.startswith("nf_detail_"):
        await tampil_detail_netflix(update, int(data[10:]))
    elif data.startswith("nf_profil_"):
        await tampil_profil(update, int(data[10:]))
    elif data.startswith("nf_hapus_konfirm_"):
        nid = int(data[17:])
        n = netflix_get(nid)
        kb = [[
            InlineKeyboardButton("✅ Ya, Hapus", callback_data=f"nf_hapus_{nid}"),
            InlineKeyboardButton("❌ Batal", callback_data=f"nf_detail_{nid}"),
        ]]
        await query.edit_message_text(
            f"⚠️ *Yakin hapus akun Netflix ini?*\n\n📧 {n['email']}\n\nSemua profil juga akan terhapus!",
            parse_mode='Markdown', reply_markup=InlineKeyboardMarkup(kb)
        )
    elif data.startswith("nf_hapus_"):
        nid = int(data[9:])
        netflix_hapus(nid)
        kb = [[InlineKeyboardButton("« Menu Utama", callback_data="start_menu")]]
        await query.edit_message_text("✅ Akun Netflix berhasil dihapus.", reply_markup=InlineKeyboardMarkup(kb))
    elif data.startswith("nf_hapus_profil_"):
        pid = int(data[16:])
        p = profil_get(pid)
        profil_hapus(pid)
        kb = [[InlineKeyboardButton("« Kembali", callback_data=f"nf_profil_{p['netflix_id']}")]]
        await query.edit_message_text("✅ Profil berhasil dihapus.", reply_markup=InlineKeyboardMarkup(kb))


async def tampil_list_netflix(update):
    query = update.callback_query
    list_n = netflix_get_all()

    if not list_n:
        kb = [
            [InlineKeyboardButton("➕ Tambah Akun Netflix", callback_data="tambah_netflix")],
            [InlineKeyboardButton("« Menu Utama", callback_data="start_menu")],
        ]
        await query.edit_message_text(
            "🎬 *Netflix Premium*\n\n❌ Belum ada akun Netflix.",
            parse_mode='Markdown', reply_markup=InlineKeyboardMarkup(kb)
        )
        return

    teks = f"🎬 *Daftar Akun Netflix* ({len(list_n)} akun)\n━━━━━━━━━━━━━━━━━━━━\n\n"
    kb = []
    for n in list_n:
        profil_list = profil_get_all(n['id'])
        teks += f"📧 `{n['email']}` — {len(profil_list)} profil\n"
        kb.append([InlineKeyboardButton(f"🎬 {n['email']}", callback_data=f"nf_detail_{n['id']}")])

    kb.append([InlineKeyboardButton("➕ Tambah Akun", callback_data="tambah_netflix")])
    kb.append([InlineKeyboardButton("« Menu Utama", callback_data="start_menu")])
    await query.edit_message_text(teks, parse_mode='Markdown', reply_markup=InlineKeyboardMarkup(kb))


async def tampil_detail_netflix(update, nid):
    query = update.callback_query
    n = netflix_get(nid)
    if not n:
        await query.edit_message_text("❌ Data tidak ditemukan.")
        return

    profil_list = profil_get_all(nid)

    teks = (
        f"🎬 *Detail Akun Netflix*\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"📧 *Email  :* `{n['email']}`\n"
        f"🔑 *Password :* `{n['password']}`\n"
        f"💳 *Metode Bayar :* {n['metode_bayar']}\n"
        f"📅 *Expired Akun :* {format_tgl(n['expired_akun']) if n['expired_akun'] else '-'}\n"
        f"📝 *Catatan :* {n['catatan'] or '-'}\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"👥 *Profil ({len(profil_list)}/5):*\n\n"
    )

    for p in profil_list:
        sisa = sisa_hari(p['expired'])
        icon = status_icon(sisa)
        teks += (
            f"{icon} *Profil {p['nomor_profil']}* — {p['nama_profil'] or 'Tanpa nama'}\n"
            f"   👤 {p['nama_pelanggan'] or '-'} | 📱 {p['no_hp'] or '-'}\n"
            f"   ⏰ {format_tgl(p['expired'])} ({sisa} hari)\n"
            f"   💰 {format_rp(p['harga'])}\n\n"
        )

    kb = [
        [InlineKeyboardButton("👥 Kelola Profil", callback_data=f"nf_profil_{nid}")],
        [
            InlineKeyboardButton("🗑️ Hapus Akun", callback_data=f"nf_hapus_konfirm_{nid}"),
            InlineKeyboardButton("« Kembali", callback_data="menu_netflix"),
        ],
    ]
    await query.edit_message_text(teks, parse_mode='Markdown', reply_markup=InlineKeyboardMarkup(kb))


async def tampil_profil(update, nid):
    query = update.callback_query
    profil_list = profil_get_all(nid)
    n = netflix_get(nid)

    teks = (
        f"👥 *Kelola Profil Netflix*\n"
        f"📧 {n['email']}\n"
        f"━━━━━━━━━━━━━━━━━━━━\n\n"
    )

    kb = []
    for p in profil_list:
        sisa = sisa_hari(p['expired'])
        icon = status_icon(sisa)
        label = f"{icon} Profil {p['nomor_profil']} — {p['nama_pelanggan'] or '-'} ({sisa}hr)"
        teks += f"{label}\n"
        kb.append([InlineKeyboardButton(
            f"🗑️ Hapus Profil {p['nomor_profil']}",
            callback_data=f"nf_hapus_profil_{p['id']}"
        )])

    if len(profil_list) < 5:
        kb.append([InlineKeyboardButton("➕ Tambah Profil", callback_data=f"tambah_profil_{nid}")])

    kb.append([InlineKeyboardButton("« Kembali", callback_data=f"nf_detail_{nid}")])

    await query.edit_message_text(
        teks or "Belum ada profil.",
        parse_mode='Markdown',
        reply_markup=InlineKeyboardMarkup(kb)
    )
