import os
import psycopg2
import psycopg2.extras
from dotenv import load_dotenv
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

def get_conn():
    conn = psycopg2.connect(DATABASE_URL)
    return conn

def init_db():
    conn = get_conn()
    c = conn.cursor()

    c.execute('''CREATE TABLE IF NOT EXISTS netflix (
        id SERIAL PRIMARY KEY,
        email TEXT NOT NULL,
        password TEXT,
        tgl_ubah_pw TEXT,
        metode_bayar TEXT,
        catatan TEXT,
        status TEXT DEFAULT 'aktif',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')

    c.execute('''CREATE TABLE IF NOT EXISTS netflix_profil (
        id SERIAL PRIMARY KEY,
        netflix_id INTEGER NOT NULL,
        nomor INTEGER NOT NULL,
        nama TEXT NOT NULL,
        pin TEXT,
        expired TEXT,
        status TEXT DEFAULT 'aktif',
        FOREIGN KEY (netflix_id) REFERENCES netflix(id) ON DELETE CASCADE
    )''')

    c.execute('''CREATE TABLE IF NOT EXISTS disney (
        id SERIAL PRIMARY KEY,
        nama_paket TEXT DEFAULT 'DISNEY 1 BULAN SHARING',
        no_hp TEXT,
        email TEXT NOT NULL,
        expired_langganan TEXT NOT NULL,
        catatan TEXT,
        status TEXT DEFAULT 'aktif',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')

    c.execute('''CREATE TABLE IF NOT EXISTS disney_perangkat (
        id SERIAL PRIMARY KEY,
        disney_id INTEGER NOT NULL,
        nama TEXT NOT NULL,
        expired TEXT,
        status TEXT DEFAULT 'aktif',
        FOREIGN KEY (disney_id) REFERENCES disney(id) ON DELETE CASCADE
    )''')

    c.execute('''CREATE TABLE IF NOT EXISTS youtube (
        id SERIAL PRIMARY KEY,
        email TEXT NOT NULL,
        password TEXT,
        expired TEXT NOT NULL,
        catatan TEXT,
        status TEXT DEFAULT 'aktif',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')

    c.execute('''CREATE TABLE IF NOT EXISTS pengingat_log (
        id SERIAL PRIMARY KEY,
        tipe TEXT NOT NULL,
        ref_id INTEGER NOT NULL,
        jenis TEXT NOT NULL,
        tanggal TEXT NOT NULL
    )''')

    conn.commit()
    conn.close()
    print("✅ Database PostgreSQL siap!")

# ══ HELPERS ═══════════════════════════════════════════════

def fetchone(sql, params=()):
    conn = get_conn()
    c = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    c.execute(sql, params)
    r = c.fetchone()
    conn.close()
    return dict(r) if r else None

def fetchall(sql, params=()):
    conn = get_conn()
    c = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    c.execute(sql, params)
    r = c.fetchall()
    conn.close()
    return [dict(x) for x in r]

def execute(sql, params=()):
    conn = get_conn()
    c = conn.cursor()
    c.execute(sql, params)
    conn.commit()
    conn.close()

def insert(sql, params=()):
    conn = get_conn()
    c = conn.cursor()
    c.execute(sql + " RETURNING id", params)
    rid = c.fetchone()[0]
    conn.commit()
    conn.close()
    return rid

# ══ NETFLIX ═══════════════════════════════════════════════

def nf_all(status='aktif'):
    if status:
        return fetchall("SELECT * FROM netflix WHERE status=%s ORDER BY id DESC", (status,))
    return fetchall("SELECT * FROM netflix ORDER BY id DESC")

def nf_get(nid):
    return fetchone("SELECT * FROM netflix WHERE id=%s", (nid,))

def nf_add(data):
    return insert(
        "INSERT INTO netflix (email, password, tgl_ubah_pw, metode_bayar, catatan) VALUES (%s,%s,%s,%s,%s)",
        (data.get('email'), data.get('password',''), data.get('tgl_ubah_pw',''), data.get('metode_bayar',''), data.get('catatan',''))
    )

def nf_update(nid, data):
    fields = ', '.join([f"{k}=%s" for k in data.keys()])
    execute(f"UPDATE netflix SET {fields} WHERE id=%s", list(data.values())+[nid])

def nf_delete(nid):
    execute("DELETE FROM netflix WHERE id=%s", (nid,))

def profil_all(nid):
    return fetchall("SELECT * FROM netflix_profil WHERE netflix_id=%s ORDER BY nomor", (nid,))

def profil_get(pid):
    return fetchone("SELECT * FROM netflix_profil WHERE id=%s", (pid,))

def profil_add(data):
    return insert(
        "INSERT INTO netflix_profil (netflix_id, nomor, nama, pin, expired) VALUES (%s,%s,%s,%s,%s)",
        (data.get('netflix_id'), data.get('nomor'), data.get('nama'), data.get('pin',''), data.get('expired',''))
    )

def profil_update(pid, data):
    fields = ', '.join([f"{k}=%s" for k in data.keys()])
    execute(f"UPDATE netflix_profil SET {fields} WHERE id=%s", list(data.values())+[pid])

def profil_delete(pid):
    execute("DELETE FROM netflix_profil WHERE id=%s", (pid,))

# ══ DISNEY+ ═══════════════════════════════════════════════

def ds_all(status='aktif'):
    if status:
        return fetchall("SELECT * FROM disney WHERE status=%s ORDER BY expired_langganan ASC", (status,))
    return fetchall("SELECT * FROM disney ORDER BY expired_langganan ASC")

def ds_get(did):
    return fetchone("SELECT * FROM disney WHERE id=%s", (did,))

def ds_add(data):
    return insert(
        "INSERT INTO disney (nama_paket, no_hp, email, expired_langganan, catatan) VALUES (%s,%s,%s,%s,%s)",
        (data.get('nama_paket','DISNEY 1 BULAN SHARING'), data.get('no_hp',''), data.get('email'), data.get('expired_langganan'), data.get('catatan',''))
    )

def ds_update(did, data):
    fields = ', '.join([f"{k}=%s" for k in data.keys()])
    execute(f"UPDATE disney SET {fields} WHERE id=%s", list(data.values())+[did])

def ds_delete(did):
    execute("DELETE FROM disney WHERE id=%s", (did,))

def perangkat_all(did):
    return fetchall("SELECT * FROM disney_perangkat WHERE disney_id=%s AND status='aktif' ORDER BY id", (did,))

def perangkat_get(rid):
    return fetchone("SELECT * FROM disney_perangkat WHERE id=%s", (rid,))

def perangkat_add(data):
    return insert(
        "INSERT INTO disney_perangkat (disney_id, nama, expired) VALUES (%s,%s,%s)",
        (data.get('disney_id'), data.get('nama'), data.get('expired',''))
    )

def perangkat_update(rid, data):
    fields = ', '.join([f"{k}=%s" for k in data.keys()])
    execute(f"UPDATE disney_perangkat SET {fields} WHERE id=%s", list(data.values())+[rid])

def perangkat_delete(rid):
    execute("DELETE FROM disney_perangkat WHERE id=%s", (rid,))

# ══ YOUTUBE ════════════════════════════════════════════════

def yt_all(status='aktif'):
    if status:
        return fetchall("SELECT * FROM youtube WHERE status=%s ORDER BY expired ASC", (status,))
    return fetchall("SELECT * FROM youtube ORDER BY expired ASC")

def yt_get(yid):
    return fetchone("SELECT * FROM youtube WHERE id=%s", (yid,))

def yt_add(data):
    return insert(
        "INSERT INTO youtube (email, password, expired, catatan) VALUES (%s,%s,%s,%s)",
        (data.get('email'), data.get('password',''), data.get('expired'), data.get('catatan',''))
    )

def yt_update(yid, data):
    fields = ', '.join([f"{k}=%s" for k in data.keys()])
    execute(f"UPDATE youtube SET {fields} WHERE id=%s", list(data.values())+[yid])

def yt_delete(yid):
    execute("DELETE FROM youtube WHERE id=%s", (yid,))

# ══ PENGINGAT ══════════════════════════════════════════════

def sudah_kirim(tipe, ref_id, jenis, tgl):
    r = fetchone("SELECT id FROM pengingat_log WHERE tipe=%s AND ref_id=%s AND jenis=%s AND tanggal=%s", (tipe, ref_id, jenis, tgl))
    return r is not None

def simpan_log(tipe, ref_id, jenis, tgl):
    insert("INSERT INTO pengingat_log (tipe, ref_id, jenis, tanggal) VALUES (%s,%s,%s,%s)", (tipe, ref_id, jenis, tgl))

# ══ STATISTIK ══════════════════════════════════════════════

def get_stats():
    nf = fetchone("SELECT COUNT(*) as n FROM netflix WHERE status='aktif'")['n']
    pr = fetchone("SELECT COUNT(*) as n FROM netflix_profil WHERE status='aktif'")['n']
    ds = fetchone("SELECT COUNT(*) as n FROM disney WHERE status='aktif'")['n']
    pg = fetchone("SELECT COUNT(*) as n FROM disney_perangkat WHERE status='aktif'")['n']
    yt = fetchone("SELECT COUNT(*) as n FROM youtube WHERE status='aktif'")['n']
    return {"netflix":nf,"profil":pr,"disney":ds,"perangkat":pg,"youtube":yt}

# ══ BACKUP ═════════════════════════════════════════════════

def get_backup_text():
    from utils import format_tgl, sisa_hari, status_icon
    from datetime import date
    teks = f"📋 *BACKUP DATA — {date.today().strftime('%d %B %Y')}*\n"
    teks += "━━━━━━━━━━━━━━━━━━━━\n\n"

    teks += "🎬 *NETFLIX*\n"
    for n in nf_all():
        teks += f"┌ 📧 `{n['email']}`\n"
        teks += f"├ 🔑 `{n['password'] or '-'}`\n"
        teks += f"├ 📅 Ubah PW: {n['tgl_ubah_pw'] or '-'}\n"
        teks += f"└ 👥 Profil:\n"
        for p in profil_all(n['id']):
            sisa = sisa_hari(p['expired']) if p['expired'] else 999
            icon = status_icon(sisa)
            expired_str = format_tgl(p['expired']) if p['expired'] else 'Aktif'
            teks += f"   {icon} {p['nomor']}. {p['nama']} | {p['pin'] or '-'} | {expired_str}\n"
        teks += "\n"

    teks += "🏰 *DISNEY+*\n"
    for d in ds_all():
        teks += f"┌ 📦 {d['nama_paket']}\n"
        teks += f"├ 📱 {d['no_hp'] or '-'}\n"
        teks += f"├ 📧 `{d['email']}`\n"
        teks += f"├ ⏰ {format_tgl(d['expired_langganan'])}\n"
        teks += f"└ 📱 Perangkat:\n"
        for p in perangkat_all(d['id']):
            sisa = sisa_hari(p['expired']) if p['expired'] else 999
            icon = status_icon(sisa)
            teks += f"   {icon} {p['nama']} | {format_tgl(p['expired']) if p['expired'] else '-'}\n"
        teks += "\n"

    teks += "📺 *YOUTUBE*\n"
    for y in yt_all():
        sisa = sisa_hari(y['expired'])
        icon = status_icon(sisa)
        teks += f"┌ 📧 `{y['email']}`\n"
        teks += f"├ 🔑 `{y['password'] or '-'}`\n"
        teks += f"└ {icon} Expired: {format_tgl(y['expired'])}\n\n"

    return teks
