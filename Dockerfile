FROM python:3.11-slim

WORKDIR /app

# System dependencies required to build psycopg2 from source.
RUN apt-get update && \
    apt-get install -y --no-install-recommends libpq-dev gcc build-essential && \
    rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Separate step so Docker can cache the layer and skip reinstall on code-only changes.
RUN pip install pytest

COPY . .

# Compile translation catalogs (.po -> .mo). Run after COPY so the .po files are available.
RUN pybabel compile -d tripcash/translations

# Porta padrão exposta
EXPOSE 8000

# Send access and error logs to stdout/stderr so Docker captures them via 'docker-compose logs'.
CMD ["gunicorn", "-b", "0.0.0.0:8000", "--access-logfile", "-", "--error-logfile", "-", "tripcash:create_app()"]
