import logging
import logging.handlers
from pathlib import Path

from fraud_detection.config.config_loader import get_config



def ensure_directory(path):
    """Create directory if it does not exist."""
    p = Path(path)
    if not p.exists():
        p.mkdir(parents=True, exist_ok=True)


def build_log_path(service_name):
    """Return the directory path for a given service."""
    cfg = get_config()
    logs_root = Path(cfg["paths"]["logs"]["root"])
    service_dir = logs_root / service_name
    ensure_directory(service_dir)
    return service_dir


def get_logger(service_name):
    """
    Return a logger configured for the given service.
    Each service writes logs to its own folder inside logs/.
    """
    logger = logging.getLogger(service_name)

    # Prevent adding handlers multiple times
    if logger.handlers:
        return logger

    logger.setLevel(logging.INFO)

    log_dir = build_log_path(service_name)
    log_file = log_dir / f"{service_name}.log"

    # File handler with rotation
    file_handler = logging.handlers.RotatingFileHandler(
        log_file,
        maxBytes=5_000_000,  # 5 MB before rotation
        backupCount=5        # keep last 5 rotated logs
    )
    file_handler.setLevel(logging.INFO)

    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)

    # Log format
    log_format = (
        "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
    )
    formatter = logging.Formatter(log_format, datefmt="%Y-%m-%d %H:%M:%S")

    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)

    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    logger.propagate = False
    return logger
