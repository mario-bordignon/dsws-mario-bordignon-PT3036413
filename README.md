# Desenvolvimento Web com Flask

Repositório referente à aulas de DSWS
Aluno: Mario Antonio Bordignon
Prontuário: PT3036413

## 1. Preparando o Ambiente

Crie o ambiente virtual na raiz:
```powershell
python -m venv venv
```

Conceda permissão:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

Ative o ambiente virtual:
```powershell
.\venv\Scripts\Activate.ps1
```

Instale as dependências necessárias:
```powershell
pip install -r requirements/common.txt
```

## 2. Criando e Configurando o Banco de Dados

Defina a variável de ambiente da aplicação e inicie o shell interativo do Flask:
```powershell
$env:FLASK_APP = "hello.py"
flask shell
```

Execute os comandos abaixo para criar o DB:
```python
from hello import db, Role, User

# Cria as tabelas no banco de dados
db.create_all()

# Associa a função padrão 'User' para qualquer registro sem função
[setattr(u, 'role', Role.query.filter_by(name='User').first()) for u in User.query.filter_by(role_id=None).all()]; db.session.commit()

exit()
```

## 3. Iniciando Localmente

Para iniciar o servidor de desenvolvimento localmente:
```powershell
flask --app hello run --debug
```

Acesse a aplicação pelo endereço: http://127.0.0.1:5000
