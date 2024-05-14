import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
os.environ['AWS_DEFAULT_REGION'] = 'us-test-1'
os.environ['AWS_ACCESS_KEY_ID'] = 'test-access-key-id'
os.environ['AWS_SECRET_ACCESS_KEY'] = 'test-secret-access-key'
os.environ['AWS_ENDPOINT_URL'] = 'https://sqs.us-test-1.amazonaws.com'
os.environ['WORKER_QUEUE_URL'] = 'https://sqs.us-test-1.amazonaws.com/123456789012/test-queue'
os.environ['LOG_LEVEL'] = 'DEBUG'
os.environ['API_PORT'] = '8000'

import unittest
from unittest.mock import patch, MagicMock
from botocore.exceptions import NoCredentialsError, EndpointConnectionError

import config
import sqs


class TestSQSFunctions(unittest.TestCase):

    @patch('sqs.boto3.client')
    def test_create_sqs_client_success(self, mock_boto_client):
        mock_sqs_client = MagicMock()
        mock_boto_client.return_value = mock_sqs_client
        sqs_client = sqs.create_sqs_client()
        mock_boto_client.assert_called_once_with(
            'sqs',
            region_name=config.AWS_DEFAULT_REGION,
            aws_access_key_id=config.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=config.AWS_SECRET_ACCESS_KEY,
            endpoint_url=config.AWS_ENDPOINT_URL
        )
        mock_sqs_client.list_queues.assert_called_once()
        self.assertEqual(sqs_client, mock_sqs_client)

    @patch('sqs.boto3.client')
    def test_create_sqs_client_no_credentials(self, mock_boto_client):
        mock_boto_client.side_effect = NoCredentialsError()
        sqs_client = sqs.create_sqs_client()
        self.assertIsNone(sqs_client)

    @patch('sqs.boto3.client')
    def test_create_sqs_client_endpoint_error(self, mock_boto_client):
        mock_boto_client.side_effect = EndpointConnectionError(endpoint_url=config.AWS_ENDPOINT_URL)
        sqs_client = sqs.create_sqs_client()
        self.assertIsNone(sqs_client)

    @patch('sqs.boto3.client')
    def test_create_sqs_client_unexpected_error(self, mock_boto_client):
        mock_boto_client.side_effect = Exception("Unexpected error")
        sqs_client =sqs.create_sqs_client()
        self.assertIsNone(sqs_client)

    @patch('sqs.sqs')
    def test_get_from_queue_success(self, mock_sqs):
        mock_sqs.receive_message.return_value = {
            'Messages': [{'Body': 'test message', 'ReceiptHandle': 'test_receipt_handle'}]}
        message = sqs.get_from_queue()
        mock_sqs.receive_message.assert_called_once_with(
            QueueUrl=config.WORKER_QUEUE_URL,
            MaxNumberOfMessages=1,
            WaitTimeSeconds=20
        )
        self.assertEqual(message, {'Body': 'test message', 'ReceiptHandle': 'test_receipt_handle'})

    @patch('sqs.sqs')
    def test_get_from_queue_no_message(self, mock_sqs):
        mock_sqs.receive_message.return_value = {}
        message = sqs.get_from_queue()
        mock_sqs.receive_message.assert_called_once_with(
            QueueUrl=config.WORKER_QUEUE_URL,
            MaxNumberOfMessages=1,
            WaitTimeSeconds=20
        )
        self.assertIsNone(message)

    @patch('sqs.sqs')
    def test_get_from_queue_error(self, mock_sqs):
        mock_sqs.receive_message.side_effect = Exception("Error receiving message")
        message = sqs.get_from_queue()
        self.assertIsNone(message)

    @patch('sqs.sqs')
    def test_delete_from_queue_success(self, mock_sqs):
        sqs.delete_from_queue('test_receipt_handle')
        mock_sqs.delete_message.assert_called_once_with(
            QueueUrl=config.WORKER_QUEUE_URL,
            ReceiptHandle='test_receipt_handle'
        )

    @patch('sqs.sqs')
    def test_delete_from_queue_error(self, mock_sqs):
        mock_sqs.delete_message.side_effect = Exception("Error deleting message")
        sqs.delete_from_queue('test_receipt_handle')

    @patch('sqs.sqs')
    def test_send_message_to_queue_success(self, mock_sqs):
        sqs.send_message_to_queue('test message')
        mock_sqs.send_message.assert_called_once_with(
            QueueUrl=config.WORKER_QUEUE_URL,
            MessageBody='test message'
        )

    @patch('sqs.sqs')
    def test_send_message_to_queue_error(self, mock_sqs):
        mock_sqs.send_message.side_effect = Exception("Error sending message")
        sqs.send_message_to_queue('test message')

    @patch.object(sqs.logger, 'error')
    @patch('sqs.sqs', None)
    def test_client_not_initialized(self, mock_logger_error):
        functions_to_test = [
            (sqs.get_from_queue, (), {}),
            (sqs.delete_from_queue, ('test_receipt_handle',), {}),
            (sqs.send_message_to_queue, ('test message',), {})
        ]

        for func, args, kwargs in functions_to_test:
            with self.subTest(func=func.__name__):
                func(*args, **kwargs)
                mock_logger_error.assert_called_with("SQS client is not initialized.")


if __name__ == '__main__':
    unittest.main()
