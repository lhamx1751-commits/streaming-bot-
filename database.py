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

    # ── NETFLIX ──────────────────────────────────────────
    c.execute('''CREATE TABLE IF NOT EXISTS netflix (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        email TEXT NOT NULL,
        password TEXT NOT NULL,
        metode_bayar TEXT DEFAULT 'Visa',
        expired_akun TEXT,
        catatan TEXT,
        status TEXT DEFAULT 'aktif',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')

    c.execute('''CREATE TABLE IF NOT EXISTS netflix_profil (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        netflix_id INTEGER NOT NULL,
        nomor_profil INTEGER NOT NULL,
        nama_profil TEXT,
        nama_pelanggan TEXT,
        no_hp TEXT,
        expired TEXT NOT NULL,
        harga INTEGER DEFAULT 0,
        status TEXT DEFAULT 'aktif',
        FOREIGN KEY (netflix_id) REFERENCES netflix(id)
    )''')

    # ── DISNEY+ ──────────────────────────────────────────
    c.execute('''CREATE TABLE IF NOT EXISTS disney (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        no_hp TEXT,
        email TEXT NOT NULL,
        password TEXT,
        expired_langganan TEXT NOT NULL,
        harga INTEGER DEFAULT 0,
        catatan TEXT,
        status TEXT DEFAULT 'aktif',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')

    c.execute('''CREATE TABLE IF NOT EXISTS disney_perangkat (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        disney_id INTEGER NOT NULL,
        nama_perangkat TEXT NOT NULL,
        nama_pelanggan TEXT,
        no_hp TEXT,
        tanggal_login TEXT,
        status TEXT DEFAULT 'aktif',
        FOREIGN KEY (disney_id) REFERENCES disney(id)
    )''')

    # ── YOUTUBE ──────────────────────────────────────────
    c.execute('''CREATE TABLE IF NOT EXISTS youtube (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        email_akun TEXT NOT NULL,
        password TEXT,
        expired_langganan TEXT NOT NULL,
        harga INTEGER DEFAULT 0,
        catatan TEXT,
        status TEXT DEFAULT 'aktif',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')

    c.execute('''CREATE TABLE IF NOT EXISTS youtube_member (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        youtube_id INTEGER NOT NULL,
        email_pembeli TEXT NOT NULL,
        nama_pelanggan TEXT,
        no_hp TEXT,
        status TEXT DEFAULT 'aktif',
        FOREIGN KEY (youtube_id) REFERENCES youtube(id)
    )''')

    # ── PENGINGAT LOG ────────────────────────────────────
    c.execute('''CREATE TABLE IF NOT EXISTS pengingat_log (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        tipe TEXT NOT NULL,
        ref_id INTEGER NOT NULL,
        jenis TEXT NOT NULL,
        tanggal TEXT NOT NULL
    )''')

    conn.commit()
    conn.close()

# ══ NETFLIX ═══════════════════════════════════════════════

def netflix_tambah(data: dict) -> int:
    conn = get_conn()
    c = conn.cursor()
    c.execute('''INSERT INTO netflix (email, password, metode_bayar, expired_akun, catatan)
                 VALUES (?,?,?,?,?)''',
              (data['email'], data['password'], data.get('metode_bayar','Visa'),
               data.get('expired_akun',''), data.get('catatan','')))
    nid = c.lastrowid
    conn.commit(); conn.close()
    return nid

def netflix_get_all():
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT * FROM netflix WHERE status='aktif' ORDER BY id DESC")
    r = c.fetchall(); conn.close(); return r

def netflix_get(nid):
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT * FROM netflix WHERE id=?", (nid,))
    r = c.fetchone(); conn.close(); return r

def netflix_update(nid, data):
    conn = get_conn()
    c = conn.cursor()
    fields = ', '.join([f"{k}=?" for k in data.keys()])
    c.execute(f"UPDATE netflix SET {fields} WHERE id=?", list(data.values())+[nid])
    conn.commit(); conn.close()

def netflix_hapus(nid):
    conn = get_conn()
    c = conn.cursor()
    c.execute("DELETE FROM netflix WHERE id=?", (nid,))
    c.execute("DELETE FROM netflix_profil WHERE netflix_id=?", (nid,))
    conn.commit(); conn.close()

def profil_tambah(nid, data) -> int:
    conn = get_conn()
    c = conn.cursor()
    c.execute('''INSERT INTO netflix_profil
                 (netflix_id, nomor_profil, nama_profil, nama_pelanggan, no_hp, expired, harga)
                 VALUES (?,?,?,?,?,?,?)''',
              (nid, data['nomor_profil'], data.get('nama_profil',''),
               data.get('nama_pelanggan',''), data.get('no_hp',''),
               data['expired'], data.get('harga',0)))
    pid = c.lastrowid
    conn.commit(); conn.close(); return pid

def profil_get_all(nid):
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT * FROM netflix_profil WHERE netflix_id=? ORDER BY nomor_profil", (nid,))
    r = c.fetchall(); conn.close(); return r

def profil_get(pid):
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT * FROM netflix_profil WHERE id=?", (pid,))
    r = c.fetchone(); conn.close(); return r

def profil_update(pid, data):
    conn = get_conn()
    c = conn.cursor()
    fields = ', '.join([f"{k}=?" for k in data.keys()])
    c.execute(f"UPDATE netflix_profil SET {fields} WHERE id=?", list(data.values())+[pid])
    conn.commit(); conn.close()

def profil_hapus(pid):
    conn = get_conn()
    c = conn.cursor()
    c.execute("DELETE FROM netflix_profil WHERE id=?", (pid,))
    conn.commit(); conn.close()

# ══ DISNEY+ ═══════════════════════════════════════════════

def disney_tambah(data) -> int:
    conn = get_conn()
    c = conn.cursor()
    c.execute('''INSERT INTO disney (no_hp, email, password, expired_langganan, harga, catatan)
                 VALUES (?,?,?,?,?,?)''',
              (data.get('no_hp',''), data['email'], data.get('password',''),
               data['expired_langganan'], data.get('harga',0), data.get('catatan','')))
    did = c.lastrowid
    conn.commit(); conn.close(); return did

def disney_get_all():
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT * FROM disney WHERE status='aktif' ORDER BY expired_langganan ASC")
    r = c.fetchall(); conn.close(); return r

def disney_get(did):
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT * FROM disney WHERE id=?", (did,))
    r = c.fetchone(); conn.close(); return r

def disney_update(did, data):
    conn = get_conn()
    c = conn.cursor()
    fields = ', '.join([f"{k}=?" for k in data.keys()])
    c.execute(f"UPDATE disney SET {fields} WHERE id=?", list(data.values())+[did])
    conn.commit(); conn.close()

def disney_hapus(did):
    conn = get_conn()
    c = conn.cursor()
    c.execute("DELETE FROM disney WHERE id=?", (did,))
    c.execute("DELETE FROM disney_perangkat WHERE disney_id=?", (did,))
    conn.commit(); conn.close()

def perangkat_tambah(did, data) -> int:
    conn = get_conn()
    c = conn.cursor()
    c.execute('''INSERT INTO disney_perangkat
                 (disney_id, nama_perangkat, nama_pelanggan, no_hp, tanggal_login)
                 VALUES (?,?,?,?,?)''',
              (did, data['nama_perangkat'], data.get('nama_pelanggan',''),
               data.get('no_hp',''), data.get('tanggal_login','')))
    rid = c.lastrowid
    conn.commit(); conn.close(); return rid

def perangkat_get_all(did):
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT * FROM disney_perangkat WHERE disney_id=? AND status='aktif'", (did,))
    r = c.fetchall(); conn.close(); return r

def perangkat_hapus(rid):
    conn = get_conn()
    c = conn.cursor()
    c.execute("DELETE FROM disney_perangkat WHERE id=?", (rid,))
    conn.commit(); conn.close()

# ══ YOUTUBE ════════════════════════════════════════════════

def yt_tambah(data) -> int:
    conn = get_conn()
    c = conn.cursor()
    c.execute('''INSERT INTO youtube (email_akun, password, expired_langganan, harga, catatan)
                 VALUES (?,?,?,?,?)''',
              (data['email_akun'], data.get('password',''),
               data['expired_langganan'], data.get('harga',0), data.get('catatan','')))
    yid = c.lastrowid
    conn.commit(); conn.close(); return yid

def yt_get_all():
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT * FROM youtube WHERE status='aktif' ORDER BY expired_langganan ASC")
    r = c.fetchall(); conn.close(); return r

def yt_get(yid):
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT * FROM youtube WHERE id=?", (yid,))
    r = c.fetchone(); conn.close(); return r

def yt_update(yid, data):
    conn = get_conn()
    c = conn.cursor()
    fields = ', '.join([f"{k}=?" for k in data.keys()])
    c.execute(f"UPDATE youtube SET {fields} WHERE id=?", list(data.values())+[yid])
    conn.commit(); conn.close()

def yt_hapus(yid):
    conn = get_conn()
    c = conn.cursor()
    c.execute("DELETE FROM youtube WHERE id=?", (yid,))
    c.execute("DELETE FROM youtube_member WHERE youtube_id=?", (yid,))
    conn.commit(); conn.close()

def member_tambah(yid, data) -> int:
    conn = get_conn()
    c = conn.cursor()
    c.execute('''INSERT INTO youtube_member
                 (youtube_id, email_pembeli, nama_pelanggan, no_hp)
                 VALUES (?,?,?,?)''',
              (yid, data['email_pembeli'], data.get('nama_pelanggan',''), data.get('no_hp','')))
    mid = c.lastrowid
    conn.commit(); conn.close(); return mid

def member_get_all(yid):
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT * FROM youtube_member WHERE youtube_id=? AND status='aktif'", (yid,))
    r = c.fetchall(); conn.close(); return r

def member_hapus(mid):
    conn = get_conn()
    c = conn.cursor()
    c.execute("DELETE FROM youtube_member WHERE id=?", (mid,))
    conn.commit(); conn.close()

# ══ PENGINGAT ══════════════════════════════════════════════

def sudah_kirim(tipe, ref_id, jenis, tgl):
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT id FROM pengingat_log WHERE tipe=? AND ref_id=? AND jenis=? AND tanggal=?",
              (tipe, ref_id, jenis, tgl))
    r = c.fetchone(); conn.close(); return r is not None

def simpan_log(tipe, ref_id, jenis, tgl):
    conn = get_conn()
    c = conn.cursor()
    c.execute("INSERT INTO pengingat_log (tipe,ref_id,jenis,tanggal) VALUES (?,?,?,?)",
              (tipe, ref_id, jenis, tgl))
    conn.commit(); conn.close()

def get_statistik():
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT COUNT(*) as n FROM netflix WHERE status='aktif'")
    nf = c.fetchone()['n']
    c.execute("SELECT COUNT(*) as n FROM disney WHERE status='aktif'")
    ds = c.fetchone()['n']
    c.execute("SELECT COUNT(*) as n FROM youtube WHERE status='aktif'")
    yt = c.fetchone()['n']
    c.execute("SELECT COUNT(*) as n FROM netflix_profil WHERE status='aktif'")
    profil = c.fetchone()['n']
    c.execute("SELECT COUNT(*) as n FROM disney_perangkat WHERE status='aktif'")
    perangkat = c.fetchone()['n']
    c.execute("SELECT COUNT(*) as n FROM youtube_member WHERE status='aktif'")
    member = c.fetchone()['n']
    conn.close()
    return {'netflix':nf,'disney':ds,'youtube':yt,'profil':profil,'perangkat':perangkat,'member':member}
