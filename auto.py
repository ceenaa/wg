import os
import time
from dotenv import load_dotenv

import analysis
import sheet

load_dotenv()
max_transfer = float(os.getenv("MAX_TRANSFER"))


def controller():
    analysis.reload()
    sheet.main()
    for peer in analysis.sortedPeer:
        if peer.active == 1 and peer.transfer >= max_transfer:
            analysis.pause_user(peer.name)
        if peer.transfer < max_transfer:
            break


def auto(delay):
    while True:
        controller()
        time.sleep(delay)
