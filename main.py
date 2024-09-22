import time
import os 

from utils import make_csv_file_save_to_db, get_results_from_ti, send_email, get_today
from configs import CSV_DIR, CSV_BASE, SUBJECT_BASE, logger

if __name__ == '__main__':
    logger.info('start')
    while True:
        today = get_today()
        csv_file_path = f'{CSV_DIR}/{CSV_BASE}_{today}.csv'
        if not os.path.exists(csv_file_path):
            try:
                results = get_results_from_ti()
            except Exception as e:
                logger.error(e)
                results = []

            if results:
                results, csv_filename = make_csv_file_save_to_db(results=results)
                if results:
                    send_email(results, subject= f"{SUBJECT_BASE} {today}", attached_file=csv_filename)
        time.sleep(3600)
       
