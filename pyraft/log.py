import logging
import sys

class ClosingStreamHandler(logging.StreamHandler):
    def close(self):
        self.flush()
        super().close()

def set_logging(logging_level=logging.INFO, log_file=".log", stdout_log=True):
    logger = logging.getLogger()
    logger.setLevel(logging_level)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    for handler in logger.handlers:
        logger.removeHandler(handler)

    handler = logging.FileHandler(log_file)
    handler.setLevel(logging_level)
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    if stdout_log:
        handler = ClosingStreamHandler(sys.stdout)
        handler.setLevel(logging_level)
        handler.setFormatter(formatter)
        logger.addHandler(handler)

    logger = logging.getLogger("werkzeug")
    logger.setLevel(logging.ERROR)
    logger = logging.getLogger("urllib3.connectionpool")
    logger.setLevel(logging.ERROR)

    logging.info('=== Logging started ===')