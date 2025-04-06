import logging

# Configure the root logger:
# - The format includes the time of the log, the name of the logger, the log level, and the log message.
# - The logging level is set to INFO, so messages with INFO level and higher (WARNING, ERROR, CRITICAL) will be output.
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)

# Set the logging level for the "httpx" module to WARNING.
# This reduces verbosity from the httpx library by only showing warnings and errors.
logging.getLogger("httpx").setLevel(logging.WARNING)

# Create a logger for the current module.
# __name__ gives the module's name, so this logger will be specific to this file.
logger = logging.getLogger(__name__)
