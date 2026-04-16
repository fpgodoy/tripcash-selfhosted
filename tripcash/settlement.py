from datetime import datetime
from flask import Blueprint, flash, g, redirect, render_template, request, url_for
from werkzeug.exceptions import abort
from flask_babel import _
from tripcash.auth import login_required
from tripcash.db import get_db

bp = Blueprint('settlement', __name__)


@bp.route('/settlement', methods=('GET', 'POST'))
@login_required
def show():
    db = get_db()

    # Get current trip
    db.execute(
        'SELECT * FROM users INNER JOIN trip on trip.trip_id=users.current_trip WHERE users.id=%s',
        (g.user['id'],)
    )
    g.trip = db.fetchone()

    if not g.trip:
        return redirect(url_for('trip.trip'))

    if not g.trip['is_group_trip']:
        flash("This is not a group trip. You cannot manage settlements.")
        return redirect(url_for('list.list'))

    db.execute('SELECT * FROM trip_participant WHERE trip_id = %s ORDER BY id', (g.trip['trip_id'],))
    participants = db.fetchall()

    if not participants:
        return render_template('settlement.html', balances=[], participants=[])

    # Calculate balances
    balances = {p['id']: {'id': p['id'], 'name': p['name'], 'net': 0.0, 'is_user': p['is_user']} for p in participants}

    # 1. Process Expenses
    db.execute('SELECT id, amount, is_split, payer_participant_id FROM post WHERE trip = %s', (g.trip['trip_id'],))
    expenses = db.fetchall()

    # Busca todos os splits da viagem em uma única query (elimina N+1)
    db.execute(
        '''SELECT es.expense_id, es.participant_id, es.amount_owed
        FROM expense_split es
        JOIN post p ON es.expense_id = p.id
        WHERE p.trip = %s''',
        (g.trip['trip_id'],)
    )
    all_splits = db.fetchall()
    splits_by_expense = {}
    for s in all_splits:
        splits_by_expense.setdefault(s['expense_id'], []).append(s)

    for exp in expenses:
        if exp['payer_participant_id'] in balances:
            # Credit the payer for fronting the money
            balances[exp['payer_participant_id']]['net'] += float(exp['amount'])

        if exp['is_split']:
            # Subtract fraction owed from debtors (usando dados já buscados)
            splits = splits_by_expense.get(exp['id'], [])
            for split in splits:
                if split['participant_id'] in balances:
                    balances[split['participant_id']]['net'] -= float(split['amount_owed'])
        else:
            # Not split, they consumed it fully themselves
            if exp['payer_participant_id'] in balances:
                balances[exp['payer_participant_id']]['net'] -= float(exp['amount'])

    # 2. Process Manual Settlements (Acertos)
    db.execute(
        'SELECT payer_participant_id, receiver_participant_id, amount FROM participant_payment WHERE trip_id = %s',
        (g.trip['trip_id'],)
    )
    payments = db.fetchall()

    for pay in payments:
        if pay['payer_participant_id'] in balances:
            balances[pay['payer_participant_id']]['net'] += float(pay['amount'])
        if pay['receiver_participant_id'] in balances:
            balances[pay['receiver_participant_id']]['net'] -= float(pay['amount'])

    # Convert to list for template
    balance_list = list(balances.values())

    return render_template('settlement.html', balances=balance_list, participants=participants)


