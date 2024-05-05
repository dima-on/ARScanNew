import telebot
import os
import json
import util_save

bot = telebot.TeleBot(token='6867372014:AAE_G_4dsmQdsfIHX29X604AK2r8HHFLf_8')

user_state = {}
user_index = {}
user_shop = {}
regist = 0

#util_save.save_json("test.txt.json", {
    #"cloth": [[1, 24, 13], [12, 245, 134]],
    #"name": ["@Drag_GameStudio", "@Drag_GameStudio1"]
#})
def get_login():
    all_db = os.listdir("ShopBD/")
    out = []
    for i in range(len(all_db)):
        path = "ShopBD/" + all_db[i]

        with open(path, 'r') as file:
            content = file.read()

        array = eval(content)
        array[12].append(all_db[i])

        out.append(array[12])

    print(out)
    return out

def instalizite_shop_setting():
    global user_shop
    with open("util/setting_shop.json", "r") as json_file:
        data = json.load(json_file)
    user_shop = data
    print(user_shop)

regist = get_login()
instalizite_shop_setting()

def save_shop_setting():

    with open("util/setting_shop.json", "w") as json_file:
        json.dump(user_shop, json_file)

def get_information(name_shop):
    print(name_shop)
    file_name = name_shop + ".json"
    out_data = util_save.open_json(file_name)
    return out_data

@bot.message_handler(commands=['start'])
def start_fun(message):
    key = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    one_button = telebot.types.KeyboardButton("рег")
    key.add(one_button)
    bot.send_message(message.chat.id, 'Hello', reply_markup=key)

@bot.message_handler(func=lambda message: user_state.get(message.chat.id) == 'wait_login')
def wait_login(message):
    log = message.text
    for i in range(len(regist)):
        if log == regist[i][0]:
            user_state[message.chat.id] = "wait_for_password"
            user_index[message.chat.id] = i
            bot.send_message(message.chat.id, "password:")
            break

@bot.message_handler(func=lambda message: user_state.get(message.chat.id) == 'wait_for_password')
def wait_for_password(message):
    password = message.text
    if password == regist[user_index.get(message.chat.id)][1]:

        key = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
        one_button = telebot.types.KeyboardButton("инфа")
        two_button = telebot.types.KeyboardButton("выйти")

        key.add(one_button)
        key.add(two_button)

        bot.send_message(message.chat.id, 'привет', reply_markup=key)

        user_state[message.chat.id] = None
        user_shop[str(message.chat.id)] = regist[user_index.get(message.chat.id)][2]
        save_shop_setting()
        print(user_shop)
    else:
        bot.send_message(message.chat.id, "no")
        user_state[message.chat.id] = None

@bot.message_handler(content_types=["text"])
def answer(message):
    if message.text == "рег":
        user_state[message.chat.id] = "wait_login"
        bot.send_message(message.chat.id, "login:")

    if message.text == "инфа":
        print(user_shop)
        print(message.chat.id)
        data = get_information(user_shop.get(str(message.chat.id)))
        for i in range(len(data["name"])):
            text = str(data["name"][i]) + " заказал " + str(data["cloth"][i])
            bot.send_message(message.chat.id, text)

        key = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
        zero_button = telebot.types.KeyboardButton("инфа")
        one_button = telebot.types.KeyboardButton("clean")
        two_button = telebot.types.KeyboardButton("выйти")
        key.add(zero_button)
        key.add(one_button)
        key.add(two_button)

        bot.send_message(message.chat.id, 'd', reply_markup=key)

    if message.text == "выйти":
        user_shop[str(message.chat.id)] = None
        start_fun(message)
        save_shop_setting()
        print(user_shop)

    if message.text == "clean":
        util_save.clear_json(user_shop[str(message.chat.id)] + ".json")

        key = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
        one_button = telebot.types.KeyboardButton("инфа")
        two_button = telebot.types.KeyboardButton("выйти")

        key.add(one_button)
        key.add(two_button)

        bot.send_message(message.chat.id, 'привет', reply_markup=key)

if __name__ == "__main__":
    bot.polling(non_stop=True)

