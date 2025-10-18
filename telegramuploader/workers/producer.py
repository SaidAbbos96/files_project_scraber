"""
File Producer - Fayllarni qayta ishlash va queue ga qo'yish uchun
"""
import os
import asyncio
import aiohttp
from pathlib import Path
from typing import Dict, Any

from utils.files import safe_filename
from utils.text import clean_title
from utils.logger_core import logger
from utils.disk_monitor import get_disk_monitor
from ..core.downloader import FileDownloader
from ..handlers.notification import NotificationHandler


class FileProducer:
    """Fayllarni yuklab olish va queue ga qo'yish uchun class"""

    def __init__(self, downloader: FileDownloader, notifier: NotificationHandler, orchestrator=None):
        self.downloader = downloader
        self.notifier = notifier
        self.orchestrator = orchestrator
        # Batch mode: individual notifications'ni kamaytirish
        self._quiet_mode = orchestrator is not None

    async def process_file(self, session: aiohttp.ClientSession, semaphore: asyncio.Semaphore,
                           queue: asyncio.Queue, row: Dict[str, Any], config: Dict[str, Any]) -> None:
        """
        Bitta faylni qayta ishlash va queue ga qo'yish - Main orchestrator method

        Args:
            session: aiohttp session
            semaphore: Concurrent operations semaphore  
            queue: Fayllar queue
            row: DB dan olingan fayl ma'lumotlari
            config: Konfiguratsiya
        """
        try:
            # 1. Dastlabki validatsiya
            file_info = self._extract_file_info(row)
            if not await self._validate_file_info(file_info):
                return

            # 2. Fayl yo'li va hajmini aniqlash
            file_path, url_size = await self._prepare_file_path(session, file_info, config)
            if not file_path:
                return

            # 3. Mavjud faylni tekshirish
            size, file_needs_download = await self._check_existing_file(file_path, url_size, file_info)

            # 4. Download qilish (agar kerak bo'lsa)
            if file_needs_download:
                size = await self._download_file(session, semaphore, file_info, file_path, url_size, config)
                if not size:
                    return

            # 5. Upload yoki cleanup
            await self._handle_post_download(queue, file_info, file_path, size, config)

        except Exception as e:
            logger.error(
                f"❌ Producer da xato: {file_info.get('title', 'Unknown')} - {e}")

    def _extract_file_info(self, row: Dict[str, Any]) -> Dict[str, Any]:
        """DB row'dan fayl ma'lumotlarini ajratib olish"""
        return {
            "id": row["id"],
            "file_url": row.get("file_url"),
            "title": row.get("title"),
            "uploaded": row.get("uploaded", False)
        }

    async def _validate_file_info(self, file_info: Dict[str, Any]) -> bool:
        """Fayl ma'lumotlarini validatsiya qilish"""
        # Upload qilingan faylni tashlab ketish
        if file_info["uploaded"]:
            logger.info(
                f"⏭️ Fayl avval upload qilingan, o'tkazib yuborildi: {file_info['title']}")
            if not self._quiet_mode:
                await self.notifier.send_already_uploaded(file_info["title"], file_info["id"])
            if self.orchestrator:
                # filename ni keyinroq olish kerak, hozircha title ishlatamiz
                await self.orchestrator.update_progress(True, True, file_info["title"])
            return False

        # URL validatsiyasi
        if not file_info["file_url"] or "https://t.me/" in file_info["file_url"]:
            logger.warning(f"❌ file_url yo'q: {file_info['title']}")
            return False

        return True

    async def _prepare_file_path(self, session: aiohttp.ClientSession, file_info: Dict[str, Any],
                                 config: Dict[str, Any]) -> tuple[str, int]:
        """Fayl yo'li va server hajmini tayyorlash - parallel safe"""
        ext = Path(file_info["file_url"]).suffix or ".mp4"
        base_filename = safe_filename(clean_title(
            file_info["title"] or "untitled"), "")
        
        # Parallel conflict oldini olish uchun file ID qo'shish
        filename = f"{base_filename}_{file_info['id']}{ext}"
        output_path = os.path.join(config["download_dir"], filename)

        # URL dan file size olish
        url_size = await self.downloader.get_file_size(session, file_info["file_url"])

        return output_path, url_size

    async def _check_existing_file(self, file_path: str, url_size: int, file_info: Dict[str, Any]) -> tuple[int, bool]:
        """Mavjud faylni tekshirish va qaror qabul qilish"""
        if not os.path.exists(file_path):
            return None, True  # Fayl yo'q, download kerak

        is_valid, reason = self.downloader.check_file_integrity(
            file_path, url_size)
        filename = os.path.basename(file_path)

        if is_valid:
            # Mavjud faylni ishlatish
            size = os.path.getsize(file_path)
            logger.info(f"♻️ Fayl mavjud va to'liq: {filename}")

            if not self._quiet_mode:
                await self.notifier.send_file_exists(
                    file_info["title"], file_info["id"], filename, size /
                    (1024**3)
                )
            return size, False
        else:
            # Faylni qayta yuklash
            await self._handle_invalid_file(file_path, reason, file_info, url_size)
            return None, True

    async def _handle_invalid_file(self, file_path: str, reason: str, file_info: Dict[str, Any], url_size: int):
        """Noto'g'ri faylni qayta ishlash"""
        filename = os.path.basename(file_path)
        local_gb = os.path.getsize(file_path) / (1024 ** 3)
        size_gb = url_size / (1024 ** 3) if url_size else 0

        logger.warning(f"⚠️ {reason}: {filename}. Qayta yuklanadi.")
        logger.warning(f"   Local: {local_gb:.2f}GB, Server: {size_gb:.2f}GB")
        logger.info(
            f"🔄 [{file_info['id']}] Fayl tekshirildi - noto'g'ri, o'chiriladi va qayta yuklanadi")

        await self.notifier.send_file_redownload(
            file_info["title"], file_info["id"], filename, reason, local_gb, size_gb
        )

        # Noto'g'ri faylni o'chirish
        try:
            os.remove(file_path)
            logger.info(
                f"🗑️ [{file_info['id']}] Noto'g'ri fayl o'chirildi: {filename}")
        except Exception as e:
            logger.error(f"❌ [{file_info['id']}] Faylni o'chirishda xato: {e}")

    async def _download_file(self, session: aiohttp.ClientSession, semaphore: asyncio.Semaphore,
                             file_info: Dict[str, Any], file_path: str, url_size: int,
                             config: Dict[str, Any]) -> int:
        """Faylni yuklab olish"""
        filename = os.path.basename(file_path)
        size_gb = url_size / (1024 ** 3) if url_size else 0

        # 🔍 Disk joy tekshiruvi - faqat yangi download uchun
        disk_monitor = get_disk_monitor()
        should_download = True
        
        if disk_monitor and config.get("disk_monitor_enabled", True):
            # Fayl hajmi + minimal joy kerak
            if not disk_monitor.has_enough_space(url_size):
                logger.warning(f"⏸️ [{file_info['id']}] DISK JOY KAM! Yangi download skip qilinadi...")
                logger.info(disk_monitor.get_status_message())
                
                # Eski fayllarni tozalash (agar yoqilgan bo'lsa)
                if config.get("cleanup_old_files", True):
                    cleaned = await disk_monitor.cleanup_old_files(
                        max_age_hours=config.get("file_max_age_hours", 1)  # 1 soat eski fayllar
                    )
                    if cleaned > 0:
                        logger.info(f"🧹 {cleaned} ta eski fayl tozalandi")
                
                # Download qilmaslik
                should_download = False
                logger.info(f"⏭️ [{file_info['id']}] Download skip qilindi, mavjud fayllar telegram upload davom etadi")
                
                if not self._quiet_mode:
                    await self.notifier.send_message(
                        f"⏸️ DISK SPACE KAM: Download skip\n"
                        f"📄 {file_info['title']}\n"
                        f"💾 Kerak: {size_gb:.2f} GB\n"
                        f"📤 Mavjud fayllar upload davom etadi"
                    )

        # Download jarayoni - faqat disk space yetarli bo'lsa
        if should_download:
            # logger.info(f"📥 [{file_info['id']}] Download boshlandi: {filename}")

            # Notification yuborish
            if not self._quiet_mode:
                await self.notifier.send_file_start(file_info["title"], file_info["id"], filename, size_gb)

            size = await self.downloader.download(session, semaphore, file_info["file_url"], file_path, filename)
            logger.info(
                f"📥 [{file_info['id']}] Download tugadi: {filename} - size: {size}")

            if not size:
                logger.error(
                    f"❌ [{file_info['id']}] Yuklash muvaffaqiyatsiz: {filename}")
                if not self._quiet_mode:
                    await self.notifier.send_file_failed(file_info["title"], file_info["id"], filename)
                return None

            # Yuklangan fayl hajmini tekshirish
            return self._verify_downloaded_file(file_path, size)
        else:
            # Download skip - mavjud fayl bormi tekshiramiz
            if os.path.exists(file_path):
                size = os.path.getsize(file_path)
                logger.info(f"📁 [{file_info['id']}] Mavjud fayl topildi: {filename} - size: {size}")
                return self._verify_downloaded_file(file_path, size)
            else:
                logger.info(f"⏭️ [{file_info['id']}] Fayl yo'q, skip qilindi: {filename}")
                return None

    def _verify_downloaded_file(self, file_path: str, size: int) -> int:
        """Yuklangan faylni tekshirish"""
        if os.path.exists(file_path):
            actual_size = os.path.getsize(file_path)
            if actual_size > 0:
                size = actual_size
                logger.info(
                    f"✅ Yuklangan fayl hajmi: {size / (1024**3):.2f} GB")
        return size

    async def _handle_post_download(self, queue: asyncio.Queue, file_info: Dict[str, Any],
                                    file_path: str, size: int, config: Dict[str, Any]):
        """Download'dan keyingi amallar - upload yoki cleanup"""
        filename = os.path.basename(file_path)
        upload_workers = config.get(
            "upload_workers", config.get("upload_concurrency", 1))

        if upload_workers > 0:
            # Upload queue'ga qo'yish
            await self._add_to_upload_queue(queue, file_info, file_path, filename, size)
        else:
            # Faqat download mode - cleanup
            await self._handle_download_only_mode(file_path, filename, size, config)

    async def _add_to_upload_queue(self, queue: asyncio.Queue, file_info: Dict[str, Any],
                                   file_path: str, filename: str, size: int):
        """Faylni upload queue'ga qo'shish"""
        logger.info(f"📤 Queue ga qo'shildi: {filename}")

        if not self._quiet_mode:
            await self.notifier.send_file_completed(
                file_info["title"], file_info["id"], filename, size /
                (1024 * 1024)
            )

        await queue.put({
            "id": file_info["id"],
            "local_path": file_path,
            "filename": filename,
            "title": file_info["title"],
            "size": size,
        })

    async def _handle_download_only_mode(self, file_path: str, filename: str, size: int, config: Dict[str, Any]):
        """Faqat download mode - Telegramga yuborilmaydi"""
        logger.info(
            f"✅ Download tugadi: {filename} ({size / (1024**3):.2f} GB) - Upload o'chirilgan")

        # Clear files agar kerak bo'lsa
        if config.get("clear_uploaded_files", False):
            try:
                os.remove(file_path)
                logger.info(f"🗑️ Fayl o'chirildi: {filename}")
            except Exception as e:
                logger.error(f"❌ Faylni o'chirishda xato: {e}")
