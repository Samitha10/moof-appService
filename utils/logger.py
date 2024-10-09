import os
import logging
from datetime import datetime
from logging.handlers import QueueHandler, QueueListener
from queue import Queue

# # Set up the queue and handlers
# log_queue = Queue()
# queue_handler = QueueHandler(log_queue)
# queue_listener = QueueListener(log_queue, logging.StreamHandler())

#! Older Logging function without Async
# Get the current date
current_date = datetime.now().strftime("%Y_%m_%d")

# Create a folder named with the current date
logs_folder = os.path.join(os.getcwd(), "logs", current_date)
os.makedirs(logs_folder, exist_ok=True)

# Create a log file inside this folder
LOG_FILE = f"{current_date}.log"
LOG_FILE_PATH = os.path.join(logs_folder, LOG_FILE)


# Custom logging handler to append date and time statement once
class CustomHandler(logging.FileHandler):
    def __init__(self, filename, mode="a", encoding="utf-8", delay=False):
        super().__init__(filename, mode, encoding, delay)
        self.initialized = False

    def emit(self, record):
        if not self.initialized:
            date_time_statement = (
                f"\n"
                f"------------Date and time of logging happens: "
                f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}-------------\n"
                # f"File of execution: {os.path.abspath(__file__)}\n"
            )
            self.stream.write(f"{date_time_statement}\n")
            self.initialized = True
        super().emit(record)


# Set up logging to use this log file
logging.basicConfig(
    level=logging.INFO,
    format="[ %(asctime)s ] %(filename)s : %(lineno)d %(name)s - %(levelname)s - %(message)s",
    handlers=[CustomHandler(LOG_FILE_PATH, encoding="utf-8")],
)

#! Older Logging function without Async Upto this line.

# logging.basicConfig(level=logging.DEBUG)
# logger = logging.getLogger(__name__)
# logger.addHandler(queue_handler)

# # Start the queue listener
# queue_listener.start()


# # Function to stop the queue listener
# def stop_listener():
#     queue_listener.stop()


# # Example usage
# logging.info("This is a test log entry.")
# logging.info("logging has started")
# logging.error("Error message from same_logging")
# logging.info("This is an info message.")
# logging.warning("This is a warning message.")
# logging.error("This is an error message.")
# logging.critical("This is a critical message.")
