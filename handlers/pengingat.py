from telegram.ext import ContextTypes
from database import *
from utils import sisa_hari
from datetime import datetime
import os, logging

ADMIN_ID = int(os.getenv("ADMIN_ID", "0"))
logger = logging.getLogger(__name__)

async def cek_pengingat(context: ContextTypes.DEFAULT_TYPE):
    today = datetime.now().strftime("%Y-%m-%d")

    # Netflix profil
    for n in netflix_get_all():
        for p in profil_get_all(n['id']):
            sisa = sisa_hari(p['expired'])
            for hari in [7, 3, 1]:
                if sisa == hari:
                    jenis = f"H-{hari}"
                    if not sudah_kirim("netflix_profil", p['id'], jenis, today):
                        icon = "🔴" if hari==1 else "🟡" if hari==3 else "🟠"
                        teks = (
                            f"{icon} *PENGINGAT NETFLIX — {jenis}*\n"
                            f"━━━━━━━━━━━━━━━━━━━━\n"
                            f"🎬 Profil {p['nomor_profil']} — {p['nama_profil'] or '-'}\n"
                            f"👤 {p['nama_pelanggan'] or '-'}\n"
                            f"📱 {p['no_hp'] or '-'}\n"
                            f"📧 {n['email']}\n"
                            f"⏰ Expired: {p['expired']}\n"
                            f"💰 Rp {p['harga']:,}"
                        )
                        try:
                            await context.bot.send_message(ADMIN_ID, teks, parse_mode='Markdown')
                            simpan_log("netflix_profil", p['id'], jenis, today)
                        except Exception as e:
                            logger.error(f"Gagal kirim: {e}")

    # Disney+
    for d in disney_get_all():
        sisa = sisa_hari(d['expired_langganan'])
        for hari in [7, 3, 1]:
            if sisa == hari:
                jenis = f"H-{hari}"
                if not sudah_kirim("disney", d['id'], jenis, today):
                    icon = "🔴" if hari==1 else "🟡" if hari==3 else "🟠"
                    teks = (
                        f"{icon} *PENGINGAT DISNEY+ — {jenis}*\n"
                        f"━━━━━━━━━━━━━━━━━━━━\n"
                        f"🏰 {d['email']}\n"
                        f"📱 {d['no_hp'] or '-'}\n"
                        f"⏰ Expired: {d['expired_langganan']}\n"
                        f"💰 Rp {d['harga']:,}"
                    )
                    try:
                        await context.bot.send_message(ADMIN_ID, teks, parse_mode='Markdown')
                        simpan_log("disney", d['id'], jenis, today)
                    except Exception as e:
                        logger.error(f"Gagal kirim: {e}")

    # YouTube
    for y in yt_get_all():
        sisa = sisa_hari(y['expired_langganan'])
        for hari in [7, 3, 1]:
            if sisa == hari:
                jenis = f"H-{hari}"
                if not sudah_kirim("youtube", y['id'], jenis, today):
                    icon = "🔴" if hari==1 else "🟡" if hari==3 else "🟠"
                    teks = (
                        f"{icon} *PENGINGAT YOUTUBE — {jenis}*\n"
                        f"━━━━━━━━━━━━━━━━━━━━\n"
                        f"📺 {y['email_akun']}\n"
                        f"⏰ Expired: {y['expired_langganan']}\n"
                        f"💰 Rp {y['harga']:,}"
                    )
                    try:
                        await context.bot.send_message(ADMIN_ID, teks, parse_mode='Markdown')
                        simpan_log("youtube", y['id'], jenis, today)
                    except Exception as e:
                        logger.error(f"Gagal kirim: {e}")
