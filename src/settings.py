import os

DB_HOST = os.getenv('DB_HOST')
BATCH_SIZE = os.getenv('BATCH_SIZE')
BATCH_INTERVAL = os.getenv('BATCH_INTERVAL')
LOG_LEVEL = os.getenv('LOG_LEVEL', 'DEBUG')

# because docker sets the environment variables, so python will not see the 
# need for using default values
if BATCH_SIZE == '':
    BATCH_SIZE = 100
else: 
    BATCH_SIZE = int(BATCH_SIZE)
if BATCH_INTERVAL == '':
    BATCH_INTERVAL = 180
else: 
    BATCH_INTERVAL = int(BATCH_INTERVAL)

if LOG_LEVEL == '':
    LOG_LEVEL = 'DEBUG'
