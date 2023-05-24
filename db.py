import sqlite3

conn = sqlite3.connect('users.db')
c = conn.cursor()


def create_table():
    c.execute("""CREATE TABLE users (
                name text,
                address text primary key not null unique,
                last_handshake text,
                transfer real
                )""")


def load_all_peers():
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
        c = conn.cursor()
        c.execute("INSERT OR REPLACE INTO users VALUES(? ,? ,? ,?)",
                  (name, address, last_handshake, transfer))


def load_lastRecords():
    file = open("peers.txt", "r")
    lines = file.readlines()
    file.close()
    for i in range(0, len(lines), 4):
        name = lines[i].strip()
        address = lines[i + 1].strip()
        last_handshake = lines[i + 2].strip()
        transfer = float(lines[i + 3].strip())
        c = conn.cursor()
        c.execute("INSERT OR REPLACE INTO users VALUES (? ,? ,? ,?)",
                  (name, address, last_handshake, transfer))


def write_to_db(peers):
    for peer in peers:
        c = conn.cursor()
        c.execute("UPDATE users SET last_handshake = ? , transfer = ? WHERE name = ?",
                  (peer.last_handshake, peer.transfer, peer.name))


conn.commit()
conn.close()
