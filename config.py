import os

class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-change-in-production")
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL", "sqlite:///card_portfolio.db")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    TCG_API_KEY = os.getenv("TCG_API_KEY", "")
    TCG_BASE_URL = "https://api.tcgapi.dev/v1"
