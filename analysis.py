from datetime import date

from dotenv import load_dotenv

import models
import os
import subprocess

load_dotenv()
confName = os.environ.get("CONF_NAME")

global total, count, maxUsage, maxPeer, sortedPeer, peerMap
lastTotal = 0
lastPeerMap = {}

startTime = date(2023, 4, 19)


def MibToGiB(mib):
    return mib / 1024


def kibToGiB(kib):
    return kib / 1024 / 1024


def calcAverage():
    avg = total / count
    avg = round(avg, 2)
    return avg


def dailyAverage():
    nowTime = date.today()
    res = (nowTime - startTime).days
    return total / res


def totalDays():
    nowTime = date.today()
    return (nowTime - startTime).days


def import_req():
    file = open("peers.txt", "r")
    lines = file.readlines()
    global lastTotal, lastPeerMap
    for i in range(0, len(lines), 4):
        name = lines[i].strip()
        address = lines[i + 1].strip()
        last_handshake = lines[i + 2].strip()
        transfer = float(lines[i + 3].strip())
        lastTotal += transfer
        lastPeerMap[name] = models.peer(name, address, last_handshake, transfer)
    file.close()


def reload():
    # file = open("res.txt", "w")
    # wg = subprocess.check_output("wg", shell=True)
    # file.write(wg.decode("utf-8"))
    # file.close()

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

    for i in range(5, len(lines), 7):
        if i + 5 >= len(lines):
            break
        transfer = lines[i + 5].split(" ")
        if len(transfer) < 3 or transfer[2] != "transfer:":
            continue
        address = lines[i + 3].split(" ")[4]
        last_handshake = lines[i + 4].split(": ")[1]
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

        transfer = round(transfer, 2)
        name = '%s' % confName
        name += address.split(".")[3].split("/")[0]

        p = models.peer(name, address, last_handshake, transfer)
        peerMap[name] = p
        total += transfer

    for p in peerMap.keys():
        if p in lastPeerMap.keys():
            peerMap[p].transfer += round(lastPeerMap[p].transfer, 2)
    for p in lastPeerMap.keys():
        if p not in peerMap.keys():
            peerMap[p] = lastPeerMap[p]

    peers = peerMap.values()
    total += lastTotal
    total = round(total, 2)

    sortedPeer = sorted(peers, key=lambda peer: peer.transfer, reverse=True)
    maxPeer = sortedPeer[0]
    maxUsage = maxPeer.transfer
    count = len(sortedPeer)


import_req()
