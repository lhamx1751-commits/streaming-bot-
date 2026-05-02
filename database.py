import os, sqlite3
from dotenv import load_dotenv
load_dotenv()

# Coba PostgreSQL dulu, kalau gagal pakai SQLite
DATABASE_URL = os.getenv("DATABASE_URL", "")
USE_PG = bool(DATABASE_URL)

if USE_PG:
    import urllib.parse as urlparse
    url = urlparse.urlparse(DATABASE_URL)
    PG_CONFIG = {
        "host": url.hostname,
        "port": url.port or 5432,
        "database": url.path[1:],
        "user": url.username,
        "password": url.password,
    }

DB_PATH = os.getenv("DB_PATH", "streaming.db")

def get_conn():
    if USE_PG:
        import psycopg2
        import psycopg2.extras
        conn = psycopg2.connect(**PG_CONFIG)
        conn.autocommit = False
        return conn
    else:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        return conn

def fetchone(sql, params=()):
    conn = get_conn()
    try:
        if USE_PG:
            import psycopg2.extras
            # Convert $1 style to %s for psycopg2
            sql = sql.replace('$1','%s').replace('$2','%s').replace('$3','%s').replace('$4','%s').replace('$5','%s')
            c = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
            c.execute(sql, params)
            r = c.fetchone()
            return dict(r) if r else None
        else:
            c = conn.cursor()
            c.execute(sql, params)
            r = c.fetchone()
            return dict(r) if r else None
    finally:
        conn.close()

def fetchall(sql, params=()):
    conn = get_conn()
    try:
        if USE_PG:
            import psycopg2.extras
            sql = sql.replace('$1','%s').replace('$2','%s').replace('$3','%s').replace('$4','%s').replace('$5','%s')
            c = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
            c.execute(sql, params)
            return [dict(r) for r in c.fetchall()]
        else:
            c = conn.cursor()
            c.execute(sql, params)
            return [dict(r) for r in c.fetchall()]
    finally:
        conn.close()

def execute(sql, params=()):
    conn = get_conn()
    try:
        if USE_PG:
            sql = sql.replace('$1','%s').replace('$2','%s').replace('$3','%s').replace('$4','%s').replace('$5','%s')
        c = conn.cursor()
        c.execute(sql, params)
        conn.commit()
    finally:
        conn.close()

def insert(sql, params=()):
    conn = get_conn()
    try:
        if USE_PG:
            sql = sql.replace('$1','%s').replace('$2','%s').replace('$3','%s').replace('$4','%s').replace('$5','%s')
            sql = sql + " RETURNING id"
            import psycopg2.extras
            c = conn.cursor()
            c.execute(sql, params)
            rid = c.fetchone()[0]
            conn.commit()
            return rid
        else:
            sql_sqlite = sql + ""
            c = conn.cursor()
            c.execute(sql_sqlite, params)
            conn.commit()
            return c.lastrowid
    finally:
        conn.close()

def init_db():
    conn = get_conn()
    c = conn.cursor()
    if USE_PG:
        serial = "SERIAL"
        ts = "TIMESTAMP DEFAULT CURRENT_TIMESTAMP"
    else:
        serial = "INTEGER"
        ts = "TIMESTAMP DEFAULT CURRENT_TIMESTAMP"

    tables = [
        f'''CREATE TABLE IF NOT EXISTS netflix (
            id {serial} PRIMARY KEY,
            email TEXT NOT NULL,
            password TEXT,
            tgl_ubah_pw TEXT,
            metode_bayar TEXT,
            catatan TEXT,
            status TEXT DEFAULT 'aktif',
            created_at {ts}
        )''',
        f'''CREATE TABLE IF NOT EXISTS netflix_profil (
            id {serial} PRIMARY KEY,
            netflix_id INTEGER NOT NULL,
            nomor INTEGER NOT NULL,
            nama TEXT NOT NULL,
            pin TEXT,
            expired TEXT,
            status TEXT DEFAULT 'aktif'
        )''',
        f'''CREATE TABLE IF NOT EXISTS disney (
            id {serial} PRIMARY KEY,
            nama_paket TEXT DEFAULT 'DISNEY 1 BULAN SHARING',
            no_hp TEXT,
            email TEXT NOT NULL,
            expired_langganan TEXT NOT NULL,
            catatan TEXT,
            status TEXT DEFAULT 'aktif',
            created_at {ts}
        )''',
        f'''CREATE TABLE IF NOT EXISTS disney_perangkat (
            id {serial} PRIMARY KEY,
            disney_id INTEGER NOT NULL,
            nama TEXT NOT NULL,
            expired TEXT,
            status TEXT DEFAULT 'aktif'
        )''',
        f'''CREATE TABLE IF NOT EXISTS youtube (
            id {serial} PRIMARY KEY,
            email TEXT NOT NULL,
            password TEXT,
            expired TEXT NOT NULL,
            catatan TEXT,
            status TEXT DEFAULT 'aktif',
            created_at {ts}
        )''',
        f'''CREATE TABLE IF NOT EXISTS pengingat_log (
            id {serial} PRIMARY KEY,
            tipe TEXT NOT NULL,
            ref_id INTEGER NOT NULL,
            jenis TEXT NOT NULL,
            tanggal TEXT NOT NULL
        )''',
    ]
    for t in tables:
        c.execute(t)
    conn.commit()
    conn.close()
    print(f"✅ Database {'PostgreSQL' if USE_PG else 'SQLite'} siap!")

