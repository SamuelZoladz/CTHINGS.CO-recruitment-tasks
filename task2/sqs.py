import logging
import boto3
from botocore.exceptions import NoCredentialsError, PartialCredentialsError, EndpointConnectionError

import config

logging.basicConfig(level=config.LOG_LEVEL)
logger = logging.getLogger(__name__)


def create_sqs_client():
    try:
        sqs_client = boto3.client(
            'sqs',
            region_name=config.AWS_DEFAULT_REGION,
            aws_access_key_id=config.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=config.AWS_SECRET_ACCESS_KEY,
            endpoint_url=config.AWS_ENDPOINT_URL
        )
        sqs_client.list_queues()
        logger.info("Connected to SQS successfully.")
        return sqs_client
    except (NoCredentialsError, PartialCredentialsError) as e:
        logger.error("Invalid AWS credentials: %s", e)
    except EndpointConnectionError as e:
        logger.error("Failed to connect to the endpoint: %s", e)
    except Exception as e:
        logger.error("An unexpected error occurred: %s", e)
    return None


sqs = create_sqs_client()


def get_from_queue():
    if not sqs:
        logger.error("SQS client is not initialized.")
        return None
    try:
        response = sqs.receive_message(
            QueueUrl=config.WORKER_QUEUE_URL,
            MaxNumberOfMessages=1,
            WaitTimeSeconds=20
        )
        if 'Messages' in response:
            return response['Messages'][0]
        else:
            return None
    except Exception as e:
        logger.error(f"Error retrieving message from queue: {e}")
        return None


def delete_from_queue(receipt_handle):
    if not sqs:
        logger.error("SQS client is not initialized.")
        return
    try:
        sqs.delete_message(
            QueueUrl=config.WORKER_QUEUE_URL,
            ReceiptHandle=receipt_handle
        )
        logger.info("Message deleted from queue successfully.")
    except Exception as e:
        logger.error(f"Error deleting message from queue: {e}")


def send_message_to_queue(message):
    if not sqs:
        logger.error("SQS client is not initialized.")
        return
    try:
        sqs.send_message(
            QueueUrl=config.WORKER_QUEUE_URL,
            MessageBody=message
        )
        logger.info(f"Message sent to queue: {message}")
    except Exception as e:
        logger.error(f"Error sending message to queue: {e}")
