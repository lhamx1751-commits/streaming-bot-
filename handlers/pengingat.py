from telegram.ext import ContextTypes
from database import nf_all, ds_all, yt_all, profil_all, perangkat_all, sudah_kirim, simpan_log
from utils import sisa_hari, format_tgl, status_icon
from datetime import datetime
import os, logging

ADMIN_ID = int(os.getenv("ADMIN_ID", "0"))
logger = logging.getLogger(__name__)

async def kirim_laporan_pagi(context: ContextTypes.DEFAULT_TYPE):
    today = datetime.now().strftime("%Y-%m-%d")
    teks = f"☀️ *LAPORAN PAGI — {datetime.now().strftime('%d %B %Y')}*\n━━━━━━━━━━━━━━━━━━━━\n\n"
    ada = False

    # Netflix profil
    for n in nf_all():
        for p in profil_all(n['id']):
            if not p['expired']: continue
            sisa = sisa_hari(p['expired'])
            if sisa <= 7:
                ada = True
                icon = status_icon(sisa)
                label = "Expired HARI INI!" if sisa == 0 else f"{sisa} hari lagi"
                teks += f"{icon} 🎬 *{p['nama']}* (Profil {p['nomor']})\n"
                teks += f"   📧 {n['email']}\n"
                teks += f"   ⏰ {label}\n\n"

    # Disney perangkat
    for d in ds_all():
        for p in perangkat_all(d['id']):
            if not p['expired']: continue
            sisa = sisa_hari(p['expired'])
            if sisa <= 7:
                ada = True
                icon = status_icon(sisa)
                label = "Expired HARI INI!" if sisa == 0 else f"{sisa} hari lagi"
                teks += f"{icon} 📱 *{p['nama']}* (Disney)\n"
                teks += f"   📧 {d['email']}\n"
                teks += f"   ⏰ {label}\n\n"

    # YouTube
    for y in yt_all():
        sisa = sisa_hari(y['expired'])
        if sisa <= 7:
            ada = True
            icon = status_icon(sisa)
            label = "Expired HARI INI!" if sisa == 0 else f"{sisa} hari lagi"
            teks += f"{icon} 📺 *YouTube* — {y['email']}\n"
            teks += f"   ⏰ {label}\n\n"

    if not ada:
        teks += "✅ Semua akun aman! Tidak ada yang akan expired dalam 7 hari."

    try:
        await context.bot.send_message(ADMIN_ID, teks, parse_mode='Markdown')
    except Exception as e:
        logger.error(f"Gagal kirim laporan pagi: {e}")

async def cek_pengingat(context: ContextTypes.DEFAULT_TYPE):
    today = datetime.now().strftime("%Y-%m-%d")

    # Netflix profil
    for n in nf_all():
        for p in profil_all(n['id']):
            if not p['expired']: continue
            sisa = sisa_hari(p['expired'])
            for hari in [7, 3, 1]:
                if sisa == hari:
                    jenis = f"H-{hari}"
                    if not sudah_kirim("nf_profil", p['id'], jenis, today):
                        icon = "🔴" if hari==1 else "🟡" if hari==3 else "🟠"
                        teks = (
                            f"{icon} *PENGINGAT NETFLIX — {jenis}*\n━━━━━━━━━━━━━━━━━━━━\n"
                            f"🎬 Profil {p['nomor']} — *{p['nama']}*\n"
                            f"📧 {n['email']}\n"
                            f"🔑 {n['password']}\n"
                            f"📌 PIN: {p['pin'] or '-'}\n"
                            f"⏰ Expired: {format_tgl(p['expired'])}"
                        )
                        try:
                            await context.bot.send_message(ADMIN_ID, teks, parse_mode='Markdown')
                            simpan_log("nf_profil", p['id'], jenis, today)
                        except Exception as e:
                            logger.error(f"Error: {e}")

    # Disney perangkat
    for d in ds_all():
        for p in perangkat_all(d['id']):
            if not p['expired']: continue
            sisa = sisa_hari(p['expired'])
            for hari in [7, 3, 1]:
                if sisa == hari:
                    jenis = f"H-{hari}"
                    if not sudah_kirim("ds_perangkat", p['id'], jenis, today):
                        icon = "🔴" if hari==1 else "🟡" if hari==3 else "🟠"
                        teks = (
                            f"{icon} *PENGINGAT DISNEY+ — {jenis}*\n━━━━━━━━━━━━━━━━━━━━\n"
                            f"📱 *{p['nama']}*\n"
                            f"📧 {d['email']}\n"
                            f"📱 HP: {d['no_hp'] or '-'}\n"
                            f"⏰ Expired Perangkat: {format_tgl(p['expired'])}"
                        )
                        try:
                            await context.bot.send_message(ADMIN_ID, teks, parse_mode='Markdown')
                            simpan_log("ds_perangkat", p['id'], jenis, today)
                        except Exception as e:
                            logger.error(f"Error: {e}")

    # YouTube
    for y in yt_all():
        sisa = sisa_hari(y['expired'])
        for hari in [7, 3, 1]:
            if sisa == hari:
                jenis = f"H-{hari}"
                if not sudah_kirim("youtube", y['id'], jenis, today):
                    icon = "🔴" if hari==1 else "🟡" if hari==3 else "🟠"
                    teks = (
                        f"{icon} *PENGINGAT YOUTUBE — {jenis}*\n━━━━━━━━━━━━━━━━━━━━\n"
                        f"📺 *{y['email']}*\n"
                        f"🔑 {y['password'] or '-'}\n"
                        f"⏰ Expired: {format_tgl(y['expired'])}"
                    )
                    try:
                        await context.bot.send_message(ADMIN_ID, teks, parse_mode='Markdown')
                        simpan_log("youtube", y['id'], jenis, today)
                    except Exception as e:
                        logger.error(f"Error: {e}")
