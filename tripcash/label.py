from flask import (Blueprint, blueprints, flash, g, redirect, render_template,
                   request, session, url_for)
from werkzeug.exceptions import abort

from tripcash.auth import login_required
from tripcash.db import get_db

bp = Blueprint('label', __name__)

# Form to create new label and List of registered labels
@bp.route('/label', methods=('GET', 'POST'))
@login_required
def label():

    # Get db data
    db = get_db()
    db.execute(
        'SELECT label_id, label_name FROM labels WHERE user_id=%s',
        (g.user['id'],),
    )
    label_list = db.fetchall()

    if request.method == 'POST':
        # Get the data
        user = session.get('user_id')
        label = request.form['label'].strip()
        error = None

        # Validate the data
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

    return render_template('label.html', labels=label_list)


# Edit the name of a registered label
@bp.route('/<int:id>/editlabel', methods=('GET', 'POST'))
@login_required
def editlabel(id):

    # Get the data
    label = get_label(id)
    db = get_db()
    db.execute(
        'SELECT label_name FROM labels WHERE user_id=%s', (g.user['id'],)
    )
    label_list = db.fetchall()

    if request.method == 'POST':
        # Get the form data
        user = session.get('user_id')
        label = request.form['label'].strip()
        error = None

        # Validate the data
        checklabel = []
        for row in label_list:
            checklabel.append(row[0].upper())

        if not label:
            error = 'Need to fill the new label name.'

        if label.upper() in checklabel:
            error = f'Label {label} is already registered.'

        # Change the label name
        if error is None:
            db.execute(
                'UPDATE labels SET label_name = %s WHERE label_id = %s',
                (label, id),
            )
            g.db.commit()

            return redirect(url_for('label.label'))

    return render_template('editlabel.html', labels=label_list, label=label)


# Delete a registered label
@bp.route('/<int:id>/deletelabel', methods=('POST',))
@login_required
def deletelabel(id):
    # Get the data
    label = get_label(id)
    user = session.get('user_id')
    db = get_db()
    db.execute('DELETE FROM labels WHERE label_id = %s', (id,))

    # Check if exist a label called others
    db.execute(
        'SELECT label_id FROM labels WHERE user_id=%s AND label_name=%s',
        (g.user['id'], 'others'),
    )
    check_others = db.fetchone()

    # Create an others label if not existing
    if check_others is None:
        db.execute(
            'INSERT INTO labels (label_name, user_id) VALUES (%s, %s)',
            ('others', user),
        )
        db.execute(
            'SELECT label_id FROM labels WHERE user_id=%s AND label_name=%s',
            (g.user['id'], 'others'),
        )
        check_others = db.fetchone()

    # Change all the data from the deleted label do others label
    db.execute(
        'UPDATE post SET label = %s WHERE label =%s', (check_others[0], id)
    )
    g.db.commit()
    return redirect(url_for('label.label'))


# Get the clicked button label
def get_label(id):
    db = get_db()
    db.execute('SELECT * FROM labels WHERE label_id = %s', (id,))
    label = db.fetchone()

    if label is None:
        abort(404, "This label doesn't exist.")

    if label['user'] != g.user['id']:
        abort(403)

    return label
