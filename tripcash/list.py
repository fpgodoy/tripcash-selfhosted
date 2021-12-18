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
        "SELECT trip, post_date AS date, currency, amount, title, label FROM post WHERE author_id = ?", (user,)
    ).fetchall()


    return render_template('list.html', list=list)