import time
from flask import Flask, render_template, request, jsonify
import WorkFile
import ssl

context = ssl.SSLContext(ssl.PROTOCOL_TLS)
context.load_cert_chain(certfile='ssl/cert.pem', keyfile='ssl/private.pem')


app = Flask(__name__)



@app.route('/')
def index():
    # Вызовите функции из вашей программы
    WorkFile.BeginFun()
    return render_template('GUI/index.html')


@app.route('/lick', methods=['POST'])
def lick():
    # Обработка загрузки фото
    uploaded_file = request.files['photo']

    TopIndex = request.form.get('TopIndex')

    DownIndex = request.form.get('DownIndex')



    if uploaded_file.filename != '':


        # Сохраняем загруженное фото в папке uploads
        upload_folder = 'static/Input/'
        uploaded_file.save(upload_folder + uploaded_file.filename)

        path = upload_folder + uploaded_file.filename
        XPr, YPr, SizeDis, TopSize, XPrDown, YPrDown, DownSize = WorkFile.resImage(path, int(TopIndex), int(DownIndex))

    return jsonify({'XPr': XPr, 'YPr': YPr, 'SizeDis': SizeDis, 'TopSize': TopSize, 'XPrDown': XPrDown, 'YPrDown': YPrDown, 'DownSize': DownSize})


@app.route('/StartProgram', methods=['POST'])
def StartAll():
    Top_Image_Path = WorkFile.Top_Image_Path
    Down_Image_Path = WorkFile.Down_Image_Path
    return jsonify({'result_image': Top_Image_Path, 'result_imageD': Down_Image_Path})
if __name__ == '__main__':
    #app.run(host='0.0.0.0', port=443, ssl_context=context)
    app.run(host='0.0.0.0', port=5000)
