from copy import deepcopy
import os
from pathlib import Path as PathlibPath

# .env faylni yuklash
from dotenv import load_dotenv
env_path = PathlibPath(__file__).parent.parent / ".env"
load_dotenv(env_path)

# Database configuration
# PostgreSQL connection settings
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "files_project")
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "")
DB_STATEMENT_TIMEOUT_MS = int(os.getenv("DB_STATEMENT_TIMEOUT_MS", "0"))

# Legacy local database settings (deprecated - use PostgreSQL)
# DB_LOCAL_NAME = os.getenv("DB_LOCAL_NAME", "local_files")
# DB_PATH = f"local_db/{DB_LOCAL_NAME}.db"

def get_database_url():
    """Get PostgreSQL database URL from environment variables"""
    return f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

def get_async_database_url():
    """Get async PostgreSQL database URL from environment variables"""
    return f"postgresql+asyncpg://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

def get_db_engine_options():
    """Engine options for SQLAlchemy, configurable via env."""
    pool_size = int(os.getenv("DB_POOL_SIZE", "10"))
    max_overflow = int(os.getenv("DB_MAX_OVERFLOW", "20"))
    pool_pre_ping = os.getenv("DB_POOL_PRE_PING", "false").lower() in ("true", "1", "yes")
    pool_recycle = int(os.getenv("DB_POOL_RECYCLE", "1800"))
    connect_timeout = int(os.getenv("DB_CONNECT_TIMEOUT", "5"))
    application_name = os.getenv("DB_APPLICATION_NAME", "files_project_scraber")

    return {
        "pool_size": pool_size,
        "max_overflow": max_overflow,
        "pool_pre_ping": pool_pre_ping,
        "pool_recycle": pool_recycle,
        "connect_args": {"connect_timeout": connect_timeout, "application_name": application_name},
        "echo": False,
    }

def get_db_statement_timeout_ms() -> int:
    """Return statement timeout in milliseconds (0 for unlimited)."""
    return DB_STATEMENT_TIMEOUT_MS

# Other configuration
LOGGING_ENABLED = os.getenv(
    "LOGGING_ENABLED", "True").lower() in ("true", "1", "yes")
FILE_MIN_SIZE = int(
    os.getenv("FILE_MIN_SIZE", str(1024 * 1024)))  # Default: 1MB

# Worker identification
WORKER_NAME = os.getenv("WORKER_NAME", "worker_001")
# --- Umumiy sozlamalar ---
APP_CONFIG = {
    # --- Directory Settings ---
    "download_dir": os.getenv("DOWNLOAD_DIR", "downloads"),
    "results_dir": os.getenv("RESULTS_DIR", "results"),
    "finish_dir": os.getenv("FINISH_DIR", "finish"),

    # --- Concurrency Settings - Environment'dan o'qiladi ---
    # Backward compatibility
    "concurrency": int(os.getenv("DOWNLOAD_CONCURRENCY", "2")),
    "scrape_concurrency": int(os.getenv("SCRAPE_CONCURRENCY", "5")),
    "download_concurrency": int(os.getenv("DOWNLOAD_CONCURRENCY", "2")),
    "download_base_timeout": int(os.getenv("DOWNLOAD_BASE_TIMEOUT", "1800")),
    "download_max_retries": int(os.getenv("DOWNLOAD_MAX_RETRIES", "3")),
    "download_chunk_size": int(os.getenv("DOWNLOAD_CHUNK_SIZE", "262144")),
    "upload_concurrency": int(os.getenv("UPLOAD_CONCURRENCY", "2")),
    "upload_workers": int(os.getenv("UPLOAD_WORKERS", "2")),

    # --- Downloader Pagination ---
    "download_page_limit": int(os.getenv("DOWNLOAD_PAGE_LIMIT", "50")),

    # --- Scraper Queue/Batch Settings ---
    "scraper_queue_max": int(os.getenv("SCRAPER_QUEUE_MAX", "10000")),
    "db_batch_timeout": float(os.getenv("DB_BATCH_TIMEOUT", "5")),
    "db_max_retries": int(os.getenv("DB_MAX_RETRIES", "3")),
    "db_cache_path": os.getenv("DB_CACHE_PATH", "logs/db_cache.jsonl"),

    # --- Timing Settings - Environment'dan o'qiladi ---
    "sleep_min": float(os.getenv("SLEEP_MIN", "0.5")),
    "sleep_max": float(os.getenv("SLEEP_MAX", "2.5")),
    "enable_sleep": os.getenv("ENABLE_SLEEP", "true").lower() in ("true", "1", "yes"),

    # --- Processing Settings - Environment'dan o'qiladi ---
    "checkpoint_batch": int(os.getenv("CHECKPOINT_BATCH", "100")),
    "clear_uploaded_files": os.getenv("CLEAR_UPLOADED_FILES", "true").lower() in ("true", "1", "yes"),
    "stop_limit_page": False,  # Internal setting, hardcoded
    "stop_limit": False,       # Internal setting, hardcoded
    "stop_download_limit": False,  # Internal setting, hardcoded

    # --- Notification Settings - Environment'dan o'qiladi ---
    "send_startup_notifications": os.getenv("SEND_STARTUP_NOTIFICATIONS", "true").lower() in ("true", "1", "yes"),
    "notification_quiet_mode": os.getenv("NOTIFICATION_QUIET_MODE", "false").lower() in ("true", "1", "yes"),
    "notification_rate_limit": float(os.getenv("NOTIFICATION_RATE_LIMIT", "1.0")),

    # --- Telegram Settings - Environment'dan o'qiladi ---
    # Override default group
    "telegram_group": os.getenv("TELEGRAM_GROUP", None),

    # --- Disk Monitoring Settings - Environment'dan o'qiladi ---
    "disk_monitor_enabled": os.getenv("DISK_MONITOR_ENABLED", "true").lower() in ("true", "1", "yes"),
    "min_free_space_gb": float(os.getenv("MIN_FREE_SPACE_GB", "1.0")),
    "disk_check_interval": int(os.getenv("DISK_CHECK_INTERVAL", "60")),
    "max_wait_for_space_minutes": int(os.getenv("MAX_WAIT_FOR_SPACE_MINUTES", "30")),
    "cleanup_old_files": os.getenv("CLEANUP_OLD_FILES", "true").lower() in ("true", "1", "yes"),
    "file_max_age_hours": float(os.getenv("FILE_MAX_AGE_HOURS", "1")),

    # --- Mode Settings - Environment'dan o'qiladi ---
    # "1" - scrape, "2" - download, "3" - download+upload
    "work_mode": os.getenv("WORK_MODE", None),
    "mode": os.getenv("MODE", "parallel"),       # parallel/sequential
    "debug": os.getenv("DEBUG", "false").lower() in ("true", "1", "yes"),
    "sort_by_size": os.getenv("SORT_BY_SIZE", "false").lower() in ("true", "1", "yes"),

    # --- Streaming Settings - Environment'dan o'qiladi ---
    "use_streaming_upload": os.getenv("USE_STREAMING_UPLOAD", "false").lower() in ("true", "1", "yes"),
    "keep_files_on_disk": os.getenv("KEEP_FILES_ON_DISK", "false").lower() in ("true", "1", "yes"),

    # --- Bot API upload ---
    "use_bot_api_upload": os.getenv("USE_BOT_API_UPLOAD", "false").lower() in ("true", "1", "yes"),
    "bot_api_token": os.getenv("BOT_API_TOKEN", None),
    "bot_api_chat_id": os.getenv("BOT_API_CHAT_ID", None),
}

