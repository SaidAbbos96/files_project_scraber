"""
Streaming Producer - Fayllarni stream orqali Telegram ga yuklash
"""
import asyncio
import aiohttp
from typing import Dict, Any

from utils.logger_core import logger
from ..core.stream_uploader import StreamingUploader
from ..handlers.notification import NotificationHandler
from core.FileDB import FileDB


class StreamingProducer:
    """Stream orqali download va upload qilish uchun class"""
    
    def __init__(self, stream_uploader: StreamingUploader, notifier: NotificationHandler, 
                 orchestrator=None):
        self.stream_uploader = stream_uploader
        self.notifier = notifier
        self.orchestrator = orchestrator
        self._quiet_mode = orchestrator is not None
        
    async def process_file_streaming(
        self,
        session: aiohttp.ClientSession,
        semaphore: asyncio.Semaphore,
        row: Dict[str, Any],
        config: Dict[str, Any],
        db: FileDB
    ) -> bool:
        """
        Faylni stream orqali qayta ishlash - disk ga saqlamasdan
        
        Args:
            session: aiohttp session
            semaphore: Concurrency control
            row: DB qatoridan olingan fayl ma'lumotlari
            config: Konfiguratsiya
            db: Database connection
            
        Returns:
            True if successful, False otherwise
        """
        file_info = {
            "id": row["id"],
            "file_url": row.get("file_url"),
            "title": row.get("title"),
            "file_size": row.get("file_size", 0),
            "uploaded": row.get("uploaded", False),
            "image": row.get("image"),
            "language": row.get("language"),
            "categories": row.get("categories", []),
            "actors": row.get("actors"),
            "year": row.get("year"),
            "country": row.get("country"),
            "description": row.get("description"),
        }
        
        try:
            # 1. Validatsiya
            if file_info["uploaded"]:
                logger.info(f"⏭️ Allaqachon yuklangan: {file_info['title']}")
                if self.orchestrator:
                    await self.orchestrator.update_progress(True, True, file_info["title"])
                return True
            
            if not file_info["file_url"] or "https://t.me/" in file_info["file_url"]:
                logger.warning(f"❌ URL yo'q yoki noto'g'ri: {file_info['title']}")
                if self.orchestrator:
                    await self.orchestrator.update_progress(True, False, file_info["title"])
                return False
            
            # 2. Notification - download boshlandi
            if not self._quiet_mode:
                await self.notifier.send_download_started(
                    file_info["title"], 
                    file_info["file_size"],
                    file_info["id"]
                )
            
            logger.info(f"🚀 Streaming boshlandi: {file_info['title']}")
            
            # 3. Stream orqali download va upload
            async with semaphore:
                # group_ref ni olish - bo'sh bo'lsa None
                group_ref = config.get("telegram_group")
                if group_ref and group_ref.strip() == "":
                    group_ref = None  # Bo'sh string o'rniga None
                
                success = await self.stream_uploader.stream_and_upload(
                    url=file_info["file_url"],
                    item=file_info,
                    config=config,
                    session=session,
                    group_ref=group_ref
                )
            
            # 4. Natijani qayd qilish
            if success:
                logger.info(f"✅ Streaming muvaffaqiyatli: {file_info['title']}")
                
                # DB ni yangilash
                db.mark_file_uploaded(file_info["id"])
                
                # Notification - upload tugadi
                if not self._quiet_mode:
                    await self.notifier.send_upload_complete(
                        file_info["title"],
                        file_info["file_size"],
                        file_info["id"]
                    )
                
                # Progress yangilash
                if self.orchestrator:
                    await self.orchestrator.update_progress(True, True, file_info["title"])
                
                return True
            else:
                logger.error(f"❌ Streaming muvaffaqiyatsiz: {file_info['title']}")
                
                # Notification - xato
                if not self._quiet_mode:
                    await self.notifier.send_upload_failed(
                        file_info["title"],
                        file_info["id"],
                        "Streaming failed"
                    )
                
                # Progress yangilash
                if self.orchestrator:
                    await self.orchestrator.update_progress(True, False, file_info["title"])
                
                return False
                
        except Exception as e:
            import traceback
            logger.error(f"❌ Streaming xatosi: {file_info['title']} - {e}")
            logger.error(f"🔍 Traceback:\n{traceback.format_exc()}")
            
            # Error notification
            if not self._quiet_mode:
                await self.notifier.send_upload_failed(
                    file_info["title"],
                    file_info["id"],
                    str(e)
                )
            
            # Progress yangilash
            if self.orchestrator:
                await self.orchestrator.update_progress(True, False, file_info["title"])
            
            return False
