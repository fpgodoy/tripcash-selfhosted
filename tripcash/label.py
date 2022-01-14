from flask import (
    Blueprint, blueprints, flash, g, redirect, render_template, request, session, url_for
)

from tripcash.db import get_db

from tripcash.auth import login_required

from werkzeug.exceptions import abort

bp = Blueprint('label', __name__)

# Form to create new label and List of registered labels
@bp.route('/label', methods=('GET', 'POST'))
@login_required
def label():
    
    # Get db data
    db = get_db()
    label_list = db.execute(
        'SELECT label_id, label_name FROM labels WHERE user=?', (g.user['id'],)
    ).fetchall()

    if request.method == 'POST':
        user = session.get('user_id')
        label = request.form['label'].strip()
        error = None

        checklabel = []
        for row in label_list:
            checklabel.append(row['label_name'].upper())

        if not label:
            error = 'Need to fill the label name.'

        if label.upper() in checklabel:
            error = f"Label {label} is already registered."

        if error is None:
                # Insert the new label into the DB
                db.execute(
                    'INSERT INTO labels (label_name, user) VALUES (?, ?)',
                    (label, user)
                )
                db.commit()
                        
                return redirect(url_for("label.label"))
                
            
        flash(error)

    return render_template('label.html', labels=label_list)
    
# Edit the name of a registered label
@bp.route('/<int:id>/editlabel', methods=('GET', 'POST'))
@login_required
def editlabel(id):

    label = get_label(id)

    db = get_db()
    label_list = db.execute(
        'SELECT label_name FROM labels WHERE user=?', (g.user['id'],)
    ).fetchall()

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
            error = f"Label {label} is already registered."

        if error is None:
                db.execute(
                    "UPDATE labels SET label_name = ? WHERE label_id = ?",
                    (label, id)
                )
                db.commit()
                        
                return redirect(url_for("label.label"))

    return render_template('editlabel.html', labels=label_list, label=label)

# Delete a registered label
@bp.route('/<int:id>/deletelabel', methods=('POST',))
@login_required
def deletelabel(id):
    label = get_label(id)
    user = session.get('user_id')
    db = get_db()
    db.execute('DELETE FROM labels WHERE label_id = ?', (id,))
    try:
        db.execute(
            'INSERT INTO labels (label_name, user) VALUES (?, ?)', ('others', user)
            )
    except:
        pass
    others_label = db.execute('SELECT label_id FROM labels WHERE user=? AND label_name=?', (g.user['id'], 'others')).fetchone()
    db.execute(
        'UPDATE post SET label = ? WHERE label =?', (others_label[0], id)
    )
    db.commit()
    return redirect(url_for('label.label'))

# Get the clicked button label
def get_label(id):
    label = get_db().execute(
        'SELECT * FROM labels WHERE label_id = ?',
        (id,)
    ).fetchone()
    
    if label is None:
        abort(404, "This label doesn't exist.")

    if label['user'] != g.user['id']:
        abort(403)

    return label