from datetime import datetime
from app import db


class PriceHistory(db.Model):
    __tablename__ = "price_history"

    id = db.Column(db.Integer, primary_key=True)
    card_id = db.Column(db.Text, db.ForeignKey("cards.id"), nullable=False)
    price = db.Column(db.Float, nullable=False)
    fetched_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
