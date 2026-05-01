from datetime import datetime, date
import os
from dotenv import load_dotenv
load_dotenv()

ADMIN_ID = int(os.getenv("ADMIN_ID", "0"))

def cek_admin(uid): return uid == ADMIN_ID

def sisa_hari(exp):
    try:
        return (datetime.strptime(exp, "%Y-%m-%d").date() - date.today()).days
    except: return -999

def format_tgl(tgl):
    try: return datetime.strptime(tgl, "%Y-%m-%d").strftime("%d %B %Y")
    except: return tgl or '-'

def validasi_tgl(tgl):
    for fmt in ["%d-%m-%Y", "%d/%m/%Y", "%Y-%m-%d"]:
        try: return datetime.strptime(tgl.strip(), fmt).strftime("%Y-%m-%d")
        except: continue
    return None

def status_icon(sisa):
    if sisa < 0: return "🔴"
    if sisa <= 3: return "🟡"
    if sisa <= 7: return "🟠"
    return "🟢"

def format_rp(n):
    try: return f"Rp {int(n):,}".replace(",", ".")
    except: return "Rp 0"
