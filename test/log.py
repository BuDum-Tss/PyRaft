import logging


def set_logging(logging_level=logging.INFO):
    logger = logging.getLogger()
    logger.setLevel(logging_level)
    logging.basicConfig(filename='.log',
                        filemode='a',
                        format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
                        datefmt='%H:%M:%S',
                        level=logging_level)

    logger = logging.getLogger("werkzeug")
    logger.setLevel(logging.ERROR)
    logger = logging.getLogger("urllib3.connectionpool")
    logger.setLevel(logging.ERROR)
    logging.info('=== Logging started ===')
