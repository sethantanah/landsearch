import logging
import sys
import traceback
from logging.handlers import TimedRotatingFileHandler
from pathlib import Path
from datetime import datetime


class ErrorLineTracker:
    @staticmethod
    def get_error_location():
        """Get the file name, line number, and function name where the error occurred."""
        try:
            # Get the current stack frame
            frame = sys._getframe(2)  # Go up 2 frames to get the caller's location
            filename = frame.f_code.co_filename
            lineno = frame.f_lineno
            function = frame.f_code.co_name
            return filename, lineno, function
        except Exception:
            return "Unknown", 0, "Unknown"


class JSONExtractionError(Exception):
    """
    Custom exception for JSON extraction errors with detailed error information.

    Attributes:
        message (str): Error message
        error_type (str): Type of error encountered
        error_location (str): Where in the extraction process the error occurred
        original_error (Exception, optional): The original exception that caused this error
        input_data (str, optional): Snippet of the problematic input data
        file_name (str): Name of the file where the error occurred
        line_number (int): Line number where the error occurred
        function_name (str): Name of the function where the error occurred
    """

    def __init__(
        self,
        message: str,
        error_type: str = "Unknown",
        error_location: str = "Unknown",
        original_error: Exception = None,
        input_data: str = None,
    ):
        self.message = message
        self.error_type = error_type
        self.error_location = error_location
        self.original_error = original_error
        self.input_data = input_data[:100] if input_data else None

        # Get error location information
        self.file_name, self.line_number, self.function_name = (
            ErrorLineTracker.get_error_location()
        )

        # Build detailed error message
        detailed_message = f"""
JSON Extraction Error:
- Message: {self.message}
- Error Type: {self.error_type}
- Location: {self.error_location}
- File: {self.file_name}
- Line Number: {self.line_number}
- Function: {self.function_name}
- Original Error: {str(self.original_error) if self.original_error else 'None'}
- Input Data Preview: {self.input_data + '...' if self.input_data else 'None'}
- Stack Trace: 
{traceback.format_exc()}
"""
        super().__init__(detailed_message)

    def log_error(self, logger) -> None:
        """Log the error using the provided logger."""
        logger.error(f"JSON Extraction Error: {self.message}")
        logger.error(
            f"File: {self.file_name}, Line: {self.line_number}, Function: {self.function_name}"
        )
        logger.debug(f"Error Type: {self.error_type}")
        logger.debug(f"Location: {self.error_location}")
        if self.original_error:
            logger.debug(f"Original Error: {str(self.original_error)}")
        if self.input_data:
            logger.debug(f"Input Preview: {self.input_data}")


def setup_logger(
    name: str, log_dir: str = "logs", level=logging.INFO, console_output: bool = True
) -> logging.Logger:
    """
    Set up a logger with time-based rotation and console output.

    Args:
        name (str): Name of the logger
        log_dir (str): Directory to store log files
        level: Logging level
        console_output (bool): Whether to output logs to console

    Returns:
        logging.Logger: Configured logger instance
    """
    # Create logger
    logger = logging.getLogger(name)
    logger.setLevel(level)

    # Create logs directory if it doesn't exist
    log_dir_path = Path(log_dir)
    log_dir_path.mkdir(parents=True, exist_ok=True)

    # Create formatter
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # Create TimedRotatingFileHandler
    log_file = log_dir_path / f"{name}.log"
    file_handler = TimedRotatingFileHandler(
        filename=log_file,
        when="midnight",  # Rotate at midnight
        interval=1,  # Rotate every day
        backupCount=30,  # Keep 30 days of logs
        encoding="utf-8",
    )
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    # Add console handler if requested
    if console_output:
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

    return logger