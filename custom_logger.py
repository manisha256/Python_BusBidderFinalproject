import logging
import os

DATA_DIR = os.path.join(os.getcwd(), "data")
os.makedirs(DATA_DIR, exist_ok=True)

APP_LOG_FILE = os.path.join(DATA_DIR, "app_events.log")
REJECT_LOG_FILE = os.path.join(DATA_DIR, "rejected_records.log")

# --- 1. General App Events Logger ---
app_logger = logging.getLogger("BusBidderAppLogger")
app_logger.setLevel(logging.INFO)
if not app_logger.handlers:
    app_handler = logging.FileHandler(APP_LOG_FILE, encoding="utf-8")
    app_handler.setLevel(logging.INFO)
    app_formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s", datefmt="%Y-%m-%d %H:%M:%S")
    app_handler.setFormatter(app_formatter)
    app_logger.addHandler(app_handler)

# --- 2. Rejected Records Logger ---
reject_logger = logging.getLogger("BusBidderRejectLogger")
reject_logger.setLevel(logging.WARNING)
if not reject_logger.handlers:
    reject_handler = logging.FileHandler(REJECT_LOG_FILE, encoding="utf-8")
    reject_handler.setLevel(logging.WARNING)
    reject_formatter = logging.Formatter("%(asctime)s [REJECTED] %(message)s", datefmt="%Y-%m-%d %H:%M:%S")
    reject_handler.setFormatter(reject_formatter)
    reject_logger.addHandler(reject_handler)

def log_event(message: str, level: str = "INFO"):
    """Logs general application events (options chosen, user actions, bookings, confirmations)."""
    lvl = level.upper()
    if lvl == "DEBUG":
        app_logger.debug(message)
    elif lvl == "WARNING":
        app_logger.warning(message)
    elif lvl == "ERROR":
        app_logger.error(message)
    else:
        app_logger.info(message)

def log_rejection(record_info: str, reason: str):
    """Logs records that were rejected during data ingestion or validation."""
    reject_logger.warning(f"Record: {record_info} | Reason: {reason}")