import os
import subprocess
from datetime import date
from dotenv import load_dotenv
import db
import models
import copy

load_dotenv()
confName = os.environ.get("CONF_NAME")

global total, count, maxUsage, maxPeer
peerMap = {}
sortedPeer = []
cached_peerMap = {}
startTime = date(2023, 4, 19)
cached_total = 0
cache_address = db.r.smembers("users")

for ad in cache_address:
    cached_address = ad
    cached_name = db.r.hget(ad, "name")
    cached_last_handshake = db.r.hget(ad, "last_handshake")
    cached_transfer = db.r.hget(ad, "transfer")
    if cached_transfer is None:
        cached_transfer = 0
    cached_transfer = float(cached_transfer)
    cached_total += float(cached_transfer)
    cached_peer = models.peer(cached_name, cached_address, cached_last_handshake, cached_transfer)
    cached_peerMap[cached_name] = cached_peer


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

    global total, count, maxUsage, maxPeer, sortedPeer, peerMap, cached_peerMap, cached_total

    total = 0
    total += cached_total
    count = 0
    maxUsage = 0
    maxPeer = None
    sortedPeer = []
    peerMap = {}
    peerMap = copy.copy(cached_peerMap)

    for i in range(5, len(lines), 7):
        if i + 5 >= len(lines):
            break
        if 'allowed' in lines[i + 2]:
            break
        transfer = lines[i + 5].split(" ")
        if len(transfer) < 3 or transfer[2] != "transfer:":
            continue
        address = lines[i + 3]
        address = address.split(": ")[1]
        address = address.strip()

        last_handshake = lines[i + 4].split(": ")[1].strip()
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

        name = db.r.hget(address, "name")
        total += transfer
        if peerMap.get(name) is not None:
            peerMap[name].increaseTransfer(transfer)
            peerMap[name].last_handshake = last_handshake
        else:
            p = models.peer(name, address, last_handshake, transfer)
            peerMap[name] = p

    peers = peerMap.values()
    sortedPeer = sorted(peers, key=lambda peer: peer.transfer, reverse=True)
    maxPeer = sortedPeer[0]
    maxUsage = maxPeer.transfer
    count = len(sortedPeer)


def export():
    file = open("peers.txt", "w")
    for peer in sortedPeer:
        file.write(str(peer) + "\n")
    file.close()


def set_transferToZero(name):
    peerMap[name].transfer = 0
    global sortedPeer
    sortedPeer = sorted(peerMap.values(), key=lambda peer: peer.transfer, reverse=True)


def pause_user(name):
    file = open("/etc/wireguard/wg0.conf", "r")
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
    file = open("/etc/wireguard/wg0.conf", "w")
    file.writelines(lines)
    file.close()
    reload()
    export()
    os.system("sudo systemctl restart wg-quick@wg0.service")
    db.cache_last_records()
    global cached_peerMap, cached_total
    cached_peerMap = copy.copy(peerMap)
    cached_total = total


def resume_user(name):
    file = open("/etc/wireguard/wg0.conf", "r")
    lines = file.readlines()
    file.close()
    for i in range(13, len(lines), 6):
        n = lines[i].split(" ")[1]
        if n == name:
            if lines[i+1][0] != "#":
                raise Exception("User already resumed")
            lines[i + 1] = lines[i + 1][1:]
            lines[i + 2] = lines[i + 2][1:]
            lines[i + 3] = lines[i + 3][1:]
            lines[i + 4] = lines[i + 4][1:]
            break
    file = open("/etc/wireguard/wg0.conf", "w")
    file.writelines(lines)
    file.close()
    reload()
    set_transferToZero(name)
    export()
    os.system("sudo systemctl restart wg-quick@wg0.service")
    db.cache_last_records()
    global cached_peerMap, cached_total
    cached_peerMap = copy.copy(peerMap)
    cached_total = total
