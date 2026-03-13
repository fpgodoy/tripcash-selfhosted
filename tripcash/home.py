from flask import (Blueprint, blueprints, flash, g, redirect, render_template,
                   request, session, url_for)
from flask_babel import _

from tripcash.auth import login_required
from tripcash.db import get_db

bp = Blueprint('home', __name__)


@bp.route('/', methods=('GET', 'POST'))
def index():
    db = get_db()

    if g.user and 'id' in g.user:
        user = g.user['id']

        db.execute(
            'SELECT trip_id, trip_name FROM trip WHERE user_id=%s',
            (g.user['id'],),
        )
        trip_list = db.fetchall()

        # Save the trip selected in the dropdown to the user's profile.
        if request.method == 'POST':
            current_trip = request.form['trip_name']
            error = None

            if error is None:
                db.execute(
                    'UPDATE users SET current_trip=%s WHERE id=%s',
                    (current_trip, g.user['id']),
                )
                g.db.commit()

            else:
                flash(error)

        db.execute(
            'SELECT users.current_trip AS trip_id, trip.trip_name AS trip_name FROM users INNER JOIN trip on trip.trip_id=users.current_trip WHERE users.id=%s',
            (user,),
        )
        g.trip = db.fetchone()

        db.execute(
            'SELECT EXISTS(SELECT 1 FROM trip WHERE user_id=%s)',
            (g.user['id'],),
        )
        trip_count = db.fetchone()

        if trip_count[0] != 0:
            return render_template('index.html', trip_list=trip_list)
        else:
            return redirect(url_for('home.firsttime'))

    return render_template('index.html')


# Resets the active trip so the user can switch to a different one.
@bp.route('/change_trip')
def change_trip():
    db = get_db()
    db.execute(
        'UPDATE users SET current_trip=NULL WHERE id=%s', (g.user['id'],)
    )
    g.db.commit()
    return redirect(url_for('index'))


# First-time setup: shown when the user has no trips yet.
@bp.route('/firsttime', methods=('GET', 'POST'))
def firsttime():
    db = get_db()

    if request.method == 'POST':
        author = session.get('user_id')
        trip = request.form['trip_name'].strip()
        error = None

        if not trip:
            error = _('Trip name is required.')

        if error is None:
            db.execute(
                'INSERT INTO trip (user_id, trip_name) VALUES (%s, %s)',
                (author, trip),
            )
            g.db.commit()
            return redirect(url_for('index'))
        flash(error)

    db.execute(
        'SELECT EXISTS(SELECT 1 FROM trip WHERE user_id=%s)', (g.user['id'],)
    )
    trip_count = db.fetchone()

    if trip_count[0] != 0:
        return redirect(url_for('index'))

    return render_template('firsttime.html')
