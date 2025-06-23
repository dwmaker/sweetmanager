#!/bin/sh
set -e

# Executa as migrações do banco de dados
echo "Aplicando migrações do banco de dados..."
python manage.py migrate


# Verifica se o superusuário existe
#if ! python manage.py shell -c "from django.contrib.auth import get_user_model; User = get_user_model(); exit(0) if User.objects.filter(username='admin').exists() else exit(1)"; then
#    echo "Criando superusuário..."
#    python manage.py createsuperuser --noinput --username admin --email admin@example.com
#else
#    echo "Superusuário já existe, pulando criação."
#fi

# Coleta arquivos estáticos (opcional, dependendo do seu setup)
echo "Coletando arquivos estáticos..."
python manage.py collectstatic --noinput

# Executa o comando passado para o container (ex: gunicorn, runserver)
exec "$@"
