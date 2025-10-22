from copy import deepcopy
import os
from pathlib import Path as PathlibPath

# .env faylni yuklash
from dotenv import load_dotenv
env_path = PathlibPath(__file__).parent.parent / ".env"
load_dotenv(env_path)

# Environment variables'dan o'qish (default qiymatlar bilan)
DB_LOCAL_NAME = os.getenv("DB_LOCAL_NAME", "local_files")
LOGGING_ENABLED = os.getenv(
    "LOGGING_ENABLED", "True").lower() in ("true", "1", "yes")
FILE_MIN_SIZE = int(
    os.getenv("FILE_MIN_SIZE", str(1024 * 1024)))  # Default: 1MB
DB_PATH = f"local_db/{DB_LOCAL_NAME}.db"

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
