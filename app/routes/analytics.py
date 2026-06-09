from flask import Blueprint, render_template, jsonify
from flask_login import login_required, current_user
from app.services.analyzer import analyze_transactions, portfolio_trend, trade_advice

analytics_bp = Blueprint("analytics", __name__)


@analytics_bp.route("/analytics")
@login_required
def view():
    analysis = analyze_transactions(current_user.id)
    trend = portfolio_trend(current_user.id)
    advice = trade_advice(current_user.id)
    return render_template("analytics.html", analysis=analysis, trend=trend, advice=advice)


@analytics_bp.route("/analytics/portfolio.json")
@login_required
def portfolio_json():
    return jsonify(portfolio_trend(current_user.id))
