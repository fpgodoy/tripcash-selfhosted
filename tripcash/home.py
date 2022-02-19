from flask import (Blueprint, blueprints, flash, g, redirect, render_template,
                   request, session, url_for)

from tripcash.auth import login_required
from tripcash.db import get_db

bp = Blueprint('home', __name__)


@bp.route('/', methods=('GET', 'POST'))
def index():
    # Access DB data.
    db = get_db()

    if g.user:
        user = g.user['id']

        # Get the trip list to populate the menu.
        db.execute(
            'SELECT trip_id, trip_name FROM trip WHERE user_id=%s',
            (g.user['id'],),
        )
        trip_list = db.fetchall()

        # Select the current trip from the menu list.
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

        # Check the current trip of the user.
        db.execute(
            'SELECT users.current_trip AS trip_id, trip.trip_name AS trip_name FROM users INNER JOIN trip on trip.trip_id=users.current_trip WHERE users.id=%s',
            (user,),
        )
        g.trip = db.fetchone()

        # Check the user has a trip.
        db.execute(
            'SELECT EXISTS(SELECT 1 FROM trip WHERE user_id=%s)',
            (g.user['id'],),
        )
        trip_count = db.fetchone()

        # Render the standard index it the user has trips.
        if trip_count[0] != 0:
            return render_template('index.html', trip_list=trip_list)

        # Render the welcome page to create the first trip if user don't have any one.
        else:
            return redirect(url_for('home.firsttime'))

    return render_template('index.html')

# Clear the current trip column to show the select trip menu.
@bp.route('/change_trip')
def change_trip():
    # Access DB data.
    db = get_db()

    # Update current trip to NULL.
    db.execute(
        'UPDATE users SET current_trip=NULL WHERE id=%s', (g.user['id'],)
    )
    g.db.commit()
    return redirect(url_for('index'))


# Render the welcome page to new users and for whom don't have any trip.
@bp.route('/firsttime', methods=('GET', 'POST'))
def firsttime():
    db = get_db()

    # Get and validate the form data.
    if request.method == 'POST':
        author = session.get('user_id')
        trip = request.form['trip_name'].strip()
        error = None

        if not trip:
            error = 'Need to fill the trip name.'

        # Insert the trip on DB.
        if error is None:
            db.execute(
                'INSERT INTO trip (user_id, trip_name) VALUES (%s, %s)',
                (author, trip),
            )
            g.db.commit()

            return redirect(url_for('index'))
        flash(error)

    # Check if the user has a trip.
    db.execute(
        'SELECT EXISTS(SELECT 1 FROM trip WHERE user_id=%s)', (g.user['id'],)
    )
    trip_count = db.fetchone()

    # If user has a trip render the standard index page.
    if trip_count[0] != 0:
        return redirect(url_for('index'))

    # Otherwise render the welcome page.
    return render_template('firsttime.html')
