import os

DB_HOST = os.getenv('DB_HOST')
BATCH_SIZE = os.getenv('BATCH_SIZE', '100')
BATCH_INTERVAL = os.getenv('BATCH_INTERVAL', '180')
LOG_LEVEL = os.getenv('LOG_LEVEL', 'DEBUG')
