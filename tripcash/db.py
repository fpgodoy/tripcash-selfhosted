import os
import click
import psycopg2
import psycopg2.extras
import psycopg2.pool
from dotenv import load_dotenv
from flask import g
from flask.cli import with_appcontext


# Carrega as variáveis de ambiente do arquivo .env
load_dotenv()

# Acesse as variáveis de ambiente usando os.environ
db_user = os.environ.get('DB_USER')
db_password = os.environ.get('DB_PASSWORD')
db_host = os.environ.get('DB_HOST')
db_name = os.environ.get('DB_NAME')

# Pool de conexões compartilhado entre threads (lazy init na primeira chamada)
_connection_pool = None


def get_pool():
    """Retorna o pool de conexões. Cria na primeira chamada (lazy init)."""
    global _connection_pool
    if _connection_pool is None or _connection_pool.closed:
        _connection_pool = psycopg2.pool.ThreadedConnectionPool(
            minconn=2,
            maxconn=10,
            host=db_host,
            database=db_name,
            user=db_user,
            password=db_password,
        )
    return _connection_pool


def get_db():
    """Retorna um cursor DictCursor para a conexão do request atual.
    A conexão fica armazenada em g.db e é devolvida ao pool no final do request.
    """
    if 'db' not in g:
        g.db = get_pool().getconn()
    return g.db.cursor(cursor_factory=psycopg2.extras.DictCursor)


def close_db(e=None):
    """Devolve a conexão ao pool ao final do request.
    Faz rollback para garantir estado limpo antes de devolver ao pool.
    """
    db = g.pop('db', None)
    if db is not None:
        try:
            # Garante que não há transações abertas antes de devolver ao pool
            if not db.closed:
                db.rollback()
            get_pool().putconn(db)
        except Exception:
            db.close()


def init_db():
    db = get_db()

    # Drop existing tables to recreate clean schema
    db.execute('DROP TABLE IF EXISTS participant_payment CASCADE;')
    db.execute('DROP TABLE IF EXISTS expense_split CASCADE;')
    db.execute('DROP TABLE IF EXISTS post CASCADE;')
    db.execute('DROP TABLE IF EXISTS trip_participant CASCADE;')
    db.execute('DROP TABLE IF EXISTS trip CASCADE;')
    db.execute('DROP TABLE IF EXISTS labels CASCADE;')
    db.execute('DROP TABLE IF EXISTS users CASCADE;')

    # Create the tables on DB

    db.execute(
        'CREATE TABLE users (id SERIAL PRIMARY KEY,'
        'username TEXT UNIQUE NOT NULL,'
        'current_trip INTEGER,'
        'password TEXT NOT NULL);'
    )

    db.execute(
        'CREATE TABLE labels (label_id SERIAL PRIMARY KEY,'
        'label_name TEXT NOT NULL,'
        'user_id INTEGER,'  # NULL = categoria global do sistema
        'FOREIGN KEY (user_id) REFERENCES users (id));'
    )

    db.execute(
        'CREATE TABLE trip (trip_id SERIAL PRIMARY KEY,'
        'trip_name TEXT NOT NULL,'
        'is_group_trip BOOLEAN DEFAULT FALSE,'
        'user_id INTEGER NOT NULL,'
        'FOREIGN KEY (user_id) REFERENCES users (id));'
    )

    db.execute(
        'CREATE TABLE trip_participant (id SERIAL PRIMARY KEY,'
        'trip_id INTEGER NOT NULL,'
        'name TEXT NOT NULL,'
        'is_user BOOLEAN DEFAULT FALSE,'
        'FOREIGN KEY (trip_id) REFERENCES trip (trip_id) ON DELETE CASCADE);'
    )

    db.execute(
        'CREATE TABLE post (id SERIAL PRIMARY KEY,'
        'author_id INTEGER NOT NULL,'
        'trip INTEGER NOT NULL,'
        'post_date DATE NOT NULL,'
        'amount NUMERIC NOT NULL,'
        'title TEXT NOT NULL,'
        'label INTEGER NOT NULL,'
        'is_split BOOLEAN DEFAULT FALSE,'
        'payer_participant_id INTEGER,'
        'FOREIGN KEY (author_id) REFERENCES users (id),'
        'FOREIGN KEY (label) REFERENCES labels (label_id),'
        'FOREIGN KEY (payer_participant_id) REFERENCES trip_participant (id) ON DELETE RESTRICT,'
        'FOREIGN KEY (trip) REFERENCES trip (trip_id) ON DELETE CASCADE);'
    )

    db.execute(
        'CREATE TABLE expense_split (id SERIAL PRIMARY KEY,'
        'expense_id INTEGER NOT NULL,'
        'participant_id INTEGER NOT NULL,'
        'amount_owed NUMERIC NOT NULL,'
        'FOREIGN KEY (expense_id) REFERENCES post (id) ON DELETE CASCADE,'
        'FOREIGN KEY (participant_id) REFERENCES trip_participant (id) ON DELETE RESTRICT);'
    )

    db.execute(
        'CREATE TABLE participant_payment (id SERIAL PRIMARY KEY,'
        'trip_id INTEGER NOT NULL,'
        'payer_participant_id INTEGER NOT NULL,'
        'receiver_participant_id INTEGER NOT NULL,'
        'amount NUMERIC NOT NULL,'
        'payment_date DATE NOT NULL,'
        'FOREIGN KEY (trip_id) REFERENCES trip (trip_id) ON DELETE CASCADE,'
        'FOREIGN KEY (payer_participant_id) REFERENCES trip_participant (id) ON DELETE RESTRICT,'
        'FOREIGN KEY (receiver_participant_id) REFERENCES trip_participant (id) ON DELETE RESTRICT);'
    )

    # Índices de performance para colunas frequentemente filtradas
    db.execute('CREATE INDEX idx_post_trip ON post(trip);')
    db.execute('CREATE INDEX idx_post_trip_date ON post(trip, post_date);')
    db.execute('CREATE INDEX idx_expense_split_expense ON expense_split(expense_id);')
    db.execute('CREATE INDEX idx_expense_split_participant ON expense_split(participant_id);')
    db.execute('CREATE INDEX idx_trip_participant_trip ON trip_participant(trip_id);')
    db.execute('CREATE INDEX idx_labels_user ON labels(user_id);')
    db.execute('CREATE INDEX idx_participant_payment_trip ON participant_payment(trip_id);')

    # Categorias padrão globais — user_id NULL, compartilhadas por todos os usuários.
    # Nomes armazenados em inglês e traduzidos em runtime via Flask-Babel.
    # Babel extraction hooks: _('Food'); _('Transport'); _('Tickets'); _('Accommodation'); _('Others')
    db.execute(
        "INSERT INTO labels (label_name, user_id) VALUES "
        "('Food', NULL), ('Transport', NULL), ('Tickets', NULL), "
        "('Accommodation', NULL), ('Others', NULL)"
    )

    g.db.commit()


# Start the tables creation
@click.command('init-db')
@with_appcontext
def init_db_command():
    """Clear the existing data and create new tables."""
    init_db()
    click.echo('Initialized the database.')


def init_app(app):
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)
