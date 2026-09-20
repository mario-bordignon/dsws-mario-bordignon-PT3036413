# =====================
# IMPORTAÇÕES DO FLASK 
# =====================
# region

# --- Bibliotecas padrão Python ---
import os
import requests
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

# --- Núcleo Flask ---
from flask import Flask, render_template, request, session, redirect, url_for, flash

# --- Interface e utilidades ---
from flask_bootstrap import Bootstrap
from flask_moment import Moment

# --- Formulários e Validações ---
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField, PasswordField
from wtforms.validators import DataRequired

# --- Banco de dados ---
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

# endregion




# ======================
# CONFIGURAÇÕES BÁSICAS
# ======================
# region

basedir = os.path.abspath(os.path.dirname(__file__))

# Recarrega o .env agora usando o caminho absoluto do projeto,
# garantindo que funcione não importa de onde o Flask for iniciado
load_dotenv(os.path.join(basedir, '.env'), override=True)

app = Flask(__name__)
app.config['SECRET_KEY'] = 'chaveultrasecreta' # Segurança contra CSRF
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'data.sqlite')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# --- MAILGUN ---
app.config['MAILGUN_API_URL'] = os.environ.get('MAILGUN_API_URL')
app.config['MAILGUN_API_KEY'] = os.environ.get('MAILGUN_API_KEY')
app.config['MAILGUN_FROM'] = os.environ.get('MAILGUN_FROM')

PRONTUARIO_ALUNO = 'PT3036413'
NOME_ALUNO = 'Mario Bordignon'

DESTINATARIOS_ADMIN = [
    'marioantoniobordignon585@gmail.com',
    'm.bordignon@aluno.ifsp.edu.br',
]
# endregion




# ====================
# INICIANDO EXTENSÕES 
# =====================
# region

db = SQLAlchemy(app)
bootstrap = Bootstrap(app)
moment = Moment(app)
migrate = Migrate(app, db)

# endregion




# ================
# CLASSES WTFORMS
# ================
# region

class NameForm(FlaskForm):
    name = StringField('Qual o seu nome?', validators=[DataRequired()])
    submit = SubmitField('Enviar')

#endregion




# =====================
# MODELOS DB SQLALCHEMY 
# ======================
# region

# --- Cargos ---
class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    users = db.relationship('User', backref='role', lazy='dynamic') # Uma Role pode estar ligada a vários Users

    def __repr__(self):
        return f'<Role {self.name}>'

# --- Usuários ---
class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, index=True)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id')) # FK apontando para o id da tabela roles

    def __repr__(self):
        return f'<User {self.username}>'
# endregion




# ================
# ENVIO DE E-MAIL
# ================
# region

def send_email(to, subject, text):
    destinatarios = ', '.join(to) if isinstance(to, (list, tuple)) else to

    resposta = requests.post(
        app.config['MAILGUN_API_URL'],
        auth=('api', app.config['MAILGUN_API_KEY']),
        data={
            'from': app.config['MAILGUN_FROM'],
            'to': destinatarios,
            'subject': subject,
            'text': text,
        }
    )

    # DEBUG temporário: mostra no terminal o que o Mailgun respondeu
    print(f'[Mailgun] status={resposta.status_code} resposta={resposta.text}')

    return resposta

def notify_new_user(user):
    corpo = (
        f'Prontuário: {PRONTUARIO_ALUNO}\n'
        f'Nome do aluno: {NOME_ALUNO}\n'
        f'Usuário cadastrado: {user.username}'
    )
    resposta = send_email(
        DESTINATARIOS_ADMIN,
        '[DSWS] Novo usuário cadastrado',
        corpo
    )
    return resposta.status_code == 200

# endregion





# --- CONTEXTOS GLOBAIS ---
# region

# --- Relógio global ---
@app.context_processor
def inject_time():
    return dict(current_time=datetime.utcnow())

#endregion





# --- ROTAS ---
# region

# --- Rota Raíz --- 
@app.route('/', methods=['GET', 'POST'])
def index():
    form = NameForm()

    if form.validate_on_submit():
        user = User.query.filter_by(username=form.name.data).first()
        
        if user is None:
            # Usa a role padrão 'User' para todo novo cadastro
            default_role = Role.query.filter_by(name='User').first()
            
            user = User(username=form.name.data, role=default_role)
            db.session.add(user)
            db.session.commit()

            email_enviado = notify_new_user(user) # notificar sobre a criação

            if email_enviado:
                flash('Usuário cadastrado e e-mail enviado com sucesso!', 'success')
            else:
                flash('Usuário cadastrado, mas ocorreu um erro ao enviar o e-mail.', 'warning')

            session['known'] = False
        else:
            session['known'] = True
            
        session['name'] = form.name.data
        return redirect(url_for('index'))
    
    return render_template('index.html',
                           form=form,
                           nome_completo=session.get('name'),
                           known=session.get('known', False))

# endregion





# --- ERROR HANDLING ---
# region

# --- ERRO 404 ---
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

# --- ERRO 500 - SERVIDOR ---
@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500

# endregion





# --- SERVIDOR LOCAL ---
if __name__ == '__main__':
    app.run(debug=True)