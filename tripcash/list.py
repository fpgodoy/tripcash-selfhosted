from flask import Blueprint, flash, g, redirect, render_template, request, url_for
from flask_babel import _
from werkzeug.exceptions import abort

from tripcash.auth import login_required
from tripcash.db import get_db

bp = Blueprint('list', __name__)


# List all the registered expenses
@bp.route('/list')
@login_required
def list():
    # Access DB data
    db = get_db()
    db.execute(
        '''SELECT users.current_trip AS trip_id, trip.trip_name AS trip_name, trip.user_id AS trip_owner_id
           FROM users INNER JOIN trip on trip.trip_id=users.current_trip WHERE users.id=%s''',
        (g.user['id'],),
    )
    g.trip = db.fetchone()

    # Redireciona se não há viagem ativa
    if not g.trip:
        return redirect(url_for('trip.trip'))

    # Verifica se o usuário é dono da viagem ou apenas participante
    is_owner = (g.trip['trip_owner_id'] == g.user['id'])

    user_participant_id = None
    if g.trip['trip_id']:
        db.execute('SELECT is_group_trip FROM trip WHERE trip_id = %s', (g.trip['trip_id'],))
        if db.fetchone()['is_group_trip']:
            db.execute(  # noqa: E501
                'SELECT id FROM trip_participant WHERE trip_id = %s AND is_user = TRUE AND name = %s',
                (g.trip['trip_id'], g.user['username'])
            )
            user_part = db.fetchone()
            if user_part:
                user_participant_id = user_part[0]

    # Participantes não-donos só visualizam despesas com "Dividir" ativo (is_split = TRUE)
    # Donos da viagem visualizam todas as despesas, incluindo as individuais
    split_filter = '' if is_owner else 'AND post.is_split = TRUE'

    # Get the list of expenses from the current user and trip
    db.execute(
        f'''SELECT post.id, post.post_date AS date,
           CASE
               WHEN trip.is_group_trip = FALSE THEN post.amount
               WHEN post.is_split = TRUE THEN COALESCE(es.amount_owed, 0)
               WHEN post.payer_participant_id = %s THEN post.amount
               ELSE 0
           END AS amount,
           post.title, labels.label_name AS label
           FROM post
           INNER JOIN labels ON post.label=labels.label_id
           INNER JOIN trip ON post.trip = trip.trip_id
           LEFT JOIN expense_split es ON es.expense_id = post.id AND es.participant_id = %s
           WHERE post.trip = %s {split_filter} ORDER BY date''',
        (user_participant_id, user_participant_id, g.trip['trip_id']),
    )
    expenses = db.fetchall()
    # Translate the label names for system default categories
    expenses = [dict(row) | {'label': _(row['label'])} for row in expenses]

    return render_template('list.html', list=expenses)


