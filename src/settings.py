import json
import os


if os.path.exists('/etc/app/config.json'):
    with open('/etc/app/config.json') as secrets_file:
        secrets = json.load(secrets_file)
        for key in ['ad_user', 'ad_pass']:
            if key in secrets and secrets[key] is not None:
                os.environ[str.upper(key)] = secrets[key]

DB_HOST = os.getenv('DB_HOST')
BATCH_SIZE = int(os.getenv('BATCH_SIZE', 100))
BATCH_INTERVAL = int(os.getenv('BATCH_INTERVAL', 180))
LOG_LEVEL = os.getenv('LOG_LEVEL', ' DEBUG')
