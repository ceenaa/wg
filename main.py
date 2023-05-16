import analysis
import os
import telebot

import sheet

API_KEY = os.getenv("API_KEY")
bot = telebot.TeleBot(API_KEY)


def total_request(message):
    return message.text == "Total"


@bot.message_handler(func=total_request)
def send_total(message):
    try:
        bot.send_message(message.chat.id, f"{round(analysis.total, 2)} Gib")
    except Exception as err:
        bot.send_message(message.chat.id, type(err).__name__ + " " + str(err))


def average_request(message):
    return message.text == "Average"


@bot.message_handler(func=average_request)
def send_average(message):
    try:
        bot.send_message(message.chat.id, analysis.calcAverage())
    except Exception as err:
        bot.send_message(message.chat.id, type(err).__name__ + " " + str(err))


def all_request(message):
    return message.text == "All"


@bot.message_handler(func=all_request)
def send_all(message):
    try:
        s = ""
        i = 0
        for peer in analysis.sortedPeer:
            s += str(peer) + "\n----------------\n"
            i += 1
            if i % 20 == 0:
                bot.send_message(message.chat.id, s)
                s = ""
        if s != "":
            bot.send_message(message.chat.id, s)
    except Exception as err:
        bot.send_message(message.chat.id, type(err).__name__ + " " + str(err))


def count_request(message):
    return message.text == "Count"


@bot.message_handler(func=count_request)
def send_count(message):
    try:
        bot.send_message(message.chat.id, analysis.count)
    except Exception as err:
        bot.send_message(message.chat.id, type(err).__name__ + " " + str(err))


def max_request(message):
    return message.text == "Max"


@bot.message_handler(func=max_request)
def send_max(message):
    try:
        bot.send_message(message.chat.id, str(analysis.maxPeer))
    except Exception as err:
        bot.send_message(message.chat.id, type(err).__name__ + " " + str(err))


def max_request(message):
    return message.text == "Reload"


@bot.message_handler(func=max_request)
def send_max(message):
    try:
        analysis.reload()
        sheet.main()
        bot.send_message(message.chat.id, "Reloaded!")
    except Exception as err:
        bot.send_message(message.chat.id, type(err).__name__ + " " + str(err))


def daily_average_request(message):
    return message.text == "Daily average"


@bot.message_handler(func=daily_average_request)
def send_daily_average(message):
    try:
        bot.send_message(message.chat.id, f"{round(analysis.dailyAverage(), 2)} Gib")
    except Exception as err:
        bot.send_message(message.chat.id, type(err).__name__ + " " + str(err))


def total_days_request(message):
    return message.text == "Total days"


def export_request(message):
    return message.text == "Export"


@bot.message_handler(func=export_request)
def send_export(message):
    try:
        analysis.export()
        bot.send_message(message.chat.id, "Exported!")
    except Exception as err:
        bot.send_message(message.chat.id, type(err).__name__ + " " + str(err))


@bot.message_handler(func=total_days_request)
def send_total_days(message):
    try:
        bot.send_message(message.chat.id, analysis.totalDays())
    except Exception as err:
        bot.send_message(message.chat.id, type(err).__name__ + " " + str(err))


def user_request(message):
    t = message.text[0]
    t = t.lowwer()
    t += message.text[1:]
    return t in analysis.peerMap.keys()


@bot.message_handler(func=user_request)
def send_npk(message):
    cid = message.chat.id
    message_text = message.text
    try:
        bot.send_message(cid, analysis.peerMap[message_text])
    except Exception as err:
        bot.send_message(message.chat.id, type(err).__name__ + " " + str(err))


def pause_request(message):
    p = message.text.split(" ")[0]
    name = message.text.split(" ")[1]
    return p == "Pause" and name in analysis.peerMap.keys()


@bot.message_handler(func=pause_request)
def send_pause(message):
    try:
        name = message.text.split(" ")[1]
        analysis.pause_user(name)
        bot.send_message(message.chat.id, "Paused!")
    except Exception as err:
        bot.send_message(message.chat.id, type(err).__name__ + " " + str(err))


def unpause_request(message):
    p = message.text.split(" ")[0]
    name = message.text.split(" ")[1]
    return p == "Resume" and name in analysis.peerMap.keys()


@bot.message_handler(func=unpause_request)
def send_unpause(message):
    try:
        name = message.text.split(" ")[1]
        analysis.resume_user(name)
        bot.send_message(message.chat.id, "Resumed!")
    except Exception as err:
        bot.send_message(message.chat.id, type(err).__name__ + " " + str(err))


bot.infinity_polling(timeout=10, long_polling_timeout=5)
