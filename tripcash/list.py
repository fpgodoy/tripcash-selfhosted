from flask import (Blueprint, blueprints, flash, g, redirect, render_template,
                   request, session, url_for)
from werkzeug.exceptions import abort

from tripcash.auth import login_required
from tripcash.db import get_db

bp = Blueprint('list', __name__)

# List all the registered expenses
@bp.route('/list')
@login_required
def list():
    # Access DB data
    db = get_db()
    user = g.user['id']
    db.execute(
        'SELECT users.current_trip AS trip_id, trip.trip_name AS trip_name FROM users INNER JOIN trip on trip.trip_id=users.current_trip WHERE users.id=%s',
        (g.user['id'],),
    )
    g.trip = db.fetchone()

    # Get the list of expenses from the current user and trip
    db.execute(
        'SELECT id, post.post_date AS date, post.amount, post.title, labels.label_name AS label FROM post INNER JOIN labels ON post.label=labels.label_id WHERE post.author_id = %s AND post.trip = %s ORDER BY date',
        (user, g.trip[0]),
    )
    list = db.fetchall()

    return render_template('list.html', list=list)


# List the sum of expenses by label
@bp.route('/total', methods=('GET', 'POST'))
@login_required
def total():
    # Access DB data
    db = get_db()
    user = g.user['id']

    # Get the current trip
    db.execute(
        'SELECT users.current_trip AS trip_id, trip.trip_name AS trip_name FROM users INNER JOIN trip on trip.trip_id=users.current_trip WHERE users.id=%s',
        (g.user['id'],),
    )
    g.trip = db.fetchone()

    # Get the dates with registered expenses
    db.execute(
        'SELECT DISTINCT post_date FROM post WHERE trip = %s AND author_id = %s ORDER BY post_date',
        (g.trip[0], g.user['id']),
    )
    dates = db.fetchall()

    if request.method == 'POST':
        # Get the selected date to filter data
        date = request.form['date']
        error = None

        checkdates = []
        for row in dates:
            checkdates.append(str(row[0]))

        # Get the unfiltered data showing all the totals
        if date == 'all':
            db.execute(
                'SELECT SUM(post.amount) AS amount, labels.label_name AS label FROM post INNER JOIN labels ON post.label=labels.label_id  WHERE post.trip = %s AND post.author_id = %s GROUP BY labels.label_name',
                (g.trip[0], g.user['id']),
            )
            totals = db.fetchall()
            return render_template(
                'total.html', totals=totals, dates_list=dates, date='Trip'
            )

        # Check the submited value
        if not date or (str(date) not in checkdates):
            error = 'Invalid date.'

        if error is None:
            # Get the filtered data from DB
            db.execute(
                'SELECT SUM(post.amount) AS amount, labels.label_name AS label FROM post INNER JOIN labels ON post.label=labels.label_id  WHERE post.trip = %s AND post.author_id = %s AND post.post_date = %s GROUP BY labels.label_name',
                (g.trip[0], g.user['id'], date),
            )
            totals = db.fetchall()

            return render_template(
                'total.html', totals=totals, dates_list=dates, date=date
            )

        else:
            flash(error)

    # Get the unfiltered data showing all the totals
    db.execute(
        'SELECT SUM(post.amount) AS amount, labels.label_name AS label FROM post INNER JOIN labels ON post.label=labels.label_id  WHERE post.trip = %s AND post.author_id = %s GROUP BY labels.label_name',
        (g.trip[0], g.user['id']),
    )
    totals = db.fetchall()

    return render_template(
        'total.html', totals=totals, dates_list=dates, date='Trip'
    )


# Get the clicked button expense ID to edit
def get_expense(id):
    db = get_db()
    db.execute('SELECT * FROM post WHERE id = %s', (id,))
    expense = db.fetchone()

    if expense is None:
        abort(404, "Register doesn't exist.")

    if expense['author_id'] != g.user['id']:
        abort(403)

    return expense


# Form to edit the expenses
@bp.route('/<int:id>/edit', methods=('GET', 'POST'))
@login_required
def edit(id):
    expense = get_expense(id)

    # Access DB data
    db = get_db()
    db.execute(
        'SELECT users.current_trip AS trip_id, trip.trip_name AS trip_name FROM users INNER JOIN trip on trip.trip_id=users.current_trip WHERE users.id=%s',
        (g.user['id'],),
    )
    g.trip = db.fetchone()
    
    # Get the label list.
    db.execute(
        'SELECT label_id, label_name FROM labels WHERE user_id = %s',
        (g.user['id'],),
    )
    label_list = db.fetchall()
    
    # Get the trip list.
    db.execute(
        'SELECT trip_id, trip_name FROM trip WHERE user_id = %s',
        (g.user['id'],),
    )
    trip_list = db.fetchall()

    checklabel = []
    for row in label_list:
        checklabel.append(row[0])

    checktrip = []
    for row in trip_list:
        checktrip.append(row[0])

    if request.method == 'POST':

        # Get the current data to fill the form
        trip = int(request.form['trip'])
        date = request.form['date']
        amount = request.form['amount']
        title = request.form['title']
        label = int(request.form['label'])
        error = None

        # Validate the form data
        if not trip or not date or not amount or not title or not label:
            error = 'All the fields should be filled.'

        if label not in checklabel:
            error = 'Invalid label.'

        if trip not in checktrip:
            error = 'Invalid trip.'

        if error is None:
            # Update the expense on DB
            db.execute(
                'UPDATE post SET trip = %s, post_date = %s, amount = %s, title = %s, label = %s WHERE id = %s',
                (trip, date, amount, title, label, id),
            )
            g.db.commit()
            return redirect(url_for('list.list'))

        flash(error)

    return render_template(
        'edit.html',
        label_list=label_list,
        trip_list=trip_list,
        expense=expense,
    )


# Delete an expense
@bp.route('/<int:id>/delete', methods=('POST',))
@login_required
def delete(id):
    get_expense(id)
    db = get_db()
    db.execute('DELETE FROM post WHERE id = %s', (id,))
    g.db.commit()
    return redirect(url_for('list.list'))
