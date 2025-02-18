#!/bin/bash

# 1) Executar makemigrations
echo "Executando makemigrations..."
python3 manage.py makemigrations

# 2) Executar migrate
echo "Executando migrate..."
python3 manage.py migrate

# 3) Coletar arquivos estáticos
echo "Coletando arquivos estáticos..."
python3 manage.py collectstatic --noinput --clear|| echo "Falha ao coletar estáticos, mas prosseguindo..."

# 4) Iniciar o servidor Django com uWSGI
echo "Iniciando Django com uWSGI..."
uwsgi --ini /app/uwsgi.ini