MAX_SIZE_BYTES = 4 * 1024 * 1024 * 1024  # 4GB
BROWSER_CONFIG = {
    "browser": "chromium",  # chromium | firefox | webkit
    "headless": int(os.getenv("HEADLESS", "1")) == 1,
    "viewport": {"width": 1280, "height": 720},
    "user_agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    ),
    "proxy": None,
    "slow_mo": 0,
    "device_scale_factor": 1.0,
    "locale": "uz-UZ",
    "geolocation": None,
    "permissions": ["geolocation"],
}


# Environment variables'dan Telegram konfiguratsiyasini o'qish
TELEGRAM_API_ID = int(os.getenv("TELEGRAM_API_ID", "28837519"))
TELEGRAM_API_HASH = os.getenv(
    "TELEGRAM_API_HASH", "e22cefa35ca74ad27a92bceebd1291b3")
TELEGRAM_PHONE_NUMBER = os.getenv("TELEGRAM_PHONE_NUMBER", "+998200089990")
FILES_GROUP_ID = os.getenv("FILES_GROUP_ID", "-1002699309226")
FILES_GROUP_LINK = os.getenv(
    "FILES_GROUP_LINK", "https://t.me/+GGzAizSJb-g0MzQy")
TELEGRAM_USER_IS_PREMIUM = os.getenv("TELEGRAM_USER_IS_PREMIUM", True)


def make_config(site_config, overrides=None):
    """
    Config yaratish funksiyasi

    Args:
        site_config: Site-specific konfiguratsiya
        overrides: Qo'shimcha override qilingan sozlamalar

    Returns:
        dict: To'liq konfiguratsiya
    """
    base = deepcopy(APP_CONFIG)
    base.update(site_config)
    if overrides:
        base.update(overrides)
    return base


# ==========================================
# CONFIGURATION NOTES
# ==========================================
#
# Tez-tez o'zgaradigan sozlamalar .env faylida:
# - SCRAPE_CONCURRENCY: Performance tuning
# - DOWNLOAD_CONCURRENCY: Download speed
# - UPLOAD_CONCURRENCY: Upload speed
# - SLEEP_MIN/MAX: Rate limiting
# - MIN_FREE_SPACE_GB: Disk management
# - MODE: parallel/sequential
# - DEBUG: Development mode
#
# Static sozlamalar config.py da:
# - MAX_SIZE_BYTES: Hard limit
# - BROWSER_CONFIG: Browser settings
# - Telegram credentials: Security
#
# .env faylini o'zgartirish uchun:
# cp .env.example .env
# nano .env
