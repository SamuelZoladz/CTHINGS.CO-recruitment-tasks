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
AWS_DEFAULT_REGION = set_and_check_env_var('AWS_DEFAULT_REGION')
AWS_ENDPOINT_URL = set_and_check_env_var('AWS_ENDPOINT_URL')
AWS_ACCESS_KEY_ID = set_and_check_env_var('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = set_and_check_env_var('AWS_SECRET_ACCESS_KEY')
WORKER_QUEUE_URL = set_and_check_env_var('WORKER_QUEUE_URL')
API_PORT = set_and_check_env_var('API_PORT')
