# app/logger.py
import logging
from logging.handlers import TimedRotatingFileHandler
import os
import json

LOG_DIR = "logs"
LOG_FILE = "application.log"

os.makedirs(LOG_DIR, exist_ok=True)

class JsonFormatter(logging.Formatter):
    def format(self, record):
        log_record = {
            "timestamp": self.formatTime(record, self.datefmt),
            "logger": record.name,
            "level": record.levelname,
            "message": record.getMessage(),
            "pathname": record.pathname,
            "funcName": record.funcName,
            "lineno": record.lineno,
        }
        return json.dumps(log_record)

def get_logger(name: str = "uv_example") -> logging.Logger:
    
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)

    if not logger.handlers:
        log_path = os.path.join(LOG_DIR, LOG_FILE)

        handler = TimedRotatingFileHandler(
            filename=log_path,
            when="midnight",
            interval=1,
            backupCount=7,
            encoding="utf-8"
        )

        formatter = JsonFormatter(datefmt="%Y-%m-%d %H:%M:%S")
        handler.setFormatter(formatter)

        logger.addHandler(handler)

    return logger