# ══ NETFLIX ═══════════════════════════════════════════════

def nf_all(status='aktif'):
    if status:
        return fetchall("SELECT * FROM netflix WHERE status=$1 ORDER BY id DESC", (status,))
    return fetchall("SELECT * FROM netflix ORDER BY id DESC")

def nf_get(nid): return fetchone("SELECT * FROM netflix WHERE id=$1", (nid,))

def nf_add(data):
    return insert(
        "INSERT INTO netflix (email, password, tgl_ubah_pw, metode_bayar, catatan) VALUES ($1,$2,$3,$4,$5)",
        (data.get('email'), data.get('password',''), data.get('tgl_ubah_pw',''), data.get('metode_bayar',''), data.get('catatan',''))
    )

def nf_update(nid, data):
    for k, v in data.items():
        execute(f"UPDATE netflix SET {k}=$1 WHERE id=$2", (v, nid))

def nf_delete(nid):
    execute("DELETE FROM netflix_profil WHERE netflix_id=$1", (nid,))
    execute("DELETE FROM netflix WHERE id=$1", (nid,))

def profil_all(nid): return fetchall("SELECT * FROM netflix_profil WHERE netflix_id=$1 ORDER BY nomor", (nid,))
def profil_get(pid): return fetchone("SELECT * FROM netflix_profil WHERE id=$1", (pid,))

def profil_add(data):
    return insert(
        "INSERT INTO netflix_profil (netflix_id, nomor, nama, pin, expired) VALUES ($1,$2,$3,$4,$5)",
        (data.get('netflix_id'), data.get('nomor'), data.get('nama'), data.get('pin',''), data.get('expired',''))
    )

def profil_update(pid, data):
    for k, v in data.items():
        execute(f"UPDATE netflix_profil SET {k}=$1 WHERE id=$2", (v, pid))

def profil_delete(pid): execute("DELETE FROM netflix_profil WHERE id=$1", (pid,))

# ══ DISNEY+ ═══════════════════════════════════════════════

def ds_all(status='aktif'):
    if status:
        return fetchall("SELECT * FROM disney WHERE status=$1 ORDER BY expired_langganan ASC", (status,))
    return fetchall("SELECT * FROM disney ORDER BY expired_langganan ASC")

def ds_get(did): return fetchone("SELECT * FROM disney WHERE id=$1", (did,))

def ds_add(data):
    return insert(
        "INSERT INTO disney (nama_paket, no_hp, email, expired_langganan, catatan) VALUES ($1,$2,$3,$4,$5)",
        (data.get('nama_paket','DISNEY 1 BULAN SHARING'), data.get('no_hp',''), data.get('email'), data.get('expired_langganan'), data.get('catatan',''))
    )

def ds_update(did, data):
    for k, v in data.items():
        execute(f"UPDATE disney SET {k}=$1 WHERE id=$2", (v, did))

def ds_delete(did):
    execute("DELETE FROM disney_perangkat WHERE disney_id=$1", (did,))
    execute("DELETE FROM disney WHERE id=$1", (did,))

def perangkat_all(did): return fetchall("SELECT * FROM disney_perangkat WHERE disney_id=$1 AND status='aktif' ORDER BY id", (did,))
def perangkat_get(rid): return fetchone("SELECT * FROM disney_perangkat WHERE id=$1", (rid,))

def perangkat_add(data):
    return insert(
        "INSERT INTO disney_perangkat (disney_id, nama, expired) VALUES ($1,$2,$3)",
        (data.get('disney_id'), data.get('nama'), data.get('expired',''))
    )

