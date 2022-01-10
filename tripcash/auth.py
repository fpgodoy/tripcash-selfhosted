import functools

from flask import (
    Blueprint, blueprints, flash, g, redirect, render_template, request, session, url_for
)
from werkzeug.security import check_password_hash, generate_password_hash

from tripcash.db import get_db

bp = Blueprint('auth', __name__, url_prefix='/auth')

@bp.route('/register', methods=('GET', 'POST'))
def register():
    if request.method == 'POST':
        # Get the form data
        username = request.form['username']
        password = request.form['password']
        password2 = request.form['password2']
        db = get_db()
        error = None
        
        # Validate the typed data
        if not username:
            error = 'Username is required.'
        elif not password:
            error = 'Password is required.'
        elif password != password2:
            error = 'The password and the confirmation do not match. Please, type them again.'

        # Create the user into the database
        if error is None:
            try:
                db.execute(
                    "INSERT INTO user (username, password) VALUES (?, ?)",
                    (username, generate_password_hash(password))
                )
                db.commit()
                startlabels = ['Food', 'Transport', 'Tickets', 'Accomodation']
                user = db.execute("SELECT id FROM user WHERE username=?", (username,)).fetchone()
                for label in startlabels:
                    db.execute("INSERT INTO labels (label_name, user) VALUES (?, ?)", (label, user[0]))
                db.commit()

                session.clear()
                session['user_id'] = user['id']
                return redirect(url_for('index'))

            except db.IntegrityError:
                error = f"User {username} is already registered."            

        flash(error)
        return render_template('auth/register.html')
    
    logout()
    return render_template('auth/register.html')

@bp.route('/login', methods=('GET', 'POST'))
def login():
    if request.method == 'POST':
        # Get the form and DB data
        username = request.form['username']
        password = request.form['password']
        db = get_db()
        error = None
        user = db.execute(
            'SELECT * FROM user WHERE username = ?', (username,)
        ).fetchone()

        # Check the username and password
        if user is None:
            error = 'Incorrect username.'
        elif not check_password_hash(user['password'], password):
            error = 'Incorrect password.'
        
        if error is None:
            session.clear()
            session['user_id'] = user['id']
            return redirect(url_for('index'))

        flash(error)

    # Check if there is an user logged in
    if session.get('user_id') != None:
        return redirect(url_for('index'))

    return render_template('auth/login.html')

@bp.before_app_request
def load_logged_in_user():
    # Feed the g.user data
    user_id = session.get('user_id')

    if user_id is None:
        g.user = None
    else:
        g.user = get_db().execute(
            'SELECT * FROM user WHERE id = ?', (user_id,)
        ).fetchone()

@bp.route('/logout')
def logout():
    # Clear the session and return to the index
    session.clear()
    return redirect(url_for('index'))

def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for('auth.login'))
        
        return view(**kwargs)
    
    return wrapped_view

# Change the password of the current user
@bp.route('/changepass', methods=('GET', 'POST'))
def changepass():
    if request.method == 'POST':
        # Get the form data
        current_password = request.form['current_password']
        new_password = request.form['new_password']
        new_password2 = request.form['new_password2']
        db = get_db()
        error = None
        
        # Get the user data from DB
        user = db.execute(
            'SELECT * FROM user WHERE id = ?', (g.user['id'],)
        ).fetchone()
        
        # Validate the typed data
        if not current_password or not new_password or not new_password2:
            error = 'Need to fill all the fields.'
        
        elif not check_password_hash(user['password'], current_password):
            error = 'Incorrect current password.'

        elif new_password != new_password2:
            error = 'The password and the confirmation do not match. Please, type them again.'

        elif current_password == new_password:
            error = 'New password and current password are the same.'
        
        if error is None:
            db.execute(
                'UPDATE user SET password=? WHERE id=?', (generate_password_hash(new_password), g.user['id'])
            )
            db.commit()
            return redirect(url_for('index'))
        flash(error)
        return render_template('auth/changepass.html')
    return render_template('auth/changepass.html')