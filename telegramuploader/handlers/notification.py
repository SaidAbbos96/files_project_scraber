"""
Notification Handler - Telegram xabarlarni yuborish uchun
"""
from core.config import FILES_GROUP_LINK
from utils.logger_core import logger
from telegramuploader.telegram.telegram_client import Telegram_client, resolve_group, api_id, api_hash
from telethon import TelegramClient
import asyncio
import time
from typing import Optional
from datetime import datetime

import sys
import os
# Add the parent directory to sys.path to import telegram module
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(os.path.dirname(current_dir))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)


class NotificationHandler:
    """Telegram notification'larni boshqarish uchun class"""

    def __init__(self, default_group: str = FILES_GROUP_LINK):
        self.default_group = default_group
        self.last_request_time = 0
        self.min_interval = 1.0  # Minimum 1 second between requests
        self.rate_limited_until = 0  # Rate limit timer
        self._semaphore = asyncio.Semaphore(1)  # Only one request at a time

    async def send_safe(self, message: str, group_ref: Optional[str] = None) -> bool:
        """Safe notification - xatolik bo'lsa ham jarayonni to'xtatmaydi"""
        try:
            return await self.send_message(message, group_ref)
        except Exception as e:
            logger.warning(f"⚠️ Notification yuborishda xato (ignore): {e}")
            return False

    async def _enforce_rate_limit(self):
        """Rate limiting'ni kuzatish"""
        current_time = time.time()

        # Agar rate limit qo'yilgan bo'lsa, kutish
        if current_time < self.rate_limited_until:
            wait_time = self.rate_limited_until - current_time
            logger.warning(f"⏰ Rate limit: {wait_time:.1f} soniya kutish...")
            await asyncio.sleep(wait_time)

        # Minimum interval'ni kuzatish
        time_since_last = current_time - self.last_request_time
        if time_since_last < self.min_interval:
            wait_time = self.min_interval - time_since_last
            await asyncio.sleep(wait_time)

        self.last_request_time = time.time()

    async def _handle_rate_limit_error(self, error_message: str):
        """Rate limit xatoligini qayta ishlash"""
        # "A wait of X seconds is required" xabaridan soniyalarni ajratib olish
        import re
        match = re.search(r'(\d+) seconds is required', str(error_message))
        if match:
            wait_seconds = int(match.group(1))
            logger.warning(
                f"⏰ Telegram API rate limit: {wait_seconds} soniya kutish kerak")
            self.rate_limited_until = time.time() + wait_seconds + 5  # 5 soniya qo'shimcha
            await asyncio.sleep(wait_seconds + 5)

    async def send_message(self, message: str, group_link: Optional[str] = None) -> bool:
        """Xabar yuborish with rate limiting"""
        async with self._semaphore:
            max_retries = 3
            retry_count = 0

            while retry_count < max_retries:
                try:
                    await self._enforce_rate_limit()

                    target_group = group_link or self.default_group

                    # Use existing client instead of creating new one
                    client = Telegram_client
                    if not client.is_connected():
                        await client.connect()

                    # Connect etilganmi tekshirish
                    if not await client.is_user_authorized():
                        logger.error("❌ Telegram client authorized emas")
                        return False
                    # Gruppaning entity'sini olish
                    entity = await client.get_entity(target_group)

                    # Xabar yuborish
                    await client.send_message(entity, message, parse_mode="HTML")
                    return True

                except Exception as e:
                    error_str = str(e)
                    if "wait of" in error_str and "seconds is required" in error_str:
                        await self._handle_rate_limit_error(error_str)
                        retry_count += 1
                        continue
                    else:
                        logger.error(f"❌ Xabar yuborishda xatolik: {e}")
                        return False

            logger.error(
                f"❌ {max_retries} urinishdan so'ng xabar yuborib bo'lmadi")
            return False

    async def send_file_start(self, title: str, file_id: int, filename: str, size_gb: float) -> bool:
        """Fayl yuklash boshlangani haqida xabar"""
        # Agar hajmi juda kichik bo'lsa, noma'lum deb ko'rsatamiz
        if size_gb < 0.01:  # 10MB dan kichik
            size_text = "❓ Noma'lum"
        else:
            size_text = f"{size_gb:.2f} GB"

        message = (
            f"🚀 <b>Fayl yuklash boshlandi</b>\n"
            f"📄 <b>Nom:</b> {title}\n"
            f"🆔 <b>ID:</b> {file_id}\n"
            f"📁 <b>Fayl:</b> {filename}\n"
            f"💾 <b>Hajmi:</b> {size_text}"
        )
        return await self.send_safe(message)

    async def send_file_completed(self, title: str, file_id: int, filename: str, size_mb: float) -> bool:
        """Fayl yuklash tugagani haqida xabar"""
        message = (
            f"✅ <b>Fayl muvaffaqiyatli yuklandi</b>\n"
            f"📄 <b>Nom:</b> {title}\n"
            f"🆔 <b>ID:</b> {file_id}\n"
            f"📁 <b>Fayl:</b> {filename}\n"
            f"💾 <b>Hajmi:</b> {size_mb:.2f} MB\n"
            f"📤 <b>Telegram'ga yuklash boshlanyapti...</b>"
        )
        return await self.send_safe(message)

    async def send_file_failed(self, title: str, file_id: int, filename: str) -> bool:
        """Fayl yuklash muvaffaqiyatsiz bo'lgani haqida xabar"""
        message = (
            f"❌ <b>Fayl yuklash muvaffaqiyatsiz</b>\n"
            f"📄 <b>Nom:</b> {title}\n"
            f"🆔 <b>ID:</b> {file_id}\n"
            f"📁 <b>Fayl:</b> {filename}"
        )
        return await self.send_safe(message)

    async def send_upload_success(self, title: str, file_id: int, filename: str, size_mb: float) -> bool:
        """Telegram'ga yuklash muvaffaqiyatli bo'lgani haqida xabar"""
        message = (
            f"🎉 <b>Fayl muvaffaqiyatli yuborildi!</b>\n"
            f"📄 <b>Nom:</b> {title}\n"
            f"🆔 <b>ID:</b> {file_id}\n"
            f"📁 <b>Fayl:</b> {filename}\n"
            f"💾 <b>Hajmi:</b> {size_mb:.2f} MB\n"
            f"✅ <b>Telegram'ga muvaffaqiyatli yuklandi</b>"
        )
        return await self.send_safe(message)

    async def send_upload_failed(self, title: str, file_id: int, filename: str, size_mb: float) -> bool:
        """Telegram'ga yuklash muvaffaqiyatsiz bo'lgani haqida xabar"""
        message = (
            f"❌ <b>Telegram'ga yuklash muvaffaqiyatsiz!</b>\n"
            f"📄 <b>Nom:</b> {title}\n"
            f"🆔 <b>ID:</b> {file_id}\n"
            f"📁 <b>Fayl:</b> {filename}\n"
            f"💾 <b>Hajmi:</b> {size_mb:.2f} MB\n"
            f"⚠️ <b>Iltimos, loglarni tekshiring</b>"
        )
        return await self.send_safe(message)

    async def send_file_exists(self, title: str, file_id: int, filename: str, size_gb: float) -> bool:
        """Mavjud fayl ishlatilayotgani haqida xabar"""
        message = (
            f"♻️ <b>Mavjud fayl ishlatiladi</b>\n"
            f"📄 <b>Nom:</b> {title}\n"
            f"🆔 <b>ID:</b> {file_id}\n"
            f"📁 <b>Fayl:</b> {filename}\n"
            f"💾 <b>Hajmi:</b> {size_gb:.2f} GB\n"
            f"⚡ <b>Qayta yuklash shart emas</b>"
        )
        return await self.send_safe(message)

    async def send_file_redownload(self, title: str, file_id: int, filename: str, reason: str, local_gb: float, server_gb: float) -> bool:
        """Fayl qayta yuklanayotgani haqida xabar"""
        message = (
            f"🔄 <b>Fayl qayta yuklanadi</b>\n"
            f"📄 <b>Nom:</b> {title}\n"
            f"🆔 <b>ID:</b> {file_id}\n"
            f"📁 <b>Fayl:</b> {filename}\n"
            f"⚠️ <b>Sabab:</b> {reason}\n"
            f"📊 Local: {local_gb:.2f}GB, Server: {server_gb:.2f}GB"
        )
        return await self.send_safe(message)

    async def send_already_uploaded(self, title: str, file_id: int) -> bool:
        """Fayl avval yuklangan bo'lgani haqida xabar"""
        message = (
            f"⏭️ <b>Fayl avval yuklangan</b>\n"
            f"📄 <b>Nom:</b> {title}\n"
            f"🆔 <b>ID:</b> {file_id}\n"
            f"✅ <b>Qayta yuklash shart emas</b>"
        )
        return await self.send_safe(message)

    async def notify_batch_progress(self, completed: int, total: int, current_file: str, group_link: Optional[str] = None) -> bool:
        """Batch progress xabari - faqat muhim milestone'larda"""
        # Faqat 25%, 50%, 75% va 100%'da xabar yuborish
        progress_percent = (completed / total * 100) if total > 0 else 0

        if not self._should_send_progress_notification(progress_percent):
            return True  # Skip notification but return success

        message = (
            f"⏳ **PROGRESS UPDATE**\n\n"
            f"📊 **Holat:** {completed}/{total} ({progress_percent:.1f}%)\n"
            f"🔄 **Joriy fayl:** `{current_file}`\n"
            f"🕐 **Vaqt:** {datetime.now().strftime('%H:%M:%S')}"
        )
        return await self.send_message(message, group_link)

    def _should_send_progress_notification(self, progress_percent: float) -> bool:
        """Progress notification yuborish kerakmi?"""
        milestones = [25, 50, 75, 100]
        return any(abs(progress_percent - milestone) < 1 for milestone in milestones)

    async def notify_batch_complete(self, total_files: int, successful: int, failed: int, group_link: Optional[str] = None) -> bool:
        """Batch yakunlanishi haqida xabar"""
        success_rate = (successful / total_files *
                        100) if total_files > 0 else 0
        message = (
            f"📊 **BATCH YAKUNLANDI**\n\n"
            f"📁 **Jami fayllar:** {total_files}\n"
            f"✅ **Muvaffaqiyatli:** {successful}\n"
            f"❌ **Xatolik:** {failed}\n"
            f"📈 **Muvaffaqiyat:** {success_rate:.1f}%\n"
            f"🕐 **Vaqt:** {datetime.now().strftime('%H:%M:%S')}"
        )
        return await self.send_message(message, group_link)
