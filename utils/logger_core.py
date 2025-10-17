import logging
from pathlib import Path
from datetime import datetime
import os

from core.config import LOGGING_ENABLED


def create_log_filename(name):
    """Unique log file nomi yaratish"""
    logs_dir = Path("logs")
    logs_dir.mkdir(exist_ok=True)

    # Format: modulename_YYYY-MM-DD_HH-MM-SS.log
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    return logs_dir / f"{name}_{timestamp}.log"


def cleanup_old_logs(days_old=7):
    """Eski log fayllarni o'chirish (default: 7 kundan eski)"""
    logs_dir = Path("logs")
    if not logs_dir.exists():
        return

    from datetime import timedelta
    cutoff_time = datetime.now() - timedelta(days=days_old)

    deleted_count = 0
    for log_file in logs_dir.glob("*.log"):
        if log_file.stat().st_mtime < cutoff_time.timestamp():
            try:
                log_file.unlink()
                deleted_count += 1
            except OSError:
                pass

    return deleted_count


def get_logger(name="scraper", log_file=None):
    logger = logging.getLogger(name)

    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    # Remove existing handlers to avoid duplicate logs
    if logger.hasHandlers():
        logger.handlers.clear()

    if LOGGING_ENABLED:
        logger.setLevel(logging.INFO)
        # Console handler
        ch = logging.StreamHandler()
        ch.setLevel(logging.INFO)
        ch.setFormatter(formatter)
        logger.addHandler(ch)

        # File handler with unique filename
        if log_file is None:
            log_file = create_log_filename(name)

        fh = logging.FileHandler(Path(log_file))
        fh.setLevel(logging.INFO)
        fh.setFormatter(formatter)
        logger.addHandler(fh)
    else:
        logger.setLevel(logging.INFO)
        # Faqat INFO larni chiqarish uchun filter

        class InfoOnlyFilter(logging.Filter):
            def filter(self, record):
                return record.levelno == logging.INFO

        ch = logging.StreamHandler()
        ch.setLevel(logging.INFO)
        ch.addFilter(InfoOnlyFilter())
        ch.setFormatter(formatter)
        logger.addHandler(ch)

    return logger


logger = get_logger("main")
