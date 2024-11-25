import logging
from logging import getLogger

logging.basicConfig(
    format="fastbruno :: %(levelname)s - %(message)s", level=logging.DEBUG
)
bruno_logger = logging.getLogger("fastbruno")
