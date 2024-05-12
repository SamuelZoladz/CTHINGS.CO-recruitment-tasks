import unittest
from datetime import datetime
from unittest.mock import mock_open, patch

from src import logs_tool


class TestParseLogLine(unittest.TestCase):
    def test_parse_log_line_valid(self):
        line = "2021-01-01 12:00:00,123 - TestService - INFO - This is a test message"
        expected_result = {
            'datetime': datetime(2021, 1, 1, 12, 0, 0, 123000),
            'service': 'TestService',
            'severity': 'INFO',
            'message': 'This is a test message'
        }
        result = logs_tool.parse_log_line(line)
        self.assertEqual(result, expected_result)

    def test_parse_log_line_message_with_split_signs(self):
        line = "2021-01-01 12:00:00,123 - TestService - INFO - This is a test message - and this is also message"
        expected_result = {
            'datetime': datetime(2021, 1, 1, 12, 0, 0, 123000),
            'service': 'TestService',
            'severity': 'INFO',
            'message': 'This is a test message - and this is also message'
        }
        result = logs_tool.parse_log_line(line)
        self.assertEqual(result, expected_result)

    def test_parse_log_line_malformed(self):
        line = "Malformed log line"
        with self.assertRaises(ValueError) as context:
            logs_tool.parse_log_line(line)
        self.assertIn("Log line is malformed, not enough parts", str(context.exception))

    def test_parse_log_line_incorrect_timestamp(self):
        line = "2021:01-01 12:00:00,123 - TestService - INFO - This is a test message"
        with self.assertRaises(ValueError) as context:
            logs_tool.parse_log_line(line)
        self.assertIn("Timestamp format is incorrect", str(context.exception))


class TestParseLogFile(unittest.TestCase):
    def test_parse_log_file_valid(self):
        lines = [
            "2021-01-01 12:00:00,123 - TestService - INFO - Message one\n",
            "2021-01-01 12:01:00,456 - TestService - ERROR - Message two\n"
        ]
        expected_results = [
            {
                'datetime': datetime(2021, 1, 1, 12, 0, 0, 123000),
                'service': 'TestService',
                'severity': 'INFO',
                'message': 'Message one'
            },
            {
                'datetime': datetime(2021, 1, 1, 12, 1, 0, 456000),
                'service': 'TestService',
                'severity': 'ERROR',
                'message': 'Message two'
            }
        ]
        with patch('src.logs_tool.parse_log_line') as mock_parse_log_line:
            mock_parse_log_line.side_effect = lambda x: {
                'datetime': datetime(2021, 1, 1, 12, 0, 0, 123000),
                'service': 'TestService',
                'severity': 'INFO',
                'message': 'Message one'
            } if "Message one" in x else {
                'datetime': datetime(2021, 1, 1, 12, 1, 0, 456000),
                'service': 'TestService',
                'severity': 'ERROR',
                'message': 'Message two'
            }
            result = logs_tool.parse_log_file(lines)
            self.assertEqual(result, expected_results)

    def test_parse_log_file_ValueError(self):
        lines = [
            "2021-01-01 12:00:00,123 - TestService - INFO - Message one\n",
            "2021-01-01 12:01:00,456 - TestService - ERROR - Message two\n"
        ]
        with patch('src.logs_tool.parse_log_line') as mock_parse_log_line:
            mock_parse_log_line.side_effect = ValueError()
            result = logs_tool.parse_log_file(lines)
            self.assertEqual(result, None)


class TestReadLogFile(unittest.TestCase):
    def test_read_log_file_valid(self):
        file_data = "First line\nSecond line\nThird line"
        m = mock_open(read_data=file_data)
        with patch('builtins.open', m):
            result = logs_tool.read_log_file('dummy_path')
        self.assertEqual(['First line\n', 'Second line\n', 'Third line'], result)

    def test_read_log_file_not_found_error(self):
        with patch('builtins.open', mock_open()) as mocked_open:
            mocked_open.side_effect = FileNotFoundError()
            result = logs_tool.read_log_file('fake_path')
            self.assertIsNone(result)

    def test_read_log_file_permission_error(self):
        with patch('builtins.open', mock_open()) as mocked_open:
            mocked_open.side_effect = PermissionError()
            result = logs_tool.read_log_file('fake_path')
            self.assertIsNone(result)

    def test_read_log_file_generic_exception(self):
        with patch('builtins.open', mock_open()) as mocked_open:
            mocked_open.side_effect = Exception('Unexpected error')
            result = logs_tool.read_log_file('fake_path')
            self.assertIsNone(result)


if __name__ == '__main__':
    unittest.main()
