from flask import (
    Blueprint, blueprints, flash, g, redirect, render_template, request, session, url_for
)

from tripcash.db import get_db

from tripcash.auth import login_required

bp = Blueprint('trip', __name__)

@bp.route('/trip', methods=('GET', 'POST'))
@login_required
def trip():
    db = get_db()

    if request.method == 'POST':
        author = session.get('user_id')
        trip = request.form['trip_name']
        error = None

        if not trip:
            error = 'Need to fill the trip name.'

        if error is None:
                try:
                    db.execute(
                        "INSERT INTO trip (user, trip_name) VALUES (?, ?)",
                        (author, trip)
                    )
                    db.commit()

                except db.IntegrityError:
                    error = f"Trip {trip} is already registered."
                else:                    
                    return redirect(url_for("index"))
                
            
        flash(error)

    return render_template('trip.html')
    