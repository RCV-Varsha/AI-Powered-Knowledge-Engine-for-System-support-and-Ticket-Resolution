"""
Scheduler for automatic category performance monitoring
"""

import time
import schedule
import logging
from datetime import datetime
from notification_system import NotificationManager, load_config_from_env

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('notification_scheduler.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def run_monitoring_check():
    """Run the category performance monitoring check"""
    try:
        logger.info("Starting scheduled monitoring check...")
        
        config = load_config_from_env()
        manager = NotificationManager(config)
        
        results = manager.check_and_notify()
        
        logger.info(f"Monitoring check completed: {results['status']}")
        
        if 'categories' in results:
            for cat_result in results['categories']:
                logger.info(f"Processed category: {cat_result['category']}")
                for notif_type, success in cat_result['notifications'].items():
                    logger.info(f"  {notif_type}: {'Success' if success else 'Failed'}")
        
        return results
        
    except Exception as e:
        logger.error(f"Error in monitoring check: {e}")
        return {"status": "error", "error": str(e)}

def setup_scheduler():
    """Setup the monitoring schedule"""
    logger.info("Setting up notification scheduler...")
    
    # Run every 2 hours
    schedule.every(2).hours.do(run_monitoring_check)
    
    # Also run every day at 9 AM for daily summary
    schedule.every().day.at("09:00").do(run_monitoring_check)
    
    logger.info("Scheduler setup complete. Monitoring will run every 2 hours and daily at 9 AM.")

def main():
    """Main scheduler loop"""
    setup_scheduler()
    
    logger.info("Starting notification scheduler...")
    logger.info("Press Ctrl+C to stop")
    
    try:
        while True:
            schedule.run_pending()
            time.sleep(60)  # Check every minute
    except KeyboardInterrupt:
        logger.info("Scheduler stopped by user")
    except Exception as e:
        logger.error(f"Scheduler error: {e}")

if __name__ == "__main__":
    main()
    