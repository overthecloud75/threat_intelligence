import os

PRODUCTION_MODE = True  # Release를 의미 

# Log
LOG_DIR = 'logs'
if not os.path.exists(LOG_DIR ):
    os.mkdir(LOG_DIR )

# csv
CSV_DIR = 'csv'
if not os.path.exists(CSV_DIR):
    os.mkdir(CSV_DIR)

