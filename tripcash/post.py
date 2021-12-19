from flask import (
    Blueprint, blueprints, flash, g, redirect, render_template, request, session, url_for
)
from tripcash.auth import login_required

from tripcash.db import get_db

bp = Blueprint('post', __name__)

@bp.route('/post', methods=('GET', 'POST'))
@login_required
def post():
    # Access DB data
    db = get_db()
    g.trip = db.execute(
            "SELECT user.current_trip AS trip_id, trip.trip_name AS trip_name FROM user INNER JOIN trip on trip.trip_id=user.current_trip WHERE user.id=?", (g.user['id'],)
        ).fetchone()
    currency_list = db.execute(
        'SELECT currency_name FROM currency'
    ).fetchall()
    label_list = db.execute(
        'SELECT label_id, label_name FROM labels'
    ).fetchall()
    
    
    if request.method == 'POST':       
        author = g.user['id']
        trip = g.trip[0]
        date = request.form['date']
        currency = request.form['currency']
        amount = request.form['amount']
        title = request.form['title']
        label = request.form['label']
        error = None

        if not date or not currency or not amount or not title or not label:
            error = 'All the fields should be filled.'
        
        # if currency not in currency_list[0]:
        #     error = 'Invalid currency.'
        
        # if label not in label_list[0]:
        #     error = 'Invalid label.'
        
        if error is None:
            db.execute(
                "INSERT INTO post (author_id, trip, post_date, currency, amount, title, label) VALUES (?, ?, ?, ?, ?, ?, ?)",
                (author, trip, date, currency, amount, title, label)
            )
            db.commit()
            return redirect(url_for('list.list'))
        
        flash(error)

    return render_template('post.html', currency_list=currency_list, label_list=label_list)
