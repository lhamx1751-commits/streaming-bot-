from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, ConversationHandler, CommandHandler, MessageHandler, filters, CallbackQueryHandler
from database import *
from utils import validasi_tgl, format_tgl, parse_bulk_perangkat, parse_bulk_profil

# States
NF_EMAIL, NF_PASS, NF_UBAH_PW, NF_METODE, NF_CATATAN = range(5)
PR_NOMOR, PR_NAMA, PR_PIN, PR_EXPIRED = range(10,14)
EDIT_NF_F, EDIT_NF_V = range(20,22)
EDIT_PR_F, EDIT_PR_V = range(22,24)
PERP_NF = 24
DS_PAKET, DS_HP, DS_EMAIL, DS_EXPIRED, DS_CATATAN = range(30,35)
PG_NAMA, PG_EXPIRED = range(36,38)
EDIT_DS_F, EDIT_DS_V = range(38,40)
EDIT_PG_F, EDIT_PG_V = range(40,42)
PERP_DS = 42
YT_EMAIL, YT_PASS, YT_EXPIRED, YT_CATATAN = range(50,54)
EDIT_YT_F, EDIT_YT_V = range(54,56)
PERP_YT = 56
CARI_INPUT = 60
BULK_PG = 70
BULK_PR = 71

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
            NF_METODE: [MessageHandler(filters.TEXT & ~filters.COMMAND, nf_metode)],
            NF_CATATAN: [MessageHandler(filters.TEXT & ~filters.COMMAND, nf_catatan)],
        },
        fallbacks=[CommandHandler("batal", batal)],
        name="tnf", persistent=False,
    )

async def nf_mulai(update, context):
    await update.callback_query.answer()
    context.user_data.clear()
    await update.callback_query.message.reply_text(
        "🎬 *Tambah Akun Netflix*\n/batal untuk cancel\n\n*1/5* — Masukkan *email Netflix*:",
        parse_mode='Markdown', reply_markup=ReplyKeyboardRemove()
    )
    return NF_EMAIL

async def nf_email(update, context):
    context.user_data['email'] = update.message.text.strip()
    await update.message.reply_text("*2/5* — *Password*:\n_(ketik '-' jika tidak ada)_", parse_mode='Markdown')
    return NF_PASS

async def nf_pass(update, context):
    context.user_data['password'] = update.message.text.strip()
    await update.message.reply_text("*3/5* — *Tanggal ubah password* terakhir:\n_(contoh: 1 April 2026, atau '-')_", parse_mode='Markdown')
    return NF_UBAH_PW

async def nf_ubah_pw(update, context):
    context.user_data['tgl_ubah_pw'] = update.message.text.strip()
    kb = ReplyKeyboardMarkup([["Visa","Mastercard"],["GoPay","OVO"],["Transfer","-"]], one_time_keyboard=True, resize_keyboard=True)
    await update.message.reply_text("*4/5* — *Metode bayar*:", parse_mode='Markdown', reply_markup=kb)
    return NF_METODE

async def nf_metode(update, context):
    context.user_data['metode_bayar'] = update.message.text.strip()
    await update.message.reply_text("*5/5* — *Catatan*:\n_(ketik '-' jika tidak ada)_", parse_mode='Markdown', reply_markup=ReplyKeyboardRemove())
    return NF_CATATAN

