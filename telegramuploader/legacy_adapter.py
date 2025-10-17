"""
Legacy Integration Adapter - Eski koddan yangi sistemaga o'tish uchun
"""
from telegramuploader import TelegramUploaderOrchestrator, select_debug_files
from utils.logger_core import logger
from utils.disk_monitor import init_disk_monitor
from telegramuploader.telegram.telegram_client import Telegram_client, send_startup_messages
import os
import asyncio
import aiohttp
from typing import List, Dict, Any

from core.FileDB import FileDB
import sys
import os
# Add the parent directory to sys.path to import telegram module
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)


async def download_and_upload(CONFIG: Dict[str, Any]) -> None:
    """
    Legacy download_and_upload function - yangi sistemani ishlatadi

    Args:
        CONFIG: Konfiguratsiya dictionary
    """
    logger.info("📥 Download+Upload bosqichi ishga tushmoqda...")
    os.makedirs(CONFIG["download_dir"], exist_ok=True)
    
    # 💾 Disk monitor'ni ishga tushirish
    if CONFIG.get("disk_monitor_enabled", True):
        init_disk_monitor(
            download_dir=CONFIG["download_dir"],
            min_free_gb=CONFIG.get("min_free_space_gb", 5.0),
            check_interval=CONFIG.get("disk_check_interval", 60)
        )

    db = FileDB()

    # Config'da sort_by_size parametrini tekshirish
    sort_by_size = 1 if CONFIG.get("sort_by_size", False) else 0
    items = db.get_files(CONFIG["name"], sort_by_size=sort_by_size)

    if sort_by_size:
        logger.info(f"📊 Fayllar eng kichik hajmdan boshlab tartiblanadi")
    else:
        logger.info(f"📊 Fayllar standart tartibda qayta ishlanadi")

    # print("items", items)
    if not items:
        logger.warning(f"❌ {CONFIG['name']} uchun DB da fayl yo'q.")
        return
    else:
        logger.info(f"📊 {len(items)} ta fayl topildi {CONFIG['name']} uchun.")

    # --- DEBUG: Eng kichik 10 faylni ko'rsatish va tanlash ---
    if CONFIG.get("debug", False):
        items = await select_debug_files(items, CONFIG)
        if not items:
            return

    mode = CONFIG.get("mode", "sequential")  # sequential yoki parallel

    async with Telegram_client:
        await send_startup_messages(client=Telegram_client)

    async with aiohttp.ClientSession() as session:
        # Download concurrency semaphore
        download_concurrency = CONFIG.get(
            "download_concurrency", CONFIG.get("concurrency", 2))
        sem = asyncio.Semaphore(download_concurrency)

        # Yangi orchestrator ishlatamiz
        orchestrator = TelegramUploaderOrchestrator(CONFIG)

        # Streaming mode tekshirish
        use_streaming = CONFIG.get("use_streaming_upload", True)
        
        if use_streaming:
            logger.info("🚀 Streaming mode - fayllar disk ga saqlanmaydi")
            await orchestrator.process_files_streaming(items, session, sem, db)
        elif mode == "sequential":
            logger.info("🚀 Sequential mode - klassik qayta ishlash")
            await orchestrator.process_files_sequential(items, session, sem, db)
        else:
            logger.info("🚀 Parallel mode - klassik qayta ishlash")
            await orchestrator.process_files_parallel(items, session, sem, db)

    logger.info(f"\n✅ Jarayon tugadi. {CONFIG['name']} fayllari yangilandi.")


async def sequential_mode(items: List[Dict[str, Any]], session: aiohttp.ClientSession,
                          sem: asyncio.Semaphore, CONFIG: Dict[str, Any], db: FileDB) -> None:
    """
    Legacy sequential mode function - yangi sistemani ishlatadi

    Args:
        items: Fayllar ro'yxati
        session: aiohttp session
        sem: Semaphore
        CONFIG: Konfiguratsiya
        db: Database
    """
    orchestrator = TelegramUploaderOrchestrator(CONFIG)
    await orchestrator.process_files_sequential(items, session, sem, db)


async def parallel_mode(items: List[Dict[str, Any]], session: aiohttp.ClientSession,
                        sem: asyncio.Semaphore, CONFIG: Dict[str, Any], db: FileDB) -> None:
    """
    Legacy parallel mode function - yangi sistemani ishlatadi

    Args:
        items: Fayllar ro'yxati
        session: aiohttp session
        sem: Semaphore
        CONFIG: Konfiguratsiya
        db: Database
    """
    orchestrator = TelegramUploaderOrchestrator(CONFIG)
    await orchestrator.process_files_parallel(items, session, sem, db)


async def streaming_mode(items: List[Dict[str, Any]], session: aiohttp.ClientSession,
                        sem: asyncio.Semaphore, CONFIG: Dict[str, Any], db: FileDB) -> None:
    """
    Streaming mode - fayllarni disk ga saqlamasdan to'g'ridan-to'g'ri yuklash

    Args:
        items: Fayllar ro'yxati
        session: aiohttp session
        sem: Semaphore
        CONFIG: Konfiguratsiya
        db: Database
    """
    orchestrator = TelegramUploaderOrchestrator(CONFIG)
    await orchestrator.process_files_streaming(items, session, sem, db)


# Legacy function aliases
select_debug_files_legacy = select_debug_files
