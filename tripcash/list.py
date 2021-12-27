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
    g.trip = db.execute(
            "SELECT user.current_trip AS trip_id, trip.trip_name AS trip_name FROM user INNER JOIN trip on trip.trip_id=user.current_trip WHERE user.id=?", (g.user['id'],)
        ).fetchone()

    list = db.execute(
        "SELECT post.post_date AS date, post.amount, post.title, labels.label_name AS label FROM post INNER JOIN labels ON post.label=labels.label_id WHERE post.author_id = ? AND post.trip = ?"
        , (user, g.trip[0])
    ).fetchall()

    return render_template('list.html', list=list)

@bp.route('/total')
@login_required
def total():
    # Access DB data
    db = get_db()
    user = g.user['id']
    g.trip = db.execute(
            "SELECT user.current_trip AS trip_id, trip.trip_name AS trip_name FROM user INNER JOIN trip on trip.trip_id=user.current_trip WHERE user.id=?", (g.user['id'],)
        ).fetchone()

    totals = db.execute(
        "SELECT SUM(post.amount) AS amount, labels.label_name AS label FROM post INNER JOIN labels ON post.label=labels.label_id  WHERE post.trip = ? AND post.author_id = ? GROUP BY label"
        , (g.trip[0], g.user['id'])
    ).fetchall()

    return render_template('total.html', totals=totals)