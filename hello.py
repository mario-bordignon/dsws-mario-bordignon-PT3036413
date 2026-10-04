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
from wtforms import StringField, SubmitField, BooleanField
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

# Recebem o aviso sempre, a cada novo usuário
DESTINATARIOS_FIXOS = [
    'm.bordignon@aluno.ifsp.edu.br',
]

CAIXA_TESTE = '1'
EMAIL_CAIXA = os.environ.get(f'FLASKY_CAIXA{CAIXA_TESTE}')
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
    enviar_caixa = BooleanField(f'Deseja enviar e-mail para {EMAIL_CAIXA}?')
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

# --- E-mails enviados (log) ---
class EmailEnviado(db.Model):
    __tablename__ = 'emails_enviados'
    id = db.Column(db.Integer, primary_key=True)
    de = db.Column(db.String(100))
    para = db.Column(db.String(300))
    assunto = db.Column(db.String(200))
    texto = db.Column(db.Text)
    data_hora = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<EmailEnviado {self.assunto!r} para {self.para!r}>'
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

    # debug
    print(f'[Mailgun] to={destinatarios} status={resposta.status_code} resposta={resposta.text}')

    return resposta

def notify_new_user(user, destinatarios):
    assunto = '[DSWS] Novo usuário cadastrado'
    corpo = (
        f'Prontuário: {PRONTUARIO_ALUNO}\n'
        f'Nome do aluno: {NOME_ALUNO}\n'
        f'Usuário cadastrado: {user.username}'
    )
    resposta = send_email(
        destinatarios,
        assunto,
        corpo
    )

    # Registra o envio no banco
    log = EmailEnviado(
        de=user.username,
        para=', '.join(destinatarios),
        assunto=assunto,
        texto=corpo,
    )
    db.session.add(log)
    db.session.commit()

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
            default_role = (Role.query.filter_by(name='Usuário').first()
                            or Role.query.filter_by(name='User').first())
            
            user = User(username=form.name.data, role=default_role)
            db.session.add(user)
            db.session.commit()

            # Fixos sempre; o FLASKY_CAIXA só se a caixa estiver marcada
            destinatarios = list(DESTINATARIOS_FIXOS)
            if form.enviar_caixa.data and EMAIL_CAIXA and EMAIL_CAIXA not in destinatarios:
                destinatarios.append(EMAIL_CAIXA)

            if notify_new_user(user, destinatarios): # notificar sobre a criação
                flash('Usuário cadastrado e e-mail enviado com sucesso!', 'success')
            else:
                flash('Usuário cadastrado, mas ocorreu um erro ao enviar o e-mail.', 'warning')

            session['known'] = False
        else:
            session['known'] = True
            
        session['name'] = form.name.data
        return redirect(url_for('index'))
    
    # Lista de usuários cadastrados (com a role de cada um)
    todos_os_usuarios = User.query.order_by(User.id).all()

    return render_template('index.html',
                           form=form,
                           nome_completo=session.get('name'),
                           known=session.get('known', False),
                           users=todos_os_usuarios)

# --- E-MAILS ENVIADOS ---
@app.route('/emails')
def emails_enviados():
    todos_os_emails = EmailEnviado.query.order_by(EmailEnviado.data_hora.desc()).all()
    return render_template('emails.html', emails=todos_os_emails)

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