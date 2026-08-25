from datetime import datetime
from flask import Flask, render_template, request, session, redirect, url_for, flash
from flask_bootstrap import Bootstrap
from flask_moment import Moment

from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField, PasswordField
from wtforms.validators import DataRequired

app = Flask(__name__)

# Chave ultra secreta
app.config['SECRET_KEY'] = 'chaveultrasecreta'

# region CLASSES
# Classe do formulário
class InfoForm(FlaskForm):
    nome = StringField('Informe o seu nome:', validators=[DataRequired()])
    sobrenome = StringField('Informe o seu sobrenome:', validators=[DataRequired()])
    instituicao = StringField('Informe a sua instituição de ensino:', validators=[DataRequired()])
    
    disciplina = SelectField('Informe a sua disciplina:', choices=[
        ('', 'Escolha uma opção'),
        ('DWBC', 'DWBC'), # (Valor, Rótulo)
        ('PABD', 'PABD'), 
        ('DSWS', 'DSWS')
    ],
        # Mensagem de erro (apenas a fim de UX)
        validators=[DataRequired(message="Por favor, selecione uma disciplina válida na lista.")]
    )
    submit = SubmitField('Submit')

# Classe de Login Forms
class LoginForm(FlaskForm):
    usuario = StringField('Usuário ou e-mail', validators=[DataRequired()])
    senha = PasswordField('Informe a sua senha', validators=[DataRequired()])
    submit = SubmitField('Enviar')
# endregion

# Iniciando extensões
bootstrap = Bootstrap(app)
moment = Moment(app)

# Relógio global
@app.context_processor
def inject_time():
    return dict(current_time=datetime.utcnow())

# RAÍZ
@app.route('/', methods=['GET', 'POST'])
def index():
    form = InfoForm()
    
    # SE formulário enviado: atualiza dados
    if form.validate_on_submit():
        old_nome = session.get('nome')
        
        # Nome novo?
        if old_nome is not None and old_nome != form.nome.data:
            flash('Parece que você alterou o seu nome!')
            
        session['nome'] = form.nome.data
        session['sobrenome'] = form.sobrenome.data
        session['instituicao'] = form.instituicao.data
        session['disciplina'] = form.disciplina.data
        return redirect(url_for('index'))
    
    # Lembrei do uso de IF NOT no python e pesquisando vi que daria para utilizar aqui também, então usei para remover os "nones"
    if not session.get('nome'):
        session['nome'] = 'Mario'
        session['sobrenome'] = 'Bordignon'
        session['instituicao'] = 'IFSP'
        session['disciplina'] = 'Escolha uma opção'
        
    # Coletando os dados do contexto da requisição
    ip_cliente = request.remote_addr
    host_app = request.host
        
    # Renderiza a página enviando todas as variáveis necessárias[cite: 3]
    return render_template('index.html', 
                           form=form, 
                           nome=session.get('nome'),
                           sobrenome=session.get('sobrenome'),
                           instituicao=session.get('instituicao'),
                           disciplina=session.get('disciplina'),
                           ip_cliente=ip_cliente,
                           host_app=host_app,)

# LOGIN
@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    
    if form.validate_on_submit():
        session['usuario_login'] = form.usuario.data
        return redirect(url_for('login_response'))
        
    return render_template('login.html', form=form) 


# LOGIN RESPONSE
@app.route('/loginResponse')
def login_response():
    usuario = session.get('usuario_login', 'Desconhecido')
    
    return render_template('acesso.html', usuario=usuario)

# ERRO 404
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

# ERRO 500 - SERVIDOR
@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500

# Ativação local
if __name__ == '__main__':
    app.run(debug=True)

    