from flask import Blueprint, flash, g, redirect, render_template, request, url_for
from werkzeug.exceptions import abort

from tripcash.auth import login_required
from tripcash.db import get_db

bp = Blueprint('trip', __name__)


@bp.route('/trip', methods=('GET', 'POST'))
@login_required
def trip():
    # Get the data
    db = get_db()
    db.execute(
        '''SELECT * FROM trip WHERE user_id=%s
           UNION
           SELECT trip.* FROM trip
           INNER JOIN trip_participant ON trip.trip_id = trip_participant.trip_id
           WHERE trip_participant.name=%s AND trip_participant.is_user=TRUE
           ORDER BY trip_id''',
        (g.user['id'], g.user['username'])
    )
    trip_list = db.fetchall()
    current_trip_id = g.user['current_trip']
    return render_template('trip.html', trips=trip_list, current_trip_id=current_trip_id)


@bp.route('/trip/new', methods=('GET', 'POST'))
@login_required
def createtrip():
    if request.method == 'POST':
        author = g.user['id']
        trip_name = request.form['trip_name'].strip()
        is_group_trip = request.form.get('is_group_trip') == 'on'
        error = None

        db = get_db()
        db.execute(
            '''SELECT trip_name FROM trip WHERE user_id=%s
               UNION
               SELECT trip.trip_name FROM trip
               INNER JOIN trip_participant ON trip.trip_id = trip_participant.trip_id
               WHERE trip_participant.name=%s AND trip_participant.is_user=TRUE''',
            (g.user['id'], g.user['username'])
        )
        trip_list = db.fetchall()

        # Ensure the typed trip is a new trip
        checktrip = [row['trip_name'].upper() for row in trip_list]

        if not trip_name:
            error = 'Need to fill the trip name.'
        elif trip_name.upper() in checktrip:
            error = f'Trip {trip_name} is already registered.'

        # Insert the trip on the DB
        if error is None:
            db.execute(
                'INSERT INTO trip (user_id, trip_name, is_group_trip) VALUES (%s, %s, %s) RETURNING trip_id',
                (author, trip_name, is_group_trip),
            )
            new_trip_id = db.fetchone()['trip_id']

            if is_group_trip:
                # Add the user as a participant by default
                db.execute(
                    'INSERT INTO trip_participant (trip_id, name, is_user) VALUES (%s, %s, TRUE)',
                    (new_trip_id, g.user['username'])
                )

            g.db.commit()

            if is_group_trip:
                return redirect(url_for('trip.edittrip', id=new_trip_id))

            return redirect(url_for('trip.trip'))

        flash(error)

    return render_template('createtrip.html')


# Edit the name of a registered trip
@bp.route('/<int:id>/edittrip', methods=('GET', 'POST'))
@login_required
def edittrip(id):

    trip = get_trip(id)

    db = get_db()
    db.execute(
        '''SELECT trip_name FROM trip WHERE user_id=%s
           UNION
           SELECT trip.trip_name FROM trip
           INNER JOIN trip_participant ON trip.trip_id = trip_participant.trip_id
           WHERE trip_participant.name=%s AND trip_participant.is_user=TRUE''',
        (g.user['id'], g.user['username'])
    )
    trip_list = db.fetchall()

    if request.method == 'POST':
        if trip['user_id'] != g.user['id']:
            flash("Only the owner can edit the trip.")
            return redirect(url_for('trip.edittrip', id=id))

        trip_name = request.form['trip_name'].strip()
        error = None

        # Ensure there isn't another trip with the same name and validate the data
        checktrip = [row[0].upper() for row in trip_list if row[0] != trip['trip_name']]

        if not trip_name:
            error = 'Need to fill the trip name.'

        if trip_name.upper() in checktrip:
            error = f'Trip {trip_name} is already registered.'

        # Update the trip name on the DB
        if error is None:
            db.execute(
                'UPDATE trip SET trip_name = %s WHERE trip_id = %s', (trip_name, id)
            )
            g.db.commit()

            return redirect(url_for('trip.trip'))

        flash(error)

    # Get participants if it is a group trip
    participants = []
    if trip['is_group_trip']:
        db.execute('SELECT * FROM trip_participant WHERE trip_id=%s ORDER BY id', (id,))
        participants = db.fetchall()

    return render_template('edittrip.html', trip=trip, participants=participants)


