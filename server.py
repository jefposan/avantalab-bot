from flask import Flask, send_file
import os

app = Flask(__name__)


@app.route('/')
def home():
    return '<h3>✅ Servidor rodando. Acesse /dados.csv para visualizar o arquivo.</h3>'


@app.route('/dados.csv')
def baixar_csv():
    caminho = "dados.csv"
    if os.path.exists(caminho):
        return send_file(caminho, mimetype="text/csv", as_attachment=False)
    else:
        return "Arquivo não encontrado.", 404


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