async def nf_catatan(update, context):
    context.user_data['catatan'] = update.message.text.strip()
    nid = nf_add(context.user_data)
    await update.message.reply_text(
        f"✅ *Akun Netflix berhasil ditambahkan!*\n\n"
        f"📧 {context.user_data['email']}\n"
        f"🆔 ID: #{nid}\n\n"
        f"Sekarang tambahkan profil via /start → Netflix → Kelola Profil",
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
        name="tpr", persistent=False,
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
    try: context.user_data['nomor'] = int(update.message.text.strip())
    except:
        await update.message.reply_text("❌ Masukkan angka 1-5")
        return PR_NOMOR
    await update.message.reply_text("*2/4* — *Nama profil*:", parse_mode='Markdown', reply_markup=ReplyKeyboardRemove())
    return PR_NAMA

async def pr_nama(update, context):
    context.user_data['nama'] = update.message.text.strip()
    await update.message.reply_text("*3/4* — *PIN*:\n_(ketik '-' jika tidak ada)_", parse_mode='Markdown')
    return PR_PIN

async def pr_pin(update, context):
    context.user_data['pin'] = update.message.text.strip()
    await update.message.reply_text(
        "ّ*4/4* — *Tanggal expired*:\n_(contoh: 17 Mei 2026, atau '-' jika aktif)_",
        parse_mode='Markdown'
    )
    return PR_EXPIRED

async def pr_expired(update, context):
    tgl_raw = update.message.text.strip()
    if tgl_raw == '-':
        context.user_data['expired'] = ''
    else:
        tgl = validasi_tgl(tgl_raw)
        if not tgl:
            await update.message.reply_text("❌ Format salah! Contoh: 17 Mei 2026 atau 17-05-2026")
            return PR_EXPIRED
        context.user_data['expired'] = tgl
    profil_add(context.user_data)
    await update.message.reply_text(
        f"✅ *Profil {context.user_data['nomor']} — {context.user_data['nama']} berhasil ditambahkan!*\n\nKetik /start untuk kembali.",
        parse_mode='Markdown', reply_markup=ReplyKeyboardRemove()
    )
    context.user_data.clear()
    return ConversationHandler.END

# ── BULK PROFIL ───────────────────────────────────────────

def conv_bulk_profil():
    return ConversationHandler(
        entry_points=[CallbackQueryHandler(bulk_pr_mulai, pattern="^bulk_profil_")],
        states={BULK_PR: [MessageHandler(filters.TEXT & ~filters.COMMAND, bulk_pr_proses)]},
        fallbacks=[CommandHandler("batal", batal)],
        name="bpr", persistent=False,
    )

async def bulk_pr_mulai(update, context):
    await update.callback_query.answer()
    nid = int(update.callback_query.data.split("_")[2])
    context.user_data.clear()
    context.user_data['bulk_nid'] = nid
    n = nf_get(nid)
    profil = profil_all(nid)
    nomor_ada = [p['nomor'] for p in profil]
    nomor_tersedia = [str(i) for i in range(1,6) if i not in nomor_ada]

    teks = (
        f"👥 *Bulk Tambah Profil Netflix*\n"
        f"📧 {n['email']}\n"
        f"━━━━━━━━━━━━━━━━━━━━\n\n"
        f"Slot tersedia: *{', '.join(nomor_tersedia)}*\n\n"
        f"Kirim semua profil sekaligus, format bebas:\n\n"
        f"Format 1 (dengan nomor):\n"
        f"`1|Dyah|1111|17 Mei 2026`\n"
        f"`2|Baylee|1888|18 Mei 2026`\n\n"
        f"Format 2 (tanpa nomor, urut otomatis):\n"
        f"`Dyah|1111|17 Mei 2026`\n"
        f"`Baylee|1888|18 Mei 2026`\n\n"
        f"Format 3 (tanggal natural):\n"
        f"`Dyah|1111|17 mei 2026`\n"
        f"`Baylee|1888|18-05-2026`\n\n"
        f"⚠️ PIN & tanggal bisa dikosongkan\n"
        f"Tulis *expired* jika sudah expired"
    )
    await update.callback_query.message.reply_text(teks, parse_mode='Markdown', reply_markup=ReplyKeyboardRemove())
    return BULK_PR

async def bulk_pr_proses(update, context):
    nid = context.user_data['bulk_nid']
    profil_existing = profil_all(nid)
    nomor_ada = [p['nomor'] for p in profil_existing]
    slot_tersedia = [i for i in range(1,6) if i not in nomor_ada]

    hasil = parse_bulk_profil(update.message.text)
    berhasil = []
    gagal = []

    for i, item in enumerate(hasil):
        nomor = item.get('nomor', i+1)

        # Assign nomor otomatis kalau tidak valid
        if nomor not in slot_tersedia:
            if slot_tersedia:
                nomor = slot_tersedia[0]
            else:
                gagal.append(f"⚠️ {item['nama']} → Slot penuh")
                continue

        slot_tersedia.remove(nomor)
        nomor_ada.append(nomor)

        profil_add({
            'netflix_id': nid,
            'nomor': nomor,
            'nama': item['nama'],
            'pin': item.get('pin',''),
            'expired': item.get('expired','')
        })

        expired_str = format_tgl(item['expired']) if item.get('expired') else 'Aktif'
        berhasil.append(f"✅ *{nomor}. {item['nama']}* | {item.get('pin','-')} | {expired_str}")

    teks = f"👥 *Hasil Bulk Profil Netflix*\n━━━━━━━━━━━━━━━━━━━━\n\n"
    if berhasil:
        teks += f"✅ *Berhasil ({len(berhasil)}):*\n" + '\n'.join(berhasil) + '\n\n'
    if gagal:
        teks += f"⚠️ *Gagal ({len(gagal)}):*\n" + '\n'.join(gagal) + '\n\n'
    teks += "_Ketik /start untuk kembali ke menu._"

    await update.message.reply_text(teks, parse_mode='Markdown')
    context.user_data.clear()
    return ConversationHandler.END

# ── EDIT NETFLIX ──────────────────────────────────────────

def conv_edit_netflix():
    return ConversationHandler(
        entry_points=[CallbackQueryHandler(edit_nf_mulai, pattern="^edit_nf_")],
        states={
            EDIT_NF_F: [MessageHandler(filters.TEXT & ~filters.COMMAND, edit_nf_f)],
            EDIT_NF_V: [MessageHandler(filters.TEXT & ~filters.COMMAND, edit_nf_v)],
        },
        fallbacks=[CommandHandler("batal", batal)],
        name="enf", persistent=False,
    )

async def edit_nf_mulai(update, context):
    await update.callback_query.answer()
    nid = int(update.callback_query.data.split("_")[2])
    n = nf_get(nid)
    context.user_data.clear()
    context.user_data['edit_id'] = nid
    kb = ReplyKeyboardMarkup([["📧 Email","🔑 Password"],["📅 Ubah PW","💳 Metode"],["📝 Catatan"]], one_time_keyboard=True, resize_keyboard=True)
    await update.callback_query.message.reply_text(
        f"✏️ *Edit Akun Netflix*\n📧 {n['email']}\n\nPilih yang mau diedit:",
        parse_mode='Markdown', reply_markup=kb
    )
    return EDIT_NF_F

NF_MAP = {"📧 email":"email","🔑 password":"password","📅 ubah pw":"tgl_ubah_pw","💳 metode":"metode_bayar","📝 catatan":"catatan"}

async def edit_nf_f(update, context):
    f = update.message.text.strip().lower()
    db_f = NF_MAP.get(f)
    if not db_f:
        await update.message.reply_text("❌ Pilih dari tombol.")
        return EDIT_NF_F
    context.user_data['ef'] = db_f
    await update.message.reply_text(f"Masukkan nilai baru:", reply_markup=ReplyKeyboardRemove())
    return EDIT_NF_V

async def edit_nf_v(update, context):
    nf_update(context.user_data['edit_id'], {context.user_data['ef']: update.message.text.strip()})
    await update.message.reply_text("✅ Berhasil diupdate! Ketik /start untuk kembali.")
    context.user_data.clear()
    return ConversationHandler.END

# ── EDIT PROFIL ───────────────────────────────────────────

def conv_edit_profil():
    return ConversationHandler(
        entry_points=[CallbackQueryHandler(edit_pr_mulai, pattern="^edit_profil_")],
        states={
            EDIT_PR_F: [MessageHandler(filters.TEXT & ~filters.COMMAND, edit_pr_f)],
            EDIT_PR_V: [MessageHandler(filters.TEXT & ~filters.COMMAND, edit_pr_v)],
        },
        fallbacks=[CommandHandler("batal", batal)],
        name="epr", persistent=False,
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
    return EDIT_PR_F

PR_MAP = {"👤 nama":"nama","📌 pin":"pin","⏰ expired":"expired"}

async def edit_pr_f(update, context):
    f = update.message.text.strip().lower()
    db_f = PR_MAP.get(f)
    if not db_f:
        await update.message.reply_text("❌ Pilih dari tombol.")
        return EDIT_PR_F
    context.user_data['ef'] = db_f
    hint = "\n_(contoh: 17 Mei 2026)_" if db_f == 'expired' else ""
    await update.message.reply_text(f"Masukkan nilai baru:{hint}", parse_mode='Markdown', reply_markup=ReplyKeyboardRemove())
    return EDIT_PR_V

async def edit_pr_v(update, context):
    value = update.message.text.strip()
    if context.user_data['ef'] == 'expired':
        tgl = validasi_tgl(value)
        if not tgl and value != '-':
            await update.message.reply_text("❌ Format salah! Contoh: 17 Mei 2026")
            return EDIT_PR_V
        value = tgl or ''
    profil_update(context.user_data['edit_id'], {context.user_data['ef']: value})
    await update.message.reply_text("✅ Profil berhasil diupdate!")
    context.user_data.clear()
    return ConversationHandler.END

# ── PERPANJANG NETFLIX ────────────────────────────────────

def conv_perp_netflix():
    return ConversationHandler(
        entry_points=[CallbackQueryHandler(perp_nf_mulai, pattern="^perp_nf_")],
        states={PERP_NF: [MessageHandler(filters.TEXT & ~filters.COMMAND, perp_nf_tgl)]},
        fallbacks=[CommandHandler("batal", batal)],
        name="pnf", persistent=False,
    )

async def perp_nf_mulai(update, context):
    await update.callback_query.answer()
    nid = int(update.callback_query.data.split("_")[2])
    context.user_data.clear()
    context.user_data['pid'] = nid
    await update.callback_query.message.reply_text(
        "🔄 *Perpanjang Netflix*\n\nMasukkan *expired baru* untuk semua profil:\n_(contoh: 17 Mei 2026)_",
        parse_mode='Markdown', reply_markup=ReplyKeyboardRemove()
    )
    return PERP_NF

async def perp_nf_tgl(update, context):
    tgl = validasi_tgl(update.message.text.strip())
    if not tgl:
        await update.message.reply_text("❌ Format salah! Contoh: 17 Mei 2026")
        return PERP_NF
    nid = context.user_data['pid']
    for p in profil_all(nid):
        profil_update(p['id'], {'expired': tgl})
    await update.message.reply_text(
        f"✅ *Semua profil berhasil diperpanjang!*\n\n⏰ Expired baru: {format_tgl(tgl)}",
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
            DS_EXPIRED: [MessageHandler(filters.TEXT & ~filters.COMMAND, ds_expired)],
            DS_CATATAN: [MessageHandler(filters.TEXT & ~filters.COMMAND, ds_catatan)],
        },
        fallbacks=[CommandHandler("batal", batal)],
        name="tds", persistent=False,
    )

async def ds_mulai(update, context):
    await update.callback_query.answer()
    context.user_data.clear()
    kb = ReplyKeyboardMarkup([["DISNEY 1 BULAN SHARING"],["DISNEY 3 BULAN SHARING"]], one_time_keyboard=True, resize_keyboard=True)
    await update.callback_query.message.reply_text(
        "🏰 *Tambah Akun Disney+*\n/batal untuk cancel\n\n*1/5* — Pilih *nama paket*:",
        parse_mode='Markdown', reply_markup=kb
    )
    return DS_PAKET

async def ds_paket(update, context):
    context.user_data['nama_paket'] = update.message.text.strip()
    await update.message.reply_text("*2/5* — *No HP* pemilik akun:\n_(ketik '-' jika tidak ada)_", parse_mode='Markdown', reply_markup=ReplyKeyboardRemove())
    return DS_HP

async def ds_hp(update, context):
    context.user_data['no_hp'] = update.message.text.strip()
    await update.message.reply_text("*3/5* — *Email* akun Disney+:", parse_mode='Markdown')
    return DS_EMAIL

async def ds_email(update, context):
    context.user_data['email'] = update.message.text.strip()
    await update.message.reply_text("*4/5* — *Expired langganan*:\n_(contoh: 24 Maret 2027)_", parse_mode='Markdown')
    return DS_EXPIRED

async def ds_expired(update, context):
    tgl = validasi_tgl(update.message.text.strip())
    if not tgl:
        await update.message.reply_text("❌ Format salah! Contoh: 24 Maret 2027")
        return DS_EXPIRED
    context.user_data['expired_langganan'] = tgl
    await update.message.reply_text("*5/5* — *Catatan*:\n_(ketik '-' jika tidak ada)_", parse_mode='Markdown')
    return DS_CATATAN

async def ds_catatan(update, context):
    context.user_data['catatan'] = update.message.text.strip()
    did = ds_add(context.user_data)
    await update.message.reply_text(
        f"✅ *Akun Disney+ berhasil ditambahkan!*\n\n"
        f"📧 {context.user_data['email']}\n"
        f"⏰ {format_tgl(context.user_data['expired_langganan'])}\n"
        f"🆔 ID: #{did}\n\n"
        f"Tambahkan perangkat via /start → Disney+",
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
        name="tpg", persistent=False,
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
    await update.message.reply_text("*2/2* — *Tanggal expired* perangkat:\n_(contoh: 9 Mei 2026, atau '-')_", parse_mode='Markdown')
    return PG_EXPIRED

async def pg_expired(update, context):
    tgl_raw = update.message.text.strip()
    tgl = validasi_tgl(tgl_raw) if tgl_raw != '-' else ''
    context.user_data['expired'] = tgl or ''
    perangkat_add(context.user_data)
    await update.message.reply_text(
        f"✅ *{context.user_data['nama']} berhasil ditambahkan!*\n\nKetik /start untuk kembali.",
        parse_mode='Markdown', reply_markup=ReplyKeyboardRemove()
    )
    context.user_data.clear()
    return ConversationHandler.END

# ── BULK PERANGKAT ────────────────────────────────────────

def conv_bulk_perangkat():
    return ConversationHandler(
        entry_points=[CallbackQueryHandler(bulk_pg_mulai, pattern="^bulk_perangkat_")],
        states={BULK_PG: [MessageHandler(filters.TEXT & ~filters.COMMAND, bulk_pg_proses)]},
        fallbacks=[CommandHandler("batal", batal)],
        name="bpg", persistent=False,
    )

async def bulk_pg_mulai(update, context):
    await update.callback_query.answer()
    did = int(update.callback_query.data.split("_")[2])
    context.user_data.clear()
    context.user_data['bulk_did'] = did
    d = ds_get(did)
    pg_existing = perangkat_all(did)
    slot_tersisa = 5 - len(pg_existing)

    teks = (
        f"📱 *Bulk Tambah Perangkat Disney+*\n"
        f"📧 {d['email']}\n"
        f"━━━━━━━━━━━━━━━━━━━━\n\n"
        f"Slot tersedia: *{slot_tersisa}*\n\n"
        f"Kirim semua perangkat sekaligus:\n\n"
        f"Format bebas — satu baris satu perangkat:\n\n"
        f"`Oppo phone|9 mei 2026`\n"
        f"`Infinix phone|10 mei 2026`\n"
        f"`Chrome browser|18-05-2026`\n"
        f"`Samsung TV|21 mei 2026`\n\n"
        f"Tanggal format bebas: *17 Mei 2026* atau *17-05-2026*\n"
        f"Tanggal bisa dikosongkan: `Oppo phone|`"
    )
    await update.callback_query.message.reply_text(teks, parse_mode='Markdown', reply_markup=ReplyKeyboardRemove())
    return BULK_PG

async def bulk_pg_proses(update, context):
    did = context.user_data['bulk_did']
    pg_existing = perangkat_all(did)
    slot_tersisa = 5 - len(pg_existing)

    hasil = parse_bulk_perangkat(update.message.text)
    berhasil = []
    gagal = []

    for item in hasil:
        if len(berhasil) >= slot_tersisa:
            gagal.append(f"⚠️ {item['nama']} → Slot penuh (maks 5)")
            continue
        perangkat_add({'disney_id': did, 'nama': item['nama'], 'expired': item.get('expired','')})
        expired_str = format_tgl(item['expired']) if item.get('expired') else '-'
        berhasil.append(f"✅ *{item['nama']}* | ⏰ {expired_str}")

    teks = f"📱 *Hasil Bulk Perangkat Disney+*\n━━━━━━━━━━━━━━━━━━━━\n\n"
    if berhasil:
        teks += f"✅ *Berhasil ({len(berhasil)}):*\n" + '\n'.join(berhasil) + '\n\n'
    if gagal:
        teks += f"⚠️ *Gagal ({len(gagal)}):*\n" + '\n'.join(gagal) + '\n\n'
    teks += "_Ketik /start untuk kembali ke menu._"

    await update.message.reply_text(teks, parse_mode='Markdown')
    context.user_data.clear()
    return ConversationHandler.END

# ── EDIT DISNEY ───────────────────────────────────────────

def conv_edit_disney():
    return ConversationHandler(
        entry_points=[CallbackQueryHandler(edit_ds_mulai, pattern="^edit_ds_")],
        states={
            EDIT_DS_F: [MessageHandler(filters.TEXT & ~filters.COMMAND, edit_ds_f)],
            EDIT_DS_V: [MessageHandler(filters.TEXT & ~filters.COMMAND, edit_ds_v)],
        },
        fallbacks=[CommandHandler("batal", batal)],
        name="eds", persistent=False,
    )

async def edit_ds_mulai(update, context):
    await update.callback_query.answer()
    did = int(update.callback_query.data.split("_")[2])
    d = ds_get(did)
    context.user_data.clear()
    context.user_data['edit_id'] = did
    kb = ReplyKeyboardMarkup([["📱 HP","📧 Email"],["⏰ Expired","📦 Paket"],["📝 Catatan"]], one_time_keyboard=True, resize_keyboard=True)
    await update.callback_query.message.reply_text(
        f"✏️ *Edit Disney+*\n📧 {d['email']}\n\nPilih yang mau diedit:",
        parse_mode='Markdown', reply_markup=kb
    )
    return EDIT_DS_F

DS_MAP = {"📱 hp":"no_hp","📧 email":"email","⏰ expired":"expired_langganan","📦 paket":"nama_paket","📝 catatan":"catatan"}

async def edit_ds_f(update, context):
    f = update.message.text.strip().lower()
    db_f = DS_MAP.get(f)
    if not db_f:
        await update.message.reply_text("❌ Pilih dari tombol.")
        return EDIT_DS_F
    context.user_data['ef'] = db_f
    hint = "\n_(contoh: 24 Maret 2027)_" if db_f == 'expired_langganan' else ""
    await update.message.reply_text(f"Masukkan nilai baru:{hint}", parse_mode='Markdown', reply_markup=ReplyKeyboardRemove())
    return EDIT_DS_V

async def edit_ds_v(update, context):
    value = update.message.text.strip()
    if context.user_data['ef'] == 'expired_langganan':
        tgl = validasi_tgl(value)
        if not tgl:
            await update.message.reply_text("❌ Format salah! Contoh: 24 Maret 2027")
            return EDIT_DS_V
        value = tgl
    ds_update(context.user_data['edit_id'], {context.user_data['ef']: value})
    await update.message.reply_text("✅ Berhasil diupdate!")
    context.user_data.clear()
    return ConversationHandler.END

# ── EDIT PERANGKAT ────────────────────────────────────────

def conv_edit_perangkat():
    return ConversationHandler(
        entry_points=[CallbackQueryHandler(edit_pg_mulai, pattern="^edit_perangkat_")],
        states={
            EDIT_PG_F: [MessageHandler(filters.TEXT & ~filters.COMMAND, edit_pg_f)],
            EDIT_PG_V: [MessageHandler(filters.TEXT & ~filters.COMMAND, edit_pg_v)],
        },
        fallbacks=[CommandHandler("batal", batal)],
        name="epg", persistent=False,
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
    return EDIT_PG_F

PG_MAP = {"📱 nama":"nama","⏰ expired":"expired"}

async def edit_pg_f(update, context):
    f = update.message.text.strip().lower()
    db_f = PG_MAP.get(f)
    if not db_f:
        await update.message.reply_text("❌ Pilih dari tombol.")
        return EDIT_PG_F
    context.user_data['ef'] = db_f
    await update.message.reply_text("Masukkan nilai baru:", reply_markup=ReplyKeyboardRemove())
    return EDIT_PG_V

async def edit_pg_v(update, context):
    value = update.message.text.strip()
    if context.user_data['ef'] == 'expired':
        tgl = validasi_tgl(value)
        if not tgl and value != '-':
            await update.message.reply_text("❌ Format salah! Contoh: 9 Mei 2026")
            return EDIT_PG_V
        value = tgl or ''
    perangkat_update(context.user_data['edit_id'], {context.user_data['ef']: value})
    await update.message.reply_text("✅ Perangkat berhasil diupdate!")
    context.user_data.clear()
    return ConversationHandler.END

# ── PERPANJANG DISNEY ─────────────────────────────────────

def conv_perp_disney():
    return ConversationHandler(
        entry_points=[CallbackQueryHandler(perp_ds_mulai, pattern="^perp_ds_")],
        states={PERP_DS: [MessageHandler(filters.TEXT & ~filters.COMMAND, perp_ds_tgl)]},
        fallbacks=[CommandHandler("batal", batal)],
        name="pds", persistent=False,
    )

async def perp_ds_mulai(update, context):
    await update.callback_query.answer()
    did = int(update.callback_query.data.split("_")[2])
    d = ds_get(did)
    context.user_data.clear()
    context.user_data['pid'] = did
    await update.callback_query.message.reply_text(
        f"🔄 *Perpanjang Disney+*\n📧 {d['email']}\nExpired sekarang: {format_tgl(d['expired_langganan'])}\n\nMasukkan *expired baru*:\n_(contoh: 24 Maret 2028)_",
        parse_mode='Markdown', reply_markup=ReplyKeyboardRemove()
    )
    return PERP_DS

async def perp_ds_tgl(update, context):
    tgl = validasi_tgl(update.message.text.strip())
    if not tgl:
        await update.message.reply_text("❌ Format salah! Contoh: 24 Maret 2028")
        return PERP_DS
    ds_update(context.user_data['pid'], {'expired_langganan': tgl})
    await update.message.reply_text(f"✅ *Disney+ berhasil diperpanjang!*\n\n⏰ Expired baru: {format_tgl(tgl)}", parse_mode='Markdown')
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
        name="tyt", persistent=False,
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
    await update.message.reply_text("*3/4* — *Expired langganan*:\n_(contoh: 3 Mei 2026)_", parse_mode='Markdown')
    return YT_EXPIRED

async def yt_expired(update, context):
    tgl = validasi_tgl(update.message.text.strip())
    if not tgl:
        await update.message.reply_text("❌ Format salah! Contoh: 3 Mei 2026")
        return YT_EXPIRED
    context.user_data['expired'] = tgl
    await update.message.reply_text("*4/4* — *Catatan*:\n_(ketik '-' jika tidak ada)_", parse_mode='Markdown')
    return YT_CATATAN

async def yt_catatan(update, context):
    context.user_data['catatan'] = update.message.text.strip()
    yid = yt_add(context.user_data)
    await update.message.reply_text(
        f"✅ *Akun YouTube berhasil ditambahkan!*\n\n📧 {context.user_data['email']}\n⏰ {format_tgl(context.user_data['expired'])}\n🆔 ID: #{yid}",
        parse_mode='Markdown', reply_markup=ReplyKeyboardRemove()
    )
    context.user_data.clear()
    return ConversationHandler.END

def conv_edit_youtube():
    return ConversationHandler(
        entry_points=[CallbackQueryHandler(edit_yt_mulai, pattern="^edit_yt_")],
        states={
            EDIT_YT_F: [MessageHandler(filters.TEXT & ~filters.COMMAND, edit_yt_f)],
            EDIT_YT_V: [MessageHandler(filters.TEXT & ~filters.COMMAND, edit_yt_v)],
        },
        fallbacks=[CommandHandler("batal", batal)],
        name="eyt", persistent=False,
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
    return EDIT_YT_F

YT_MAP = {"📧 email":"email","🔑 password":"password","⏰ expired":"expired","📝 catatan":"catatan"}

async def edit_yt_f(update, context):
    f = update.message.text.strip().lower()
    db_f = YT_MAP.get(f)
    if not db_f:
        await update.message.reply_text("❌ Pilih dari tombol.")
        return EDIT_YT_F
    context.user_data['ef'] = db_f
    await update.message.reply_text("Masukkan nilai baru:", reply_markup=ReplyKeyboardRemove())
    return EDIT_YT_V

async def edit_yt_v(update, context):
    value = update.message.text.strip()
    if context.user_data['ef'] == 'expired':
        tgl = validasi_tgl(value)
        if not tgl:
            await update.message.reply_text("❌ Format salah! Contoh: 3 Mei 2026")
            return EDIT_YT_V
        value = tgl
    yt_update(context.user_data['edit_id'], {context.user_data['ef']: value})
    await update.message.reply_text("✅ Berhasil diupdate!")
    context.user_data.clear()
    return ConversationHandler.END

def conv_perp_youtube():
    return ConversationHandler(
        entry_points=[CallbackQueryHandler(perp_yt_mulai, pattern="^perp_yt_")],
        states={PERP_YT: [MessageHandler(filters.TEXT & ~filters.COMMAND, perp_yt_tgl)]},
        fallbacks=[CommandHandler("batal", batal)],
        name="pyt", persistent=False,
    )

async def perp_yt_mulai(update, context):
    await update.callback_query.answer()
    yid = int(update.callback_query.data.split("_")[2])
    y = yt_get(yid)
    context.user_data.clear()
    context.user_data['pid'] = yid
    await update.callback_query.message.reply_text(
        f"🔄 *Perpanjang YouTube*\n📧 {y['email']}\nExpired sekarang: {format_tgl(y['expired'])}\n\nMasukkan *expired baru*:\n_(contoh: 3 Mei 2027)_",
        parse_mode='Markdown', reply_markup=ReplyKeyboardRemove()
    )
    return PERP_YT

async def perp_yt_tgl(update, context):
    tgl = validasi_tgl(update.message.text.strip())
    if not tgl:
        await update.message.reply_text("❌ Format salah! Contoh: 3 Mei 2027")
        return PERP_YT
    yt_update(context.user_data['pid'], {'expired': tgl})
    await update.message.reply_text(f"✅ *YouTube berhasil diperpanjang!*\n\n⏰ Expired baru: {format_tgl(tgl)}", parse_mode='Markdown')
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
    await update.message.reply_text("🔍 *Cari Akun*\n\nMasukkan keyword:\n_(nama, email, HP, atau nama perangkat)_", parse_mode='Markdown')
    return CARI_INPUT

async def cari_proses(update, context):
    kw = update.message.text.strip().lower()
    teks = f"🔍 *Hasil Cari: '{kw}'*\n━━━━━━━━━━━━━━━━━━━━\n\n"
    kb = []
    ada = False

    for n in nf_all():
        if kw in n['email'].lower():
            ada = True
            teks += f"🎬 `{n['email']}`\n"
            kb.append([InlineKeyboardButton(f"🎬 {n['email']}", callback_data=f"nf_detail_{n['id']}")])
        for p in profil_all(n['id']):
            if kw in p['nama'].lower():
                ada = True
                teks += f"👤 *{p['nama']}* (Profil {p['nomor']}) — {n['email']}\n"

    for d in ds_all():
        if kw in d['email'].lower() or kw in (d['no_hp'] or '').lower():
            ada = True
            teks += f"🏰 `{d['email']}`\n"
            kb.append([InlineKeyboardButton(f"🏰 {d['email']}", callback_data=f"ds_detail_{d['id']}")])
        for p in perangkat_all(d['id']):
            if kw in p['nama'].lower():
                ada = True
                teks += f"📱 *{p['nama']}* — {d['email']}\n"

    for y in yt_all():
        if kw in y['email'].lower():
            ada = True
            teks += f"📺 `{y['email']}`\n"
            kb.append([InlineKeyboardButton(f"📺 {y['email']}", callback_data=f"yt_detail_{y['id']}")])

    if not ada:
        teks += "❌ Tidak ada hasil yang ditemukan."

    kb.append([InlineKeyboardButton("« Menu Utama", callback_data="start_menu")])
    await update.message.reply_text(teks, parse_mode='Markdown', reply_markup=InlineKeyboardMarkup(kb))
    return ConversationHandler.END
