from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, ConversationHandler, CommandHandler, MessageHandler, filters, CallbackQueryHandler
from database import nf_add, nf_update, nf_get, profil_add, profil_update, profil_get, profil_all
from database import ds_add, ds_update, ds_get, perangkat_add, perangkat_update, perangkat_get
from database import yt_add, yt_update, yt_get
from utils import validasi_tgl, format_tgl

# ── STATES ───────────────────────────────────────────────
NF_EMAIL, NF_PASS, NF_UBAH_PW, NF_CATATAN = range(4)
PR_NOMOR, PR_NAMA, PR_PIN, PR_EXPIRED = range(10, 14)
EDIT_NF_FIELD, EDIT_NF_VAL = range(20, 22)
EDIT_PR_FIELD, EDIT_PR_VAL = range(22, 24)
PERP_NF_TGL = 24

DS_HP, DS_EMAIL, DS_PASS, DS_PAKET, DS_EXPIRED, DS_CATATAN = range(30, 36)
PG_NAMA, PG_EXPIRED = range(36, 38)
EDIT_DS_FIELD, EDIT_DS_VAL = range(38, 40)
EDIT_PG_FIELD, EDIT_PG_VAL = range(40, 42)
PERP_DS_TGL = 42

YT_EMAIL, YT_PASS, YT_EXPIRED, YT_CATATAN = range(50, 54)
EDIT_YT_FIELD, EDIT_YT_VAL = range(54, 56)
PERP_YT_TGL = 56

CARI_INPUT = 60

