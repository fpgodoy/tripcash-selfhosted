#!/bin/sh
set -e

echo "==> Aguardando banco de dados..."
# Tenta conectar ao PostgreSQL até ter sucesso (max 30 tentativas)
MAX_TRIES=30
COUNT=0
until python -c "
import os, psycopg2
psycopg2.connect(
    host=os.environ['DB_HOST'],
    dbname=os.environ['DB_NAME'],
    user=os.environ['DB_USER'],
    password=os.environ['DB_PASSWORD']
)
print('Banco disponivel.')
" 2>/dev/null; do
    COUNT=$((COUNT+1))
    if [ "$COUNT" -ge "$MAX_TRIES" ]; then
        echo "ERRO: banco nao respondeu apos $MAX_TRIES tentativas."
        exit 1
    fi
    echo "   Tentativa $COUNT/$MAX_TRIES — aguardando 1s..."
    sleep 1
done

echo "==> Aplicando migrations (alembic upgrade head)..."
alembic upgrade head

echo "==> Iniciando aplicacao (gunicorn)..."
exec gunicorn \
    -b 0.0.0.0:8000 \
    --workers "${GUNICORN_WORKERS:-1}" \
    --worker-tmp-dir /dev/shm \
    --access-logfile - \
    --error-logfile - \
    "tripcash:create_app()"
