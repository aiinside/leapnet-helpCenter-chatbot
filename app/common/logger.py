import json
import logging
from logging.handlers import TimedRotatingFileHandler

from app.config import get_settings

class JSONFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:  # type: ignore[override]
        log_record = {
            "timestamp": self.formatTime(record, self.datefmt),
            "level": record.levelname,
            "logger": record.name,
        }
        if isinstance(record.msg, dict):
            log_record.update(record.msg)
        else:
            log_record["message"] = record.getMessage()
        if record.exc_info:
            log_record["exc_info"] = self.formatException(record.exc_info)
        return json.dumps(log_record, ensure_ascii=False)


def create_logger(name: str, log_file: str) -> logging.Logger:
    settings = get_settings()
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)

    if not logger.handlers:
        print(settings.log.directory)
        handler = TimedRotatingFileHandler(
            settings.log.directory / log_file, when="midnight", backupCount=90
        )
        handler.setFormatter(JSONFormatter())
        logger.addHandler(handler)
        logger.propagate = False

    print(logger)
    return logger
