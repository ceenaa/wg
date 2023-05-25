import sqlite3


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
    file = open("/etc/wireguard/wg1.conf", "r")
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
        if lines[i+1][0] == "#":
            active = False
        c.execute("INSERT OR REPLACE INTO users VALUES(? ,? ,? ,?, ?)",
                  (name, address, last_handshake, transfer, active))


def load_lastRecords(conn):
    c = conn.cursor()
    file = open("peers.txt", "r")
    lines = file.readlines()
    file.close()
    for i in range(0, len(lines), 4):
        name = lines[i].strip()
        address = lines[i + 1].strip()
        last_handshake = lines[i + 2].strip()
        transfer = float(lines[i + 3].strip())
        active = c.execute("SELECT active FROM users WHERE name = ?", (name,)).fetchone()[0]
        c.execute("INSERT OR REPLACE INTO users VALUES (? ,? ,? ,?, ?)",
                  (name, address, last_handshake, transfer, active))


def write_to_db(conn, peers):
    c = conn.cursor()
    for peer in peers:
        c.execute("UPDATE users SET last_handshake = ? , transfer = ? WHERE name = ?",
                  (peer.last_handshake, peer.transfer, peer.name))


def pause_user(conn, name):
    c = conn.cursor()
    c.execute("UPDATE users SET active = 1 WHERE name = ?", (name,))


def resume_user(conn, name):
    c = conn.cursor()
    c.execute("UPDATE users SET active = 0 WHERE name = ?", (name,))

