import functools

from flask import (
    Blueprint, blueprints, flash, g, redirect, render_template, request, session, url_for
)

from tripcash.db import get_db

bp = Blueprint('post', __name__)

@bp.route('/post', methods=('GET', 'POST'))
def post():
    # Access DB data
    db = get_db()
    trip_list = db.execute(
        "SELECT trip_name FROM trip"
    ).fetchall()
    currency_list = db.execute(
        "SELECT currency_name FROM currency"
    ).fetchall()
    label_list = db.execute(
        "SELECT label_name FROM labels"
    ).fetchall()
    
    
    if request.method == 'POST':
        author = session['user_id']
        trip = request.form['trip']
        date = request.form['date']
        currency = request.form['currency']
        amount = request.form['amount']
        title = request.form['title']
        label = request.form['label']
        error = None

        if not trip or not date or not currency or not amount or not title or not label:
            error = 'All the fields should be filled.'
        
        if error is None:
            db.execute(
                "INSERT INTO post (author_id, trip, post_date, currency, amount, title, label) VALUES (?, ?, ?, ?, ?, ?, ?)",
                (author, trip, date, currency, amount, title, label)
            )
            db.commit()
            return redirect(url_for("index"))
        
        flash(error)

    return render_template('post.html', trip_list=trip_list, currency_list=currency_list, label_list=label_list)
