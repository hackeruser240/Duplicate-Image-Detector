# scripts/logger_setup.py
import logging
import os
import sys

def loggerSetup():
    """
    Configures the root logger with FileHandler and StreamHandler.
    """
    # Create the logs directory if it doesn't exist
    if not os.path.exists("logs"):
        os.mkdir("logs")
    log_file = os.path.join("logs", 'log.txt')

    # Get the root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)

    # Create the FileHandler
    file_handler = logging.FileHandler(log_file, "w")
    file_handler.setLevel(logging.DEBUG)
    file_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s', datefmt='%d-%b-%Y %I:%M:%S %p')
    file_handler.setFormatter(file_formatter)

    # Create the StreamHandler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    #console_formatter = logging.Formatter('%(name)s: %(levelname)s - %(message)s')
    console_formatter = logging.Formatter('%(message)s')
    console_handler.setFormatter(console_formatter)

    # Add handlers to the root logger
    root_logger.addHandler(file_handler)
    root_logger.addHandler(console_handler)

    # Return handlers just in case, but they are now attached to the root logger
    return file_handler, console_handler