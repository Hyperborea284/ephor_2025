#!/bin/bash

# 1) Executar makemigrations
echo "Executando makemigrations..."
python3 manage.py makemigrations

# 2) Executar migrate
echo "Executando migrate..."
python3 manage.py migrate

# Carregar variáveis do .env (se existir)
if [ -f .env ]; then
    echo "Carregando variáveis do arquivo .env..."
    export $(grep -v '^#' .env | xargs)
fi

# 3) Criar superusuário (usando variáveis do ambiente/.env)
echo "Criando superusuário..."
DJANGO_SUPERUSER_USERNAME=${DJANGO_SUPERUSER_USERNAME:-admin}
DJANGO_SUPERUSER_EMAIL=${DJANGO_SUPERUSER_EMAIL:-admin@example.com}
DJANGO_SUPERUSER_PASSWORD=${DJANGO_SUPERUSER_PASSWORD:-password}

python3 manage.py createsuperuser \
    --username "$DJANGO_SUPERUSER_USERNAME" \
    --email "$DJANGO_SUPERUSER_EMAIL" \
    --noinput >/dev/null 2>&1 || true  # Ignora falhas

# Definir senha separadamente (necessário mesmo com --noinput)
echo "Definindo senha para o superusuário..."
python3 manage.py shell -c "from django.contrib.auth import get_user_model; User = get_user_model(); u = User.objects.get(username='$DJANGO_SUPERUSER_USERNAME'); u.set_password('$DJANGO_SUPERUSER_PASSWORD'); u.save()"

# 4) Coletar arquivos estáticos
echo "Coletando arquivos estáticos..."
python3 manage.py collectstatic --noinput || echo "Falha ao coletar estáticos, mas prosseguindo..."

# 5) Iniciar o servidor Django com uWSGI
echo "Iniciando Django com uWSGI..."
uwsgi --ini /app/uwsgi.ini