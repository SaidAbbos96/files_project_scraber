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


async def check_and_queue_existing_files(db: FileDB, config: Dict[str, Any]) -> None:
    """
    Downloads papkasidagi mavjud fayllarni tekshirish va upload queue ga qo'yish
    """
    from pathlib import Path
    from utils.files import safe_filename
    
    downloads_dir = Path(config["download_dir"])
    if not downloads_dir.exists():
        return
    
    logger.info("📁 Downloads papkasidagi mavjud fayllarni tekshirish...")
    
    # Downloads papkasidagi barcha fayllar
    existing_files = list(downloads_dir.glob("*.mp4"))
    if not existing_files:
        logger.info("📁 Downloads papkasida fayllar topilmadi")
        return
    
    logger.info(f"📁 {len(existing_files)} ta fayl topildi downloads papkasida")
    
    # Database dan barcha yuklanmagan fayllarni olish
    all_undownloaded = db.get_undownloaded_files(config["name"])
    
    # Mavjud fayllarni database bilan match qilish
    matched_files = []
    for local_file in existing_files:
        local_filename = local_file.name
        
        # Database dan mos faylni topish
        for db_file in all_undownloaded:
            expected_filename = safe_filename(db_file["title"]) + f"_{db_file['id']}.mp4"
            
            if expected_filename == local_filename:
                # File hajmini tekshirish
                local_size = local_file.stat().st_size
                server_size = db_file.get("file_size", 0)
                
                if server_size and local_size > 0:
                    size_diff_mb = abs(server_size - local_size) / (1024 ** 2)
                    
                    if size_diff_mb > 100:  # 100MB dan katta farq
                        logger.warning(f"⚠️ Hajm farqi: {local_filename}")
                        logger.warning(f"   Local: {local_size / (1024**3):.2f}GB, Server: {server_size / (1024**3):.2f}GB")
                        
                        # Noto'g'ri faylni o'chirish va database status reset
                        try:
                            local_file.unlink()
                            logger.info(f"🗑️ Noto'g'ri fayl o'chirildi: {local_filename}")
                            
                            # Database da local_path ni reset qilish
                            db.update_file(db_file["id"], local_path=None)
                            logger.info(f"🔄 Database status reset qilindi: {db_file['id']}")
                            
                        except Exception as e:
                            logger.error(f"❌ Faylni o'chirishda xato: {e}")
                    else:
                        # Fayl to'g'ri - database update qilish va upload queue ga qo'yish
                        db.update_file(
                            db_file["id"], 
                            local_path=str(local_file),
                            file_size=local_size
                        )
                        matched_files.append((local_file, db_file))
                        logger.info(f"✅ To'g'ri fayl topildi: {local_filename}")
                break
    
    if matched_files:
        logger.info(f"📤 {len(matched_files)} ta fayl upload qilish uchun tayyorlandi")
    else:
        logger.info("📤 Upload qilish uchun tayyor fayllar yo'q")


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

    # ✅ Faqat yuklanmagan fayllarni olish
    items = db.get_undownloaded_files(CONFIG["name"])

    # Config'da sort_by_size parametrini tekshirish
    sort_by_size = CONFIG.get("sort_by_size", False)
    if sort_by_size:
        logger.info(f"📊 Yuklanmagan fayllar eng kichik hajmdan boshlab tartiblanadi")
        # Yuklanmagan fayllarni hajm bo'yicha tartiblash
        items = sorted(items, key=lambda x: x.get('file_size', 0) or 0)
    else:
        logger.info(f"📊 Yuklanmagan fayllar standart tartibda qayta ishlanadi")

    # print("items", items)
    if not items:
        logger.warning(f"❌ {CONFIG['name']} uchun DB da fayl yo'q.")
        return
    else:
        logger.info(f"📊 {len(items)} ta yuklanmagan fayl topildi {CONFIG['name']} uchun.")

    # ✅ Local downloads papkasidagi mavjud fayllarni tekshirish
    await check_and_queue_existing_files(db, CONFIG)

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
