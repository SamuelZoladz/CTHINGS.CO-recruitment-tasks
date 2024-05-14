import os
import logging

logger = logging.getLogger(__name__)
logging.basicConfig(level=os.getenv('LOG_LEVEL', 'INFO').upper())


def set_and_check_env_var(var_name):
    value = os.getenv(var_name)
    if not value:
        logger.error(f"{var_name} not set.")
    else:
        logger.debug(f"{var_name} set: {value}.")
    return value


LOG_LEVEL = os.getenv('LOG_LEVEL', '').upper()

if LOG_LEVEL not in ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']:
    logger.warning(f"Invalid LOG_LEVEL: {LOG_LEVEL}. Using default level: INFO.")
    LOG_LEVEL = 'INFO'

else:
    logger.debug(f"LOG_LEVEL set: {LOG_LEVEL}.")
    LOG_LEVEL = LOG_LEVEL.upper()

MONGODB_URI = set_and_check_env_var('MONGODB_URI')

DATABASE_NAME = set_and_check_env_var('DATABASE_NAME')

COLLECTION_NAME = set_and_check_env_var('COLLECTION_NAME')
