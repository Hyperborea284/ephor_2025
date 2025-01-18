#!/bin/bash

# 1) Criar o superusuário (se necessário)
echo "Criando superusuário..."
python3 manage.py createsuperuser --noinput --username admin --email admin@example.com || echo "Superusuário já existe ou erro ao criar."

# 2) Executar makemigrations
echo "Executando makemigrations..."
python3 manage.py makemigrations

# 3) Executar migrate
echo "Executando migrate..."
python3 manage.py migrate

# 4) Coletar arquivos estáticos
echo "Coletando arquivos estáticos..."
python3 manage.py collectstatic --noinput || echo "Falha ao coletar estáticos, mas prosseguindo..."

# 5) Iniciar o servidor Django com uWSGI
echo "Iniciando Django com uWSGI..."
uwsgi --ini /app/uwsgi.ini