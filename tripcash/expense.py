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

from datetime import datetime

bp = Blueprint('expense', __name__)


@bp.route('/expense', methods=('GET', 'POST'))
@login_required
def expense():
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

    checklabel = []
    for row in label_list:
        checklabel.append(row[0])

    if request.method == 'POST':
        author = g.user['id']
        trip = g.trip['trip_id']
        date = request.form['date']
        amount = request.form['amount']
        title = request.form['title']
        label = int(request.form['label'])
        error = None

        if not date or not amount or not title or not label:
            error = 'All the fields should be filled.'

        if label not in checklabel:
            error = 'Invalid label.'

        if error is None:
            db.execute(
                'INSERT INTO post (author_id, trip, post_date, amount, title, label) VALUES (?, ?, ?, ?, ?, ?)',
                (author, trip, date, amount, title, label),
            )
            db.commit()
            return redirect(url_for('list.list'))

        flash(error)

    return render_template(
        'expense.html', label_list=label_list, today=datetime.today()
    )
