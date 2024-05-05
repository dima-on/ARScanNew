from flask import Flask, render_template, request, jsonify
import WorkFile
import ssl
import telegram_bot
import threading

import util_save

context = ssl.SSLContext(ssl.PROTOCOL_TLS)
context.load_cert_chain(certfile='ssl/cert.pem', keyfile='ssl/private.pem')


app = Flask(__name__)



@app.route('/')
def index():
    # Вызовите функции из вашей программы
    return render_template('GUI/index.html')


@app.route('/lick', methods=['POST'])
def lick():
    # Обработка загрузки фото
    uploaded_file = request.files['photo']
    tag = request.form.get('tag')
    TopIndex = request.form.get('TopIndex')
    DownIndex = request.form.get('DownIndex')



    if uploaded_file.filename != '':


        upload_folder = 'static/Input/'
        uploaded_file.save(upload_folder + "test.png")


        path = upload_folder + "test.png"
        tup = WorkFile.resImage(path, int(TopIndex), int(DownIndex), tag)
        XPr = tup[0]
        YPr = tup[1]
        SizeDis = tup[2]
        TopSize = tup[3]
        XPrDown = tup[4]
        YPrDown = tup[5]
        DownSize = tup[6]
        del tup

    return jsonify({'XPr': XPr, 'YPr': YPr, 'SizeDis': SizeDis, 'TopSize': TopSize, 'XPrDown': XPrDown, 'YPrDown': YPrDown, 'DownSize': DownSize})


@app.route('/StartProgram', methods=['POST'])
def StartAll():
    tag = request.form.get('tag')

    path = "ShopBD/" + str(tag) + ".txt"
    with open(path, 'r') as file:
        content = file.read()
    array = eval(content)

    Top_Image_Path = array[0]
    Down_Image_Path = array[5]
    Top_Price = array[10]
    Down_Price = array[11]
    print(Down_Price)
    return jsonify({'result_image': Top_Image_Path, 'result_imageD': Down_Image_Path, 'Top_Price': Top_Price, 'Down_Price': Down_Price})

@app.route('/send_buy', methods=['POST'])
def send_buy():
    name = request.form.get('name')
    id_buy = request.form.get('id')
    id_buy = [url.strip() for url in id_buy.split(",")]
    print(id_buy)
    tag = request.form.get('tag')
    data = util_save.open_json(tag + ".txt.json")
    data["cloth"].append(id_buy)
    data["name"].append(name)
    util_save.save_json(tag + ".txt.json", data)
    return jsonify({'result': "sus"})
def run_telegram_bot():
    telegram_bot.bot.polling(non_stop=True)

def run_flask_app():
    #app.run(host='0.0.0.0', port=5000)
    app.run(host='0.0.0.0', port=443, ssl_context=context)

if __name__ == '__main__':
    telegram_thread = threading.Thread(target=run_telegram_bot)
    flask_thread = threading.Thread(target=run_flask_app)

    telegram_thread.start()
    flask_thread.start()


