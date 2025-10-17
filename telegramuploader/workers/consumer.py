"""
File Consumer - Queue dan fayllarni olib Telegramga yuborish uchun
"""
import asyncio
from typing import Dict, Any

from core.FileDB import FileDB
from utils.telegram import detect_telegram_type
from utils.logger_core import logger
from ..core.uploader import TelegramUploader
from ..handlers.notification import NotificationHandler


def handle_post_upload(file_id: int, local_path: str, size: int, config: Dict[str, Any],
                       db: FileDB, success: bool, filename: str) -> None:
    """Fayl yuborilgandan keyingi amallarni bajarish"""
    if success:
        db.update_file(
            file_id,
            uploaded=True,
            local_path=local_path,
            file_size=size,
            mime="video/mp4",
            telegram_type=detect_telegram_type("video/mp4"),
        )
        if config.get("clear_uploaded_files", False):
            try:
                import os
                os.remove(local_path)
                logger.info(f"🗑️ Fayl o'chirildi: {local_path}")
                db.update_file(file_id, local_path=None)
            except Exception as e:
                logger.error(f"❌ O'chirishda xato: {e}")
    else:
        logger.error(f"❌ Telegramga yuborishda xato: {filename}")


class FileConsumer:
    """Queue dan fayllarni olib Telegramga yuborish uchun class"""

    def __init__(self, uploader: TelegramUploader, notifier: NotificationHandler, orchestrator=None):
        self.uploader = uploader
        self.notifier = notifier
        self.orchestrator = orchestrator
        # Batch mode: individual notifications'ni kamaytirish
        self._quiet_mode = orchestrator is not None

    async def consume_queue(self, queue: asyncio.Queue, config: Dict[str, Any], db: FileDB) -> None:
        """Queue dan fayllarni qayta ishlash (parallel mode uchun)"""
        while True:
            try:
                item = await queue.get()
            except asyncio.CancelledError:
                break

            await self._process_item(item, config, db)
            queue.task_done()

    async def process_single_item(self, item: Dict[str, Any], config: Dict[str, Any], db: FileDB) -> None:
        """Bitta itemni qayta ishlash (sequential mode uchun)"""
        await self._process_item(item, config, db)

    async def _process_item(self, item: Dict[str, Any], config: Dict[str, Any], db: FileDB) -> None:
        """Bitta itemni qayta ishlash (ichki funksiya)"""
        file_id = item["id"]
        local_path = item["local_path"]
        filename = item["filename"]
        title = item["title"]
        size = item["size"]

        # 🔑 To'liq ma'lumotlarni DB dan olish
        row = db.get_file(file_id)
        if not row:
            logger.error(f"❌ DB dan topilmadi: {file_id}")
            return

        # ✅ Agar fayl avval upload qilingan bo'lsa, tashlab ketamiz
        if row.get("uploaded", False):
            logger.info(
                f"⏭️ Fayl avval upload qilingan, o'tkazib yuborildi: {title}")
            # Avval yuklangan haqida notification spam bo'lmasligi uchun yubormaymiz
            if not self._quiet_mode:
                await self.notifier.send_already_uploaded(title, file_id)
            return

        logger.info(f"➡️ Yuborilmoqda: {title}")

        # ✅ Row ga local_path qo'shamiz (queue dan kelgan)
        row_with_path = dict(row) if row else {}
        row_with_path["local_path"] = local_path
        row_with_path["file_size"] = size

        # Upload qilish
        success = await self.uploader.upload_file(row_with_path, config)

        # Natija haqida xabar (faqat muhim paytlarda)
        size_mb = size / (1024 * 1024) if size else 0
        if success:
            logger.info(
                f"✅ Muvaffaqiyatli yuborildi: {filename} ({size_mb:.2f} MB)")
            if not self._quiet_mode:
                await self.notifier.send_upload_success(title, file_id, filename, size_mb)
        else:
            logger.error(f"❌ Yuborishda xatolik: {filename}")
            if not self._quiet_mode:
                await self.notifier.send_upload_failed(title, file_id, filename, size_mb)

        # Post-upload actions
        handle_post_upload(file_id, local_path, size,
                           config, db, success, filename)
