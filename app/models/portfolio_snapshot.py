from datetime import date
from app import db


class PortfolioSnapshot(db.Model):
    __tablename__ = "portfolio_snapshots"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    total_value = db.Column(db.Float, nullable=False)
    snapshot_date = db.Column(db.Date, default=date.today, nullable=False)
