from flask import Blueprint, render_template, jsonify
from flask_login import login_required, current_user
from app.models.collection import CollectionItem
from app.services.analyzer import analyze_transactions, portfolio_trend, trade_advice

analytics_bp = Blueprint("analytics", __name__)


def _live_collection_value(user_id: int) -> float:
    """Sum quantity × latest recorded price for every card in the user's collection."""
    items = CollectionItem.query.filter_by(user_id=user_id).all()
    total = 0.0
    for item in items:
        latest = item.card.price_history[-1].price if item.card.price_history else 0
        total += item.quantity * latest
    return round(total, 2)


@analytics_bp.route("/analytics")
@login_required
def view():
    analysis = analyze_transactions(current_user.id)
    trend = portfolio_trend(current_user.id)
    advice = trade_advice(current_user.id)
    current_value = _live_collection_value(current_user.id)
    return render_template("analytics.html", analysis=analysis, trend=trend,
                           advice=advice, current_value=current_value)


@analytics_bp.route("/analytics/portfolio.json")
@login_required
def portfolio_json():
    return jsonify(portfolio_trend(current_user.id))
