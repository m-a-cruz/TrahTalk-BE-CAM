from apscheduler.schedulers.background import BackgroundScheduler
import atexit
import app.model.predict as predict

def safe_train_prophet():
    try:
        predict.train_prophet()
    except Exception as e:
        print(f"Error in train_prophet: {e}")


def start_scheduler():
    scheduler = BackgroundScheduler()
    scheduler.add_job(
        func=safe_train_prophet,
        trigger='interval',
        hours=1,
        id='prophet_training'
    )
    scheduler.start()

    atexit.register(lambda: scheduler.shutdown())
