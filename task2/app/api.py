from fastapi import FastAPI, HTTPException
import threading
import logging

import sqs
import config

logging.basicConfig(level=config.LOG_LEVEL)
logger = logging.getLogger(__name__)

app = FastAPI()


@app.post("/event")
def post_event(msg: dict):
    if 'msg' not in msg:
        logger.warning("Missing 'msg' key in the payload.")
        raise HTTPException(status_code=400, detail="Missing 'msg' key in the payload.")
    threading.Thread(target=sqs.send_message_to_queue, args=(msg['msg'],)).start()
    return {"status": f"Message received: {msg['msg']}"}
