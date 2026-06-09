from datetime import datetime
import bcrypt
from flask_login import UserMixin
from app import db, login_manager


class User(UserMixin, db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.Text, unique=True, nullable=False)
    password_hash = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    collection = db.relationship("CollectionItem", backref="user", lazy=True)
    transactions = db.relationship("Transaction", backref="user", lazy=True)
    portfolio_snapshots = db.relationship("PortfolioSnapshot", backref="user", lazy=True)

    def set_password(self, password: str):
        self.password_hash = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

    def check_password(self, password: str) -> bool:
        return bcrypt.checkpw(password.encode(), self.password_hash.encode())


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))