# List the sum of expenses by label
@bp.route('/total', methods=('GET', 'POST'))
@login_required
def total():
    # Access DB data
    db = get_db()

    # Get the current trip
    db.execute(
        '''SELECT users.current_trip AS trip_id, trip.trip_name AS trip_name, trip.user_id AS trip_owner_id
           FROM users INNER JOIN trip on trip.trip_id=users.current_trip WHERE users.id=%s''',
        (g.user['id'],),
    )
    g.trip = db.fetchone()

    # Redireciona se não há viagem ativa
    if not g.trip:
        return redirect(url_for('trip.trip'))

    # Verifica se o usuário é dono da viagem ou apenas participante
    is_owner = (g.trip['trip_owner_id'] == g.user['id'])

    # Participantes não-donos só visualizam totais de despesas com "Dividir" ativo
    split_filter = '' if is_owner else 'AND post.is_split = TRUE'

    # Get the dates with registered expenses
    db.execute(
        f'SELECT DISTINCT post_date FROM post WHERE trip = %s {split_filter} ORDER BY post_date',
        (g.trip['trip_id'],),
    )
    dates = db.fetchall()

    user_participant_id = None
    if g.trip['trip_id']:
        db.execute('SELECT is_group_trip FROM trip WHERE trip_id = %s', (g.trip['trip_id'],))
        if db.fetchone()['is_group_trip']:
            db.execute(  # noqa: E501
                'SELECT id FROM trip_participant WHERE trip_id = %s AND is_user = TRUE AND name = %s',
                (g.trip['trip_id'], g.user['username'])
            )
            user_part = db.fetchone()
            if user_part:
                user_participant_id = user_part[0]

    if request.method == 'POST':
        # Get the selected date to filter data
        date = request.form['date']
        error = None

        checkdates = [str(row[0]) for row in dates]

        # Get the unfiltered data showing all the totals
        if date == 'all':
            db.execute(
                f'''SELECT SUM(
                   CASE
                       WHEN trip.is_group_trip = FALSE THEN post.amount
                       WHEN post.is_split = TRUE THEN COALESCE(es.amount_owed, 0)
                       WHEN post.payer_participant_id = %s THEN post.amount
                       ELSE 0
                   END
                   ) AS amount, labels.label_name AS label
                   FROM post
                   INNER JOIN labels ON post.label=labels.label_id
                   INNER JOIN trip ON post.trip = trip.trip_id
                   LEFT JOIN expense_split es ON es.expense_id = post.id AND es.participant_id = %s
                   WHERE post.trip = %s {split_filter} GROUP BY labels.label_name''',
                (user_participant_id, user_participant_id, g.trip['trip_id']),
            )
            totals = db.fetchall()
            totals = [dict(row) | {'label': _(row['label'])} for row in totals]
            return render_template('total.html', totals=totals, dates_list=dates, date='Trip')

        # Check the submitted value
        if not date or (str(date) not in checkdates):
            error = 'Invalid date.'

        if error is None:
            # Get the filtered data from DB
            db.execute(
                f'''SELECT SUM(
                   CASE
                       WHEN trip.is_group_trip = FALSE THEN post.amount
                       WHEN post.is_split = TRUE THEN COALESCE(es.amount_owed, 0)
                       WHEN post.payer_participant_id = %s THEN post.amount
                       ELSE 0
                   END
                   ) AS amount, labels.label_name AS label
                   FROM post
                   INNER JOIN labels ON post.label=labels.label_id
                   INNER JOIN trip ON post.trip = trip.trip_id
                   LEFT JOIN expense_split es ON es.expense_id = post.id AND es.participant_id = %s
                   WHERE post.trip = %s AND post.post_date = %s {split_filter} GROUP BY labels.label_name''',
                (user_participant_id, user_participant_id, g.trip['trip_id'], date),
            )
            totals = db.fetchall()
            totals = [dict(row) | {'label': _(row['label'])} for row in totals]

            return render_template('total.html', totals=totals, dates_list=dates, date=date)

        else:
            flash(error)

    # Get the unfiltered data showing all the totals
    db.execute(
        f'''SELECT SUM(
           CASE
               WHEN trip.is_group_trip = FALSE THEN post.amount
               WHEN post.is_split = TRUE THEN COALESCE(es.amount_owed, 0)
               WHEN post.payer_participant_id = %s THEN post.amount
               ELSE 0
           END
           ) AS amount, labels.label_name AS label
           FROM post
           INNER JOIN labels ON post.label=labels.label_id
           INNER JOIN trip ON post.trip = trip.trip_id
           LEFT JOIN expense_split es ON es.expense_id = post.id AND es.participant_id = %s
           WHERE post.trip = %s {split_filter} GROUP BY labels.label_name''',
        (user_participant_id, user_participant_id, g.trip['trip_id']),
    )
    totals = db.fetchall()
    totals = [dict(row) | {'label': _(row['label'])} for row in totals]

    return render_template('total.html', totals=totals, dates_list=dates, date='Trip')


# Get the clicked button expense ID to edit
def get_expense(id):
    db = get_db()
    db.execute('SELECT * FROM post WHERE id = %s', (id,))
    expense = db.fetchone()

    if expense is None:
        abort(404, "Register doesn't exist.")

    # Permite edição para o autor original OU para qualquer participante da viagem
    if expense['author_id'] != g.user['id']:
        db.execute(
            'SELECT id FROM trip_participant WHERE trip_id = %s AND name = %s AND is_user = TRUE',
            (expense['trip'], g.user['username'])
        )
        if not db.fetchone():
            abort(403)

    return expense


