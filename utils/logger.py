import os
import sys

from loguru import logger as loguru_logger

from settings.settings import LoggingSettings
from utils.env_loader import is_running_in_docker

logging_settings = LoggingSettings()

# Function to configure logger
def logger(name: str):
    # Use os.path.join to construct safe file paths
    if is_running_in_docker():
        base_path = "/" + logging_settings.LOG_PATH
    else:
        base_path = logging_settings.LOG_PATH

    log_file_path = os.path.join(base_path, f"{name}")


    # Remove any existing handlers before reconfiguring
    loguru_logger.remove()

    # Add file-based handler
    loguru_logger.add(
        log_file_path,
        rotation="10 MB",  # Rotate log file at 10 MB
        retention="7 days",  # Retain logs for 7 days
        level="INFO",
        format=logging_settings.LOG_FORMAT,
    )

    # Colors in docker/terminal: https://github.com/Delgan/loguru/issues/1173
    loguru_logger.add(sys.stderr, colorize=True)


    """
        #  https://www.highlight.io/blog/5-best-python-logging-libraries
        loguru_logger.trace("This is a trace message.") # won't be shown default
        
        loguru_logger.debug("This is a debug message")
        loguru_logger.info("This is an info message.")
        loguru_logger.success("This is a success message.")
        loguru_logger.warning("This is a warning message.")
        loguru_logger.error("This is an error message.")
        loguru_logger.critical("This is a critical message.")
        
        # Specific colors
        loguru_logger.opt(colors=True).warning("We got a <red>BIG</red> problem")
    """
    loguru_logger.info(f"Logger configured for {name}, log file at {log_file_path}")

    return loguru_logger
