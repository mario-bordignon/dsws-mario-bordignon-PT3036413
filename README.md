# Desenvolvimento web com flask

## Preparando o ambiente
-> Criar Venv: python -m venv venv
-> work on venv: .\venv\Scripts\Activate.ps1
-> Baixar arquivos: pip install -r requirements/common.txt

## Criando DB
-> variável de acesso: $env:FLASK_APP = "hello.py"
    • flask shell
    • db.create_all()
    • exit()

## Iniciando localmente
-> flask --app hello run --debug