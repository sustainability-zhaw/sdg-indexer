import json
import os


if os.path.exists('/etc/app/secrets.json'):
    with open('/etc/app/secrets.json') as secrets_file:
        secrets = json.load(secrets_file)
        for key in ['ad_user', 'ad_pass']:
            if key in secrets and secrets[key] is not None:
                os.environ[str.upper(key)] = secrets[key]

AD_HOST = os.getenv('AD_HOST', 'zhaw.ch')
AD_USER = os.getenv('AD_USER')
AD_PASS = os.getenv('AD_PASS')
DB_HOST = os.getenv('DB_HOST')
BATCH_SIZE = int(os.getenv('BATCH_SIZE', 100))
BATCH_INTERVAL = int(os.getenv('BATCH_INTERVAL', 180))
LOG_LEVEL = os.getenv('LOG_LEVEL', 'ERROR')