def perangkat_update(rid, data):
    for k, v in data.items():
        execute(f"UPDATE disney_perangkat SET {k}=$1 WHERE id=$2", (v, rid))

def perangkat_delete(rid): execute("DELETE FROM disney_perangkat WHERE id=$1", (rid,))

# ══ YOUTUBE ════════════════════════════════════════════════

def yt_all(status='aktif'):
    if status:
        return fetchall("SELECT * FROM youtube WHERE status=$1 ORDER BY expired ASC", (status,))
    return fetchall("SELECT * FROM youtube ORDER BY expired ASC")

def yt_get(yid): return fetchone("SELECT * FROM youtube WHERE id=$1", (yid,))

def yt_add(data):
    return insert(
        "INSERT INTO youtube (email, password, expired, catatan) VALUES ($1,$2,$3,$4)",
        (data.get('email'), data.get('password',''), data.get('expired'), data.get('catatan',''))
    )

def yt_update(yid, data):
    for k, v in data.items():
        execute(f"UPDATE youtube SET {k}=$1 WHERE id=$2", (v, yid))

def yt_delete(yid): execute("DELETE FROM youtube WHERE id=$1", (yid,))

# ══ PENGINGAT ══════════════════════════════════════════════

def sudah_kirim(tipe, ref_id, jenis, tgl):
    return fetchone("SELECT id FROM pengingat_log WHERE tipe=$1 AND ref_id=$2 AND jenis=$3 AND tanggal=$4", (tipe, ref_id, jenis, tgl)) is not None

def simpan_log(tipe, ref_id, jenis, tgl):
    insert("INSERT INTO pengingat_log (tipe, ref_id, jenis, tanggal) VALUES ($1,$2,$3,$4)", (tipe, ref_id, jenis, tgl))

def get_stats():
    nf = (fetchone("SELECT COUNT(*) as n FROM netflix WHERE status='aktif'") or {}).get('n', 0)
    pr = (fetchone("SELECT COUNT(*) as n FROM netflix_profil WHERE status='aktif'") or {}).get('n', 0)
    ds = (fetchone("SELECT COUNT(*) as n FROM disney WHERE status='aktif'") or {}).get('n', 0)
    pg = (fetchone("SELECT COUNT(*) as n FROM disney_perangkat WHERE status='aktif'") or {}).get('n', 0)
    yt = (fetchone("SELECT COUNT(*) as n FROM youtube WHERE status='aktif'") or {}).get('n', 0)
    return {"netflix":nf,"profil":pr,"disney":ds,"perangkat":pg,"youtube":yt}

def get_backup_text():
    from utils import format_tgl, sisa_hari, status_icon
    from datetime import date
    teks = f"📋 *BACKUP DATA — {date.today().strftime('%d %B %Y')}*\n━━━━━━━━━━━━━━━━━━━━\n\n"
    teks += "🎬 *NETFLIX*\n"
    for n in nf_all():
        teks += f"┌ 📧 `{n['email']}`\n├ 🔑 `{n.get('password') or '-'}`\n├ 📅 {n.get('tgl_ubah_pw') or '-'}\n└ 👥 Profil:\n"
        for p in profil_all(n['id']):
            sisa = sisa_hari(p.get('expired','')) if p.get('expired') else 999
            teks += f"   {status_icon(sisa)} {p['nomor']}. {p['nama']} | {p.get('pin') or '-'} | {format_tgl(p.get('expired','')) if p.get('expired') else 'Aktif'}\n"
        teks += "\n"
    teks += "🏰 *DISNEY+*\n"
    for d in ds_all():
        teks += f"┌ 📦 {d['nama_paket']}\n├ 📱 {d.get('no_hp') or '-'}\n├ 📧 `{d['email']}`\n├ ⏰ {format_tgl(d['expired_langganan'])}\n└ 📱 Perangkat:\n"
        for p in perangkat_all(d['id']):
            sisa = sisa_hari(p.get('expired','')) if p.get('expired') else 999
            teks += f"   {status_icon(sisa)} {p['nama']} | {format_tgl(p.get('expired','')) if p.get('expired') else '-'}\n"
        teks += "\n"
    teks += "📺 *YOUTUBE*\n"
    for y in yt_all():
        sisa = sisa_hari(y['expired'])
        teks += f"┌ 📧 `{y['email']}`\n├ 🔑 `{y.get('password') or '-'}`\n└ {status_icon(sisa)} {format_tgl(y['expired'])}\n\n"
    return teks
