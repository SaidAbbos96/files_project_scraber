from copy import deepcopy
from anyio import Path
import os
from pathlib import Path as PathlibPath

# .env faylni yuklash
from dotenv import load_dotenv
env_path = PathlibPath(__file__).parent.parent / ".env"
load_dotenv(env_path)

# Environment variables'dan o'qish (default qiymatlar bilan)
DB_LOCAL_NAME = Path(os.getenv("DB_LOCAL_NAME", "local_files"))
LOGGING_ENABLED = os.getenv(
    "LOGGING_ENABLED", "True").lower() in ("true", "1", "yes")
FILE_MIN_SIZE = int(
    os.getenv("FILE_MIN_SIZE", str(1024 * 1024)))  # Default: 1MB
DB_PATH = Path(os.getenv("DB_PATH", f"local_db/{DB_LOCAL_NAME}.db"))
# --- Umumiy sozlamalar ---
APP_CONFIG = {
    "download_dir": os.getenv("DOWNLOAD_DIR", "downloads"),
    "results_dir": os.getenv("RESULTS_DIR", "results"),
    "finish_dir": os.getenv("FINISH_DIR", "finish"),

    # --- Concurrency Settings ---
    # Umumiy concurrency (eski, backward compatibility uchun)
    "concurrency": 2,
    "scrape_concurrency": 5,        # Sahifalrni scraping qilishda parallel workers soni
    # Fayllarni yuklashda parallel workers soni
    "download_concurrency": 2,      # ✅ 2 TA PARALLEL DOWNLOAD
    # Telegramga yuborishda parallel workers soni
    # Upload concurrency
    "upload_concurrency": 2,        # ✅ 2 TA PARALLEL UPLOAD
    # Upload consumer workers soni
    # Upload workers
    "upload_workers": 2,            # ✅ 2 TA WORKER

    # --- Timing Settings ---
    "sleep_min": 0.5,
    "sleep_max": 2.5,
    "enable_sleep": True,

    # --- Processing Settings ---
    "checkpoint_batch": 100,
    "clear_uploaded_files": True,   # ✅ Yuklangan fayllarni o'chirish
    "stop_limit_page": False,
    "stop_limit": False,
    "stop_download_limit": False,

    # --- Notification Settings ---
    "send_startup_notifications": True,  # Startup message'larni yuborish
    # Batch mode'da individual notifications'ni kamaytirish
    "notification_quiet_mode": False,    # ✅ Har bir fayl haqida xabar bersin
    # Minimum interval between notifications (seconds)
    "notification_rate_limit": 1.0,

    # --- Telegram Settings ---
    # Telegram guruh ID/link (None bo'lsa default ishlatiladi)
    "telegram_group": None,

    # --- Disk Monitoring Settings ---
    "disk_monitor_enabled": True,   # ✅ Disk monitoring yoqilgan
    # ✅ Minimal bo'sh joy (5GB parallel mode uchun)
    "min_free_space_gb": 1.0,
    # Disk tekshirish intervali (soniya, default: 1 daqiqa)
    "disk_check_interval": 60,      # ✅ Har 1 daqiqada tekshirish
    # Disk joy uchun maksimal kutish (daqiqa)
    "max_wait_for_space_minutes": 30,  # ✅ 30 daqiqa kutish
    "cleanup_old_files": True,      # ✅ Eski fayllarni avtomatik tozalash
    "file_max_age_hours": 1,        # ✅ 1 soatdan eski fayllarni o'chirish

    # --- Mode Settings ---
    "work_mode": None,              # "1" - scrape, "2" - download, "3" - download+upload
    # ✅ PARALLEL (parallel, bir nechta fayl bir vaqtda)
    "mode": "parallel",
    "debug": False,
    "sort_by_size": False,           # Eng kichik fayldan boshlash uchun

    # --- Streaming Settings ---
    # Stream orqali yuklash (disk ga saqlamasdan)
    "use_streaming_upload": False,  # ✅ STREAMING O'CHIRILGAN (klassik mode)
    "keep_files_on_disk": False,    # ✅ Fayllarni O'CHIRISH (upload'dan keyin)
}

MAX_SIZE_BYTES = 4 * 1024 * 1024 * 1024  # 4GB
BROWSER_CONFIG = {
    "browser": "chromium",  # chromium | firefox | webkit
    "headless": True,
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
    base = deepcopy(APP_CONFIG)
    base.update(site_config)
    if overrides:
        base.update(overrides)
    return base