async def batal(update, context):
    context.user_data.clear()
    await update.message.reply_text("❌ Dibatalkan. Ketik /start untuk menu.", reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END

# ══ NETFLIX ═══════════════════════════════════════════════

def conv_tambah_netflix():
    return ConversationHandler(
        entry_points=[CallbackQueryHandler(nf_mulai, pattern="^tambah_netflix$")],
        states={
            NF_EMAIL: [MessageHandler(filters.TEXT & ~filters.COMMAND, nf_email)],
            NF_PASS: [MessageHandler(filters.TEXT & ~filters.COMMAND, nf_pass)],
            NF_UBAH_PW: [MessageHandler(filters.TEXT & ~filters.COMMAND, nf_ubah_pw)],
            NF_CATATAN: [MessageHandler(filters.TEXT & ~filters.COMMAND, nf_catatan)],
        },
        fallbacks=[CommandHandler("batal", batal)],
        name="tambah_nf", persistent=False,
    )

async def nf_mulai(update, context):
    await update.callback_query.answer()
    context.user_data.clear()
    await update.callback_query.message.reply_text(
        "🎬 *Tambah Akun Netflix*\n/batal untuk cancel\n\n*1/4* — Masukkan *email Netflix*:",
        parse_mode='Markdown', reply_markup=ReplyKeyboardRemove()
    )
    return NF_EMAIL

async def nf_email(update, context):
    context.user_data['email'] = update.message.text.strip()
    await update.message.reply_text("*2/4* — Masukkan *password*:", parse_mode='Markdown')
    return NF_PASS

async def nf_pass(update, context):
    context.user_data['password'] = update.message.text.strip()
    await update.message.reply_text("*3/4* — *Tanggal ubah password* terakhir:\n_(contoh: 6 April 2026, atau '-')_", parse_mode='Markdown')
    return NF_UBAH_PW

async def nf_ubah_pw(update, context):
    context.user_data['tgl_ubah_pw'] = update.message.text.strip()
    await update.message.reply_text("*4/4* — *Catatan* tambahan:\n_(ketik '-' jika tidak ada)_", parse_mode='Markdown')
    return NF_CATATAN

async def nf_catatan(update, context):
    context.user_data['catatan'] = update.message.text.strip()
    nid = nf_add(context.user_data)
    await update.message.reply_text(
        f"✅ *Akun Netflix berhasil ditambahkan!*\n\n📧 {context.user_data['email']}\nID: #{nid}\n\nSekarang tambahkan profil dengan /start → Netflix → Kelola Profil",
        parse_mode='Markdown', reply_markup=ReplyKeyboardRemove()
    )
    context.user_data.clear()
    return ConversationHandler.END

# ── TAMBAH PROFIL ─────────────────────────────────────────

def conv_tambah_profil():
    return ConversationHandler(
        entry_points=[CallbackQueryHandler(pr_mulai, pattern="^tambah_profil_")],
        states={
            PR_NOMOR: [MessageHandler(filters.TEXT & ~filters.COMMAND, pr_nomor)],
            PR_NAMA: [MessageHandler(filters.TEXT & ~filters.COMMAND, pr_nama)],
            PR_PIN: [MessageHandler(filters.TEXT & ~filters.COMMAND, pr_pin)],
            PR_EXPIRED: [MessageHandler(filters.TEXT & ~filters.COMMAND, pr_expired)],
        },
        fallbacks=[CommandHandler("batal", batal)],
        name="tambah_profil", persistent=False,
    )

async def pr_mulai(update, context):
    await update.callback_query.answer()
    nid = int(update.callback_query.data.split("_")[2])
    context.user_data.clear()
    context.user_data['netflix_id'] = nid
    profil = profil_all(nid)
    nomor_ada = [p['nomor'] for p in profil]
    nomor_tersedia = [str(i) for i in range(1,6) if i not in nomor_ada]
    kb = ReplyKeyboardMarkup([nomor_tersedia], one_time_keyboard=True, resize_keyboard=True)
    await update.callback_query.message.reply_text(
        "👥 *Tambah Profil Netflix*\n/batal untuk cancel\n\n*1/4* — Pilih *nomor profil*:",
        parse_mode='Markdown', reply_markup=kb
    )
    return PR_NOMOR

async def pr_nomor(update, context):
    try:
        context.user_data['nomor'] = int(update.message.text.strip())
    except:
        await update.message.reply_text("❌ Masukkan angka 1-5")
        return PR_NOMOR
    await update.message.reply_text("*2/4* — *Nama profil*:\n_(contoh: Dyah)_", parse_mode='Markdown', reply_markup=ReplyKeyboardRemove())
    return PR_NAMA

async def pr_nama(update, context):
    context.user_data['nama'] = update.message.text.strip()
    await update.message.reply_text("*3/4* — *PIN profil*:\n_(contoh: 1111, atau '-')_", parse_mode='Markdown')
    return PR_PIN

async def pr_pin(update, context):
    context.user_data['pin'] = update.message.text.strip()
    await update.message.reply_text("*4/4* — *Tanggal expired* profil ini:\n_(DD-MM-YYYY atau '-' jika aktif)_", parse_mode='Markdown')
    return PR_EXPIRED

async def pr_expired(update, context):
    tgl = update.message.text.strip()
    if tgl != '-':
        tgl_db = validasi_tgl(tgl)
        if not tgl_db:
            await update.message.reply_text("❌ Format salah! DD-MM-YYYY")
            return PR_EXPIRED
        context.user_data['expired'] = tgl_db
    else:
        context.user_data['expired'] = ''
    profil_add(context.user_data)
    await update.message.reply_text(
        f"✅ *Profil {context.user_data['nomor']} — {context.user_data['nama']} berhasil ditambahkan!*\n\nKetik /start untuk kembali.",
        parse_mode='Markdown', reply_markup=ReplyKeyboardRemove()
    )
    context.user_data.clear()
    return ConversationHandler.END

# ── EDIT NETFLIX ──────────────────────────────────────────

def conv_edit_netflix():
    return ConversationHandler(
        entry_points=[CallbackQueryHandler(edit_nf_mulai, pattern="^edit_nf_")],
        states={
            EDIT_NF_FIELD: [MessageHandler(filters.TEXT & ~filters.COMMAND, edit_nf_field)],
            EDIT_NF_VAL: [MessageHandler(filters.TEXT & ~filters.COMMAND, edit_nf_val)],
        },
        fallbacks=[CommandHandler("batal", batal)],
        name="edit_nf", persistent=False,
    )

async def edit_nf_mulai(update, context):
    await update.callback_query.answer()
    nid = int(update.callback_query.data.split("_")[2])
    n = nf_get(nid)
    context.user_data.clear()
    context.user_data['edit_id'] = nid
    context.user_data['edit_type'] = 'netflix'
    kb = ReplyKeyboardMarkup([["📧 Email","🔑 Password"],["📅 Ubah PW","📝 Catatan"]], one_time_keyboard=True, resize_keyboard=True)
    await update.callback_query.message.reply_text(
        f"✏️ *Edit Akun Netflix*\n📧 {n['email']}\n\nPilih yang mau diedit:",
        parse_mode='Markdown', reply_markup=kb
    )
    return EDIT_NF_FIELD

FIELD_MAP_NF = {"📧 email": "email","🔑 password": "password","📅 ubah pw": "tgl_ubah_pw","📝 catatan": "catatan"}

async def edit_nf_field(update, context):
    field = update.message.text.strip().lower()
    db_field = FIELD_MAP_NF.get(field)
    if not db_field:
        await update.message.reply_text("❌ Pilih dari tombol.")
        return EDIT_NF_FIELD
    context.user_data['edit_field'] = db_field
    await update.message.reply_text(f"Masukkan nilai baru untuk *{field}*:", parse_mode='Markdown', reply_markup=ReplyKeyboardRemove())
    return EDIT_NF_VAL

async def edit_nf_val(update, context):
    nf_update(context.user_data['edit_id'], {context.user_data['edit_field']: update.message.text.strip()})
    await update.message.reply_text("✅ Berhasil diupdate! Ketik /start untuk kembali.")
    context.user_data.clear()
    return ConversationHandler.END

# ── EDIT PROFIL ───────────────────────────────────────────

def conv_edit_profil():
    return ConversationHandler(
        entry_points=[CallbackQueryHandler(edit_pr_mulai, pattern="^edit_profil_")],
        states={
            EDIT_PR_FIELD: [MessageHandler(filters.TEXT & ~filters.COMMAND, edit_pr_field)],
            EDIT_PR_VAL: [MessageHandler(filters.TEXT & ~filters.COMMAND, edit_pr_val)],
        },
        fallbacks=[CommandHandler("batal", batal)],
        name="edit_profil", persistent=False,
    )

async def edit_pr_mulai(update, context):
    await update.callback_query.answer()
    pid = int(update.callback_query.data.split("_")[2])
    p = profil_get(pid)
    context.user_data.clear()
    context.user_data['edit_id'] = pid
    kb = ReplyKeyboardMarkup([["👤 Nama","📌 PIN"],["⏰ Expired"]], one_time_keyboard=True, resize_keyboard=True)
    await update.callback_query.message.reply_text(
        f"✏️ *Edit Profil {p['nomor']} — {p['nama']}*\n\nPilih yang mau diedit:",
        parse_mode='Markdown', reply_markup=kb
    )
    return EDIT_PR_FIELD

FIELD_MAP_PR = {"👤 nama":"nama","📌 pin":"pin","⏰ expired":"expired"}

async def edit_pr_field(update, context):
    field = update.message.text.strip().lower()
    db_field = FIELD_MAP_PR.get(field)
    if not db_field:
        await update.message.reply_text("❌ Pilih dari tombol.")
        return EDIT_PR_FIELD
    context.user_data['edit_field'] = db_field
    await update.message.reply_text(f"Masukkan nilai baru:\n_(untuk expired gunakan DD-MM-YYYY)_", parse_mode='Markdown', reply_markup=ReplyKeyboardRemove())
    return EDIT_PR_VAL

async def edit_pr_val(update, context):
    value = update.message.text.strip()
    if context.user_data['edit_field'] == 'expired':
        tgl = validasi_tgl(value)
        if not tgl:
            await update.message.reply_text("❌ Format salah! DD-MM-YYYY")
            return EDIT_PR_VAL
        value = tgl
    profil_update(context.user_data['edit_id'], {context.user_data['edit_field']: value})
    await update.message.reply_text("✅ Profil berhasil diupdate! Ketik /start untuk kembali.")
    context.user_data.clear()
    return ConversationHandler.END

# ── PERPANJANG NETFLIX ────────────────────────────────────

def conv_perp_netflix():
    return ConversationHandler(
        entry_points=[CallbackQueryHandler(perp_nf_mulai, pattern="^perp_nf_")],
        states={PERP_NF_TGL: [MessageHandler(filters.TEXT & ~filters.COMMAND, perp_nf_tgl)]},
        fallbacks=[CommandHandler("batal", batal)],
        name="perp_nf", persistent=False,
    )

async def perp_nf_mulai(update, context):
    await update.callback_query.answer()
    nid = int(update.callback_query.data.split("_")[2])
    context.user_data.clear()
    context.user_data['perp_id'] = nid
    context.user_data['perp_type'] = 'netflix'
    await update.callback_query.message.reply_text(
        "🔄 *Perpanjang Netflix*\n\nMasukkan *tanggal expired baru profil*:\n_(DD-MM-YYYY)_\n\n_Catatan: ini update expired untuk semua profil_",
        parse_mode='Markdown', reply_markup=ReplyKeyboardRemove()
    )
    return PERP_NF_TGL

async def perp_nf_tgl(update, context):
    tgl = validasi_tgl(update.message.text.strip())
    if not tgl:
        await update.message.reply_text("❌ Format salah! DD-MM-YYYY")
        return PERP_NF_TGL
    nid = context.user_data['perp_id']
    from database import profil_all as pa, profil_update as pu
    for p in pa(nid):
        pu(p['id'], {'expired': tgl})
    await update.message.reply_text(
        f"✅ *Semua profil berhasil diperpanjang!*\n\n⏰ Expired baru: {format_tgl(tgl)}\n\nKetik /start untuk kembali.",
        parse_mode='Markdown'
    )
    context.user_data.clear()
    return ConversationHandler.END

# ══ DISNEY+ ═══════════════════════════════════════════════

def conv_tambah_disney():
    return ConversationHandler(
        entry_points=[CallbackQueryHandler(ds_mulai, pattern="^tambah_disney$")],
        states={
            DS_PAKET: [MessageHandler(filters.TEXT & ~filters.COMMAND, ds_paket)],
            DS_HP: [MessageHandler(filters.TEXT & ~filters.COMMAND, ds_hp)],
            DS_EMAIL: [MessageHandler(filters.TEXT & ~filters.COMMAND, ds_email)],
            DS_PASS: [MessageHandler(filters.TEXT & ~filters.COMMAND, ds_pass)],
            DS_EXPIRED: [MessageHandler(filters.TEXT & ~filters.COMMAND, ds_expired)],
            DS_CATATAN: [MessageHandler(filters.TEXT & ~filters.COMMAND, ds_catatan)],
        },
        fallbacks=[CommandHandler("batal", batal)],
        name="tambah_ds", persistent=False,
    )

async def ds_mulai(update, context):
    await update.callback_query.answer()
    context.user_data.clear()
    kb = ReplyKeyboardMarkup([["DISNEY 1 BULAN SHARING"],["DISNEY 3 BULAN SHARING"]], one_time_keyboard=True, resize_keyboard=True)
    await update.callback_query.message.reply_text(
        "🏰 *Tambah Akun Disney+*\n/batal untuk cancel\n\n*1/6* — Pilih *nama paket*:",
        parse_mode='Markdown', reply_markup=kb
    )
    return DS_PAKET

async def ds_paket(update, context):
    context.user_data['nama_paket'] = update.message.text.strip()
    await update.message.reply_text("*2/6* — *No HP* pemilik akun:\n_(ketik '-' jika tidak ada)_", parse_mode='Markdown', reply_markup=ReplyKeyboardRemove())
    return DS_HP

async def ds_hp(update, context):
    context.user_data['no_hp'] = update.message.text.strip()
    await update.message.reply_text("*3/6* — *Email* akun Disney+:", parse_mode='Markdown')
    return DS_EMAIL

async def ds_email(update, context):
    context.user_data['email'] = update.message.text.strip()
    await update.message.reply_text("*4/6* — *Password* akun:\n_(ketik '-' jika tidak ada)_", parse_mode='Markdown')
    return DS_PASS

async def ds_pass(update, context):
    context.user_data['password'] = update.message.text.strip()
    await update.message.reply_text("*5/6* — *Expired langganan*:\n_(DD-MM-YYYY)_", parse_mode='Markdown')
    return DS_EXPIRED

async def ds_expired(update, context):
    tgl = validasi_tgl(update.message.text.strip())
    if not tgl:
        await update.message.reply_text("❌ Format salah! DD-MM-YYYY")
        return DS_EXPIRED
    context.user_data['expired_langganan'] = tgl
    await update.message.reply_text("*6/6* — *Catatan*:\n_(ketik '-' jika tidak ada)_", parse_mode='Markdown')
    return DS_CATATAN

async def ds_catatan(update, context):
    context.user_data['catatan'] = update.message.text.strip()
    did = ds_add(context.user_data)
    await update.message.reply_text(
        f"✅ *Akun Disney+ berhasil ditambahkan!*\n\n📧 {context.user_data['email']}\n⏰ {format_tgl(context.user_data['expired_langganan'])}\nID: #{did}\n\nSekarang tambahkan perangkat via /start → Disney+",
        parse_mode='Markdown', reply_markup=ReplyKeyboardRemove()
    )
    context.user_data.clear()
    return ConversationHandler.END

# ── TAMBAH PERANGKAT ──────────────────────────────────────

def conv_tambah_perangkat():
    return ConversationHandler(
        entry_points=[CallbackQueryHandler(pg_mulai, pattern="^tambah_perangkat_")],
        states={
            PG_NAMA: [MessageHandler(filters.TEXT & ~filters.COMMAND, pg_nama)],
            PG_EXPIRED: [MessageHandler(filters.TEXT & ~filters.COMMAND, pg_expired)],
        },
        fallbacks=[CommandHandler("batal", batal)],
        name="tambah_pg", persistent=False,
    )

async def pg_mulai(update, context):
    await update.callback_query.answer()
    did = int(update.callback_query.data.split("_")[2])
    context.user_data.clear()
    context.user_data['disney_id'] = did
    await update.callback_query.message.reply_text(
        "📱 *Tambah Perangkat Disney+*\n/batal untuk cancel\n\n*1/2* — *Nama perangkat*:\n_(contoh: Oppo phone, Samsung TV)_",
        parse_mode='Markdown', reply_markup=ReplyKeyboardRemove()
    )
    return PG_NAMA

async def pg_nama(update, context):
    context.user_data['nama'] = update.message.text.strip()
    await update.message.reply_text("*2/2* — *Tanggal expired* perangkat:\n_(DD-MM-YYYY atau '-')_", parse_mode='Markdown')
    return PG_EXPIRED

async def pg_expired(update, context):
    tgl = update.message.text.strip()
    if tgl != '-':
        tgl_db = validasi_tgl(tgl)
        context.user_data['expired'] = tgl_db or ''
    else:
        context.user_data['expired'] = ''
    perangkat_add(context.user_data)
    await update.message.reply_text(
        f"✅ *Perangkat {context.user_data['nama']} berhasil ditambahkan!*\n\nKetik /start untuk kembali.",
        parse_mode='Markdown', reply_markup=ReplyKeyboardRemove()
    )
    context.user_data.clear()
    return ConversationHandler.END

# ── EDIT DISNEY ───────────────────────────────────────────

def conv_edit_disney():
    return ConversationHandler(
        entry_points=[CallbackQueryHandler(edit_ds_mulai, pattern="^edit_ds_")],
        states={
            EDIT_DS_FIELD: [MessageHandler(filters.TEXT & ~filters.COMMAND, edit_ds_field)],
            EDIT_DS_VAL: [MessageHandler(filters.TEXT & ~filters.COMMAND, edit_ds_val)],
        },
        fallbacks=[CommandHandler("batal", batal)],
        name="edit_ds", persistent=False,
    )

async def edit_ds_mulai(update, context):
    await update.callback_query.answer()
    did = int(update.callback_query.data.split("_")[2])
    d = ds_get(did)
    context.user_data.clear()
    context.user_data['edit_id'] = did
    kb = ReplyKeyboardMarkup([["📱 HP","📧 Email"],["🔑 Password","⏰ Expired"],["📦 Paket","📝 Catatan"]], one_time_keyboard=True, resize_keyboard=True)
    await update.callback_query.message.reply_text(
        f"✏️ *Edit Akun Disney+*\n📧 {d['email']}\n\nPilih yang mau diedit:",
        parse_mode='Markdown', reply_markup=kb
    )
    return EDIT_DS_FIELD

FIELD_MAP_DS = {"📱 hp":"no_hp","📧 email":"email","🔑 password":"password","⏰ expired":"expired_langganan","📦 paket":"nama_paket","📝 catatan":"catatan"}

async def edit_ds_field(update, context):
    field = update.message.text.strip().lower()
    db_field = FIELD_MAP_DS.get(field)
    if not db_field:
        await update.message.reply_text("❌ Pilih dari tombol.")
        return EDIT_DS_FIELD
    context.user_data['edit_field'] = db_field
    await update.message.reply_text(f"Masukkan nilai baru:", parse_mode='Markdown', reply_markup=ReplyKeyboardRemove())
    return EDIT_DS_VAL

async def edit_ds_val(update, context):
    value = update.message.text.strip()
    if context.user_data['edit_field'] == 'expired_langganan':
        tgl = validasi_tgl(value)
        if not tgl:
            await update.message.reply_text("❌ Format salah! DD-MM-YYYY")
            return EDIT_DS_VAL
        value = tgl
    ds_update(context.user_data['edit_id'], {context.user_data['edit_field']: value})
    await update.message.reply_text("✅ Berhasil diupdate! Ketik /start untuk kembali.")
    context.user_data.clear()
    return ConversationHandler.END

# ── EDIT PERANGKAT ────────────────────────────────────────

def conv_edit_perangkat():
    return ConversationHandler(
        entry_points=[CallbackQueryHandler(edit_pg_mulai, pattern="^edit_perangkat_")],
        states={
            EDIT_PG_FIELD: [MessageHandler(filters.TEXT & ~filters.COMMAND, edit_pg_field)],
            EDIT_PG_VAL: [MessageHandler(filters.TEXT & ~filters.COMMAND, edit_pg_val)],
        },
        fallbacks=[CommandHandler("batal", batal)],
        name="edit_pg", persistent=False,
    )

async def edit_pg_mulai(update, context):
    await update.callback_query.answer()
    rid = int(update.callback_query.data.split("_")[2])
    p = perangkat_get(rid)
    context.user_data.clear()
    context.user_data['edit_id'] = rid
    kb = ReplyKeyboardMarkup([["📱 Nama","⏰ Expired"]], one_time_keyboard=True, resize_keyboard=True)
    await update.callback_query.message.reply_text(
        f"✏️ *Edit Perangkat — {p['nama']}*\n\nPilih yang mau diedit:",
        parse_mode='Markdown', reply_markup=kb
    )
    return EDIT_PG_FIELD

FIELD_MAP_PG = {"📱 nama":"nama","⏰ expired":"expired"}

async def edit_pg_field(update, context):
    field = update.message.text.strip().lower()
    db_field = FIELD_MAP_PG.get(field)
    if not db_field:
        await update.message.reply_text("❌ Pilih dari tombol.")
        return EDIT_PG_FIELD
    context.user_data['edit_field'] = db_field
    await update.message.reply_text("Masukkan nilai baru:", reply_markup=ReplyKeyboardRemove())
    return EDIT_PG_VAL

async def edit_pg_val(update, context):
    value = update.message.text.strip()
    if context.user_data['edit_field'] == 'expired':
        tgl = validasi_tgl(value)
        if not tgl:
            await update.message.reply_text("❌ Format salah! DD-MM-YYYY")
            return EDIT_PG_VAL
        value = tgl
    perangkat_update(context.user_data['edit_id'], {context.user_data['edit_field']: value})
    await update.message.reply_text("✅ Perangkat berhasil diupdate! Ketik /start untuk kembali.")
    context.user_data.clear()
    return ConversationHandler.END

# ── PERPANJANG DISNEY ─────────────────────────────────────

def conv_perp_disney():
    return ConversationHandler(
        entry_points=[CallbackQueryHandler(perp_ds_mulai, pattern="^perp_ds_")],
        states={PERP_DS_TGL: [MessageHandler(filters.TEXT & ~filters.COMMAND, perp_ds_tgl)]},
        fallbacks=[CommandHandler("batal", batal)],
        name="perp_ds", persistent=False,
    )

async def perp_ds_mulai(update, context):
    await update.callback_query.answer()
    did = int(update.callback_query.data.split("_")[2])
    d = ds_get(did)
    context.user_data.clear()
    context.user_data['perp_id'] = did
    await update.callback_query.message.reply_text(
        f"🔄 *Perpanjang Disney+*\n📧 {d['email']}\nExpired sekarang: {format_tgl(d['expired_langganan'])}\n\nMasukkan *expired baru*:\n_(DD-MM-YYYY)_",
        parse_mode='Markdown', reply_markup=ReplyKeyboardRemove()
    )
    return PERP_DS_TGL

async def perp_ds_tgl(update, context):
    tgl = validasi_tgl(update.message.text.strip())
    if not tgl:
        await update.message.reply_text("❌ Format salah! DD-MM-YYYY")
        return PERP_DS_TGL
    ds_update(context.user_data['perp_id'], {'expired_langganan': tgl})
    await update.message.reply_text(
        f"✅ *Disney+ berhasil diperpanjang!*\n\n⏰ Expired baru: {format_tgl(tgl)}\n\nKetik /start untuk kembali.",
        parse_mode='Markdown'
    )
    context.user_data.clear()
    return ConversationHandler.END

# ══ YOUTUBE ════════════════════════════════════════════════

def conv_tambah_youtube():
    return ConversationHandler(
        entry_points=[CallbackQueryHandler(yt_mulai, pattern="^tambah_youtube$")],
        states={
            YT_EMAIL: [MessageHandler(filters.TEXT & ~filters.COMMAND, yt_email)],
            YT_PASS: [MessageHandler(filters.TEXT & ~filters.COMMAND, yt_pass)],
            YT_EXPIRED: [MessageHandler(filters.TEXT & ~filters.COMMAND, yt_expired)],
            YT_CATATAN: [MessageHandler(filters.TEXT & ~filters.COMMAND, yt_catatan)],
        },
        fallbacks=[CommandHandler("batal", batal)],
        name="tambah_yt", persistent=False,
    )

async def yt_mulai(update, context):
    await update.callback_query.answer()
    context.user_data.clear()
    await update.callback_query.message.reply_text(
        "📺 *Tambah Akun YouTube Family*\n/batal untuk cancel\n\n*1/4* — *Email* akun Google:",
        parse_mode='Markdown', reply_markup=ReplyKeyboardRemove()
    )
    return YT_EMAIL

async def yt_email(update, context):
    context.user_data['email'] = update.message.text.strip()
    await update.message.reply_text("*2/4* — *Password*:\n_(ketik '-' jika tidak ada)_", parse_mode='Markdown')
    return YT_PASS

async def yt_pass(update, context):
    context.user_data['password'] = update.message.text.strip()
    await update.message.reply_text("*3/4* — *Expired langganan*:\n_(DD-MM-YYYY)_", parse_mode='Markdown')
    return YT_EXPIRED

async def yt_expired(update, context):
    tgl = validasi_tgl(update.message.text.strip())
    if not tgl:
        await update.message.reply_text("❌ Format salah! DD-MM-YYYY")
        return YT_EXPIRED
    context.user_data['expired'] = tgl
    await update.message.reply_text("*4/4* — *Catatan*:\n_(ketik '-' jika tidak ada)_", parse_mode='Markdown')
    return YT_CATATAN

async def yt_catatan(update, context):
    context.user_data['catatan'] = update.message.text.strip()
    yid = yt_add(context.user_data)
    await update.message.reply_text(
        f"✅ *Akun YouTube berhasil ditambahkan!*\n\n📧 {context.user_data['email']}\n⏰ {format_tgl(context.user_data['expired'])}\nID: #{yid}\n\nKetik /start untuk kembali.",
        parse_mode='Markdown', reply_markup=ReplyKeyboardRemove()
    )
    context.user_data.clear()
    return ConversationHandler.END

# ── EDIT YOUTUBE ──────────────────────────────────────────

def conv_edit_youtube():
    return ConversationHandler(
        entry_points=[CallbackQueryHandler(edit_yt_mulai, pattern="^edit_yt_")],
        states={
            EDIT_YT_FIELD: [MessageHandler(filters.TEXT & ~filters.COMMAND, edit_yt_field)],
            EDIT_YT_VAL: [MessageHandler(filters.TEXT & ~filters.COMMAND, edit_yt_val)],
        },
        fallbacks=[CommandHandler("batal", batal)],
        name="edit_yt", persistent=False,
    )

async def edit_yt_mulai(update, context):
    await update.callback_query.answer()
    yid = int(update.callback_query.data.split("_")[2])
    y = yt_get(yid)
    context.user_data.clear()
    context.user_data['edit_id'] = yid
    kb = ReplyKeyboardMarkup([["📧 Email","🔑 Password"],["⏰ Expired","📝 Catatan"]], one_time_keyboard=True, resize_keyboard=True)
    await update.callback_query.message.reply_text(
        f"✏️ *Edit YouTube*\n📧 {y['email']}\n\nPilih yang mau diedit:",
        parse_mode='Markdown', reply_markup=kb
    )
    return EDIT_YT_FIELD

FIELD_MAP_YT = {"📧 email":"email","🔑 password":"password","⏰ expired":"expired","📝 catatan":"catatan"}

async def edit_yt_field(update, context):
    field = update.message.text.strip().lower()
    db_field = FIELD_MAP_YT.get(field)
    if not db_field:
        await update.message.reply_text("❌ Pilih dari tombol.")
        return EDIT_YT_FIELD
    context.user_data['edit_field'] = db_field
    await update.message.reply_text("Masukkan nilai baru:", reply_markup=ReplyKeyboardRemove())
    return EDIT_YT_VAL

async def edit_yt_val(update, context):
    value = update.message.text.strip()
    if context.user_data['edit_field'] == 'expired':
        tgl = validasi_tgl(value)
        if not tgl:
            await update.message.reply_text("❌ Format salah! DD-MM-YYYY")
            return EDIT_YT_VAL
        value = tgl
    yt_update(context.user_data['edit_id'], {context.user_data['edit_field']: value})
    await update.message.reply_text("✅ Berhasil diupdate! Ketik /start untuk kembali.")
    context.user_data.clear()
    return ConversationHandler.END

# ── PERPANJANG YOUTUBE ────────────────────────────────────

def conv_perp_youtube():
    return ConversationHandler(
        entry_points=[CallbackQueryHandler(perp_yt_mulai, pattern="^perp_yt_")],
        states={PERP_YT_TGL: [MessageHandler(filters.TEXT & ~filters.COMMAND, perp_yt_tgl)]},
        fallbacks=[CommandHandler("batal", batal)],
        name="perp_yt", persistent=False,
    )

async def perp_yt_mulai(update, context):
    await update.callback_query.answer()
    yid = int(update.callback_query.data.split("_")[2])
    y = yt_get(yid)
    context.user_data.clear()
    context.user_data['perp_id'] = yid
    await update.callback_query.message.reply_text(
        f"🔄 *Perpanjang YouTube*\n📧 {y['email']}\nExpired sekarang: {format_tgl(y['expired'])}\n\nMasukkan *expired baru*:\n_(DD-MM-YYYY)_",
        parse_mode='Markdown', reply_markup=ReplyKeyboardRemove()
    )
    return PERP_YT_TGL

async def perp_yt_tgl(update, context):
    tgl = validasi_tgl(update.message.text.strip())
    if not tgl:
        await update.message.reply_text("❌ Format salah! DD-MM-YYYY")
        return PERP_YT_TGL
    yt_update(context.user_data['perp_id'], {'expired': tgl})
    await update.message.reply_text(
        f"✅ *YouTube berhasil diperpanjang!*\n\n⏰ Expired baru: {format_tgl(tgl)}\n\nKetik /start untuk kembali.",
        parse_mode='Markdown'
    )
    context.user_data.clear()
    return ConversationHandler.END

# ── CARI ─────────────────────────────────────────────────

def conv_cari():
    return ConversationHandler(
        entry_points=[CommandHandler("cari", cari_mulai)],
        states={CARI_INPUT: [MessageHandler(filters.TEXT & ~filters.COMMAND, cari_proses)]},
        fallbacks=[CommandHandler("batal", batal)],
        name="cari", persistent=False,
    )

async def cari_mulai(update, context):
    await update.message.reply_text("🔍 Masukkan keyword pencarian:\n_(nama, email, HP, atau nama perangkat)_", parse_mode='Markdown')
    return CARI_INPUT

async def cari_proses(update, context):
    keyword = update.message.text.strip().lower()
    hasil = []

    for n in nf_all():
        if keyword in n['email'].lower() or keyword in (n['password'] or '').lower():
            hasil.append(('netflix', n))
        for p in profil_all(n['id']):
            if keyword in p['nama'].lower():
                hasil.append(('profil', p, n))

    for d in ds_all():
        if keyword in d['email'].lower() or keyword in (d['no_hp'] or '').lower():
            hasil.append(('disney', d))
        for p in perangkat_all(d['id']):
            if keyword in p['nama'].lower():
                hasil.append(('perangkat', p, d))

    for y in yt_all():
        if keyword in y['email'].lower():
            hasil.append(('youtube', y))

    if not hasil:
        await update.message.reply_text(f"❌ Tidak ditemukan hasil untuk *{keyword}*", parse_mode='Markdown')
        return ConversationHandler.END

    teks = f"🔍 *Hasil Cari: '{keyword}'*\n━━━━━━━━━━━━━━━━━━━━\n\n"
    kb = []

    for item in hasil:
        if item[0] == 'netflix':
            n = item[1]
            teks += f"🎬 *Netflix* — {n['email']}\n"
            kb.append([InlineKeyboardButton(f"🎬 {n['email']}", callback_data=f"nf_detail_{n['id']}")])
        elif item[0] == 'profil':
            p, n = item[1], item[2]
            from utils import sisa_hari as sh, status_icon as si
            sisa = sh(p['expired']) if p['expired'] else 999
            teks += f"👤 *Profil {p['nama']}* — {n['email']}\n"
        elif item[0] == 'disney':
            d = item[1]
            teks += f"🏰 *Disney+* — {d['email']}\n"
            kb.append([InlineKeyboardButton(f"🏰 {d['email']}", callback_data=f"ds_detail_{d['id']}")])
        elif item[0] == 'perangkat':
            p, d = item[1], item[2]
            teks += f"📱 *{p['nama']}* (Disney) — {d['email']}\n"
        elif item[0] == 'youtube':
            y = item[1]
            teks += f"📺 *YouTube* — {y['email']}\n"
            kb.append([InlineKeyboardButton(f"📺 {y['email']}", callback_data=f"yt_detail_{y['id']}")])

    kb.append([InlineKeyboardButton("« Menu Utama", callback_data="start_menu")])
    await update.message.reply_text(teks, parse_mode='Markdown', reply_markup=InlineKeyboardMarkup(kb))
    return ConversationHandler.END
