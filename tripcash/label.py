from flask import (
    Blueprint, blueprints, flash, g, redirect, render_template, request, session, url_for
)

from tripcash.db import get_db

from tripcash.auth import login_required

bp = Blueprint('label', __name__)

@bp.route('/label', methods=('GET', 'POST'))
@login_required
def label():
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
            error = 'Need to fill the label name.'

        if label.upper() in checklabel:
            error = f"Label {label} is already registered."

        if error is None:
                db.execute(
                    'INSERT INTO labels (label_name, user) VALUES (?, ?)',
                    (label, user)
                )
                db.commit()
                        
                return redirect(url_for("label.label"))
                
            
        flash(error)

    return render_template('label.html', labels=label_list)
    