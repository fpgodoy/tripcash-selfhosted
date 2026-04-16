import os
from logging.config import fileConfig
from dotenv import load_dotenv

from alembic import context
from sqlalchemy import create_engine, pool, text

# Carrega as variáveis de ambiente do .env antes de qualquer leitura
load_dotenv()

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Constrói a URL de conexão do PostgreSQL a partir das variáveis de ambiente.
# Formato: postgresql+psycopg2://user:password@host/dbname
db_url = (
    f"postgresql+psycopg2://"
    f"{os.environ.get('DB_USER', 'tripuser')}:"
    f"{os.environ.get('DB_PASSWORD', '')}@"
    f"{os.environ.get('DB_HOST', 'localhost')}/"
    f"{os.environ.get('DB_NAME', 'tripcashdb')}"
)

# Sobrescreve a URL placeholder do alembic.ini
config.set_main_option("sqlalchemy.url", db_url)


def run_migrations_online() -> None:
    """Executa migrations com conexão direta ao banco (modo online).
    Usa NullPool pois o Alembic é executado como processo único (CLI),
    não como servidor web com múltiplas threads.
    """
    connectable = create_engine(db_url, poolclass=pool.NullPool)

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=None,  # Sem SQLAlchemy ORM models — usamos SQL bruto
        )
        with context.begin_transaction():
            context.run_migrations()


run_migrations_online()
