from datetime import datetime
from flask import Flask, render_template, request, session, redirect, url_for, flash
from flask_bootstrap import Bootstrap
from flask_moment import Moment

from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired

app = Flask(__name__)

# Chave ultra secreta
app.config['SECRET_KEY'] = 'chaveultrasecreta'

# Classe do formulário
class NameForm(FlaskForm):
    name = StringField('Qual o seu nome?', validators=[DataRequired()])
    submit = SubmitField('Enviar')

# Iniciando extensões
bootstrap = Bootstrap(app)
moment = Moment(app)

# RAÍZ
@app.route('/')
def index():
    return render_template('index.html', current_time = datetime.utcnow())

# IDENTIFICAÇÃO
@app.route('/user/<name>')
@app.route('/user/<name>/<prontuario>')
@app.route('/user/<name>/<prontuario>/<instituicao>')
def user(name, prontuario='PT3036413', instituicao='IFSP'):
    return render_template('id.html', name=name, prontuario=prontuario, instituicao=instituicao)

# REQUISIÇÃO DE CONTEXTO
@app.route('/contextorequisicao/<name>')
def contextorequisicao(name):
    navegador = request.headers.get('User-Agent')
    ip_cliente = request.remote_addr
    host_app = request.host
    return render_template('contexto.html', name=name, navegador=navegador, ip_cliente=ip_cliente, host_app=host_app)

# ERRO 404
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

# ERRO 500 - SERVIDOR
@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500

# FORMULÁRIO
@app.route('/formulario', methods=['GET', 'POST'])
def formulario():
    form = NameForm()
    
    if form.validate_on_submit():
        old_name = session.get('name')
        
        if old_name is not None and old_name != form.name.data:
            flash('Parece que você alterou seu nome!')
        
        
        session['name'] = form.name.data
        
        return redirect(url_for('formulario'))
    
    
    return render_template('formulario.html', form=form, name=session.get('name'))





# Ativação local
if __name__ == '__main__':
    app.run(debug=True)

    