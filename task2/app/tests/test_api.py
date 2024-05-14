import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import unittest
from fastapi.testclient import TestClient
from unittest.mock import patch
import api

client = TestClient(api.app)


class TestAPI(unittest.TestCase):

    @patch('sqs.send_message_to_queue')
    def test_post_event_success(self, mock_send_message_to_queue):
        response = client.post("/event", json={"msg": "Hello, SQS!"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"status": "Message received: Hello, SQS!"})
        mock_send_message_to_queue.assert_called_once_with("Hello, SQS!")

    def test_post_event_missing_msg_key(self):
        response = client.post("/event", json={"message": "This is wrong"})
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), {"detail": "Missing 'msg' key in the payload."})


if __name__ == '__main__':
    unittest.main()
