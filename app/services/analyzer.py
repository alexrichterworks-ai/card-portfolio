from datetime import timedelta
from app.models.transaction import Transaction
from app.models.price_history import PriceHistory
from app.models.portfolio_snapshot import PortfolioSnapshot


def _price_nearest(card_id: str, after_date, days: int):
    """Return the first recorded price at least `days` after `after_date`."""
    target = after_date + timedelta(days=days)
    entry = (
        PriceHistory.query
        .filter(PriceHistory.card_id == card_id, PriceHistory.fetched_at >= target)
        .order_by(PriceHistory.fetched_at)
        .first()
    )
    return entry.price if entry else None


def _current_price(card_id: str):
    entry = (
        PriceHistory.query
        .filter_by(card_id=card_id)
        .order_by(PriceHistory.fetched_at.desc())
        .first()
    )
    return entry.price if entry else None


def analyze_transactions(user_id: int) -> dict:
    """Evaluate each sell/trade against price movement after the transaction.

    A transaction is successful if collection value increased — operationally:
    - sold: current price < sold price (card is cheaper now, good exit)
    - traded_away: card given up is worth less now than at trade date
    - traded_for: card received is worth more now than at trade date
    """
    transactions = (
        Transaction.query
        .filter_by(user_id=user_id)
        .order_by(Transaction.date.desc())
        .all()
    )

    insights = []
    totals = {"successful": 0, "unsuccessful": 0, "pending": 0}

    for tx in transactions:
        if tx.type not in ("sold", "traded_away", "traded_for"):
            continue

        tx_price = tx.price or 0
        now = _current_price(tx.card_id)
        future_30d = _price_nearest(tx.card_id, tx.date, days=30)

        if tx.type in ("sold", "traded_away"):
            outcome_now = "successful" if (now and now < tx_price) else ("unsuccessful" if now else "pending")
            outcome_30d = "successful" if (future_30d and future_30d < tx_price) else ("unsuccessful" if future_30d else "pending")
            pct_now = round(((tx_price - now) / tx_price) * 100, 1) if now else None
            pct_30d = round(((tx_price - future_30d) / tx_price) * 100, 1) if future_30d else None
        else:  # traded_for — card received should go up
            outcome_now = "successful" if (now and now > tx_price) else ("unsuccessful" if now else "pending")
            outcome_30d = "successful" if (future_30d and future_30d > tx_price) else ("unsuccessful" if future_30d else "pending")
            pct_now = round(((now - tx_price) / tx_price) * 100, 1) if now else None
            pct_30d = round(((future_30d - tx_price) / tx_price) * 100, 1) if future_30d else None

        final_outcome = outcome_30d if outcome_30d != "pending" else outcome_now
        totals[final_outcome] += 1

        insights.append({
            "card_name": tx.card.name if tx.card else tx.card_id,
            "type": tx.type,
            "tx_price": tx_price,
            "current_price": now,
            "price_30d_after": future_30d,
            "outcome_now": outcome_now,
            "outcome_30d": outcome_30d,
            "pct_change_now": pct_now,
            "pct_change_30d": pct_30d,
            "date": tx.date.strftime("%Y-%m-%d"),
        })

    win_rate = (
        round(totals["successful"] / (totals["successful"] + totals["unsuccessful"]) * 100)
        if (totals["successful"] + totals["unsuccessful"]) > 0 else None
    )

    return {
        "insights": insights,
        "totals": totals,
        "win_rate": win_rate,
    }


def portfolio_trend(user_id: int) -> list:
    snapshots = (
        PortfolioSnapshot.query
        .filter_by(user_id=user_id)
        .order_by(PortfolioSnapshot.snapshot_date)
        .all()
    )
    return [{"date": s.snapshot_date.isoformat(), "value": s.total_value} for s in snapshots]


def trade_advice(user_id: int) -> list:
    """Surface actionable recommendations based on transaction history."""
    result = analyze_transactions(user_id)
    advice = []

    unsuccessful = [i for i in result["insights"] if i["outcome_30d"] == "unsuccessful"]
    if unsuccessful:
        avg_loss = sum(abs(i["pct_change_30d"] or 0) for i in unsuccessful) / len(unsuccessful)
        advice.append({
            "type": "warning",
            "message": f"You left an average of {avg_loss:.1f}% on the table across "
                       f"{len(unsuccessful)} sell(s)/trade(s). Consider holding 30+ days before selling.",
        })

    successful = [i for i in result["insights"] if i["outcome_30d"] == "successful"]
    if successful:
        avg_gain = sum(i["pct_change_30d"] or 0 for i in successful) / len(successful)
        advice.append({
            "type": "success",
            "message": f"Your successful exits averaged {avg_gain:.1f}% gain in value — good timing pattern.",
        })

    if result["win_rate"] is not None and result["win_rate"] < 50:
        advice.append({
            "type": "warning",
            "message": f"Win rate is {result['win_rate']}%. Most cards you sold/traded went on to increase "
                       "in value. Consider tracking price trends for at least 30 days before transacting.",
        })

    return advice
