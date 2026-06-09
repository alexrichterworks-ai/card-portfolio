from apscheduler.schedulers.background import BackgroundScheduler
from app.services.price_fetcher import run_daily_job


def start_scheduler(app):
    scheduler = BackgroundScheduler()

    def job():
        with app.app_context():
            run_daily_job()

    scheduler.add_job(job, "cron", hour=0, minute=0)
    scheduler.start()
    return scheduler
