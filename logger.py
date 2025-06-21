import os
import logging
from datetime import datetime
from logging.handlers import TimedRotatingFileHandler

LOG_DIR = "logs"
os.makedirs(LOG_DIR, exist_ok=True)

today = datetime.now().strftime("%Y-%m-%d")
log_path = os.path.join(LOG_DIR, f"{today}.log")

file_handler = TimedRotatingFileHandler(
    log_path,
    when="midnight",
    interval=1,
    backupCount=7,
    encoding="utf-8",
    utc=False
)
file_handler.suffix = "%Y-%m-%d"
file_handler.setLevel(logging.DEBUG)

# copy formatter from discord logger
discord_logger = logging.getLogger("discord")
for handler in discord_logger.handlers:
    if handler.formatter:
        file_handler.setFormatter(handler.formatter)
        break
else:
    # fallback
    fallback_formatter = logging.Formatter(
        "%(asctime)s %(levelname)-8s %(name)-20s %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    file_handler.setFormatter(fallback_formatter)

discord_logger.setLevel(logging.DEBUG)
# discord_logger.addHandler(file_handler)

root_logger = logging.getLogger()
root_logger.setLevel(logging.DEBUG)
root_logger.addHandler(file_handler)
