from datetime import datetime
from app import db

# type values: bought / sold / traded_away / traded_for
class Transaction(db.Model):
    __tablename__ = "transactions"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    card_id = db.Column(db.Text, db.ForeignKey("cards.id"), nullable=False)
    type = db.Column(db.Text, nullable=False)
    quantity = db.Column(db.Integer, default=1)
    price = db.Column(db.Float)
    trade_card_id = db.Column(db.Text, db.ForeignKey("cards.id"), nullable=True)
    date = db.Column(db.DateTime, default=datetime.utcnow)
    notes = db.Column(db.Text)

    card = db.relationship("Card", foreign_keys=[card_id])
    trade_card = db.relationship("Card", foreign_keys=[trade_card_id])
