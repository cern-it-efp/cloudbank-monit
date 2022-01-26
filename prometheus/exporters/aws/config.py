#!/usr/bin/env python3

import os

# Defaults
DEFAULT_ACC_KEY = ''
DEFAULT_SEC_KEY = ''
DEFAULT_PORT = '7979'
DEFAULT_LOG_LEVEL = 'INFO'
DEFAULT_LOG_FORMAT = '[%(asctime)s] [%(name)s] [%(levelname)s]: %(message)s'
DEFAULT_LOG_DATEFMT = '%Y-%m-%d %H:%M:%S'

# Configs (tries taking from env variables, otherwise use the defaults above)
ACC_KEY = os.environ.get('AWS_EXPORTER_ACC_KEY', DEFAULT_ACC_KEY)
SEC_KEY= os.environ.get('AWS_EXPORTER_SEC_KEY', DEFAULT_SEC_KEY)
PORT = os.environ.get('BQ_EXPORTER_PORT', DEFAULT_PORT)
LOG_LEVEL = os.environ.get('BQ_EXPORTER_LOG_LEVEL', DEFAULT_LOG_LEVEL).upper()
LOG_FORMAT = os.environ.get('BQ_EXPORTER_LOG_FORMAT', DEFAULT_LOG_FORMAT)
LOG_DATEFMT = os.environ.get('BQ_EXPORTER_LOG_DATEFMT', DEFAULT_LOG_DATEFMT)
