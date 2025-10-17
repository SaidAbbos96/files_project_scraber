"""
Stream Uploader - Faylni disk ga saqlamasdan to'g'ridan-to'g'ri Telegram ga yuklash
"""
import asyncio
import aiohttp
import tempfile
import os
from pathlib import Path
from typing import Dict, Any, Optional
from tqdm import tqdm
from io import BytesIO

from core.config import FILES_GROUP_LINK
from telegramuploader.telegram.telegram_client import Telegram_client, resolve_group
from utils.logger_core import logger
from utils.helpers import categories_to_ids, make_caption
from utils.disk_monitor import get_disk_monitor
from telegramuploader.utils.diagnostics import diagnostics
import time


class StreamingUploader:
    """Faylni streaming orqali Telegram ga yuklash"""

    def __init__(self, default_group: str = FILES_GROUP_LINK, timeout: int = 7200):
        """
        Args:
            default_group: Default Telegram group (default: FILES_GROUP_LINK)
            timeout: Upload timeout (default: 2 hours)
        """
        self.default_group = default_group or FILES_GROUP_LINK
        self.timeout = timeout
        self.timeout = timeout
        self.temp_dir = Path(tempfile.gettempdir()) / "telegram_stream"
        self.temp_dir.mkdir(exist_ok=True)

    async def stream_and_upload(
        self,
        url: str,
        item: Dict[str, Any],
        config: Dict[str, Any],
        session: aiohttp.ClientSession,
        group_ref: Optional[str] = None
    ) -> bool:
        """
        Faylni stream qilib Telegram ga yuklash

        Args:
            url: Download URL
            item: Fayl ma'lumotlari
            config: Konfiguratsiya
            session: aiohttp session
            group_ref: Telegram group reference

        Returns:
            True if successful, False otherwise
        """
        filename = item.get("title", "unknown").replace(" ", "_") + ".mp4"
        temp_file = None
        start_time = time.time()

        try:
            # 1. Telegram entity olish
            entity = await self._get_telegram_entity(group_ref)
            if not entity:
                logger.error("❌ Guruh aniqlanmadi")
                return False

            logger.info(
                f"✅ Guruh aniqlandi: {getattr(entity, 'title', str(entity))}")

            # 2. Temporary file yaratish (streaming uchun)
            temp_file = self.temp_dir / f"stream_{int(time.time())}_{filename}"

            # 3. Download va parallel upload
            success = await self._download_and_upload_parallel(
                url=url,
                temp_file=temp_file,
                entity=entity,
                item=item,
                session=session
            )

            if success:
                duration = time.time() - start_time
                logger.info(
                    f"✅ Streaming upload muvaffaqiyatli: {filename} ({duration:.1f}s)")
                diagnostics.log_success(filename, duration)

                # Temporary faylni o'chirish
                if temp_file.exists():
                    temp_file.unlink()
                    logger.info(
                        f"🗑️ Temporary fayl o'chirildi: {temp_file.name}")

                return True
            else:
                duration = time.time() - start_time
                diagnostics.log_error(filename, item.get("file_size", 0),
                                      "Streaming upload failed", "", duration)
                return False

        except Exception as e:
            import traceback
            duration = time.time() - start_time
            error_msg = str(e)
            full_traceback = traceback.format_exc()

            logger.error(
                f"❌ Streaming upload xatosi: {filename} - {error_msg}")
            logger.error(f"🔍 Traceback:\n{full_traceback}")

            diagnostics.log_error(filename, item.get("file_size", 0),
                                  error_msg, full_traceback, duration)
            return False

        finally:
            # Cleanup - agar xato bo'lsa ham o'chirish
            if temp_file and temp_file.exists():
                try:
                    temp_file.unlink()
                    logger.info(f"🗑️ Cleanup: {temp_file.name} o'chirildi")
                except Exception as cleanup_error:
                    logger.warning(f"⚠️ Cleanup xatosi: {cleanup_error}")

    async def _download_and_upload_parallel(
        self,
        url: str,
        temp_file: Path,
        entity,
        item: Dict[str, Any],
        session: aiohttp.ClientSession
    ) -> bool:
        """
        Download va upload ni parallel bajarish

        Strategy:
        1. Faylni qismlar (chunks) orqali download qilish
        2. Har bir chunk ni temporary file ga yozish
        3. Download tugagach, darhol Telegram ga yuklash
        4. Upload muvaffaqiyatli bo'lsa, temp file ni o'chirish
        """
        try:
            logger.info(f"📥 Download boshlandi: {url}")

            # Download qilish
            async with session.get(url, timeout=aiohttp.ClientTimeout(total=600)) as response:
                if response.status != 200:
                    logger.error(f"❌ Download xatosi: HTTP {response.status}")
                    return False

                total_size = int(response.headers.get('content-length', 0))
                logger.info(f"💾 Fayl hajmi: {total_size / (1024**2):.2f} MB")

                # 🔍 Disk joy tekshiruvi (streaming uchun ham)
                disk_monitor = get_disk_monitor()
                if disk_monitor:
                    if not disk_monitor.has_enough_space(total_size):
                        logger.warning(
                            f"⏸️ DISK JOY KAM! Streaming download kutmoqda...")
                        logger.info(disk_monitor.get_status_message())

                        # Disk joy bo'lishini kutish
                        success = await disk_monitor.wait_for_space(total_size, max_wait_minutes=30)

                        if not success:
                            logger.error(
                                f"❌ Timeout: Disk joy yetarli emas, streaming bekor qilindi")
                            return False

                # Chunk orqali download va temp file ga yozish
                downloaded = 0
                chunk_size = 1024 * 1024  # 1MB chunks

                with open(temp_file, 'wb') as f:
                    with tqdm(total=total_size, unit='B', unit_scale=True, desc=f"📥 {temp_file.name}") as bar:
                        async for chunk in response.content.iter_chunked(chunk_size):
                            f.write(chunk)
                            downloaded += len(chunk)
                            bar.update(len(chunk))

                logger.info(
                    f"✅ Download tugadi: {downloaded / (1024**2):.2f} MB")

            # 2. Caption yaratish
            caption = await self._create_caption(item, total_size)

            # 3. Telegram ga yuklash
            logger.info(f"📤 Telegram upload boshlandi...")

            async with asyncio.timeout(self.timeout):
                with tqdm(total=total_size, unit="B", unit_scale=True, desc=f"📤 {temp_file.name}") as bar:

                    def progress(sent, total):
                        bar.n = sent
                        bar.total = total
                        bar.refresh()

                    await Telegram_client.send_file(
                        entity,
                        str(temp_file),
                        caption=caption,
                        parse_mode="html",
                        supports_streaming=True,
                        progress_callback=progress,
                    )

            logger.info(f"✅ Telegram upload tugadi")
            return True

        except asyncio.TimeoutError:
            logger.error(f"⏰ Timeout: {self.timeout//60} daqiqa")
            return False
        except Exception as e:
            logger.error(f"❌ Download/Upload xatosi: {e}")
            return False

    async def _get_telegram_entity(self, group_ref: Optional[str] = None):
        """Telegram entity olish"""
        if not Telegram_client.is_connected():
            logger.warning("⚠️ Telegram client ulanmagan, qayta ulanish...")
            await Telegram_client.connect()

        target_group = group_ref or self.default_group

        # Guruh bo'sh bo'lsa xato
        if not target_group or target_group.strip() == "":
            logger.error(
                "❌ Telegram guruh ID si berilmagan! Config da 'telegram_group' parametrini to'ldiring.")
            logger.error(
                f"💡 Yoki FILES_GROUP_LINK ishlatiladi: {FILES_GROUP_LINK}")
            target_group = FILES_GROUP_LINK

        logger.info(f"🔍 Guruhni aniqlash: {target_group}")

        entity = await resolve_group(target_group)
        return entity

    async def _create_caption(self, item: Dict[str, Any], size: int) -> str:
        """Caption yaratish"""
        logger.info("🔍 Caption yaratish boshlandi")
        logo = item.get("image", None)

        if (
            not logo
            or not isinstance(logo, str)
            or logo.strip() == ""
            or logo.startswith("data:image")
        ):
            logo = None

        try:
            # Categories ni to'g'ri formatda olish
            categories = item.get("categories", [])
            # Agar string bo'lsa, uni split qilamiz yoki list sifatida qoldiramiz
            if isinstance(categories, str):
                # Agar vergul bilan ajratilgan bo'lsa
                categories = [cat.strip()
                              for cat in categories.split(",") if cat.strip()]
            elif not isinstance(categories, list):
                categories = []

            caption_data = {
                "title": item.get("title", "No title"),
                "lang": item.get("language", "uz"),
                "category_id": ", ".join(
                    map(str, categories_to_ids(categories))
                ),
                "actors": item.get("actors") or "",
                "year": item.get("year") or "",
                "country": item.get("country") or "",
                "categories": ", ".join(categories),
                "file_size": size,  # ✅ Bytes formatda
                "url": item.get("file_url") or "",
                "desc": (item.get("description") or "")[:500],
            }

            if logo:
                caption_data["logo"] = logo

            caption = make_caption(caption_data)
            caption = caption[:4096]  # Telegram limit
            logger.info("✅ Caption yaratildi")
            return caption

        except Exception as caption_error:
            logger.error(f"❌ Caption yaratishda xato: {caption_error}")
            return f"📄 {item.get('title', 'No title')}\n💾 Hajmi: {size} bytes"


class OptimizedStreamUploader(StreamingUploader):
    """
    Optimallashtirilgan stream uploader

    Features:
    - Disk ga minimal yozish
    - Memory buffer orqali ishlash
    - Parallel download/upload chunks
    """

    async def stream_with_minimal_disk(
        self,
        url: str,
        item: Dict[str, Any],
        config: Dict[str, Any],
        session: aiohttp.ClientSession,
        group_ref: Optional[str] = None
    ) -> bool:
        """
        Minimal disk usage bilan stream qilish

        Strategiya:
        1. Kichik buffer yaratish
        2. Buffer to'lganda Telegram ga yuklash
        3. Buffer tozalash va davom etish
        """
        # TODO: Bu kelajakda implement qilamiz
        # Telegram API chunk upload ni support qilsa
        logger.warning("⚠️ Minimal disk mode hali implement qilinmagan")
        logger.info("💡 Standard streaming mode ishlatilmoqda...")

        return await self.stream_and_upload(url, item, config, session, group_ref)
