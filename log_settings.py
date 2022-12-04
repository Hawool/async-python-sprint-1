# import logging
import logging
from logging.config import dictConfig

LOG_LEVEL = 'INFO'

LOGGER_CONFIG = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'default': {
            '()': 'uvicorn.logging.DefaultFormatter',
            'fmt': '%(levelprefix)s[%(asctime)s - %(filename)s:%(lineno)s - %(funcName)s] %(message)s',
            'datefmt': '%Y-%m-%d %H:%M:%S',
        },
        'for_file': {
            '()': 'uvicorn.logging.DefaultFormatter',
            'fmt': '%(levelname)s: [%(asctime)s - %(filename)s:%(lineno)s - %(funcName)s] %(message)s',
            'datefmt': '%Y-%m-%d %H:%M:%S',
        },
    },
    'handlers': {
        'console': {
            'level': LOG_LEVEL,
            'formatter': 'default',
            'class': 'logging.StreamHandler',
            'stream': 'ext://sys.stderr',
        },
        'file': {
            'level': LOG_LEVEL,
            'class': 'logging.handlers.RotatingFileHandler',
            'formatter': 'for_file',
            'filename': 'log.log',
            'maxBytes': 5000000,
            'backupCount': 10
        }
    },
    'loggers': {
        'root': {
            'level': LOG_LEVEL,
            'handlers': ['console', 'file'],
        }
    }
}

# Initiate logger config
dictConfig(LOGGER_CONFIG)
logger = logging.getLogger('root')
