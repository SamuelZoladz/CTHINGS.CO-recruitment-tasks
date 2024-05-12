import unittest
from unittest.mock import MagicMock, patch
from src.database import MongoDBClient


class TestMongoDBClient(unittest.TestCase):
    def setUp(self):
        self.database = MongoDBClient()

    def test_singleton_instance(self):
        first_instance = MongoDBClient()
        second_instance = MongoDBClient()
        self.assertEqual(first_instance, second_instance)

    @patch('src.database.MongoClient')
    @patch('src.database.config')
    def test_connect_success(self, mock_config, mock_mongo_client):
        mock_mongo_client.return_value.admin.command.return_value = {'ok': 1.0}

        client = self.database.connect()
        self.assertIsNotNone(client)
        mock_mongo_client.assert_called_once_with(mock_config.MONGODB_URI)
        mock_mongo_client.return_value.admin.command.assert_called_with('ping')

    @patch('src.database.MongoClient')
    @patch('src.database.config')
    def test_connect_failure(self, mock_config, mock_mongo_client):
        mock_mongo_client.side_effect = Exception("Connection failure")
        client = self.database.connect()
        self.assertIsNone(client)
        mock_mongo_client.assert_called_once_with(mock_config.MONGODB_URI)

    @patch('src.database.MongoClient')
    def test_insert_data_success(self, mock_mongo_client):
        mock_db = MagicMock()
        mock_collection = MagicMock()
        mock_mongo_client.return_value.__getitem__.return_value = mock_db
        mock_db.__getitem__.return_value = mock_collection

        mock_collection.insert_many.return_value = MagicMock()

        data = [{'key': 'value'}]
        self.database.connect = MagicMock(return_value=mock_mongo_client.return_value)
        self.database.insert_data(data)

        mock_collection.insert_many.assert_called_once_with(data)

    @patch('src.database.MongoClient')
    def test_insert_data_failure(self, mock_mongo_client):
        mock_db = MagicMock()
        mock_collection = MagicMock()
        mock_collection.insert_many.side_effect = Exception("Insert failure")
        mock_mongo_client.return_value.__getitem__.return_value = mock_db
        mock_db.__getitem__.return_value = mock_collection

        data = [{'key': 'value'}]
        self.database.connect = MagicMock(return_value=mock_mongo_client.return_value)
        self.database.insert_data(data)

        mock_collection.insert_many.assert_called_once_with(data)


if __name__ == '__main__':
    unittest.main()
