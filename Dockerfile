FROM python:3.11-slim

WORKDIR /app

# System dependencies required to build psycopg2 from source.
RUN apt-get update && \
    apt-get install -y --no-install-recommends libpq-dev gcc build-essential && \
    rm -rf /var/lib/apt/lists/*

COPY requirements.txt requirements-dev.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Ferramentas de dev (pytest, flake8) só instaladas se INSTALL_DEV=true no build
# Ex: docker build --build-arg INSTALL_DEV=true .
ARG INSTALL_DEV=false
RUN if [ "$INSTALL_DEV" = "true" ]; then pip install --no-cache-dir -r requirements-dev.txt; fi

COPY . .

# Compila os catálogos de tradução (.po -> .mo). Executado após COPY para os .po estarem disponíveis.
RUN pybabel compile -d tripcash/translations

# Garante que o entrypoint seja executável
RUN chmod +x entrypoint.sh

# Porta padrão exposta
EXPOSE 8000

# O entrypoint aguarda o banco, aplica migrations (alembic upgrade head)
# e só então inicia o gunicorn.
ENTRYPOINT ["/app/entrypoint.sh"]
