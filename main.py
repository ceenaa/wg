import os
import threading

import telebot

import analysis
import auto
import db
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
        bot.send_message(message.chat.id, analysis.calc_average())
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


def usage_request(message):
    return message.text == "Usage"


@bot.message_handler(func=usage_request)
def send_usage(message):
    try:
        connection = db.connect()
        data = db.get_usage_by_name(connection, analysis.conf_name)
        name = data[0]
        start_time = data[1]
        usage = float(data[2]) + analysis.temp_usage
        usage = format(usage, '.2f')
        connection.close()
        bot.send_message(message.chat.id,
                         "Name: " + name + "\nStart time: " + start_time + " : " + str(analysis.total_days()) + "days" +"\nUsage: " + usage + " Gib")
    except Exception as err:
        bot.send_message(message.chat.id, type(err).__name__ + " " + str(err))


def reset_usage_request(message):
    return message.text == "Reset usage"


@bot.message_handler(func=reset_usage_request)
def reset_usage(message):
    try:
        connection = db.connect()
        db.reset_usage_and_date_by_name(connection, analysis.conf_name)
        connection.commit()
        connection.close()
        bot.send_message(message.chat.id, "Usage reset!")
    except Exception as err:
        bot.send_message(message.chat.id, type(err).__name__ + " " + str(err))


def make_usage_request(message):
    return message.text == "Make usage"


@bot.message_handler(func=make_usage_request)
def make_usage(message):
    try:
        connection = db.connect()
        db.make_usage_for_name(connection, analysis.conf_name)
        connection.commit()
        connection.close()
        bot.send_message(message.chat.id, "Usage made!")
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


def reload_request(message):
    return message.text == "Reload"


@bot.message_handler(func=reload_request)
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
        bot.send_message(message.chat.id, f"{round(analysis.daily_average(), 2)} Gib")
    except Exception as err:
        bot.send_message(message.chat.id, type(err).__name__ + " " + str(err))


def export_request(message):
    return message.text == "Export"


@bot.message_handler(func=export_request)
def send_export(message):
    try:
        analysis.export()
        bot.send_message(message.chat.id, "Exported!")
    except Exception as err:
        bot.send_message(message.chat.id, type(err).__name__ + " " + str(err))


def total_days_request(message):
    return message.text == "Total days"


@bot.message_handler(func=total_days_request)
def send_total_days(message):
    try:
        bot.send_message(message.chat.id, analysis.total_days())
    except Exception as err:
        bot.send_message(message.chat.id, type(err).__name__ + " " + str(err))


def pause_request(message):
    if "Pause" in message.text:
        name = message.text.split(" ")[1]
        if name in analysis.peerMap.keys():
            return True
    return False


@bot.message_handler(func=pause_request)
def send_pause(message):
    try:
        name = message.text.split(" ")[1]
        analysis.pause_user(name)
        bot.send_message(message.chat.id, "Paused!")
    except Exception as err:
        bot.send_message(message.chat.id, type(err).__name__ + " " + str(err))


def unpause_request(message):
    if "Resume" in message.text:
        name = message.text.split(" ")[1]
        if name in analysis.peerMap.keys():
            return True
    return False


@bot.message_handler(func=unpause_request)
def send_unpause(message):
    try:
        name = message.text.split(" ")[1]
        analysis.resume_user(name)
        bot.send_message(message.chat.id, "Resumed!")
    except Exception as err:
        bot.send_message(message.chat.id, type(err).__name__ + " " + str(err))


def user_request(message):
    return message.text in analysis.peerMap.keys()


@bot.message_handler(func=user_request)
def send_npk(message):
    cid = message.chat.id
    message_text = message.text
    try:
        bot.send_message(cid, analysis.peerMap[message_text])
    except Exception as err:
        bot.send_message(message.chat.id, type(err).__name__ + " " + str(err))


def paused_users_request(message):
    return message.text == "Paused users"


@bot.message_handler(func=paused_users_request)
def send_paused_users(message):
    cid = message.chat.id
    try:
        connection = db.connect()
        paused_user = db.paused_users(connection)
        connection.close()
        s = ""
        i = 0
        for pu in paused_user:
            s += str(analysis.peerMap[pu[0]]) + "\n----------------\n"
            i += 1
            if i % 20 == 0:
                bot.send_message(message.chat.id, s)
                s = ""
        if s == "":
            bot.send_message(message.chat.id, "No paused user")
        if s != "":
            bot.send_message(message.chat.id, s)

    except Exception as err:
        bot.send_message(cid, type(err).__name__ + " " + str(err))


def polling():
    bot.infinity_polling(timeout=10, long_polling_timeout=5)


analysis.reload()
sheet.main()
threading.Thread(target=lambda: auto.auto(30 * 60)).start()
polling()
