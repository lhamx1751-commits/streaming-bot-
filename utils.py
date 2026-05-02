from datetime import datetime, date
import os, re
from dotenv import load_dotenv
load_dotenv()

ADMIN_ID = int(os.getenv("ADMIN_ID", "0"))

def cek_admin(uid): return uid == ADMIN_ID

def sisa_hari(exp):
    if not exp: return 999
    try: return (datetime.strptime(exp, "%Y-%m-%d").date() - date.today()).days
    except: return -999

def format_tgl(tgl):
    if not tgl: return '-'
    try: return datetime.strptime(tgl, "%Y-%m-%d").strftime("%d %B %Y")
    except: return tgl

def validasi_tgl(tgl):
    if not tgl: return None
    tgl = tgl.strip()

    # Format standar
    for fmt in ["%d-%m-%Y", "%d/%m/%Y", "%Y-%m-%d"]:
        try: return datetime.strptime(tgl, fmt).strftime("%Y-%m-%d")
        except: continue

    # Format natural: "17 mei 2026", "17 may 2026"
    bulan_map = {
        'jan':'01','feb':'02','mar':'03','apr':'04',
        'mei':'05','may':'05','jun':'06','jul':'07',
        'agu':'08','aug':'08','sep':'09','okt':'10','oct':'10',
        'nov':'11','des':'12','dec':'12'
    }
    tgl_lower = tgl.lower().strip()
    # hapus karakter aneh
    tgl_lower = re.sub(r'[^\w\s]', ' ', tgl_lower)
    parts = tgl_lower.split()

    if len(parts) == 3:
        try:
            day = parts[0].zfill(2)
            month = bulan_map.get(parts[1][:3], None)
            year = parts[2]
            if month and len(year) == 4:
                return f"{year}-{month}-{day}"
        except: pass

    # Format "17-05-26" atau "17/05/26"
    match = re.match(r'(\d{1,2})[-/](\d{1,2})[-/](\d{2})$', tgl)
    if match:
        d, m, y = match.groups()
        return f"20{y}-{m.zfill(2)}-{d.zfill(2)}"

    return None

def status_icon(sisa):
    if sisa < 0: return "🔴"
    if sisa <= 3: return "🟡"
    if sisa <= 7: return "🟠"
    return "🟢"

def format_rp(n):
    try: return f"Rp {int(n):,}".replace(",", ".")
    except: return "-"

def parse_bulk_perangkat(text):
    """Parse format bebas untuk bulk perangkat Disney"""
    results = []
    lines = [l.strip() for l in text.strip().split('\n') if l.strip()]

    for line in lines:
        # Hapus nomor di awal: "1.", "1)", "1 "
        line = re.sub(r'^\d+[\.\)]\s*', '', line)
        # Hapus kata "perangkat:", "device:"
        line = re.sub(r'^(perangkat|device)\s*:\s*', '', line, flags=re.IGNORECASE)

        # Coba split dengan |
        if '|' in line:
            parts = [p.strip() for p in line.split('|')]
            nama = parts[0]
            tgl_raw = parts[1] if len(parts) > 1 else ''
        else:
            # Coba pisah nama dan tanggal otomatis
            # Cari pola tanggal di akhir
            tgl_pattern = re.search(r'(\d{1,2}[\s\-/]+\w+[\s\-/]+\d{2,4}|\d{1,2}[-/]\d{1,2}[-/]\d{2,4})$', line)
            if tgl_pattern:
                tgl_raw = tgl_pattern.group(1)
                nama = line[:tgl_pattern.start()].strip()
            else:
                nama = line
                tgl_raw = ''

        nama = nama.strip()
        tgl = validasi_tgl(tgl_raw) if tgl_raw else ''

        if nama:
            results.append({'nama': nama, 'expired': tgl})

    return results

def parse_bulk_profil(text):
    """Parse format bebas untuk bulk profil Netflix"""
    results = []
    lines = [l.strip() for l in text.strip().split('\n') if l.strip()]

    for i, line in enumerate(lines, 1):
        # Hapus awalan: "1.", "Profil 1:", "Profil :"
        line = re.sub(r'^(\d+[\.\)]\s*)', '', line)
        line = re.sub(r'^profil\s*\d*\s*:\s*', '', line, flags=re.IGNORECASE)

        # Split dengan |
        parts = [p.strip() for p in line.split('|')]

        # Cek apakah parts[0] adalah nomor
        nomor = i  # default pakai urutan
        start = 0
        if parts and parts[0].isdigit():
            nomor = int(parts[0])
            start = 1

        nama = parts[start].strip() if len(parts) > start else ''
        pin = parts[start+1].strip() if len(parts) > start+1 else ''
        tgl_raw = parts[start+2].strip() if len(parts) > start+2 else ''

        tgl = ''
        if tgl_raw.lower() in ['expired', 'exp', 'habis']:
            from datetime import timedelta
            tgl = (date.today() - timedelta(days=1)).strftime("%Y-%m-%d")
        elif tgl_raw:
            tgl = validasi_tgl(tgl_raw) or ''

        if nama:
            results.append({'nomor': nomor, 'nama': nama, 'pin': pin, 'expired': tgl})

    return results
