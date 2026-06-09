from datetime import datetime
from flask import Blueprint, render_template, request, redirect, url_for, jsonify, flash
from flask_login import login_required, current_user
from config import Config
from app import db
from app.models.card import Card
from app.models.collection import CollectionItem
from app.models.price_history import PriceHistory
from app.services.tcg_api import search_card, get_card_price

collection_bp = Blueprint("collection", __name__)


@collection_bp.route("/")
@collection_bp.route("/collection")
@login_required
def view():
    items = CollectionItem.query.filter_by(user_id=current_user.id).all()
    collection = []
    for item in items:
        latest = item.card.price_history[-1].price if item.card.price_history else None
        purchase = item.purchase_price or 0
        collection.append({
            "item": item,
            "current_price": latest,
            "current_value": (latest or 0) * item.quantity,
            "gain_loss": ((latest or 0) - purchase) * item.quantity,
        })
    total_value = sum(r["current_value"] for r in collection)
    return render_template("collection.html", collection=collection, total_value=total_value)


@collection_bp.route("/collection/search")
@login_required
def search():
    if not Config.TCG_API_KEY or Config.TCG_API_KEY in ("", "YOUR_API_KEY_HERE"):
        return jsonify({"error": "TCG_API_KEY is not set. Get a free key at tcgapi.dev"}), 503
    name = request.args.get("name", "").strip()
    game = request.args.get("game", "pokemon")
    if not name:
        return jsonify([])
    results = search_card(name, game)
    if results is None:
        return jsonify({"error": "API request failed. Check your TCG_API_KEY."}), 502
    return jsonify(results)


@collection_bp.route("/collection/add", methods=["POST"])
@login_required
def add():
    card_id = request.form["card_id"]
    name = request.form["name"]
    set_name = request.form.get("set_name", "")
    game = request.form.get("game", "pokemon")
    quantity = max(1, int(request.form.get("quantity", 1)))
    condition = request.form.get("condition", "NM")
    purchase_price = float(request.form.get("purchase_price") or 0)

    if not Card.query.get(card_id):
        db.session.add(Card(id=card_id, name=name, set_name=set_name, game=game))

    existing = CollectionItem.query.filter_by(
        user_id=current_user.id, card_id=card_id
    ).first()
    if existing:
        existing.quantity += quantity
    else:
        db.session.add(CollectionItem(
            user_id=current_user.id,
            card_id=card_id,
            quantity=quantity,
            condition=condition,
            purchase_price=purchase_price,
        ))

    db.session.commit()

    # Fetch price immediately so value shows straight away (don't wait for midnight job)
    if not PriceHistory.query.filter_by(card_id=card_id).first():
        price = get_card_price(card_id)
        if price:
            db.session.add(PriceHistory(card_id=card_id, price=price))
            card = Card.query.get(card_id)
            if card:
                card.last_fetched_at = datetime.utcnow()
            db.session.commit()

    flash(f"Added {name} to your collection.", "success")
    return redirect(url_for("collection.view"))


@collection_bp.route("/collection/remove/<int:item_id>", methods=["POST"])
@login_required
def remove(item_id):
    item = CollectionItem.query.get_or_404(item_id)
    if item.user_id != current_user.id:
        return "Forbidden", 403
    db.session.delete(item)
    db.session.commit()
    return redirect(url_for("collection.view"))
