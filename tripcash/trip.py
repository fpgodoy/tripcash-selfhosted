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
    trip_list = db.execute(
        'SELECT trip_name FROM trip WHERE user=?', (g.user['id'],)
    ).fetchall()

    if request.method == 'POST':
        author = session.get('user_id')
        trip = request.form['trip_name'].strip()
        error = None

        checktrip = []
        for row in trip_list:
            checktrip.append(row[0].upper())

        if not trip:
            error = 'Need to fill the trip name.'

        if trip.upper() in checktrip:
            error = f"Trip {trip} is already registered."

        if error is None:
            db.execute(
                "INSERT INTO trip (user, trip_name) VALUES (?, ?)",
                (author, trip)
            )
            db.commit()
                
            return redirect(url_for("trip.trip"))    
            
        flash(error)

    return render_template('trip.html', trips=trip_list)
    