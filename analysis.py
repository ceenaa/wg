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
startTime = date(2023, 4, 19)


def MibToGiB(mib):
    return mib / 1024


def kibToGiB(kib):
    return kib / 1024 / 1024


def calcAverage():
    avg = total / count
    avg = format(avg, '.2f')
    return avg


def dailyAverage():
    nowTime = date.today()
    res = (nowTime - startTime).days
    return total / res


def totalDays():
    nowTime = date.today()
    return (nowTime - startTime).days


def reload():
    file = open("res.txt", "w")
    wg = subprocess.check_output("wg", shell=True)
    file.write(wg.decode("utf-8"))
    file.close()

    file = open("res.txt", "r")
    lines = file.readlines()
    file.close()

    global total, count, maxUsage, maxPeer, sortedPeer, peerMap

    total = 0
    count = 0
    maxUsage = 0
    maxPeer = None
    sortedPeer = []
    peerMap = {}

    i = 5
    while i + 2 < len(lines):
        if 'allowed' in lines[i + 2]:
            i += 4
        elif 'interface' in lines[i]:
            i += 5
        else:

            transfer = lines[i + 5].split(" ")
            address = lines[i + 3]
            address = address.split(": ")[1]
            address = address.strip()
            connection = db.connect()
            user = db.get_user(connection, address)
            connection.commit()
            connection.close()
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
                transfer += MibToGiB(float(received))
            elif received_type == "KiB":
                transfer += kibToGiB(float(received))
            elif received_type == "GiB":
                transfer += float(received)

            if sent_type == "MiB":
                transfer += MibToGiB(float(sent))
            elif sent_type == "KiB":
                transfer += kibToGiB(float(sent))
            elif sent_type == "GiB":
                transfer += float(sent)

            connection = db.connect()
            user = db.get_user(connection, address)
            connection.commit()
            connection.close()
            p = models.peer(name, address, user[2], user[3], user[4])
            p.increaseTransfer(transfer)
            p.last_handshake = last_handshake
            peerMap[name] = p
            total += p.transfer
            i += 7

    connection = db.connect()
    peers = db.get_all(connection)
    connection.commit()
    connection.close()
    for user in peers:
        if user[0] not in peerMap:
            p = models.peer(user[0], user[1], user[2], user[3], user[4])
            total += p.transfer
            peerMap[user[0]] = p
    sortedPeer = sorted(peerMap.values(), key=lambda peer: peer.transfer, reverse=True)
    maxPeer = sortedPeer[0]
    maxUsage = maxPeer.transfer
    count = len(sortedPeer)


def export():
    reload()
    connection = db.connect()
    db.write_to_db(connection, sortedPeer)
    users = db.get_all(connection)
    connection.commit()
    connection.close()

    file = open("res.txt", "w")
    for user in users:
        file.write(f"{user[0]}\n{user[1]}\n{user[2]}\n{user[3]}\n")
    file.close()


def set_transferToZero(name):
    peerMap[name].transfer = 0
    global sortedPeer
    sortedPeer = sorted(peerMap.values(), key=lambda peer: peer.transfer, reverse=True)


def pause_user(name):
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
    db.write_to_db(connection, sortedPeer)
    file = open("/etc/wireguard/" + sys_name + ".conf", "w")
    file.writelines(lines)
    file.close()
    reload()
    sheet.main()
    os.system("sudo systemctl restart wg-quick@" + sys_name + ".service")
    connection.commit()
    connection.close()


def resume_user(name):
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
    db.write_to_db(connection, sortedPeer)
    file = open("/etc/wireguard/" + sys_name + ".conf", "w")
    file.writelines(lines)
    file.close()
    reload()
    set_transferToZero(name)
    sheet.main()
    os.system("sudo systemctl restart wg-quick@" + sys_name + ".service")
    connection.commit()
    connection.close()
