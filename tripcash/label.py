from flask import Blueprint, flash, g, redirect, render_template, request, url_for
from flask_babel import _
from werkzeug.exceptions import abort

from tripcash.auth import login_required
from tripcash.db import get_db

bp = Blueprint('label', __name__)


@bp.route('/label', methods=('GET', 'POST'))
@login_required
def label():
    db = get_db()
    # Retorna categorias do usuário + categorias globais (user_id IS NULL)
    # Globais aparecem primeiro (NULLS FIRST) para destacar as padrão do sistema
    db.execute(
        'SELECT label_id, label_name, user_id FROM labels '
        'WHERE user_id = %s OR user_id IS NULL '
        'ORDER BY user_id NULLS FIRST, label_name',
        (g.user['id'],),
    )
    label_list = db.fetchall()

    # Prepara dados para o template: traduz nome e indica se é padrão do sistema
    display_labels = [
        dict(row) | {
            'label_name': _(row['label_name']),
            'is_default': row['user_id'] is None
        }
        for row in label_list
    ]
    return render_template('label.html', labels=display_labels)


@bp.route('/label/new', methods=('GET', 'POST'))
@login_required
def createlabel():
    if request.method == 'POST':
        user = g.user['id']
        label_name = request.form['label'].strip()
        error = None

        db = get_db()
        # Verifica duplicatas entre categorias do usuário E globais
        db.execute(
            'SELECT label_id, label_name FROM labels WHERE user_id = %s OR user_id IS NULL',
            (g.user['id'],),
        )
        label_list = db.fetchall()

        # Previne nomes duplicados (insensível a maiúsculas/minúsculas)
        checklabel = [row['label_name'].upper() for row in label_list]

        if not label_name:
            error = 'Need to fill the label name.'
        elif label_name.upper() in checklabel:
            error = f'Label {label_name} is already registered.'

        if error is None:
            db.execute(
                'INSERT INTO labels (label_name, user_id) VALUES (%s, %s)',
                (label_name, user),
            )
            g.db.commit()

            return redirect(url_for('label.label'))

        flash(error)

    return render_template('createlabel.html')


@bp.route('/<int:id>/editlabel', methods=('GET', 'POST'))
@login_required
def editlabel(id):
    current_label = get_label(id)  # Aborta se for global ou não pertencer ao usuário
    db = get_db()
    db.execute(
        'SELECT label_name FROM labels WHERE user_id = %s OR user_id IS NULL',
        (g.user['id'],)
    )
    label_list = db.fetchall()

    if request.method == 'POST':
        new_label_name = request.form['label'].strip()
        error = None

        # Exclui o nome atual da checklist para permitir salvar sem alterações
        checklabel = [
            row[0].upper() for row in label_list
            if row[0].upper() != current_label['label_name'].upper()
        ]

        if not new_label_name:
            error = 'Need to fill the new label name.'

        if new_label_name.upper() in checklabel:
            error = f'Label {new_label_name} is already registered.'

        if error is None:
            db.execute(
                'UPDATE labels SET label_name = %s WHERE label_id = %s',
                (new_label_name, id),
            )
            g.db.commit()

            return redirect(url_for('label.label'))

        flash(error)

    display_label_list = [[_(row[0])] for row in label_list]
    return render_template('editlabel.html', labels=display_label_list, label=current_label)


@bp.route('/<int:id>/deletelabel', methods=('POST',))
@login_required
def deletelabel(id):
    get_label(id)  # Aborta se for global (user_id IS NULL) ou não pertencer ao usuário
    db = get_db()

    # Busca categoria global 'Others' como fallback para despesas órfãs
    db.execute(
        'SELECT label_id FROM labels WHERE user_id IS NULL AND label_name = %s',
        ('Others',),
    )
    others = db.fetchone()

    if others is None:
        flash("System category 'Others' not found. Cannot delete category.")
        return redirect(url_for('label.label'))

    # Move todas as despesas desta categoria para 'Others' global
    db.execute(
        'UPDATE post SET label = %s WHERE label = %s',
        (others['label_id'], id),
    )
    g.db.commit()

    # Exclui a categoria
    db.execute('DELETE FROM labels WHERE label_id = %s', (id,))
    g.db.commit()

    return redirect(url_for('label.label'))


def get_label(id):
    """Retorna o label pelo id. Aborta com 403 se for global ou não pertencer ao usuário."""
    db = get_db()
    db.execute('SELECT * FROM labels WHERE label_id = %s', (id,))
    label = db.fetchone()

    if label is None:
        abort(404, "This label doesn't exist.")

    # Categorias globais (user_id IS NULL) não podem ser modificadas por ninguém
    if label['user_id'] is None:
        abort(403, "System default categories cannot be modified.")

    if label['user_id'] != g.user['id']:
        abort(403)

    return label
