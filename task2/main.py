import threading
import uvicorn
import logging

import database
import sqs
import config

logging.basicConfig(level=config.LOG_LEVEL)
logger = logging.getLogger(__name__)


def check_queue():
    mongo_client = database.MongoDBClient()
    while True:
        message = sqs.get_from_queue()
        if message:
            mongo_client.insert_data([{"msg": message['Body']}])
            threading.Thread(target=sqs.delete_from_queue, args=(message['ReceiptHandle'],)).start()


if __name__ == "__main__":
    threading.Thread(target=check_queue, daemon=True).start()
    config = uvicorn.Config("api:app", host="0.0.0.0", port=8000)
    server = uvicorn.Server(config)
    server.run()
