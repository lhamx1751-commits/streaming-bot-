from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from database import *
from utils import sisa_hari, format_tgl, status_icon, format_rp


async def youtube_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data

    if data == "menu_youtube":
        await tampil_list_youtube(update)
    elif data.startswith("yt_detail_"):
        await tampil_detail_youtube(update, int(data[10:]))
    elif data.startswith("yt_member_"):
        await tampil_member(update, int(data[10:]))
    elif data.startswith("yt_hapus_member_"):
        mid = int(data[16:])
        from database import get_conn
        conn = get_conn()
        c = conn.cursor()
        c.execute("SELECT youtube_id FROM youtube_member WHERE id=?", (mid,))
        row = c.fetchone()
        conn.close()
        yid = row['youtube_id'] if row else 0
        member_hapus(mid)
        kb = [[InlineKeyboardButton("« Kembali", callback_data=f"yt_member_{yid}")]]
        await query.edit_message_text("✅ Member berhasil dihapus.", reply_markup=InlineKeyboardMarkup(kb))
    elif data.startswith("yt_hapus_konfirm_"):
        yid = int(data[17:])
        y = yt_get(yid)
        kb = [[
            InlineKeyboardButton("✅ Ya, Hapus", callback_data=f"yt_hapus_{yid}"),
            InlineKeyboardButton("❌ Batal", callback_data=f"yt_detail_{yid}"),
        ]]
        await query.edit_message_text(
            f"⚠️ *Yakin hapus akun YouTube ini?*\n\n📧 {y['email_akun']}",
            parse_mode='Markdown', reply_markup=InlineKeyboardMarkup(kb)
        )
    elif data.startswith("yt_hapus_"):
        yid = int(data[9:])
        yt_hapus(yid)
        kb = [[InlineKeyboardButton("« Menu Utama", callback_data="start_menu")]]
        await query.edit_message_text("✅ Akun YouTube berhasil dihapus.", reply_markup=InlineKeyboardMarkup(kb))


async def tampil_list_youtube(update):
    query = update.callback_query
    list_y = yt_get_all()

    if not list_y:
        kb = [
            [InlineKeyboardButton("➕ Tambah Akun YouTube", callback_data="tambah_youtube")],
            [InlineKeyboardButton("« Menu Utama", callback_data="start_menu")],
        ]
        await query.edit_message_text(
            "📺 *YouTube Family*\n\n❌ Belum ada akun YouTube.",
            parse_mode='Markdown', reply_markup=InlineKeyboardMarkup(kb)
        )
        return

    teks = f"📺 *Daftar Akun YouTube Family* ({len(list_y)} akun)\n━━━━━━━━━━━━━━━━━━━━\n\n"
    kb = []
    for y in list_y:
        sisa = sisa_hari(y['expired_langganan'])
        icon = status_icon(sisa)
        members = member_get_all(y['id'])
        teks += f"{icon} `{y['email_akun']}` — {len(members)}/5 member ({sisa}hr)\n"
        kb.append([InlineKeyboardButton(f"📺 {y['email_akun']}", callback_data=f"yt_detail_{y['id']}")])

    kb.append([InlineKeyboardButton("➕ Tambah Akun", callback_data="tambah_youtube")])
    kb.append([InlineKeyboardButton("« Menu Utama", callback_data="start_menu")])
    await query.edit_message_text(teks, parse_mode='Markdown', reply_markup=InlineKeyboardMarkup(kb))


async def tampil_detail_youtube(update, yid):
    query = update.callback_query
    y = yt_get(yid)
    if not y:
        await query.edit_message_text("❌ Data tidak ditemukan.")
        return

    members = member_get_all(yid)
    sisa = sisa_hari(y['expired_langganan'])
    icon = status_icon(sisa)

    teks = (
        f"📺 *Detail Akun YouTube Family*\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"📧 *Email Akun  :* `{y['email_akun']}`\n"
        f"🔑 *Password    :* `{y['password'] or '-'}`\n"
        f"⏰ *Expired     :* {format_tgl(y['expired_langganan'])}\n"
        f"{icon} *Sisa        :* {sisa} hari\n"
        f"💰 *Harga       :* {format_rp(y['harga'])}\n"
        f"📝 *Catatan     :* {y['catatan'] or '-'}\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"👥 *Member ({len(members)}/5):*\n\n"
    )

    for i, m in enumerate(members, 1):
        teks += (
            f"  {i}. 📧 `{m['email_pembeli']}`\n"
            f"     👤 {m['nama_pelanggan'] or '-'} | 📱 {m['no_hp'] or '-'}\n\n"
        )

    kb = [
        [InlineKeyboardButton("👥 Kelola Member", callback_data=f"yt_member_{yid}")],
        [
            InlineKeyboardButton("🗑️ Hapus Akun", callback_data=f"yt_hapus_konfirm_{yid}"),
            InlineKeyboardButton("« Kembali", callback_data="menu_youtube"),
        ],
    ]
    await query.edit_message_text(teks, parse_mode='Markdown', reply_markup=InlineKeyboardMarkup(kb))


async def tampil_member(update, yid):
    query = update.callback_query
    y = yt_get(yid)
    members = member_get_all(yid)

    teks = (
        f"👥 *Kelola Member YouTube*\n"
        f"📧 {y['email_akun']}\n"
        f"━━━━━━━━━━━━━━━━━━━━\n\n"
    )

    kb = []
    for m in members:
        teks += f"📧 `{m['email_pembeli']}` — {m['nama_pelanggan'] or '-'}\n"
        kb.append([InlineKeyboardButton(
            f"🗑️ Hapus {m['email_pembeli']}",
            callback_data=f"yt_hapus_member_{m['id']}"
        )])

    if len(members) < 5:
        kb.append([InlineKeyboardButton("➕ Tambah Member", callback_data=f"tambah_member_{yid}")])
    kb.append([InlineKeyboardButton("« Kembali", callback_data=f"yt_detail_{yid}")])

    await query.edit_message_text(
        teks or "Belum ada member.",
        parse_mode='Markdown',
        reply_markup=InlineKeyboardMarkup(kb)
    )
