import sqlite3, os
from dotenv import load_dotenv
load_dotenv()

DB_PATH = os.getenv("DB_PATH", "streaming.db")

def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_conn()
    c = conn.cursor()

    # NETFLIX
    c.execute('''CREATE TABLE IF NOT EXISTS netflix (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        email TEXT NOT NULL,
        password TEXT NOT NULL,
        tgl_ubah_pw TEXT,
        catatan TEXT,
        status TEXT DEFAULT 'aktif',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')

    c.execute('''CREATE TABLE IF NOT EXISTS netflix_profil (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        netflix_id INTEGER NOT NULL,
        nomor INTEGER NOT NULL,
        nama TEXT NOT NULL,
        pin TEXT,
        expired TEXT,
        status TEXT DEFAULT 'aktif',
        FOREIGN KEY (netflix_id) REFERENCES netflix(id)
    )''')

    # DISNEY+
    c.execute('''CREATE TABLE IF NOT EXISTS disney (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nama_paket TEXT DEFAULT 'DISNEY 1 BULAN SHARING',
        no_hp TEXT,
        email TEXT NOT NULL,
        password TEXT,
        expired_langganan TEXT NOT NULL,
        catatan TEXT,
        status TEXT DEFAULT 'aktif',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')

    c.execute('''CREATE TABLE IF NOT EXISTS disney_perangkat (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        disney_id INTEGER NOT NULL,
        nama TEXT NOT NULL,
        expired TEXT,
        status TEXT DEFAULT 'aktif',
        FOREIGN KEY (disney_id) REFERENCES disney(id)
    )''')

    # YOUTUBE
    c.execute('''CREATE TABLE IF NOT EXISTS youtube (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        email TEXT NOT NULL,
        password TEXT,
        expired TEXT NOT NULL,
        catatan TEXT,
        status TEXT DEFAULT 'aktif',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')

    # PENGINGAT LOG
    c.execute('''CREATE TABLE IF NOT EXISTS pengingat_log (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        tipe TEXT NOT NULL,
        ref_id INTEGER NOT NULL,
        jenis TEXT NOT NULL,
        tanggal TEXT NOT NULL
    )''')

    conn.commit()
    conn.close()

# ══ UTILS DB ══════════════════════════════════════════════

def q(table, where_id):
    conn = get_conn()
    c = conn.cursor()
    c.execute(f"SELECT * FROM {table} WHERE id=?", (where_id,))
    r = c.fetchone(); conn.close(); return r

def qa(table, where_col=None, where_val=None, order="id"):
    conn = get_conn()
    c = conn.cursor()
    if where_col:
        c.execute(f"SELECT * FROM {table} WHERE {where_col}=? ORDER BY {order}", (where_val,))
    else:
        c.execute(f"SELECT * FROM {table} ORDER BY {order}")
    r = c.fetchall(); conn.close(); return r

def upd(table, row_id, data):
    conn = get_conn()
    c = conn.cursor()
    fields = ', '.join([f"{k}=?" for k in data.keys()])
    c.execute(f"UPDATE {table} SET {fields} WHERE id=?", list(data.values())+[row_id])
    conn.commit(); conn.close()

def ins(table, data):
    conn = get_conn()
    c = conn.cursor()
    keys = ', '.join(data.keys())
    vals = ', '.join(['?']*len(data))
    c.execute(f"INSERT INTO {table} ({keys}) VALUES ({vals})", list(data.values()))
    rid = c.lastrowid; conn.commit(); conn.close(); return rid

def delete(table, row_id):
    conn = get_conn()
    c = conn.cursor()
    c.execute(f"DELETE FROM {table} WHERE id=?", (row_id,))
    conn.commit(); conn.close()

# ══ NETFLIX ═══════════════════════════════════════════════

def nf_all(status=None):
    conn = get_conn()
    c = conn.cursor()
    if status:
        c.execute("SELECT * FROM netflix WHERE status=? ORDER BY id DESC", (status,))
    else:
        c.execute("SELECT * FROM netflix WHERE status='aktif' ORDER BY id DESC")
    r = c.fetchall(); conn.close(); return r

def nf_get(nid): return q("netflix", nid)

def nf_add(data): return ins("netflix", data)

def nf_update(nid, data): upd("netflix", nid, data)

def nf_delete(nid):
    conn = get_conn()
    c = conn.cursor()
    c.execute("DELETE FROM netflix WHERE id=?", (nid,))
    c.execute("DELETE FROM netflix_profil WHERE netflix_id=?", (nid,))
    conn.commit(); conn.close()

def profil_all(nid):
    return qa("netflix_profil", "netflix_id", nid, "nomor")

def profil_get(pid): return q("netflix_profil", pid)

def profil_add(data): return ins("netflix_profil", data)

def profil_update(pid, data): upd("netflix_profil", pid, data)

def profil_delete(pid): delete("netflix_profil", pid)

# ══ DISNEY+ ═══════════════════════════════════════════════

def ds_all(status=None):
    conn = get_conn()
    c = conn.cursor()
    if status:
        c.execute("SELECT * FROM disney WHERE status=? ORDER BY expired_langganan ASC", (status,))
    else:
        c.execute("SELECT * FROM disney WHERE status='aktif' ORDER BY expired_langganan ASC")
    r = c.fetchall(); conn.close(); return r

def ds_get(did): return q("disney", did)

def ds_add(data): return ins("disney", data)

def ds_update(did, data): upd("disney", did, data)

def ds_delete(did):
    conn = get_conn()
    c = conn.cursor()
    c.execute("DELETE FROM disney WHERE id=?", (did,))
    c.execute("DELETE FROM disney_perangkat WHERE disney_id=?", (did,))
    conn.commit(); conn.close()

def perangkat_all(did):
    return qa("disney_perangkat", "disney_id", did, "id")

def perangkat_get(rid): return q("disney_perangkat", rid)

def perangkat_add(data): return ins("disney_perangkat", data)

def perangkat_update(rid, data): upd("disney_perangkat", rid, data)

def perangkat_delete(rid): delete("disney_perangkat", rid)

# ══ YOUTUBE ════════════════════════════════════════════════

def yt_all(status=None):
    conn = get_conn()
    c = conn.cursor()
    if status:
        c.execute("SELECT * FROM youtube WHERE status=? ORDER BY expired ASC", (status,))
    else:
        c.execute("SELECT * FROM youtube WHERE status='aktif' ORDER BY expired ASC")
    r = c.fetchall(); conn.close(); return r

def yt_get(yid): return q("youtube", yid)

def yt_add(data): return ins("youtube", data)

def yt_update(yid, data): upd("youtube", yid, data)

def yt_delete(yid): delete("youtube", yid)

# ══ PENGINGAT ══════════════════════════════════════════════

def sudah_kirim(tipe, ref_id, jenis, tgl):
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT id FROM pengingat_log WHERE tipe=? AND ref_id=? AND jenis=? AND tanggal=?",
              (tipe, ref_id, jenis, tgl))
    r = c.fetchone(); conn.close(); return r is not None

def simpan_log(tipe, ref_id, jenis, tgl):
    ins("pengingat_log", {"tipe":tipe,"ref_id":ref_id,"jenis":jenis,"tanggal":tgl})

# ══ STATISTIK ══════════════════════════════════════════════

def get_stats():
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT COUNT(*) as n FROM netflix WHERE status='aktif'"); nf=c.fetchone()['n']
    c.execute("SELECT COUNT(*) as n FROM netflix_profil WHERE status='aktif'"); pr=c.fetchone()['n']
    c.execute("SELECT COUNT(*) as n FROM disney WHERE status='aktif'"); ds=c.fetchone()['n']
    c.execute("SELECT COUNT(*) as n FROM disney_perangkat WHERE status='aktif'"); pg=c.fetchone()['n']
    c.execute("SELECT COUNT(*) as n FROM youtube WHERE status='aktif'"); yt=c.fetchone()['n']
    conn.close()
    return {"netflix":nf,"profil":pr,"disney":ds,"perangkat":pg,"youtube":yt}

# ══ BACKUP ═════════════════════════════════════════════════

def get_backup_text():
    from utils import format_tgl, sisa_hari, status_icon
    from datetime import date
    teks = f"📋 *BACKUP DATA — {date.today().strftime('%d %B %Y')}*\n"
    teks += "━━━━━━━━━━━━━━━━━━━━\n\n"

    # Netflix
    teks += "🎬 *NETFLIX*\n"
    for n in nf_all():
        teks += f"📧 `{n['email']}`\n"
        teks += f"🔑 `{n['password']}`\n"
        teks += f"📅 Ubah PW: {n['tgl_ubah_pw'] or '-'}\n"
        for p in profil_all(n['id']):
            sisa = sisa_hari(p['expired']) if p['expired'] else 999
            icon = status_icon(sisa)
            teks += f"  {icon} {p['nama']} | {p['pin'] or '-'} | {format_tgl(p['expired']) if p['expired'] else 'Aktif'}\n"
        teks += "\n"

    # Disney
    teks += "🏰 *DISNEY+*\n"
    for d in ds_all():
        teks += f"📦 {d['nama_paket']}\n"
        teks += f"📱 {d['no_hp'] or '-'}\n"
        teks += f"📧 `{d['email']}`\n"
        teks += f"⏰ {format_tgl(d['expired_langganan'])}\n"
        for p in perangkat_all(d['id']):
            sisa = sisa_hari(p['expired']) if p['expired'] else 999
            icon = status_icon(sisa)
            teks += f"  {icon} {p['nama']} | {format_tgl(p['expired']) if p['expired'] else '-'}\n"
        teks += "\n"

    # YouTube
    teks += "📺 *YOUTUBE*\n"
    for y in yt_all():
        sisa = sisa_hari(y['expired'])
        icon = status_icon(sisa)
        teks += f"📧 `{y['email']}`\n"
        teks += f"🔑 `{y['password'] or '-'}`\n"
        teks += f"{icon} Expired: {format_tgl(y['expired'])}\n\n"

    return teks
