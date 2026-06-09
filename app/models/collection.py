from datetime import datetime
from app import db


class CollectionItem(db.Model):
    __tablename__ = "collection"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    card_id = db.Column(db.Text, db.ForeignKey("cards.id"), nullable=False)
    quantity = db.Column(db.Integer, default=1, nullable=False)
    condition = db.Column(db.Text, default="NM")
    purchase_price = db.Column(db.Float)
    purchase_date = db.Column(db.DateTime, default=datetime.utcnow)
    notes = db.Column(db.Text)
