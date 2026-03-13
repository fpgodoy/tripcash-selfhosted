from flask import (Blueprint, blueprints, flash, g, redirect, render_template,
                   request, session, url_for)
from flask_babel import _
from werkzeug.exceptions import abort

from tripcash.auth import login_required
from tripcash.db import get_db

bp = Blueprint('label', __name__)


@bp.route('/label', methods=('GET', 'POST'))
@login_required
def label():

    db = get_db()
    db.execute(
        'SELECT label_id, label_name FROM labels WHERE user_id=%s',
        (g.user['id'],),
    )
    label_list = db.fetchall()

    if request.method == 'POST':
        user = session.get('user_id')
        label = request.form['label'].strip()
        error = None

        # Prevent duplicate categories (case-insensitive).
        checklabel = []
        for row in label_list:
            checklabel.append(row['label_name'].upper())

        if not label:
            error = 'Need to fill the label name.'

        if label.upper() in checklabel:
            error = f'Label {label} is already registered.'

        # Insert the new label into the DB
        if error is None:
            db.execute(
                'INSERT INTO labels (label_name, user_id) VALUES (%s, %s)',
                (label, user),
            )
            g.db.commit()

            return redirect(url_for('label.label'))

        flash(error)

    # System category names (e.g. Food, Transport) are translated at display time;
    # user-created ones are shown as-is.
    display_labels = [dict(row) | {'label_name': _(row['label_name'])} for row in label_list]
    return render_template('label.html', labels=display_labels)


@bp.route('/<int:id>/editlabel', methods=('GET', 'POST'))
@login_required
def editlabel(id):
    label = get_label(id)
    db = get_db()
    db.execute(
        'SELECT label_name FROM labels WHERE user_id=%s', (g.user['id'],)
    )
    label_list = db.fetchall()

    if request.method == 'POST':
        user = session.get('user_id')
        label = request.form['label'].strip()
        error = None

        checklabel = []
        for row in label_list:
            checklabel.append(row[0].upper())

        if not label:
            error = 'Need to fill the new label name.'

        if label.upper() in checklabel:
            error = f'Label {label} is already registered.'

        if error is None:
            db.execute(
                'UPDATE labels SET label_name = %s WHERE label_id = %s',
                (label, id),
            )
            g.db.commit()

            return redirect(url_for('label.label'))

    return render_template('editlabel.html', labels=label_list, label=label)


@bp.route('/<int:id>/deletelabel', methods=('POST',))
@login_required
def deletelabel(id):
    label = get_label(id)
    user = session.get('user_id')
    error = None
    db = get_db()

    # Ensure 'others' exists before reassigning expenses.
    db.execute(
        'INSERT INTO labels (label_name, user_id) SELECT %s, %s WHERE NOT EXISTS (SELECT label_id FROM labels WHERE user_id=%s AND label_name=%s)',
        ('others', g.user['id'], g.user['id'], 'others'),
    )
    g.db.commit()

    # Get 'others' label id
    db.execute(
        'SELECT label_id FROM labels WHERE user_id=%s AND label_name=%s',
        (g.user['id'], 'others'),
    )
    others = db.fetchone()

    if others['label_id'] == id:
        error = "You can't delete the others label."

    if error is None:
        # Move all expenses from the deleted category to 'others'.
        db.execute(
            'UPDATE post SET label = %s WHERE label =%s',
            (others['label_id'], id),
        )
        g.db.commit()

        # Delete the category
        db.execute('DELETE FROM labels WHERE label_id = %s', (id,))

        g.db.commit()
    else:
        flash(error)

    return redirect(url_for('label.label'))


# Fetch a label by ID, aborting with 403/404 if not found or not owned by current user.
def get_label(id):
    db = get_db()
    db.execute('SELECT * FROM labels WHERE label_id = %s', (id,))
    label = db.fetchone()

    if label is None:
        abort(404, "This label doesn't exist.")

    if label['user_id'] != g.user['id']:
        abort(403)

    return label
