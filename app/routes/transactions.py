from datetime import datetime
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from app import db
from app.models.collection import CollectionItem
from app.models.transaction import Transaction

transactions_bp = Blueprint("transactions", __name__)


@transactions_bp.route("/transactions")
@login_required
def view():
    txs = (
        Transaction.query
        .filter_by(user_id=current_user.id)
        .order_by(Transaction.date.desc())
        .all()
    )
    collection = CollectionItem.query.filter_by(user_id=current_user.id).all()
    return render_template("transactions.html", transactions=txs, collection=collection)


@transactions_bp.route("/transactions/log", methods=["POST"])
@login_required
def log():
    tx_type = request.form["type"]
    card_id = request.form["card_id"]
    quantity = max(1, int(request.form.get("quantity", 1)))
    price = float(request.form.get("price") or 0)
    trade_card_id = request.form.get("trade_card_id") or None
    date_str = request.form.get("date", "").strip()
    date = datetime.strptime(date_str, "%Y-%m-%d") if date_str else datetime.utcnow()
    notes = request.form.get("notes", "")

    db.session.add(Transaction(
        user_id=current_user.id,
        card_id=card_id,
        type=tx_type,
        quantity=quantity,
        price=price,
        trade_card_id=trade_card_id,
        date=date,
        notes=notes,
    ))

    if tx_type in ("sold", "traded_away"):
        item = CollectionItem.query.filter_by(
            user_id=current_user.id, card_id=card_id
        ).first()
        if item:
            item.quantity = max(0, item.quantity - quantity)

    db.session.commit()
    flash("Transaction logged.", "success")
    return redirect(url_for("transactions.view"))