# Form to edit the expenses
@bp.route('/<int:id>/edit', methods=('GET', 'POST'))
@login_required
def edit(id):
    expense = get_expense(id)

    # Access DB data
    db = get_db()
    db.execute(
        'SELECT trip.* FROM users INNER JOIN trip on trip.trip_id=users.current_trip WHERE users.id=%s',
        (g.user['id'],),
    )
    g.trip = db.fetchone()

    participants = []
    checkparticipant = []
    splits_dict = {}
    if g.trip and g.trip['is_group_trip']:
        db.execute('SELECT * FROM trip_participant WHERE trip_id = %s ORDER BY id', (g.trip['trip_id'],))
        participants = db.fetchall()
        for row in participants:
            checkparticipant.append(row['id'])

        if expense['is_split']:
            db.execute('SELECT participant_id, amount_owed FROM expense_split WHERE expense_id = %s', (id,))
            for spl in db.fetchall():
                splits_dict[spl['participant_id']] = spl['amount_owed']

    # Categorias: apenas globais em viagens em grupo, globais + próprias em individuais
    if g.trip and g.trip['is_group_trip']:
        db.execute('SELECT label_id, label_name FROM labels WHERE user_id IS NULL ORDER BY label_name')
    else:
        db.execute(
            'SELECT label_id, label_name FROM labels WHERE user_id = %s OR user_id IS NULL ORDER BY user_id NULLS FIRST, label_name',  # noqa: E501
            (g.user['id'],),
        )
    label_list = db.fetchall()

    # Get the trip list.
    db.execute(
        '''SELECT t.trip_id, t.trip_name, t.is_group_trip FROM trip t
           WHERE t.user_id = %s
           UNION
           SELECT t.trip_id, t.trip_name, t.is_group_trip FROM trip t
           INNER JOIN trip_participant tp ON t.trip_id = tp.trip_id
           WHERE tp.name=%s AND tp.is_user=TRUE''',
        (g.user['id'], g.user['username']),
    )
    trip_list = db.fetchall()

    checklabel = [row[0] for row in label_list]
    checktrip = [row[0] for row in trip_list]

    if request.method == 'POST':

        trip = int(request.form['trip'])
        date = request.form['date']
        amount = request.form['amount']
        title = request.form['title']
        label = int(request.form['label'])
        error = None

        is_split = request.form.get('is_split') == 'on'

        # Payer tracking (optional for non-group trips)
        payer_participant_id = None
        if g.trip['is_group_trip']:
            # Payer MUST be selected
            payer_participant_id = request.form.get('payer_participant_id')
            if not payer_participant_id or int(payer_participant_id) not in checkparticipant:
                error = 'Invalid payer participant.'
            else:
                payer_participant_id = int(payer_participant_id)

        if not trip or not date or not amount or not title or not label:
            error = 'All the fields should be filled.'
        else:
            try:
                base_amount = float(amount)
            except ValueError:
                error = 'Invalid amount format.'
                base_amount = 0.0

        if label not in checklabel:
            error = 'Invalid label.'

        if trip not in checktrip:
            error = 'Invalid trip.'

        if error is None and is_split and g.trip['is_group_trip']:
            total_fractions = 0.0
            for p_id in checkparticipant:
                fraction_amount = request.form.get(f'split_amount_{p_id}')
                if fraction_amount:
                    try:
                        total_fractions += float(fraction_amount)
                    except ValueError:
                        pass

            # Allow minor floating point drift
            if abs(round(total_fractions, 2) - round(base_amount, 2)) >= 0.01:
                error = _('The sum of split fractions must perfectly match the total expense amount.')

        if error is None:
            # Update the expense on DB
            db.execute(
                'UPDATE post SET trip = %s, post_date = %s, amount = %s, title = %s, label = %s, is_split = %s, payer_participant_id = %s WHERE id = %s',  # noqa: E501
                (trip, date, amount, title, label, is_split, payer_participant_id, id),
            )

            # Manage splits: Delete all existing and re-insert
            db.execute('DELETE FROM expense_split WHERE expense_id = %s', (id,))

            if is_split and g.trip['is_group_trip']:
                for p_id in checkparticipant:
                    fraction_amount = request.form.get(f'split_amount_{p_id}')
                    if fraction_amount:
                        try:
                            fraction_val = float(fraction_amount)
                            db.execute(
                                'INSERT INTO expense_split (expense_id, participant_id, amount_owed) VALUES (%s, %s, %s)',  # noqa: E501
                                (id, p_id, fraction_val)
                            )
                        except ValueError:
                            pass

            g.db.commit()
            return redirect(url_for('list.list'))

        flash(error)

    # Translate label names for system default categories before passing to template
    display_label_list = [(row[0], _(row[1])) for row in label_list]

    return render_template(
        'edit.html',
        label_list=display_label_list,
        trip_list=trip_list,
        expense=expense,
        participants=participants,
        splits_dict=splits_dict
    )


# Delete an expense
@bp.route('/<int:id>/delete', methods=('POST',))
@login_required
def delete(id):
    get_expense(id)
    db = get_db()
    db.execute('DELETE FROM post WHERE id = %s', (id,))
    g.db.commit()
    return redirect(url_for('list.list'))
