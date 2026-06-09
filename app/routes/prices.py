from datetime import datetime, timedelta
from flask import Blueprint, jsonify
from flask_login import login_required
from app.models.price_history import PriceHistory

prices_bp = Blueprint("prices", __name__)


@prices_bp.route("/prices/<card_id>/history")
@login_required
def card_history(card_id):
    since = datetime.utcnow() - timedelta(days=30)
    entries = (
        PriceHistory.query
        .filter(PriceHistory.card_id == card_id, PriceHistory.fetched_at >= since)
        .order_by(PriceHistory.fetched_at)
        .all()
    )
    return jsonify([
        {"date": e.fetched_at.strftime("%Y-%m-%d"), "price": e.price}
        for e in entries
    ])
