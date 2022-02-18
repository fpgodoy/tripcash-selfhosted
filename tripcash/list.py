from flask import (
    Blueprint,
    blueprints,
    flash,
    g,
    redirect,
    render_template,
    request,
    session,
    url_for,
)
from tripcash.auth import login_required

from tripcash.db import get_db

from werkzeug.exceptions import abort

bp = Blueprint('list', __name__)

# List all the registered expenses
@bp.route('/list')
@login_required
def list():
    # Access DB data
    db = get_db()
    user = g.user['id']
    g.trip = db.execute(
        'SELECT user.current_trip AS trip_id, trip.trip_name AS trip_name FROM user INNER JOIN trip on trip.trip_id=user.current_trip WHERE user.id=?',
        (g.user['id'],),
    ).fetchone()

    # Get the list of expenses from the current user and trip
    list = db.execute(
        'SELECT id, post.post_date AS date, post.amount, post.title, labels.label_name AS label FROM post INNER JOIN labels ON post.label=labels.label_id WHERE post.author_id = ? AND post.trip = ? ORDER BY date',
        (user, g.trip[0]),
    ).fetchall()

    return render_template('list.html', list=list)


# List the sum of expenses by label
@bp.route('/total', methods=('GET', 'POST'))
@login_required
def total():
    # Access DB data
    db = get_db()
    user = g.user['id']

    # Get the current trip
    g.trip = db.execute(
        'SELECT user.current_trip AS trip_id, trip.trip_name AS trip_name FROM user INNER JOIN trip on trip.trip_id=user.current_trip WHERE user.id=?',
        (g.user['id'],),
    ).fetchone()

    # Get the dates with registered expenses
    dates = db.execute(
        'SELECT DISTINCT post_date FROM post WHERE trip = ? AND author_id = ? ORDER BY post_date',
        (g.trip[0], g.user['id']),
    ).fetchall()

    if request.method == 'POST':
        # Get the selected date to filter data
        date = request.form['date']
        error = None

        checkdates = []
        for row in dates:
            checkdates.append(str(row[0]))

        # Get the unfiltered data showing all the totals
        if date == 'all':
            totals = db.execute(
                'SELECT SUM(post.amount) AS amount, labels.label_name AS label FROM post INNER JOIN labels ON post.label=labels.label_id  WHERE post.trip = ? AND post.author_id = ? GROUP BY label',
                (g.trip[0], g.user['id']),
            ).fetchall()
            return render_template(
                'total.html', totals=totals, dates_list=dates, date='Trip'
            )

        # Check the submited value
        if not date or (str(date) not in checkdates):
            error = 'Invalid date.'

        if error is None:
            # Get the filtered data from DB
            totals = db.execute(
                'SELECT SUM(post.amount) AS amount, labels.label_name AS label FROM post INNER JOIN labels ON post.label=labels.label_id  WHERE post.trip = ? AND post.author_id = ? AND post.post_date = ? GROUP BY label',
                (g.trip[0], g.user['id'], date),
            ).fetchall()

            return render_template(
                'total.html', totals=totals, dates_list=dates, date=date
            )

        else:
            flash(error)

    # Get the unfiltered data showing all the totals
    totals = db.execute(
        'SELECT SUM(post.amount) AS amount, labels.label_name AS label FROM post INNER JOIN labels ON post.label=labels.label_id  WHERE post.trip = ? AND post.author_id = ? GROUP BY label',
        (g.trip[0], g.user['id']),
    ).fetchall()

    return render_template(
        'total.html', totals=totals, dates_list=dates, date='Trip'
    )


# Get the clicked button expense ID to edit
def get_expense(id):
    expense = (
        get_db().execute('SELECT * FROM post WHERE id = ?', (id,)).fetchone()
    )

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
    g.trip = db.execute(
        'SELECT user.current_trip AS trip_id, trip.trip_name AS trip_name FROM user INNER JOIN trip on trip.trip_id=user.current_trip WHERE user.id=?',
        (g.user['id'],),
    ).fetchone()
    label_list = db.execute(
        'SELECT label_id, label_name FROM labels WHERE user = ?',
        (g.user['id'],),
    ).fetchall()
    trip_list = db.execute(
        'SELECT trip_id, trip_name FROM trip WHERE user = ?', (g.user['id'],)
    ).fetchall()

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

        if not trip or not date or not amount or not title or not label:
            error = 'All the fields should be filled.'

        if label not in checklabel:
            error = 'Invalid label.'

        if trip not in checktrip:
            error = 'Invalid trip.'

        if error is None:
            db.execute(
                'UPDATE post SET trip = ?, post_date = ?, amount = ?, title = ?, label = ? WHERE id = ?',
                (trip, date, amount, title, label, id),
            )
            db.commit()
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
    db.execute('DELETE FROM post WHERE id = ?', (id,))
    db.commit()
    return redirect(url_for('list.list'))