# Delete a registered trip
@bp.route('/<int:id>/deletetrip', methods=('POST',))
@login_required
def deletetrip(id):
    # Get the data
    trip = get_trip(id)
    if trip['user_id'] != g.user['id']:
        abort(403, "Only the owner can delete the trip.")

    db = get_db()

    # Get the current trip
    db.execute('SELECT current_trip FROM users WHERE id = %s', (g.user['id'],))
    currentrip = db.fetchone()

    # Deleta a viagem. O CASCADE da FK cuida de:
    # trip_participant, post, expense_split e participant_payment automaticamente.
    db.execute('DELETE FROM trip WHERE trip_id = %s', (id,))

    # Check if the deleted trip is the current one and clear the current trip if it is
    if trip['trip_id'] == currentrip[0]:
        db.execute(
            'UPDATE users SET current_trip=NULL WHERE id=%s', (g.user['id'],)
        )
    g.db.commit()

    return redirect(url_for('trip.trip'))


@bp.route('/<int:id>/select', methods=('POST',))
@login_required
def selecttrip(id):
    # Verify trip is accessible
    trip = get_trip(id)
    if trip:
        db = get_db()
        db.execute('UPDATE users SET current_trip = %s WHERE id = %s', (id, g.user['id']))
        g.db.commit()
        return redirect(url_for('index'))
    return redirect(url_for('trip.trip'))


@bp.route('/<int:id>/add_participant', methods=('POST',))
@login_required
def add_participant(id):
    trip = get_trip(id)
    if not trip['is_group_trip']:
        abort(400, "Not a group trip.")

    name = request.form['participant_name'].strip()
    is_registered_user = request.form.get('is_registered_user') == 'true'

    if name:
        db = get_db()
        is_user_val = False
        if is_registered_user:
            db.execute('SELECT id FROM users WHERE username = %s', (name,))
            if db.fetchone():
                is_user_val = True

        db.execute(
            'INSERT INTO trip_participant (trip_id, name, is_user) VALUES (%s, %s, %s)',
            (id, name, is_user_val)
        )
        g.db.commit()
    return redirect(url_for('trip.edittrip', id=id))


@bp.route('/<int:trip_id>/delete_participant/<int:participant_id>', methods=('POST',))
@login_required
def delete_participant(trip_id, participant_id):
    get_trip(trip_id)
    db = get_db()

    db.execute('SELECT COUNT(*) FROM expense_split WHERE participant_id = %s', (participant_id,))
    split_count = db.fetchone()[0]

    db.execute('SELECT COUNT(*) FROM post WHERE payer_participant_id = %s', (participant_id,))
    payer_count = db.fetchone()[0]

    db.execute(
        'SELECT COUNT(*) FROM participant_payment WHERE payer_participant_id = %s OR receiver_participant_id = %s',
        (participant_id, participant_id)
    )
    payment_count = db.fetchone()[0]

    if split_count > 0 or payer_count > 0 or payment_count > 0:
        flash("Cannot delete participant because they have associated expenses or payments.")
        return redirect(url_for('trip.edittrip', id=trip_id))

    db.execute('DELETE FROM trip_participant WHERE id = %s AND trip_id = %s', (participant_id, trip_id))
    g.db.commit()
    return redirect(url_for('trip.edittrip', id=trip_id))


@bp.route('/search_users', methods=('GET',))
@login_required
def search_users():
    from flask import jsonify
    q = request.args.get('q', '').strip()
    if len(q) < 2:
        return jsonify([])

    db = get_db()
    db.execute('SELECT username FROM users WHERE username ILIKE %s LIMIT 10', (f'%{q}%',))
    results = [row['username'] for row in db.fetchall()]
    return jsonify(results)


# Get the clicked button trip
def get_trip(id):
    db = get_db()
    db.execute('SELECT * FROM trip WHERE trip_id = %s', (id,))
    trip = db.fetchone()

    if trip is None:
        abort(404, "This trip doesn't exist.")

    if trip['user_id'] != g.user['id']:
        db.execute(
            'SELECT id FROM trip_participant WHERE trip_id = %s AND name = %s AND is_user = TRUE',
            (id, g.user['username'])
        )
        if not db.fetchone():
            abort(403)

    return trip
