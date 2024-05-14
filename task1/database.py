import logging
from pymongo.mongo_client import MongoClient

import config

logging.basicConfig(level=config.LOG_LEVEL)
logger = logging.getLogger(__name__)


class MongoDBClient:
    """
    Singleton MongoDBClient class to manage MongoDB connections and operations.

    This class implements the Singleton pattern to ensure that only one instance
    of this class can exist, providing a single point of access to the database connection.
    """
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            logger.info("Creating the instance")
            cls._instance = super(MongoDBClient, cls).__new__(cls)
            cls._instance.connection = None
        return cls._instance

    def connect(self):
        if self.connection is None or self.connection.admin.command("ping", check=True).get('ok') != 1.0:
            try:
                self.connection = MongoClient(config.MONGODB_URI)
                self.connection.admin.command('ping')
                logger.info("Connected to database")
            except Exception as e:
                logger.error(f"Failed to connect to MongoDB: {e}")
                self.connection = None
        return self.connection

    def insert_data(self, data):
        client = self.connect()
        if client is not None:
            try:
                db = client[config.DATABASE_NAME]
                collection = db[config.COLLECTION_NAME]
                collection.insert_many(data)
                logger.info(f"Inserted data successfully")
                logger.debug(f"Inserted data: {data}")
            except Exception as e:
                logger.error(f"Failed to insert data: {e}")

    def find_data(self, key, filter_type, value):
        client = self.connect()
        if client is not None:
            try:
                db = client[config.DATABASE_NAME]
                collection = db[config.COLLECTION_NAME]
                query = {key: {filter_type: value}}
                if collection.count_documents(query) > 0:
                    data = collection.find(query)
                    logger.info(f"Retrieved logs successfully.")
                    return data
                else:
                    logger.info(f"No logs found that meet the requirements.")
                    return None
            except Exception as e:
                logger.error(f"Failed to get data: {e}")
                return None
