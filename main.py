import analysis
import os
import telebot

API_KEY = os.getenv("API_KEY")
bot = telebot.TeleBot(API_KEY)


def total_request(message):
    return message.text == "Total"


@bot.message_handler(func=total_request)
def send_total(message):
    try:
        bot.send_message(message.chat.id, f"{round(analysis.total, 2)} Gib")
    except:
        bot.send_message(message.chat.id, "Reload needed!")


def average_request(message):
    return message.text == "Average"


@bot.message_handler(func=average_request)
def send_average(message):
    try:
        bot.send_message(message.chat.id, analysis.calcAverage())
    except:
        bot.send_message(message.chat.id, "Reload needed!")


def all_request(message):
    return message.text == "All"


@bot.message_handler(func=all_request)
def send_all(message):
    try:
        s = ""
        for peer in analysis.sortedPeer:
            s += str(peer) + "\n----------------\n"
        bot.send_message(message.chat.id, s)
    except:
        bot.send_message(message.chat.id, "Reload needed!")


def count_request(message):
    return message.text == "Count"


@bot.message_handler(func=count_request)
def send_count(message):
    try:
        bot.send_message(message.chat.id, analysis.count)
    except:
        bot.send_message(message.chat.id, "Reload needed!")


def max_request(message):
    return message.text == "Max"


@bot.message_handler(func=max_request)
def send_max(message):
    try:
        bot.send_message(message.chat.id, str(analysis.maxPeer))
    except:
        bot.send_message(message.chat.id, "Reload needed!")


def max_request(message):
    return message.text == "Reload"


@bot.message_handler(func=max_request)
def send_max(message):
    try:
        analysis.reload()
        bot.send_message(message.chat.id, "Reloaded!")
    except:
        bot.send_message(message.chat.id, "Error")


def daily_average_request(message):
    return message.text == "Daily average"


@bot.message_handler(func=daily_average_request)
def send_daily_average(message):
    try:
        bot.send_message(message.chat.id, f"{round(analysis.dailyAverage(), 2)} Gib")
    except:
        bot.send_message(message.chat.id, "Reload needed!")


def total_days_request(message):
    return message.text == "Total days"


def export_request(message):
    return message.text == "Export"


@bot.message_handler(func=export_request)
def send_export(message):
    try:
        file = open("peers.txt", "w")
        for peer in analysis.sortedPeer:
            file.write(str(peer) + "\n")
        bot.send_message(message.chat.id, "Exported!")
        file.close()
    except:
        bot.send_message(message.chat.id, "Reload needed!")


def inport_request(message):
    return message.text == "Import"


@bot.message_handler(func=inport_request)
def send_import(message):
    try:
        bot.send_message(message.chat.id, "Imported!")
    except:
        bot.send_message(message.chat.id, "Reload needed!")


@bot.message_handler(func=total_days_request)
def send_total_days(message):
    try:
        bot.send_message(message.chat.id, analysis.totalDays())
    except:
        bot.send_message(message.chat.id, "Reload needed!")


def user_request(message):
    return message.text in analysis.peerMap.keys()


@bot.message_handler(func=user_request)
def send_npk(message):
    cid = message.chat.id
    message_text = message.text
    if message_text in analysis.peerMap:
        try:
            bot.send_message(cid, analysis.peerMap[message_text])
        except:
            bot.send_message(message.chat.id, "Reload needed!")
    else:
        bot.send_message(cid, "Invalid command!")


analysis.import_req()
bot.polling()