@bp.route('/settlement/new', methods=('GET', 'POST'))
@login_required
def create():
    db = get_db()
    db.execute(
        'SELECT * FROM users INNER JOIN trip on trip.trip_id=users.current_trip WHERE users.id=%s',
        (g.user['id'],)
    )
    g.trip = db.fetchone()

    if not g.trip or not g.trip['is_group_trip']:
        return redirect(url_for('list.list'))

    if request.method == 'POST':
        payer = request.form.get('payer_id')
        receiver = request.form.get('receiver_id')
        amount = request.form.get('amount')
        date = request.form.get('date')

        if not payer or not receiver or not amount or not date:
            flash("All fields are required")
        elif payer == receiver:
            flash("Payer and receiver cannot be the same person")
        else:
            try:
                amt = float(amount)
                if amt <= 0:
                    raise ValueError
                db.execute(
                    'INSERT INTO participant_payment (trip_id, payer_participant_id, receiver_participant_id, amount, payment_date) VALUES (%s, %s, %s, %s, %s)',  # noqa: E501
                    (g.trip['trip_id'], payer, receiver, amt, date)
                )
                g.db.commit()
                return redirect(url_for('settlement.show'))
            except ValueError:
                flash("Invalid amount.")

    db.execute('SELECT * FROM trip_participant WHERE trip_id = %s ORDER BY id', (g.trip['trip_id'],))
    participants = db.fetchall()
    return render_template(
        'create_settlement.html', participants=participants, today=datetime.today().strftime('%Y-%m-%d')
    )


@bp.route('/settlement/<int:participant_id>', methods=['GET'])
@login_required
def detail(participant_id):
    db = get_db()

    # Get current trip
    db.execute(
        'SELECT * FROM users INNER JOIN trip on trip.trip_id=users.current_trip WHERE users.id=%s',
        (g.user['id'],)
    )
    g.trip = db.fetchone()

    if not g.trip or not g.trip['is_group_trip']:
        return redirect(url_for('list.list'))

    db.execute('SELECT * FROM trip_participant WHERE id = %s AND trip_id = %s', (participant_id, g.trip['trip_id']))
    participant = db.fetchone()

    if not participant:
        abort(404)

    ledger = []

    # 1. Credits: Paid for group expenses
    db.execute(
        'SELECT post_date, title, amount FROM post WHERE payer_participant_id = %s AND is_split = TRUE AND trip = %s',
        (participant_id, g.trip['trip_id'])
    )
    for row in db.fetchall():
        ledger.append({
            'date': row['post_date'],
            'title': f"{_('Paid for')} '{row['title']}'",
            'amount': float(row['amount']),
            'type': 'credit',
            'raw_date': row['post_date']
        })

    # 2. Debits: Fractions owed
    db.execute(
        '''SELECT p.post_date, p.title, s.amount_owed
        FROM expense_split s
        JOIN post p ON s.expense_id = p.id
        WHERE s.participant_id = %s AND p.trip = %s''',
        (participant_id, g.trip['trip_id'])
    )
    for row in db.fetchall():
        ledger.append({
            'date': row['post_date'],
            'title': f"{_('Owes part of')} '{row['title']}'",
            'amount': float(row['amount_owed']),
            'type': 'debit',
            'raw_date': row['post_date']
        })

    # 3. Credits: Settlements paid to others
    db.execute(
        '''SELECT pay.payment_date, pay.amount, tp.name
        FROM participant_payment pay
        JOIN trip_participant tp ON pay.receiver_participant_id = tp.id
        WHERE pay.payer_participant_id = %s AND pay.trip_id = %s''',
        (participant_id, g.trip['trip_id'])
    )
    for row in db.fetchall():
        ledger.append({
            'date': row['payment_date'],
            'title': f"{_('Payment to')} {row['name']}",
            'amount': float(row['amount']),
            'type': 'credit',
            'raw_date': row['payment_date']
        })

    # 4. Debits: Settlements received from others
    db.execute(
        '''SELECT pay.payment_date, pay.amount, tp.name
        FROM participant_payment pay
        JOIN trip_participant tp ON pay.payer_participant_id = tp.id
        WHERE pay.receiver_participant_id = %s AND pay.trip_id = %s''',
        (participant_id, g.trip['trip_id'])
    )
    for row in db.fetchall():
        ledger.append({
            'date': row['payment_date'],
            'title': f"{_('Payment from')} {row['name']}",
            'amount': float(row['amount']),
            'type': 'debit',
            'raw_date': row['payment_date']
        })

    # Sort chronologically
    ledger.sort(key=lambda x: x['raw_date'], reverse=True)

    net_balance = sum([item['amount'] if item['type'] == 'credit' else -item['amount'] for item in ledger])

    return render_template('settlement_detail.html', participant=participant, ledger=ledger, net_balance=net_balance)
