import logging
import logging.config

logging.config.fileConfig('./pl_aggregator/loggers/logging.conf', disable_existing_loggers=False)
logger = logging.getLogger('root')
