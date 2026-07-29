# A very simple Flask Hello World app for you to get started with...
from flask import Flask, request, make_response, redirect, abort
app = Flask(__name__)

# RAÍZ
@app.route('/')
def hello_world():
    return '<p>Alterações por meio do PythonAnyWhere -> GitHub</p><table><tr><td><b>Professor:</b></td><td>Professor Fabio Teixeira</td></tr><tr><td><b>Prontuário:</b></td><td>PT23820X</td></tr></table>'

# VARIÁVEL DE NOME
@app.route('/user/<name>')
def user(name):
    return '<h1>Olá, {}!</h1>'.format(name)

# REQUISIÇÃO DE CONTEXTO
@app.route('/contextorequisicao')
def contextorequisicao():
    user_agent = request.headers.get('User-Agent')
    return '<p>Seu navegador é {}'.format(user_agent)

# CÓDIGO STATUS DIFERENTE DO PADRÃO (200)
@app.route('/codigostatusdiferente')
def codigostatusdiferente():
    return '<h1>Bad Request</h1>', 400

# OBJETO RESPOSTA (Como cookies)
@app.route('/objetoresposta')
def objetoresposta():
    resposta = make_response('<h1>Documento com Cookies!</h1>')
    resposta.set_cookie('id_sessao', '12345')
    return resposta

# REDIRECIONAMENTO
@app.route('/redirecionamento')
def redirecionamento():
    return redirect('https://ptb.ifsp.edu.br/')

# ABORT 404
@app.route('/abortar')
def abortar():
    abort(404)