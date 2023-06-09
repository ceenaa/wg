import sqlite3
import analysis

def connect():
    conn = sqlite3.connect("users.db")
    return conn


def create_table(conn):
    c = conn.cursor()
    c.execute("""CREATE TABLE users (
                name text,
                address text primary key not null unique,
                last_handshake text,
                transfer real,
                active boolean
                )""")

    c.execute("""CREATE TABLE usages (
                name text,
                date text,
                transfer real
                )
        """)


def get_all(conn):
    c = conn.cursor()
    c.execute("SELECT * FROM users")
    return c.fetchall()


def get_user(conn, address):
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE address = ?", (address,))
    return c.fetchone()


def load_all_peers(conn):
    c = conn.cursor()
    file = open("/etc/wireguard/" + analysis.sys_name + ".conf", "r")
    # file = open("test.conf", "r")
    lines = file.readlines()
    file.close()
    for i in range(13, len(lines), 6):
        name = lines[i]
        name = name.split(" ")[1]
        address = lines[i + 3]
        address = address.split(" = ")[1]
        address = address.strip()
        transfer = 0
        last_handshake = "None"
        active = True
        if lines[i + 1][0] == "#":
            active = False
        c.execute("INSERT OR REPLACE INTO users VALUES(? ,? ,? ,?, ?)",
                  (name, address, last_handshake, transfer, active))


def load_last_records(conn):
    c = conn.cursor()
    file = open("peers.txt", "r")
    lines = file.readlines()
    file.close()
    for i in range(0, len(lines), 4):
        name = lines[i].strip()
        address = lines[i + 1].strip()
        last_handshake = lines[i + 2].strip()
        transfer = float(lines[i + 3].strip())
        c.execute("SELECT active FROM users WHERE name = ?", (name,))
        active = c.fetchone()[0]
        c.execute("INSERT OR REPLACE INTO users VALUES (? ,? ,? ,?, ?)",
                  (name, address, last_handshake, transfer, active))


def write_to_db(conn, peers):
    c = conn.cursor()
    for peer in peers:
        c.execute("UPDATE users SET last_handshake = ? , transfer = ? WHERE name = ?",
                  (peer.last_handshake, peer.transfer, peer.name))


def pause_user(conn, name):
    c = conn.cursor()
    c.execute("UPDATE users SET active = 0 WHERE name = ?", (name,))


def resume_user(conn, name):
    c = conn.cursor()
    c.execute("UPDATE users SET active = 1 WHERE name = ?", (name,))


def paused_users(conn):
    c = conn.cursor()
    c.execute("SELECT name FROM users WHERE active = 0")
    return c.fetchall()


def get_usage_by_name(conn, name):
    c = conn.cursor()
    c.execute("SELECT * FROM usages WHERE name = ?", (name,))
    data = c.fetchone()
    return data[0], data[1], data[2]


def make_usage_for_name(conn, name):
    c = conn.cursor()
    c.execute("INSERT INTO usages VALUES (?, date('now'), 0.01)", (name,))


def reset_usage_and_date_by_name(conn, name):
    c = conn.cursor()
    if c.execute("SELECT * FROM usages WHERE name = ?", (name,)) == None:
        c.execute("INSERT INTO usages VALUES (?, date('now'), 0.01)", (name,))
    else:
        c.execute("UPDATE usages SET transfer = 0.01 WHERE name = ?", (name,))
        c.execute("UPDATE usages SET date = date('now') WHERE name = ?", (name,))


def add_usage_by_name(conn, name, transfer):
    c = conn.cursor()
    c.execute("SELECT date FROM usages WHERE name = ?", (name,))
    date = c.fetchone()
    c.execute("UPDATE usages SET transfer = transfer + ? WHERE name = ?", (transfer, name))
