"""Schema inicial completo — tabelas, índices e categorias padrão globais.

Revision ID: 0001
Revises:
Create Date: 2026-04-14

Notas:
- Esta migration faz um reset destrutivo (DROP CASCADE) antes de recriar tudo.
- A coluna labels.user_id é NULLABLE: NULL = categoria global do sistema.
- As categorias padrão são inseridas uma única vez como registros globais
  compartilhados por todos os usuários. Nomes em inglês — traduzidos em runtime.
"""
from alembic import op

revision = '0001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Reset destrutivo — garante schema limpo
    op.execute('DROP TABLE IF EXISTS participant_payment CASCADE')
    op.execute('DROP TABLE IF EXISTS expense_split CASCADE')
    op.execute('DROP TABLE IF EXISTS post CASCADE')
    op.execute('DROP TABLE IF EXISTS trip_participant CASCADE')
    op.execute('DROP TABLE IF EXISTS trip CASCADE')
    op.execute('DROP TABLE IF EXISTS labels CASCADE')
    op.execute('DROP TABLE IF EXISTS users CASCADE')

    # Tabela de usuários
    op.execute('''
        CREATE TABLE users (
            id SERIAL PRIMARY KEY,
            username TEXT UNIQUE NOT NULL,
            current_trip INTEGER,
            password TEXT NOT NULL
        )
    ''')

    # Tabela de categorias — user_id NULL = categoria global do sistema
    op.execute('''
        CREATE TABLE labels (
            label_id SERIAL PRIMARY KEY,
            label_name TEXT NOT NULL,
            user_id INTEGER,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')

    # Tabela de viagens
    op.execute('''
        CREATE TABLE trip (
            trip_id SERIAL PRIMARY KEY,
            trip_name TEXT NOT NULL,
            is_group_trip BOOLEAN DEFAULT FALSE,
            user_id INTEGER NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')

    # Participantes de viagens em grupo
    op.execute('''
        CREATE TABLE trip_participant (
            id SERIAL PRIMARY KEY,
            trip_id INTEGER NOT NULL,
            name TEXT NOT NULL,
            is_user BOOLEAN DEFAULT FALSE,
            FOREIGN KEY (trip_id) REFERENCES trip (trip_id) ON DELETE CASCADE
        )
    ''')

    # Despesas
    op.execute('''
        CREATE TABLE post (
            id SERIAL PRIMARY KEY,
            author_id INTEGER NOT NULL,
            trip INTEGER NOT NULL,
            post_date DATE NOT NULL,
            amount NUMERIC NOT NULL,
            title TEXT NOT NULL,
            label INTEGER NOT NULL,
            is_split BOOLEAN DEFAULT FALSE,
            payer_participant_id INTEGER,
            FOREIGN KEY (author_id) REFERENCES users (id),
            FOREIGN KEY (label) REFERENCES labels (label_id),
            FOREIGN KEY (payer_participant_id) REFERENCES trip_participant (id) ON DELETE RESTRICT,
            FOREIGN KEY (trip) REFERENCES trip (trip_id) ON DELETE CASCADE
        )
    ''')

    # Divisão de despesas entre participantes
    op.execute('''
        CREATE TABLE expense_split (
            id SERIAL PRIMARY KEY,
            expense_id INTEGER NOT NULL,
            participant_id INTEGER NOT NULL,
            amount_owed NUMERIC NOT NULL,
            FOREIGN KEY (expense_id) REFERENCES post (id) ON DELETE CASCADE,
            FOREIGN KEY (participant_id) REFERENCES trip_participant (id) ON DELETE RESTRICT
        )
    ''')

    # Pagamentos manuais de acerto entre participantes
    op.execute('''
        CREATE TABLE participant_payment (
            id SERIAL PRIMARY KEY,
            trip_id INTEGER NOT NULL,
            payer_participant_id INTEGER NOT NULL,
            receiver_participant_id INTEGER NOT NULL,
            amount NUMERIC NOT NULL,
            payment_date DATE NOT NULL,
            FOREIGN KEY (trip_id) REFERENCES trip (trip_id) ON DELETE CASCADE,
            FOREIGN KEY (payer_participant_id) REFERENCES trip_participant (id) ON DELETE RESTRICT,
            FOREIGN KEY (receiver_participant_id) REFERENCES trip_participant (id) ON DELETE RESTRICT
        )
    ''')

    # Índices de performance
    op.execute('CREATE INDEX idx_post_trip ON post(trip)')
    op.execute('CREATE INDEX idx_post_trip_date ON post(trip, post_date)')
    op.execute('CREATE INDEX idx_expense_split_expense ON expense_split(expense_id)')
    op.execute('CREATE INDEX idx_expense_split_participant ON expense_split(participant_id)')
    op.execute('CREATE INDEX idx_trip_participant_trip ON trip_participant(trip_id)')
    op.execute('CREATE INDEX idx_labels_user ON labels(user_id)')
    op.execute('CREATE INDEX idx_participant_payment_trip ON participant_payment(trip_id)')

    # Categorias padrão globais — user_id NULL, compartilhadas por todos os usuários.
    # Os nomes são armazenados em inglês e traduzidos no momento da exibição via Flask-Babel.
    op.execute("""
        INSERT INTO labels (label_name, user_id) VALUES
        ('Food', NULL),
        ('Transport', NULL),
        ('Tickets', NULL),
        ('Accommodation', NULL),
        ('Others', NULL)
    """)


def downgrade() -> None:
    op.execute('DROP TABLE IF EXISTS participant_payment CASCADE')
    op.execute('DROP TABLE IF EXISTS expense_split CASCADE')
    op.execute('DROP TABLE IF EXISTS post CASCADE')
    op.execute('DROP TABLE IF EXISTS trip_participant CASCADE')
    op.execute('DROP TABLE IF EXISTS trip CASCADE')
    op.execute('DROP TABLE IF EXISTS labels CASCADE')
    op.execute('DROP TABLE IF EXISTS users CASCADE')
