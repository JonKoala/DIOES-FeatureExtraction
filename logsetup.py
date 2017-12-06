import logging
import logging.handlers


def init(filepath, logtoconsole=True, filehandler_config={}):

    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)

    # creating file handler
    fh = logging.handlers.RotatingFileHandler(filepath, **filehandler_config)
    fh.setLevel(logging.DEBUG)
    _skipline(logger, fh) # add a new line sperating each execution
    fh.setFormatter(logging.Formatter('%(asctime)s %(levelname)-8s [%(filename)s:%(lineno)d] %(message)s'))

    # creating console handler
    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)
    ch.setFormatter(logging.Formatter('%(levelname)s [%(filename)s:%(lineno)d] %(message)s'))

    logger.addHandler(fh)

    if logtoconsole:
        logger.addHandler(ch)

def _skipline(logger, fh):

    fh.setFormatter(logging.Formatter(''))
    logger.addHandler(fh)

    logging.info('\n')
