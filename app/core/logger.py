import logging
from logging.handlers import RotatingFileHandler, QueueHandler, QueueListener
from queue import Queue
import sys
from datetime import datetime

# Timestamp
timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
log_file = f"logs/drivenow_{timestamp}.log"

# Queue to write in an atomic fashion
log_queue = Queue(-1)

# Create queue handler
queue_handler = QueueHandler(log_queue)

# Root logger
logger = logging.getLogger("myapp")
logger.setLevel(logging.INFO)
logger.addHandler(queue_handler)
logger.propagate = False

# Format logs
formatter = logging.Formatter(
    fmt="%(asctime)s [%(levelname)s] %(name)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setFormatter(formatter)

file_handler = RotatingFileHandler(log_file, maxBytes=10_000_000, backupCount=5)
file_handler.setFormatter(formatter)

listener = QueueListener(log_queue, console_handler, file_handler)
listener.start()