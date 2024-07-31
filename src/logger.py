import logging
import sys
from logging import Formatter
from logging import StreamHandler
from logging.handlers import RotatingFileHandler


logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
logger.addHandler(StreamHandler(sys.stdout))
file_handler = RotatingFileHandler("logs/log.log", maxBytes=2 * 1024 * 1024, backupCount=1)
file_handler.setFormatter(Formatter(fmt=" %(asctime)s|%(levelname)s|%(message)s"))
logger.addHandler(file_handler)
