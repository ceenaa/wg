import os
import subprocess
from datetime import date
from dotenv import load_dotenv
import db
import models
import sheet

load_dotenv()
conf_name = os.environ.get("CONF_NAME")
sys_name = os.environ.get("SYSTEM_NAME")

global total, count, maxUsage, maxPeer
peerMap = {}
sortedPeer = []
temp_usage = 0


def mib_to_gib(mib):
    return mib / 1024


def kib_to_gib(kib):
    return kib / 1024 / 1024


def calc_average():
    avg = total / count
    avg = format(avg, '.2f')
    return avg


def daily_average():
    connection = db.connect()
    _, start_time, _ = db.get_usage_by_name(connection, conf_name)
    connection.close()
    start_time = start_time.split("-")
    start_time = date(year=int(start_time[0]), month=int(start_time[1]), day=int(start_time[2]))
    now_time = date.today()

    res = (now_time - start_time).days
    return total / res


def total_days():
    connection = db.connect()
    _, start_time, _ = db.get_usage_by_name(connection, conf_name)
    connection.close()
    start_time = start_time.split("-")
    start_time = date(year=int(start_time[0]), month=int(start_time[1]), day=int(start_time[2]))

    now_time = date.today()
    return (now_time - start_time).days


def reload():
    connection = db.connect()
    peers = db.get_all(connection)

    file = open("res.txt", "w")
    wg = subprocess.check_output("wg", shell=True)
    file.write(wg.decode("utf-8"))
    file.close()

    file = open("res.txt", "r")
    lines = file.readlines()
    file.close()

    global total, count, maxUsage, maxPeer, sortedPeer, peerMap, temp_usage
    temp_usage = 0
    total = 0
    count = 0
    maxUsage = 0
    maxPeer = None
    sortedPeer = []
    peerMap = {}

    i = 5
    while i + 6 < len(lines):
        if 'allowed' in lines[i + 2]:
            i += 4
        elif 'transfer' in lines[i + 4]:
            i += 6
        elif 'interface' in lines[i]:
            i += 5
        else:
            if i + 3 >= len(lines) or i + 4 >= len(lines) or i + 5 >= len(lines):
                break
            transfer = lines[i + 5].split(" ")
            address = lines[i + 3]
            address = address.split(": ")[1]
            address = address.strip()
            user = db.get_user(connection, address)

            if user is None:
                i += 7
                continue
            name = user[0]
            last_handshake = lines[i + 4].split(': ')[1].strip()
            received = transfer[3]
            received_type = transfer[4]

            sent = transfer[6]
            sent_type = transfer[7]

            transfer = 0

            if received_type == "MiB":
                transfer += mib_to_gib(float(received))
            elif received_type == "KiB":
                transfer += kib_to_gib(float(received))
            elif received_type == "GiB":
                transfer += float(received)

            if sent_type == "MiB":
                transfer += mib_to_gib(float(sent))
            elif sent_type == "KiB":
                transfer += kib_to_gib(float(sent))
            elif sent_type == "GiB":
                transfer += float(sent)

            temp_usage += transfer

            p = models.Peer(name, address, user[2], user[3], user[4])
            p.increase_transfer(transfer)
            p.last_handshake = last_handshake
            peerMap[name] = p
            total += p.transfer
            i += 7
    connection.commit()
    connection.close()

    for user in peers:
        if user[0] not in peerMap:
            p = models.Peer(user[0], user[1], user[2], user[3], user[4])
            total += p.transfer
            peerMap[user[0]] = p
    if len(peerMap) > 0:
        sortedPeer = sorted(peerMap.values(), key=lambda peer: peer.transfer, reverse=True)
    if len(sortedPeer) > 0:
        maxPeer = sortedPeer[0]
        maxUsage = maxPeer.transfer
        count = len(sortedPeer)

    temp_usage = format(temp_usage, '.2f')
    temp_usage = float(temp_usage)


def export():
    reload()

    file = open("peers.txt", "w")
    for peer in sortedPeer:
        file.write(f"{peer.name}\n{peer.address}\n{peer.last_handshake}\n{peer.transfer}\n")
    file.close()


def set_transfer_to_zero(name):
    peerMap[name].transfer = 0
    global sortedPeer
    sortedPeer = sorted(peerMap.values(), key=lambda peer: peer.transfer, reverse=True)


def pause_user(name):
    # file = open("test.conf", "r")
    file = open("/etc/wireguard/" + sys_name + ".conf", "r")
    lines = file.readlines()
    file.close()
    for i in range(13, len(lines), 6):
        n = lines[i].split(" ")[1]
        if n == name:
            if lines[i + 1][0] == "#":
                raise Exception("User already paused")
            lines[i + 1] = "#" + lines[i + 1]
            lines[i + 2] = "#" + lines[i + 2]
            lines[i + 3] = "#" + lines[i + 3]
            lines[i + 4] = "#" + lines[i + 4]
            break
    connection = db.connect()
    db.pause_user(connection, name)
    connection.commit()
    reload()
    db.write_to_db(connection, sortedPeer)
    connection.commit()
    file = open("/etc/wireguard/" + sys_name + ".conf", "w")
    # file = open("test.conf", "w")
    file.writelines(lines)
    file.close()
    sheet.main()
    db.add_usage_by_name(connection, conf_name, temp_usage)
    connection.commit()
    os.system("sudo systemctl restart wg-quick@" + sys_name + ".service")
    connection.close()


def resume_user(name):
    # file = open("test.conf", "r")
    file = open("/etc/wireguard/" + sys_name + ".conf", "r")
    lines = file.readlines()
    file.close()
    for i in range(13, len(lines), 6):
        n = lines[i].split(" ")[1]
        if n == name:
            if lines[i + 1][0] != "#":
                raise Exception("User already resumed")
            lines[i + 1] = lines[i + 1][1:]
            lines[i + 2] = lines[i + 2][1:]
            lines[i + 3] = lines[i + 3][1:]
            lines[i + 4] = lines[i + 4][1:]
            break
    connection = db.connect()
    db.resume_user(connection, name)
    connection.commit()
    reload()
    set_transfer_to_zero(name)
    db.write_to_db(connection, sortedPeer)
    connection.commit()
    file = open("/etc/wireguard/" + sys_name + ".conf", "w")
    # file = open("test.conf", "w")
    file.writelines(lines)
    file.close()
    sheet.main()
    db.add_usage_by_name(connection, conf_name, temp_usage)
    connection.commit()
    os.system("sudo systemctl restart wg-quick@" + sys_name + ".service")
    connection.close()
