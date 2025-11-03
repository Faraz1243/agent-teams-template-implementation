# app/config/logging.py
import logging
import sys

def setup_loggers():
    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    # Create console handler and set level to INFO
    # console_handler = logging.StreamHandler(sys.stdout)
    # console_handler.setLevel(logging.INFO)
    # console_handler.setFormatter(formatter)

    # Get the root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)
    
    # Remove any existing handlers
    root_logger.handlers = []
    
    # Add the console handler to the logger
    # root_logger.addHandler(console_handler)

    # Create app logger
    app_logger = logging.getLogger('app')
    app_logger.setLevel(logging.INFO)
    app_logger.handlers = []  # Clear any existing handlers
    # app_logger.addHandler(console_handler)
    
    app_logger.propagate = False


    return app_logger

# Initialize logger
logger = setup_loggers()