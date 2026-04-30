from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, ConversationHandler, CommandHandler, MessageHandler, filters, CallbackQueryHandler
from database import *
from utils import validasi_tgl, format_tgl

# Netflix states
NF_EMAIL, NF_PASS, NF_METODE, NF_EXPIRED, NF_CATATAN = range(5)
# Netflix profil states
PR_NOMOR, PR_NAMA, PR_PELANGGAN, PR_HP, PR_EXPIRED, PR_HARGA = range(10,16)
# Disney states
DS_HP, DS_EMAIL, DS_PASS, DS_EXPIRED, DS_HARGA, DS_CATATAN = range(20,26)
# Disney perangkat states
PG_NAMA, PG_PELANGGAN, PG_HP, PG_TGL = range(30,34)
# YouTube states
YT_EMAIL, YT_PASS, YT_EXPIRED, YT_HARGA, YT_CATATAN = range(40,45)
# YouTube member states
MB_EMAIL, MB_NAMA, MB_HP = range(50,53)


async def batal(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()
    await update.message.reply_text("❌ Dibatalkan.", reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END


# ══ TAMBAH NETFLIX ════════════════════════════════════════

def conv_tambah_netflix():
    return ConversationHandler(
        entry_points=[CallbackQueryHandler(mulai_nf, pattern="^tambah_netflix$")],
        states={
            NF_EMAIL: [MessageHandler(filters.TEXT & ~filters.COMMAND, nf_email)],
            NF_PASS: [MessageHandler(filters.TEXT & ~filters.COMMAND, nf_pass)],
            NF_METODE: [MessageHandler(filters.TEXT & ~filters.COMMAND, nf_metode)],
            NF_EXPIRED: [MessageHandler(filters.TEXT & ~filters.COMMAND, nf_expired)],
            NF_CATATAN: [MessageHandler(filters.TEXT & ~filters.COMMAND, nf_catatan)],
        },
        fallbacks=[CommandHandler("batal", batal)],
        name="tambah_netflix", persistent=False,
    )

async def mulai_nf(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.answer()
    context.user_data.clear()
    await update.callback_query.message.reply_text(
        "🎬 *Tambah Akun Netflix*\n/batal untuk cancel\n\n*1/5* — Masukkan *email Netflix*:",
        parse_mode='Markdown', reply_markup=ReplyKeyboardRemove()
    )
    return NF_EMAIL

async def nf_email(update, context):
    context.user_data['email'] = update.message.text.strip()
    await update.message.reply_text("*2/5* — Masukkan *password*:", parse_mode='Markdown')
    return NF_PASS

async def nf_pass(update, context):
    context.user_data['password'] = update.message.text.strip()
    kb = ReplyKeyboardMarkup([["Visa","Mastercard"],["GoPay","OVO"],["Transfer Bank"]], one_time_keyboard=True, resize_keyboard=True)
    await update.message.reply_text("*3/5* — Pilih *metode bayar*:", parse_mode='Markdown', reply_markup=kb)
    return NF_METODE

async def nf_metode(update, context):
    context.user_data['metode_bayar'] = update.message.text.strip()
    await update.message.reply_text("*4/5* — *Expired akun* Netflix:\n_(DD-MM-YYYY atau '-')_", parse_mode='Markdown', reply_markup=ReplyKeyboardRemove())
    return NF_EXPIRED

async def nf_expired(update, context):
    tgl = update.message.text.strip()
    if tgl != '-':
        tgl = validasi_tgl(tgl)
        if not tgl:
            await update.message.reply_text("❌ Format salah! DD-MM-YYYY")
            return NF_EXPIRED
    context.user_data['expired_akun'] = tgl if tgl != '-' else ''
    await update.message.reply_text("*5/5* — *Catatan* tambahan:\n_(ketik '-' jika tidak ada)_", parse_mode='Markdown')
    return NF_CATATAN

async def nf_catatan(update, context):
    context.user_data['catatan'] = update.message.text.strip()
    nid = netflix_tambah(context.user_data)
    await update.message.reply_text(
        f"✅ *Akun Netflix berhasil ditambahkan!*\n\n"
        f"📧 {context.user_data['email']}\n"
        f"💳 {context.user_data['metode_bayar']}\n"
        f"ID: #{nid}\n\n"
        f"Gunakan /start untuk kembali ke menu.",
        parse_mode='Markdown', reply_markup=ReplyKeyboardRemove()
    )
    context.user_data.clear()
    return ConversationHandler.END


# ══ TAMBAH PROFIL NETFLIX ═════════════════════════════════

def conv_tambah_profil():
    return ConversationHandler(
        entry_points=[CallbackQueryHandler(mulai_profil, pattern="^tambah_profil_")],
        states={
            PR_NOMOR: [MessageHandler(filters.TEXT & ~filters.COMMAND, pr_nomor)],
            PR_NAMA: [MessageHandler(filters.TEXT & ~filters.COMMAND, pr_nama)],
            PR_PELANGGAN: [MessageHandler(filters.TEXT & ~filters.COMMAND, pr_pelanggan)],
            PR_HP: [MessageHandler(filters.TEXT & ~filters.COMMAND, pr_hp)],
            PR_EXPIRED: [MessageHandler(filters.TEXT & ~filters.COMMAND, pr_expired)],
            PR_HARGA: [MessageHandler(filters.TEXT & ~filters.COMMAND, pr_harga)],
        },
        fallbacks=[CommandHandler("batal", batal)],
        name="tambah_profil", persistent=False,
    )

async def mulai_profil(update, context):
    await update.callback_query.answer()
    nid = int(update.callback_query.data.split("_")[2])
    context.user_data.clear()
    context.user_data['netflix_id'] = nid
    profil_list = profil_get_all(nid)
    nomor_ada = [p['nomor_profil'] for p in profil_list]
    nomor_tersedia = [str(i) for i in range(1,6) if i not in nomor_ada]
    kb = ReplyKeyboardMarkup([nomor_tersedia], one_time_keyboard=True, resize_keyboard=True)
    await update.callback_query.message.reply_text(
        "👥 *Tambah Profil Netflix*\n/batal untuk cancel\n\n*1/6* — Pilih *nomor profil*:",
        parse_mode='Markdown', reply_markup=kb
    )
    return PR_NOMOR

async def pr_nomor(update, context):
    try:
        context.user_data['nomor_profil'] = int(update.message.text.strip())
    except:
        await update.message.reply_text("❌ Masukkan angka 1-5")
        return PR_NOMOR
    await update.message.reply_text("*2/6* — *Nama profil* di Netflix:\n_(contoh: Profile 1)_", parse_mode='Markdown', reply_markup=ReplyKeyboardRemove())
    return PR_NAMA

async def pr_nama(update, context):
    context.user_data['nama_profil'] = update.message.text.strip()
    await update.message.reply_text("*3/6* — *Nama pelanggan*:", parse_mode='Markdown')
    return PR_PELANGGAN

async def pr_pelanggan(update, context):
    context.user_data['nama_pelanggan'] = update.message.text.strip()
    await update.message.reply_text("*4/6* — *No HP* pelanggan:\n_(ketik '-' jika tidak ada)_", parse_mode='Markdown')
    return PR_HP

async def pr_hp(update, context):
    context.user_data['no_hp'] = update.message.text.strip()
    await update.message.reply_text("*5/6* — *Expired profil ini*:\n_(DD-MM-YYYY)_", parse_mode='Markdown')
    return PR_EXPIRED

async def pr_expired(update, context):
    tgl = validasi_tgl(update.message.text.strip())
    if not tgl:
        await update.message.reply_text("❌ Format salah! DD-MM-YYYY")
        return PR_EXPIRED
    context.user_data['expired'] = tgl
    await update.message.reply_text("*6/6* — *Harga* profil ini:\n_(angka, contoh: 50000)_", parse_mode='Markdown')
    return PR_HARGA

async def pr_harga(update, context):
    try:
        context.user_data['harga'] = int(update.message.text.strip().replace('.','').replace(',',''))
    except:
        await update.message.reply_text("❌ Masukkan angka saja.")
        return PR_HARGA
    nid = context.user_data['netflix_id']
    profil_tambah(nid, context.user_data)
    await update.message.reply_text(
        f"✅ *Profil {context.user_data['nomor_profil']} berhasil ditambahkan!*\n\n"
        f"👤 {context.user_data['nama_pelanggan']}\n"
        f"⏰ Expired: {format_tgl(context.user_data['expired'])}\n\n"
        f"Gunakan /start untuk kembali.",
        parse_mode='Markdown', reply_markup=ReplyKeyboardRemove()
    )
    context.user_data.clear()
    return ConversationHandler.END


# ══ TAMBAH DISNEY+ ════════════════════════════════════════

def conv_tambah_disney():
    return ConversationHandler(
        entry_points=[CallbackQueryHandler(mulai_ds, pattern="^tambah_disney$")],
        states={
            DS_HP: [MessageHandler(filters.TEXT & ~filters.COMMAND, ds_hp)],
            DS_EMAIL: [MessageHandler(filters.TEXT & ~filters.COMMAND, ds_email)],
            DS_PASS: [MessageHandler(filters.TEXT & ~filters.COMMAND, ds_pass)],
            DS_EXPIRED: [MessageHandler(filters.TEXT & ~filters.COMMAND, ds_expired)],
            DS_HARGA: [MessageHandler(filters.TEXT & ~filters.COMMAND, ds_harga)],
            DS_CATATAN: [MessageHandler(filters.TEXT & ~filters.COMMAND, ds_catatan)],
        },
        fallbacks=[CommandHandler("batal", batal)],
        name="tambah_disney", persistent=False,
    )

async def mulai_ds(update, context):
    await update.callback_query.answer()
    context.user_data.clear()
    await update.callback_query.message.reply_text(
        "🏰 *Tambah Akun Disney+*\n/batal untuk cancel\n\n*1/6* — Masukkan *No HP*:\n_(ketik '-' jika tidak ada)_",
        parse_mode='Markdown', reply_markup=ReplyKeyboardRemove()
    )
    return DS_HP

async def ds_hp(update, context):
    context.user_data['no_hp'] = update.message.text.strip()
    await update.message.reply_text("*2/6* — Masukkan *email Disney+*:", parse_mode='Markdown')
    return DS_EMAIL

async def ds_email(update, context):
    context.user_data['email'] = update.message.text.strip()
    await update.message.reply_text("*3/6* — Masukkan *password*:\n_(ketik '-' jika tidak ada)_", parse_mode='Markdown')
    return DS_PASS

async def ds_pass(update, context):
    context.user_data['password'] = update.message.text.strip()
    await update.message.reply_text("*4/6* — *Expired langganan*:\n_(DD-MM-YYYY)_", parse_mode='Markdown')
    return DS_EXPIRED

async def ds_expired(update, context):
    tgl = validasi_tgl(update.message.text.strip())
    if not tgl:
        await update.message.reply_text("❌ Format salah! DD-MM-YYYY")
        return DS_EXPIRED
    context.user_data['expired_langganan'] = tgl
    await update.message.reply_text("*5/6* — *Harga* langganan:\n_(angka, contoh: 80000)_", parse_mode='Markdown')
    return DS_HARGA

async def ds_harga(update, context):
    try:
        context.user_data['harga'] = int(update.message.text.strip().replace('.','').replace(',',''))
    except:
        await update.message.reply_text("❌ Masukkan angka saja.")
        return DS_HARGA
    await update.message.reply_text("*6/6* — *Catatan*:\n_(ketik '-' jika tidak ada)_", parse_mode='Markdown')
    return DS_CATATAN

async def ds_catatan(update, context):
    context.user_data['catatan'] = update.message.text.strip()
    did = disney_tambah(context.user_data)
    await update.message.reply_text(
        f"✅ *Akun Disney+ berhasil ditambahkan!*\n\n"
        f"📧 {context.user_data['email']}\n"
        f"⏰ {format_tgl(context.user_data['expired_langganan'])}\n"
        f"ID: #{did}\n\nGunakan /start untuk kembali.",
        parse_mode='Markdown', reply_markup=ReplyKeyboardRemove()
    )
    context.user_data.clear()
    return ConversationHandler.END


# ══ TAMBAH PERANGKAT DISNEY ═══════════════════════════════

def conv_tambah_perangkat():
    return ConversationHandler(
        entry_points=[CallbackQueryHandler(mulai_pg, pattern="^tambah_perangkat_")],
        states={
            PG_NAMA: [MessageHandler(filters.TEXT & ~filters.COMMAND, pg_nama)],
            PG_PELANGGAN: [MessageHandler(filters.TEXT & ~filters.COMMAND, pg_pelanggan)],
            PG_HP: [MessageHandler(filters.TEXT & ~filters.COMMAND, pg_hp)],
            PG_TGL: [MessageHandler(filters.TEXT & ~filters.COMMAND, pg_tgl)],
        },
        fallbacks=[CommandHandler("batal", batal)],
        name="tambah_perangkat", persistent=False,
    )

async def mulai_pg(update, context):
    await update.callback_query.answer()
    did = int(update.callback_query.data.split("_")[2])
    context.user_data.clear()
    context.user_data['disney_id'] = did
    await update.callback_query.message.reply_text(
        "📱 *Tambah Perangkat Disney+*\n/batal untuk cancel\n\n*1/4* — *Nama perangkat*:\n_(contoh: Oppo Phone, Samsung TV)_",
        parse_mode='Markdown', reply_markup=ReplyKeyboardRemove()
    )
    return PG_NAMA

async def pg_nama(update, context):
    context.user_data['nama_perangkat'] = update.message.text.strip()
    await update.message.reply_text("*2/4* — *Nama pelanggan*:", parse_mode='Markdown')
    return PG_PELANGGAN

async def pg_pelanggan(update, context):
    context.user_data['nama_pelanggan'] = update.message.text.strip()
    await update.message.reply_text("*3/4* — *No HP* pelanggan:\n_(ketik '-' jika tidak ada)_", parse_mode='Markdown')
    return PG_HP

async def pg_hp(update, context):
    context.user_data['no_hp'] = update.message.text.strip()
    await update.message.reply_text("*4/4* — *Tanggal login*:\n_(DD-MM-YYYY atau '-')_", parse_mode='Markdown')
    return PG_TGL

async def pg_tgl(update, context):
    tgl = update.message.text.strip()
    if tgl != '-':
        tgl_db = validasi_tgl(tgl)
        context.user_data['tanggal_login'] = tgl_db or tgl
    else:
        context.user_data['tanggal_login'] = ''
    did = context.user_data['disney_id']
    perangkat_tambah(did, context.user_data)
    await update.message.reply_text(
        f"✅ *Perangkat berhasil ditambahkan!*\n\n"
        f"📱 {context.user_data['nama_perangkat']}\n"
        f"👤 {context.user_data['nama_pelanggan']}\n\nGunakan /start untuk kembali.",
        parse_mode='Markdown', reply_markup=ReplyKeyboardRemove()
    )
    context.user_data.clear()
    return ConversationHandler.END


# ══ TAMBAH YOUTUBE ════════════════════════════════════════

def conv_tambah_youtube():
    return ConversationHandler(
        entry_points=[CallbackQueryHandler(mulai_yt, pattern="^tambah_youtube$")],
        states={
            YT_EMAIL: [MessageHandler(filters.TEXT & ~filters.COMMAND, yt_email)],
            YT_PASS: [MessageHandler(filters.TEXT & ~filters.COMMAND, yt_pass)],
            YT_EXPIRED: [MessageHandler(filters.TEXT & ~filters.COMMAND, yt_expired)],
            YT_HARGA: [MessageHandler(filters.TEXT & ~filters.COMMAND, yt_harga)],
            YT_CATATAN: [MessageHandler(filters.TEXT & ~filters.COMMAND, yt_catatan)],
        },
        fallbacks=[CommandHandler("batal", batal)],
        name="tambah_youtube", persistent=False,
    )

async def mulai_yt(update, context):
    await update.callback_query.answer()
    context.user_data.clear()
    await update.callback_query.message.reply_text(
        "📺 *Tambah Akun YouTube Family*\n/batal untuk cancel\n\n*1/5* — Masukkan *email akun YouTube*:",
        parse_mode='Markdown', reply_markup=ReplyKeyboardRemove()
    )
    return YT_EMAIL

async def yt_email(update, context):
    context.user_data['email_akun'] = update.message.text.strip()
    await update.message.reply_text("*2/5* — Masukkan *password*:\n_(ketik '-' jika tidak ada)_", parse_mode='Markdown')
    return YT_PASS

async def yt_pass(update, context):
    context.user_data['password'] = update.message.text.strip()
    await update.message.reply_text("*3/5* — *Expired langganan*:\n_(DD-MM-YYYY)_", parse_mode='Markdown')
    return YT_EXPIRED

async def yt_expired(update, context):
    tgl = validasi_tgl(update.message.text.strip())
    if not tgl:
        await update.message.reply_text("❌ Format salah! DD-MM-YYYY")
        return YT_EXPIRED
    context.user_data['expired_langganan'] = tgl
    await update.message.reply_text("*4/5* — *Harga* langganan:\n_(angka, contoh: 40000)_", parse_mode='Markdown')
    return YT_HARGA

async def yt_harga(update, context):
    try:
        context.user_data['harga'] = int(update.message.text.strip().replace('.','').replace(',',''))
    except:
        await update.message.reply_text("❌ Masukkan angka saja.")
        return YT_HARGA
    await update.message.reply_text("*5/5* — *Catatan*:\n_(ketik '-' jika tidak ada)_", parse_mode='Markdown')
    return YT_CATATAN

async def yt_catatan(update, context):
    context.user_data['catatan'] = update.message.text.strip()
    yid = yt_tambah(context.user_data)
    await update.message.reply_text(
        f"✅ *Akun YouTube Family berhasil ditambahkan!*\n\n"
        f"📧 {context.user_data['email_akun']}\n"
        f"⏰ {format_tgl(context.user_data['expired_langganan'])}\n"
        f"ID: #{yid}\n\nGunakan /start untuk kembali.",
        parse_mode='Markdown', reply_markup=ReplyKeyboardRemove()
    )
    context.user_data.clear()
    return ConversationHandler.END


# ══ TAMBAH MEMBER YOUTUBE ═════════════════════════════════

def conv_tambah_member():
    return ConversationHandler(
        entry_points=[CallbackQueryHandler(mulai_mb, pattern="^tambah_member_")],
        states={
            MB_EMAIL: [MessageHandler(filters.TEXT & ~filters.COMMAND, mb_email)],
            MB_NAMA: [MessageHandler(filters.TEXT & ~filters.COMMAND, mb_nama)],
            MB_HP: [MessageHandler(filters.TEXT & ~filters.COMMAND, mb_hp)],
        },
        fallbacks=[CommandHandler("batal", batal)],
        name="tambah_member", persistent=False,
    )

async def mulai_mb(update, context):
    await update.callback_query.answer()
    yid = int(update.callback_query.data.split("_")[2])
    context.user_data.clear()
    context.user_data['youtube_id'] = yid
    await update.callback_query.message.reply_text(
        "👥 *Tambah Member YouTube*\n/batal untuk cancel\n\n*1/3* — *Email pembeli*:",
        parse_mode='Markdown', reply_markup=ReplyKeyboardRemove()
    )
    return MB_EMAIL

async def mb_email(update, context):
    context.user_data['email_pembeli'] = update.message.text.strip()
    await update.message.reply_text("*2/3* — *Nama pelanggan*:", parse_mode='Markdown')
    return MB_NAMA

async def mb_nama(update, context):
    context.user_data['nama_pelanggan'] = update.message.text.strip()
    await update.message.reply_text("*3/3* — *No HP*:\n_(ketik '-' jika tidak ada)_", parse_mode='Markdown')
    return MB_HP

async def mb_hp(update, context):
    context.user_data['no_hp'] = update.message.text.strip()
    yid = context.user_data['youtube_id']
    member_tambah(yid, context.user_data)
    await update.message.reply_text(
        f"✅ *Member berhasil ditambahkan!*\n\n"
        f"📧 {context.user_data['email_pembeli']}\n"
        f"👤 {context.user_data['nama_pelanggan']}\n\nGunakan /start untuk kembali.",
        parse_mode='Markdown', reply_markup=ReplyKeyboardRemove()
    )
    context.user_data.clear()
    return ConversationHandler.END
