import os

import schedule
from dotenv import load_dotenv

import analysis
import sheet
from main import bot, chat_ids

load_dotenv()
max_transfer = float(os.getenv("MAX_TRANSFER"))


def controller():
    try:
        analysis.reload()
        sheet.main()
        for peer in analysis.peerMap.keys():
            if peer.active == 1 and peer.transfer >= max_transfer:
                analysis.pause_user(peer.name)
            if peer.transfer < max_transfer:
                break
    except Exception as err:
        for c_id in chat_ids:
            bot.send_message(c_id, type(err).__name__ + " " + str(err))


def main():
    schedule.every(30).minutes.do(controller)
    while True:
        schedule.run_pending()
