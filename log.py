import logging

# ANSI escape codes for colors
COLORS = {
    "RESET": "\033[0m",
    "BOLD": "\033[1m",
    "UNDERLINE": "\033[4m",
    "BLACK": "\033[30m",
    "RED": "\033[31m",
    "GREEN": "\033[32m",
    "YELLOW": "\033[33m",
    "BLUE": "\033[34m",
    "MAGENTA": "\033[35m",
    "CYAN": "\033[36m",
    "WHITECYAN": "\u001b[37;46m",
    "WHITE": "\033[37m",
}

# Custom formatter with colors
class ColoredFormatter(logging.Formatter):
    COLORS = {
        "DEBUG": COLORS["BLUE"],
        "INFO": COLORS["WHITECYAN"],
        "WARNING": COLORS["YELLOW"],
        "ERROR": COLORS["RED"],
        "CRITICAL": COLORS["RED"],
    }

    def format(self, record):
        log_message = super(ColoredFormatter, self).format(record)
        return f"{self.COLORS.get(record.levelname, '')}{log_message}{COLORS['RESET']}"

# Global logger configuration
logger = logging.getLogger(__name__)
logger.propagate = False  # Prevent messages from being propagated to the root logger

handler = logging.StreamHandler()
colored_formatter = ColoredFormatter("%(levelname)-8s%(message)s")
handler.setFormatter(colored_formatter)
logger.addHandler(handler)

logger.setLevel(logging.INFO)
