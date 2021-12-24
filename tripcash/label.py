from flask import (
    Blueprint, blueprints, flash, g, redirect, render_template, request, session, url_for
)

from tripcash.db import get_db

from tripcash.auth import login_required

bp = Blueprint('label', __name__)

@bp.route('/label', methods=('GET', 'POST'))
@login_required
def trip():
    db = get_db()
    labels = db.execute(
        'SELECT label_name FROM labels WHERE user=?', (g.user['id'],)
    ).fetchall()

    if request.method == 'POST':
        user = session.get('user_id')
        label = request.form['label']
        error = None

        if not trip:
            error = 'Need to fill the label name.'

        if error is None:
                try:
                    db.execute(
                        'INSERT INTO labels (label_name, user) VALUES (?, ?)',
                        (label, user)
                    )
                    db.commit()

                except db.IntegrityError:
                    error = f"Label {label} is already registered."
                else:                    
                    return redirect(url_for("index"))
                
            
        flash(error)

    return render_template('label.html', labels=labels)
    