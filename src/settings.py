import json
import os

_settings = {
    "DB_HOST": os.getenv('DB_HOST'),
    "BATCH_SIZE": int(os.getenv('BATCH_SIZE', 100)),
    "BATCH_INTERVAL": int(os.getenv('BATCH_INTERVAL', 180)),
    "LOG_LEVEL": 'DEBUG',
    "MQ_HOST": "mq",
    "MQ_EXCHANGE": "zhaw-km",
    "MQ_BINDKEYS": ["indexer.*", "importer.object"],
    "MQ_HEARTBEAT": 500,
    "MQ_TIMEOUT": 300,
    "MQ_QUEUE": "indexerqueue",
    "MQ_USER": os.getenv("MQ_USER", "sdg-indexer"),
    "MQ_PASS": os.getenv("MQ_PASS", "guest")
}

if os.path.exists('/etc/app/config.json'):
    with open('/etc/app/config.json') as secrets_file:
        config = json.load(secrets_file)
        for key in config.keys():
            if config[key] is not None:
                _settings[str.upper(key)] = config[key]


DB_HOST = _settings['DB_HOST']
BATCH_SIZE = _settings['BATCH_SIZE']
BATCH_INTERVAL = _settings['BATCH_INTERVAL']
LOG_LEVEL = _settings['LOG_LEVEL']
MQ_HOST = _settings['MQ_HOST']
MQ_EXCHANGE = _settings['MQ_EXCHANGE']
MQ_BINDKEYS = _settings['MQ_BINDKEYS']
MQ_HEARTBEAT = _settings['MQ_HEARTBEAT']
MQ_TIMEOUT = _settings['MQ_TIMEOUT']
MQ_QUEUE = _settings['MQ_QUEUE']
MQ_USER = _settings['MQ_USER']
MQ_PASS = _settings['MQ_PASS']
