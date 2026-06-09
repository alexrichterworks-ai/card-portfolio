from datetime import datetime, date
from app import db
from app.models.card import Card
from app.models.collection import CollectionItem
from app.models.price_history import PriceHistory
from app.models.portfolio_snapshot import PortfolioSnapshot
from app.models.user import User
from app.services.tcg_api import get_card_price


def fetch_all_prices() -> dict:
    """Fetch current prices for every card held in any user's collection.
    Returns a card_id → price map for use in portfolio snapshotting."""
    card_ids = [row[0] for row in db.session.query(CollectionItem.card_id).distinct()]
    price_map = {}

    for card_id in card_ids:
        price = get_card_price(card_id)
        if price is None:
            continue
        price_map[card_id] = price
        db.session.add(PriceHistory(card_id=card_id, price=price))
        card = Card.query.get(card_id)
        if card:
            card.last_fetched_at = datetime.utcnow()

    db.session.commit()
    return price_map


def snapshot_portfolios(price_map: dict):
    """Record each user's total collection value for today."""
    today = date.today()

    for user in User.query.all():
        if PortfolioSnapshot.query.filter_by(user_id=user.id, snapshot_date=today).first():
            continue
        total = sum(
            item.quantity * price_map.get(item.card_id, 0)
            for item in user.collection
        )
        db.session.add(PortfolioSnapshot(user_id=user.id, total_value=total))

    db.session.commit()


def run_daily_job():
    price_map = fetch_all_prices()
    snapshot_portfolios(price_map)
