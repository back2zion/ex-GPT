import logging
import json

def log_json(event: dict):
    logging.info(json.dumps(event, ensure_ascii=False)) 