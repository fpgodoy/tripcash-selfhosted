from datetime import datetime

from flask import Blueprint, flash, g, redirect, render_template, request, url_for
from flask_babel import _

from tripcash.auth import login_required
from tripcash.db import get_db

bp = Blueprint('expense', __name__)


@bp.route('/expense', methods=('GET', 'POST'))
@login_required
def expense():
    # Access DB data.
    db = get_db()
    # Get the current trip.
    db.execute(
        'SELECT trip.* FROM users INNER JOIN trip on trip.trip_id=users.current_trip WHERE users.id=%s',
        (g.user['id'],),
    )
    g.trip = db.fetchone()

    participants = []
    checkparticipant = []
    if g.trip and g.trip['is_group_trip']:
        db.execute('SELECT * FROM trip_participant WHERE trip_id = %s ORDER BY id', (g.trip['trip_id'],))
        participants = db.fetchall()
        for row in participants:
            checkparticipant.append(row['id'])

    # Categorias: apenas globais em viagens em grupo, globais + próprias em individuais
    if g.trip and g.trip['is_group_trip']:
        db.execute('SELECT label_id, label_name FROM labels WHERE user_id IS NULL ORDER BY label_name')
    else:
        db.execute(
            'SELECT label_id, label_name FROM labels WHERE user_id = %s OR user_id IS NULL ORDER BY user_id NULLS FIRST, label_name',  # noqa: E501
            (g.user['id'],),
        )
    label_list = db.fetchall()

    checklabel = [row[0] for row in label_list]

    if request.method == 'POST':
        # Get the form data.
        author = g.user['id']
        trip = g.trip['trip_id']
        date = request.form['date']
        amount = request.form['amount']
        title = request.form['title']
        label = int(request.form['label'])
        error = None
        is_split = request.form.get('is_split') == 'on'

        # Payer id tracking (optional for non-group trips)
        payer_participant_id = None
        if g.trip['is_group_trip']:
            # Payer MUST be selected
            payer_participant_id = request.form.get('payer_participant_id')
            if not payer_participant_id or int(payer_participant_id) not in checkparticipant:
                error = 'Invalid payer participant.'
            else:
                payer_participant_id = int(payer_participant_id)

        # Validate the form data.
        if not date or not amount or not title or not label:
            error = 'All the fields should be filled.'
        else:
            try:
                base_amount = float(amount)
            except ValueError:
                error = 'Invalid amount format.'
                base_amount = 0.0

        if label not in checklabel:
            error = 'Invalid label.'

        if error is None and is_split and g.trip['is_group_trip']:
            total_fractions = 0.0
            for p_id in checkparticipant:
                fraction_amount = request.form.get(f'split_amount_{p_id}')
                if fraction_amount:
                    try:
                        total_fractions += float(fraction_amount)
                    except ValueError:
                        pass

            # Allow minor floating point drift (rounding)
            if abs(round(total_fractions, 2) - round(base_amount, 2)) >= 0.01:
                error = _('The sum of split fractions must perfectly match the total expense amount.')

        # Insert the expense on DB and show the expenses list
        if error is None:
            db.execute(
                'INSERT INTO post (author_id, trip, post_date, amount, title, label, is_split, payer_participant_id) VALUES (%s, %s, %s, %s, %s, %s, %s, %s) RETURNING id',  # noqa: E501
                (author, trip, date, amount, title, label, is_split, payer_participant_id),
            )
            new_expense_id = db.fetchone()['id']

            # If the expense is split, insert fractions for each participant
            if is_split and g.trip['is_group_trip']:
                for p_id in checkparticipant:
                    fraction_amount = request.form.get(f'split_amount_{p_id}')
                    if fraction_amount:
                        try:
                            # Use numeric value, fallback to 0 if invalid
                            fraction_val = float(fraction_amount)
                            db.execute(
                                'INSERT INTO expense_split (expense_id, participant_id, amount_owed) VALUES (%s, %s, %s)',  # noqa: E501
                                (new_expense_id, p_id, fraction_val)
                            )
                        except ValueError:
                            pass

            g.db.commit()
            return redirect(url_for('list.list'))

        flash(error)

    # Translate category names for display
    display_label_list = [(row[0], _(row[1])) for row in label_list]

    return render_template(
        'expense.html', label_list=display_label_list, today=datetime.today(), participants=participants
    )
