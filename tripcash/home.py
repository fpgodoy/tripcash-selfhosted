from flask import Blueprint, flash, g, redirect, render_template, request, url_for
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
            '''SELECT t.trip_id, t.trip_name, t.is_group_trip FROM trip t
               WHERE t.user_id=%s
               UNION
               SELECT t.trip_id, t.trip_name, t.is_group_trip FROM trip t
               INNER JOIN trip_participant tp ON t.trip_id = tp.trip_id
               WHERE tp.name=%s AND tp.is_user=TRUE''',
            (g.user['id'], g.user['username']),
        )
        trip_list = db.fetchall()

        db.execute(
            'SELECT trip.* FROM users INNER JOIN trip on trip.trip_id=users.current_trip WHERE users.id=%s',
            (user,),
        )
        g.trip = db.fetchone()

        # Usa trip_list já buscado para evitar query EXISTS redundante (#14)
        if trip_list:
            return render_template('index.html', trip_list=trip_list)
        else:
            return redirect(url_for('home.firsttime'))

    return render_template('index.html')


# First-time setup: shown when the user has no trips yet.
@bp.route('/firsttime', methods=('GET', 'POST'))
@login_required
def firsttime():
    db = get_db()

    if request.method == 'POST':
        author = g.user['id']
        trip = request.form['trip_name'].strip()
        is_group_trip = request.form.get('is_group_trip') == 'on'
        error = None

        if not trip:
            error = _('Trip name is required.')

        if error is None:
            db.execute(
                'INSERT INTO trip (user_id, trip_name, is_group_trip) VALUES (%s, %s, %s) RETURNING trip_id',
                (author, trip, is_group_trip),
            )
            new_trip_id = db.fetchone()['trip_id']

            if is_group_trip:
                db.execute(
                    'INSERT INTO trip_participant (trip_id, name, is_user) VALUES (%s, %s, TRUE)',
                    (new_trip_id, g.user['username'])
                )
            g.db.commit()

            # Since it's the first trip, set current_trip immediately so the user doesn't need to select it manually
            db.execute('UPDATE users SET current_trip=%s WHERE id=%s', (new_trip_id, author))
            g.db.commit()

            if is_group_trip:
                return redirect(url_for('trip.edittrip', id=new_trip_id))

            return redirect(url_for('index'))
        flash(error)

    db.execute(
        '''SELECT EXISTS(
             SELECT 1 FROM trip t WHERE t.user_id=%s
             UNION
             SELECT 1 FROM trip t INNER JOIN trip_participant tp ON t.trip_id = tp.trip_id
             WHERE tp.name=%s AND tp.is_user=TRUE
           )''',
        (g.user['id'], g.user['username']),
    )
    trip_count = db.fetchone()

    if trip_count[0] != 0:
        return redirect(url_for('index'))

    return render_template('firsttime.html')
