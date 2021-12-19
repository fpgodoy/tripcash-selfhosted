from flask import (
    Blueprint, blueprints, flash, g, redirect, render_template, request, session, url_for
)
from tripcash.auth import login_required

from tripcash.db import get_db

bp = Blueprint('home', __name__)

@bp.route('/', methods=('GET', 'POST'))
def index():
    # Access DB data
    db = get_db()
    
    if g.user:
        user = g.user['id']

        trip_list = db.execute(
            'SELECT trip_id, trip_name FROM trip WHERE user=?', (g.user['id'],)
        ).fetchall()

        if request.method == 'POST':        
            current_trip = request.form['trip']
            error = None

            if error is None:
                db.execute(
                    "UPDATE user SET current_trip=? WHERE id=?", (current_trip, g.user['id'])
                )
                db.commit()
            
            else:
                flash(error)

        g.trip = db.execute(
                    "SELECT user.current_trip AS trip_id, trip.trip_name AS trip_name FROM user INNER JOIN trip on trip.trip_id=user.current_trip WHERE user.id=?", (user,)
                ).fetchone()

        return render_template("index.html", trip_list=trip_list)
    return render_template("index.html")

@bp.route('/change_trip')
def change_trip():
    # Access DB data
    db = get_db()

    # Update current trip to NULL
    db.execute(
        "UPDATE user SET current_trip=NULL WHERE id=?", (g.user['id'],)
    )
    db.commit()
    return redirect(url_for('index'))