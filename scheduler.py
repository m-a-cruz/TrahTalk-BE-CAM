import logging
from apscheduler.schedulers.background import BackgroundScheduler
import atexit
import app.model.predict as predict

# Set up logging
logging.basicConfig(filename='prophet_training.log', level=logging.INFO, 
                    format='%(asctime)s - %(levelname)s - %(message)s')

def safe_train_prophet():
    try:
        logging.info("Starting Prophet model training...")
        predict.train_prophet()
        logging.info("Prophet model training completed successfully.")
    except Exception as e:
        logging.error(f"Error in train_prophet: {e}", exc_info=True)

def start_scheduler():
    scheduler = BackgroundScheduler()

    # Schedule job to run every 3 hours
    scheduler.add_job(
        func=safe_train_prophet,
        trigger='interval',
        hours=1,
        id='prophet_training'
    )
    
    # Start the scheduler
    scheduler.start()
    logging.info("Scheduler started. Prophet training will run every 3 hours.")

    # Clean up on shutdown
    atexit.register(lambda: scheduler.shutdown())
    logging.info("Scheduler shutdown registered.")
