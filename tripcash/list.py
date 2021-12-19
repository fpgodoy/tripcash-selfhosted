from flask import (
    Blueprint, blueprints, flash, g, redirect, render_template, request, session, url_for
)
from tripcash.auth import login_required

from tripcash.db import get_db

bp = Blueprint('list', __name__)

@bp.route('/list')
@login_required
def list():
    # Access DB data
    db = get_db()
    user = g.user['id']

    list = db.execute(
        "SELECT trip.trip_name AS trip, post.post_date AS date, post.currency, post.amount, post.title, labels.label_name FROM post INNER JOIN trip ON post.trip=trip.trip_id INNER JOIN labels ON post.label=labels.label_id WHERE author_id = ?"
        , (user,)
    ).fetchall()

    return render_template('list.html', list=list)

@bp.route('/total')
@login_required
def total():
    # Access DB data
    db = get_db()
    user = g.user['id']

    totals = db.execute(
        "SELECT SUM(post.amount) AS amount, labels.label_name AS label FROM post INNER JOIN labels ON post.label=labels.label_id  WHERE author_id = ? GROUP BY label"
        , (user,)
    ).fetchall()

    return render_template('total.html', totals=totals)