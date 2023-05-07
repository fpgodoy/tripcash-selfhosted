import os
import click
from dotenv import load_dotenv
import psycopg2
import psycopg2.extras
from flask import current_app, g
from flask.cli import with_appcontext


# Carrega as variáveis de ambiente do arquivo .env
load_dotenv()

# Acesse as variáveis de ambiente usando os.environ
db_user = os.environ.get('DB_USER')
db_password = os.environ.get('DB_PASSWORD')
db_host = os.environ.get('DB_HOST')
db_name = os.environ.get('DB_NAME')


def get_db():
    if 'db' not in g:
        g.db = psycopg2.connect(
            host=db_host,
            database=db_name,
            user=db_user,
            password=db_password,
        )
    return g.db.cursor(cursor_factory=psycopg2.extras.DictCursor)


def close_db(e=None):
    db = g.pop('db', None)

    if db is not None:
        db.close()


def init_db():
    db = get_db()

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
        'user_id INTEGER NOT NULL,'
        'FOREIGN KEY (user_id) REFERENCES users (id));'
    )

    db.execute(
        'CREATE TABLE post (id SERIAL PRIMARY KEY,'
        'author_id INTEGER NOT NULL,'
        'trip INTEGER NOT NULL,'
        'post_date DATE NOT NULL,'
        'amount NUMERIC NOT NULL,'
        'title TEXT NOT NULL,'
        'label INTEGER NOT NULL,'
        'FOREIGN KEY (author_id) REFERENCES users (id),'
        'FOREIGN KEY (label) REFERENCES labels (label_id));'
    )

    db.execute(
        'CREATE TABLE trip (trip_id SERIAL PRIMARY KEY,'
        'trip_name TEXT NOT NULL,'
        'user_id INTEGER NOT NULL,'
        'FOREIGN KEY (user_id) REFERENCES users (id));'
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
