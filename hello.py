from datetime import datetime
from flask import Flask, render_template, request, session, redirect, url_for, flash
from flask_bootstrap import Bootstrap
from flask_moment import Moment

from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField, PasswordField
from wtforms.validators import DataRequired

import os
from flask_sqlalchemy import SQLAlchemy

basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)

# Chave ultra secreta
app.config['SECRET_KEY'] = 'chaveultrasecreta'

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'data.sqlite')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# region CLASSES
# Classe do formulário
class InfoForm(FlaskForm):
    nome_completo = StringField('Informe o seu nome completo:', validators=[DataRequired()])
    instituicao = StringField('Informe a sua instituição de ensino:', validators=[DataRequired()])
    
    disciplina = SelectField('Informe a sua disciplina:', choices=[
        ('', 'Escolha uma opção'),
        ('DWBC', 'DWBC'),
        ('PABD', 'PABD'), 
        ('DSWS', 'DSWS')
    ],
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

# Modelo de Cargos/Papéis
class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    
    # Relacionamento: Uma Role pode estar ligada a vários Users
    users = db.relationship('User', backref='role', lazy='dynamic')

    def __repr__(self):
        return f'<Role {self.name}>'

# Modelo de Usuários (Atualizado)
class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, index=True)
    
    # Chave estrangeira apontando para o id da tabela roles
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))

    def __repr__(self):
        return f'<User {self.username}>'

# Relógio global
@app.context_processor
def inject_time():
    return dict(current_time=datetime.utcnow())

# RAÍZ
@app.route('/', methods=['GET', 'POST'])
def index():
    form = InfoForm()
    
    if form.validate_on_submit():
        # Consulta no banco de dados
        user = User.query.filter_by(username=form.nome_completo.data).first()
        
        if user is None:
            user = User(username=form.nome_completo.data)
            db.session.add(user)
            db.session.commit()
            session['known'] = False
        else:
            session['known'] = True
            
        # Atualiza a sessão
        session['nome_completo'] = form.nome_completo.data
        session['instituicao'] = form.instituicao.data
        session['disciplina'] = form.disciplina.data
        return redirect(url_for('index'))
    
    ip_cliente = request.remote_addr
    host_app = request.host
        
    return render_template('index.html', 
                           form=form, 
                           nome_completo=session.get('nome_completo'),
                           instituicao=session.get('instituicao'),
                           disciplina=session.get('disciplina'),
                           ip_cliente=ip_cliente,
                           host_app=host_app,
                           known=session.get('known', False))

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

    