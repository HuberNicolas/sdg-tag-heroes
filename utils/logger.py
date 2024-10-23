import logging
import os
from settings.settings import LoggingSettings
from utils.env_loader import is_running_in_docker

logging_settings = LoggingSettings()

# Function to configure logger
def logger(path: str):
    # Use os.path.join to concatenate paths safely

    if is_running_in_docker():
        base_path = "/" + logging_settings.LOG_PATH
    else : base_path = logging_settings.LOG_PATH

    log_file_path = os.path.join(base_path, path)

    # Remove any pre-existing handlers
    root_logger = logging.getLogger()
    if root_logger.hasHandlers():
        root_logger.handlers.clear()  # Clear existing handlers

    print(f"Configuring logger at: {log_file_path}")

    # Configure logging
    try:
        logging.basicConfig(
            filename=log_file_path,
            level=logging.INFO,
            format=logging_settings.LOG_FORMAT,
        )
        print(f"Log file path: {log_file_path}")
    except Exception as e:
        print(f"Error configuring logging: {e}")
        raise
    print(f"Created Logger: {logging}")

    # Get the logger (root logger in this case)
    return logging.getLogger()
