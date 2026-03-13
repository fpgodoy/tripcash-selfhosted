import functools

from flask import (Blueprint, blueprints, flash, g, redirect, render_template,
                   request, session, url_for)
from flask_babel import _
from werkzeug.security import check_password_hash, generate_password_hash

from tripcash.db import get_db

bp = Blueprint('auth', __name__, url_prefix='/auth')


@bp.route('/register', methods=('GET', 'POST'))
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        password2 = request.form['password2']
        db = get_db()
        error = None

        if not username:
            error = _('Username is required.')
        elif not password:
            error = _('Password is required.')
        elif password != password2:
            error = _('Passwords do not match. Please try again.')

        if error is None:
            try:
                db.execute(
                    'INSERT INTO users (username, password) VALUES (%s, %s)',
                    (username, generate_password_hash(password)),
                )
                g.db.commit()
                # Default categories are stored in English and translated at display time.
                # To add more defaults, just append to this list.
                startlabels = ['Food', 'Transport', 'Tickets', 'Accommodation']
                db.execute('SELECT id FROM users WHERE username=%s', (username,))
                user = db.fetchone()
                for label in startlabels:
                    db.execute(
                        'INSERT INTO labels (label_name, user_id) VALUES (%s, %s)',
                        (label, user[0]),
                    )
                g.db.commit()
                session.clear()
                session['user_id'] = user['id']
                return redirect(url_for('index'))

            except Exception as err:
                error = f'User {username} is already registered.'

        flash(error)
        return render_template('auth/register.html')

    logout()
    return render_template('auth/register.html')


@bp.route('/login', methods=('GET', 'POST'))
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db = get_db()
        error = None
        db.execute('SELECT * FROM users WHERE username = %s', (username,))
        user = db.fetchone()

        if user is None:
            error = _('Incorrect username.')
        elif not check_password_hash(user['password'], password):
            error = _('Incorrect password.')

        if error is None:
            session.clear()
            session['user_id'] = user['id']
            return redirect(url_for('index'))

        flash(error)

    if session.get('user_id') != None:
        return redirect(url_for('index'))

    return render_template('auth/login.html')


@bp.before_app_request
def load_logged_in_user():
    user_id = session.get('user_id')

    if user_id is None:
        g.user = None
    else:
        db = get_db()
        db.execute('SELECT * FROM users WHERE id = %s', (user_id,))
        g.user = db.fetchone()


@bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))


# Decorator to protect routes that require authentication.
def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for('auth.login'))

        return view(**kwargs)

    return wrapped_view


@bp.route('/changepass', methods=('GET', 'POST'))
def changepass():
    if request.method == 'POST':
        current_password = request.form['current_password']
        new_password = request.form['new_password']
        new_password2 = request.form['new_password2']
        db = get_db()
        error = None

        db.execute('SELECT * FROM users WHERE id = %s', (g.user['id'],))
        user = db.fetchone()

        if not current_password or not new_password or not new_password2:
            error = _('All fields are required.')
        elif not check_password_hash(user['password'], current_password):
            error = _('Incorrect current password.')
        elif new_password != new_password2:
            error = _('Passwords do not match. Please try again.')
        elif current_password == new_password:
            error = _('New password and current password are the same.')

        if error is None:
            db.execute(
                'UPDATE users SET password=%s WHERE id=%s',
                (generate_password_hash(new_password), g.user['id']),
            )
            g.db.commit()
            return redirect(url_for('index'))
        flash(error)
        return render_template('auth/changepass.html')
    return render_template('auth/changepass.html')
