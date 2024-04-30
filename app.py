from flask import Flask, render_template, request, jsonify
import WorkFile
import ssl

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
        XPr, YPr, SizeDis, TopSize, XPrDown, YPrDown, DownSize = WorkFile.resImage(path, int(TopIndex), int(DownIndex), tag)

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
    return jsonify({'result_image': Top_Image_Path, 'result_imageD': Down_Image_Path})
if __name__ == '__main__':
    #app.run(host='0.0.0.0', port=443, ssl_context=context)
    app.run(host='0.0.0.0', port=5000)
