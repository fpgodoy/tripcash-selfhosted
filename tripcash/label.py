from flask import (
    Blueprint, blueprints, flash, g, redirect, render_template, request, session, url_for
)

from tripcash.db import get_db

bp = Blueprint('label', __name__)

@bp.route('/label', methods=('GET', 'POST'))
def trip():
    db = get_db()

    if request.method == 'POST':
        label = request.form['label']
        error = None

        if not trip:
            error = 'Need to fill the label name.'

        if error is None:
                try:
                    db.execute(
                        'INSERT INTO labels (label_name) VALUES (?)',
                        (label, )
                    )
                    db.commit()

                except db.IntegrityError:
                    error = f"Label {label} is already registered."
                else:                    
                    return redirect(url_for("index"))
                
            
        flash(error)

    return render_template('label.html')
    