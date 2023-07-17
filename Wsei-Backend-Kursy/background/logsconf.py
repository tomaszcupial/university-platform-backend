import logging
import logging.handlers

logger = logging.getLogger('Octopus-Logger')
logger.setLevel(logging.DEBUG)
file_handler = logging.FileHandler('./logs.log')
file_handler.setLevel(logging.INFO)
formatter = logging.Formatter(
    "{%(asctime)s} - %(message)s", datefmt='%Y-%m-%d %H:%M:%S')
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)
handler = logging.handlers.SysLogHandler(
    address=('127.0.0.1', 514), facility=21)
logger.addHandler(handler)

logging.info("start logging")
