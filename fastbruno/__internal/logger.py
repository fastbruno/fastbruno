from logging import getLogger
import logging

logging.basicConfig(format='fastbruno :: %(levelname)s - %(message)s', level=logging.DEBUG)
bruno_logger = logging.getLogger("fastbruno")
