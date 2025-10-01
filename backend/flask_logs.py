import logging
import structlog
import os
from logging.handlers import RotatingFileHandler
from config import LogConfig

class LogSetup:
    """Flask extension for structured logging using Structlog."""
    
    def __init__(self, app=None):
        """Allow lazy initialization."""
        self.app = None
        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        """Configure logging for Flask."""
        self.app = app
        log_type = LogConfig().LOG_TYPE.lower()  # "stream" or "file"
        log_level = LogConfig().LOG_LEVEL.upper()  # "INFO", "ERROR", etc.
        log_format = LogConfig().LOG_FORMAT.lower()  # "json" or "text"
        log_dir = LogConfig().LOG_DIR
        app_log_file = os.path.join(log_dir, LogConfig().APP_LOG_NAME)
        www_log_file = os.path.join(log_dir, LogConfig().WWW_LOG_NAME)
        log_max_bytes = LogConfig().LOG_MAX_BYTES  # Max log file size
        log_copies = LogConfig().LOG_COPIES  # Number of rotated log files
        www_log_enable = LogConfig().WWW_LOG_ENABLE  # Enable/disable HTTP request logging

        # Convert log level from string to logging constant
        levels = {
            'DEBUG': logging.DEBUG,
            'INFO': logging.INFO,
            'WARNING': logging.WARNING,
            'ERROR': logging.ERROR,
            'CRITICAL': logging.CRITICAL,
        }
        level = levels.get(log_level, logging.INFO)

        # Configure Structlog
        self.configure_structlog(log_type, log_format, level, app_log_file, www_log_file, log_max_bytes, log_copies, www_log_enable)

        # Attach Structlog logger to Flask
        app.logger = structlog.get_logger("flask-app")

    def configure_structlog(self, log_type, log_format, log_level, app_log_file, www_log_file, log_max_bytes, log_copies, www_log_enable):
        """Setup Structlog with different handlers."""
        
        # Choose log format processor
        if log_format == "json":
            log_processors = [
                structlog.processors.TimeStamper(fmt="iso"),
                structlog.processors.add_log_level,
                structlog.processors.StackInfoRenderer(),
                structlog.processors.format_exc_info,
                structlog.processors.JSONRenderer(),  # JSON format for logs
            ]
        else:  # Text format
            log_processors = [
                structlog.processors.TimeStamper(fmt="iso"),
                structlog.processors.add_log_level,
                structlog.processors.StackInfoRenderer(),
                structlog.processors.format_exc_info,
                structlog.processors.ExceptionPrettyPrinter(),
                structlog.processors.UnicodeDecoder(),
                # Add callsite parameters.
                
                #structlog.processors.CallsiteParameterAdder(
                #    {
                #        structlog.processors.CallsiteParameter.FILENAME,
                #        structlog.processors.CallsiteParameter.FUNC_NAME,
                #        structlog.processors.CallsiteParameter.LINENO,
                #    }
                #),
                structlog.dev.ConsoleRenderer(colors=(log_type == "stream")),  # Colored text format logs if log_type is stream
                #structlog.processors.KeyValueRenderer(),  # Text format logs
            ]

        # Configure standard logging
        logging.basicConfig(level=log_level, format="%(message)s")

        # Define handlers
        app_handlers = []
        www_handlers = []

        if log_type == "stream":
            app_handlers.append(logging.StreamHandler())
        else:
            os.makedirs(os.path.dirname(app_log_file), exist_ok=True)
            app_handlers.append(RotatingFileHandler(app_log_file, maxBytes=log_max_bytes, backupCount=log_copies))

            if www_log_enable:
                www_handlers.append(RotatingFileHandler(www_log_file, maxBytes=log_max_bytes, backupCount=log_copies))

        # Setup Structlog for app logs
        structlog.configure(
            processors=log_processors,
            context_class=dict,
            wrapper_class=structlog.make_filtering_bound_logger(log_level),
            logger_factory=structlog.stdlib.LoggerFactory(),
            cache_logger_on_first_use=True,
        )

        # Attach handlers to standard logging
        app_logger = logging.getLogger("flask-app")
        for handler in app_handlers:
            handler.setLevel(log_level)
            app_logger.addHandler(handler)

        # Set the log format for app logs
        #formatter = logging.Formatter('[%(asctime)s.%(msecs)03d] %(levelname)s %(name)s:%(filename)s/%(funcName)s: %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
        #for handler in app_logger.handlers:
        #    handler.setFormatter(formatter)

        # Setup separate logger for HTTP requests if enabled
        if www_log_enable:
            www_logger = logging.getLogger("access-log")
            www_logger.setLevel(log_level)
            for handler in www_handlers:
                www_logger.addHandler(handler)
