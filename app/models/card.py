from app import db


class Card(db.Model):
    __tablename__ = "cards"

    id = db.Column(db.Text, primary_key=True)  # TCGApi card ID
    name = db.Column(db.Text, nullable=False)
    set_name = db.Column(db.Text)
    game = db.Column(db.Text)
    last_fetched_at = db.Column(db.DateTime)

    price_history = db.relationship("PriceHistory", backref="card", lazy=True,
                                    order_by="PriceHistory.fetched_at")
    collection_items = db.relationship("CollectionItem", backref="card", lazy=True)
