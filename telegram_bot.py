import telebot
import os
import json
import util_save
import time
import threading


bot = telebot.TeleBot(token='6867372014:AAE_G_4dsmQdsfIHX29X604AK2r8HHFLf_8')

user_state = {}
user_index = {}
user_shop = {}
keys = {} #name, num
regist = 0

#command
regist_command = "зарееструватися"
info_command = "iнформацiя"
clear_command = "очистити"
live_command = "вийти з аккаунта"


def get_login():
    all_db = os.listdir("ShopBD/")
    out = []
    for i in range(len(all_db)):
        path = "ShopBD/" + all_db[i]

        data = util_save.open_jsonAll(path)
        array = data["login_pass"]
        array.append(all_db[i])

        out.append(array)

    print(out)
    return out

def instalizite_shop_setting():
    global user_shop
    with open("util/setting_shop.json", "r") as json_file:
        data = json.load(json_file)
    user_shop = data
    print(user_shop)

def instalizite_keys():
    global keys
    filesRoot = os.listdir("order/")
    for file in filesRoot:
        path = "order/" + file
        data = util_save.open_jsonAll(path)
        count_keys = len(data["cloth"])
        keys[file] = count_keys
    print(keys)

def instalizite_all():
    global regist

    instalizite_keys()
    instalizite_shop_setting()
    regist = get_login()

instalizite_all()

def save_shop_setting():

    with open("util/setting_shop.json", "w") as json_file:
        json.dump(user_shop, json_file)

def get_information(name_shop):
    file_name = name_shop
    out_data = util_save.open_json(file_name)
    return out_data

def event_info(message):
    global keys
    data = get_information(user_shop.get(message))
    print(keys[user_shop.get(message)], len(data["cloth"]))

    if keys[user_shop.get(message)] != len(data["cloth"]):

        for i in range(keys[user_shop.get(message)], len(data["name"])):
            text = str(data["name"][i]) + " заказал " + str(data["cloth"][i])
            bot.send_message(message, text)

def send_info():
    for key in user_shop.keys():
        if user_shop.get(key) != None:
            print(key)
            event_info(key)
    for key in user_shop.keys():
        if user_shop.get(key) != None:
            data = get_information(user_shop.get(key))
            keys[user_shop.get(key)] = len(data["cloth"])

def time_info():
    while True:
        send_info()
        time.sleep(5)

def get_all_info(message):

    data = get_information(user_shop.get(str(message.chat.id)))
    for i in range(len(data["name"])):
        text = str(data["name"][i]) + " заказал " + str(data["cloth"][i])
        bot.send_message(message.chat.id, text)

    key = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    zero_button = telebot.types.KeyboardButton(info_command)
    one_button = telebot.types.KeyboardButton(clear_command)
    two_button = telebot.types.KeyboardButton(live_command)
    key.add(zero_button)
    key.add(one_button)
    key.add(two_button)

    bot.send_message(message.chat.id, 'всі замовлення', reply_markup=key)

def clear_info(message):
    util_save.clear_json(user_shop[str(message.chat.id)])
    for i in keys.keys():
        keys[i] = 0

    key = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    one_button = telebot.types.KeyboardButton(info_command)
    three_button = telebot.types.KeyboardButton(clear_command)
    two_button = telebot.types.KeyboardButton(live_command)

    key.add(one_button)
    key.add(three_button)
    key.add(two_button)

    bot.send_message(message.chat.id, 'всі замовлення очищенні', reply_markup=key)

@bot.message_handler(commands=['start'])
def start_fun(message):
    key = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    one_button = telebot.types.KeyboardButton(regist_command)
    key.add(one_button)
    bot.send_message(message.chat.id, 'Доброго дня вас вітає телеграм бот arscan цей бот допоможе менеджерам магазинів переглянути всі замовлення з сайту arscan.space', reply_markup=key)

@bot.message_handler(func=lambda message: user_state.get(message.chat.id) == 'wait_login')
def wait_login(message):
    log = message.text
    for i in range(len(regist)):
        if log == regist[i][0]:
            user_state[message.chat.id] = "wait_for_password"
            user_index[message.chat.id] = i
            bot.send_message(message.chat.id, "будь ласка, введіть пароль")
            break
    else:
        user_state[message.chat.id] = None
        bot.send_message(message.chat.id, "логін не знайдено. будь ласка перевірте введену інформацію і спробуєте ще раз")

        start_fun(message)

@bot.message_handler(func=lambda message: user_state.get(message.chat.id) == 'wait_for_password')
def wait_for_password(message):
    password = message.text
    if password == regist[user_index.get(message.chat.id)][1]:

        key = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
        one_button = telebot.types.KeyboardButton(info_command)
        three_button = telebot.types.KeyboardButton(clear_command)
        two_button = telebot.types.KeyboardButton(live_command)

        key.add(one_button)
        key.add(three_button)
        key.add(two_button)

        bot.send_message(message.chat.id, 'добрий день ви увійшли до облікового запису', reply_markup=key)

        user_state[message.chat.id] = None
        user_shop[str(message.chat.id)] = regist[user_index.get(message.chat.id)][2]
        save_shop_setting()
        print(user_shop)
    else:
        bot.send_message(message.chat.id, "пароль не вірний. будь ласка перевірте введену інформацію і спробуєте ще раз")
        user_state[message.chat.id] = None
        start_fun(message)

@bot.message_handler(content_types=["text"])
def answer(message):
    global keys
    print(message.text)

    if message.text == regist_command:
        user_state[message.chat.id] = "wait_login"
        bot.send_message(message.chat.id, "login:")

    elif message.text == info_command:
        get_all_info(message)

    elif message.text == live_command:

        user_shop[str(message.chat.id)] = None
        start_fun(message)
        save_shop_setting()
        print(user_shop)

    elif message.text == clear_command:
        clear_info(message)

    else:
        bot.send_message(message.chat.id, "Пробачте з'явилася помилка будь ласка спробуйте ще раз")
        start_fun(message)

def start_bot():
    bot.polling(none_stop=True)

def main():
    telegram_thread = threading.Thread(target=start_bot)
    res_info = threading.Thread(target=time_info)

    res_info.start()
    telegram_thread.start()

if __name__ == "__main__":
    main()
