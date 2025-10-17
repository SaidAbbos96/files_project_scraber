"""
File Downloader - Fayllarni yuklab olish uchun
"""
import os
import asyncio
import aiohttp
from pathlib import Path
from tqdm.asyncio import tqdm
from typing import Optional

from utils.logger_core import logger


class FileDownloader:
    """Fayllarni yuklab olish uchun class"""

    def __init__(self, base_timeout: int = 7200, max_retries: int = 3):
        """
        Args:
            base_timeout: Base timeout in seconds (default: 2 hours)
            max_retries: Maximum retry attempts (default: 3)
        """
        self.base_timeout = base_timeout
        self.max_retries = max_retries

    def calculate_timeout(self, file_size: int) -> int:
        """
        Fayl hajmiga qarab intelligent timeout hisoblash
        
        Args:
            file_size: File size in bytes
            
        Returns:
            Timeout in seconds
        """
        if file_size <= 0:
            return self.base_timeout
        
        # Minimum 10 minutes, maximum 4 hours (telegram upload uchun uzunroq)
        min_timeout = 600   # 10 minutes
        max_timeout = 14400  # 4 hours
        
        # Assume 50KB/s minimum speed for telegram, add 50% buffer
        calculated_timeout = int((file_size / (50 * 1024)) * 1.5)
        
        # Apply bounds
        timeout = max(min_timeout, min(calculated_timeout, max_timeout))
        
        logger.info(f"🕐 Telegram timeout: {timeout}s ({timeout/60:.1f}min) for {file_size/1024/1024:.1f}MB")
        return timeout

    async def download(self, session: aiohttp.ClientSession, semaphore: asyncio.Semaphore,
                       file_url: str, output_path: str, filename: str) -> Optional[int]:
        """
        Faylni yuklab olish

        Args:
            session: aiohttp session
            semaphore: Concurrent downloads semaphore
            file_url: Yuklab olinadigan fayl URL
            output_path: Saqlanadigan fayl path
            filename: Fayl nomi (progress uchun)

        Returns:
            File size in bytes if successful, None if failed
        """
        async with semaphore:
            try:
                # Avval file size olish
                async with session.head(file_url) as head_resp:
                    file_size = int(head_resp.headers.get("Content-Length", 0))
                
                # Intelligent timeout hisoblash
                timeout_seconds = self.calculate_timeout(file_size)
                
                # ⏰ Intelligent timeout qo'shamiz
                async with asyncio.timeout(timeout_seconds):
                    async with session.get(file_url) as resp:
                        if resp.status != 200:
                            logger.error(f"❌ Yuklab bo'lmadi: {file_url}")
                            return None

                        total = int(resp.headers.get("Content-Length", file_size or 0))

                        # Real download boshlanganda log
                        # size_gb = total / (1024 ** 3) if total else 0
                        # logger.info(
                        #     f"🚀 Download boshlandi: {filename} ({size_gb:.2f} GB)")

                        with open(output_path, "wb") as f, tqdm(
                            total=total, unit="B", unit_scale=True, desc=f"⬇️ {filename}"
                        ) as bar:
                            async for chunk in resp.content.iter_chunked(1024 * 256):
                                f.write(chunk)
                                bar.update(len(chunk))
                            f.flush()
                            os.fsync(f.fileno())  # 🔑 diskka to'liq yozilsin

                    # Tekshiramiz: to'liq yuklandi (agar Content-Length bor bo'lsa)
                    if total and os.path.getsize(output_path) != total:
                        logger.error(f"❌ Fayl to'liq yuklanmadi: {filename}")
                        os.remove(output_path)
                        return None

                    return os.path.getsize(output_path)

            except asyncio.TimeoutError:
                logger.error(
                    f"⏰ Timeout: {filename} yuklab olish {timeout_seconds//60} daqiqadan oshdi")
                if os.path.exists(output_path):
                    os.remove(output_path)
                return None
            except Exception as e:
                logger.error(f"❌ Yuklab olishda xato: {e}")
                if os.path.exists(output_path):
                    os.remove(output_path)
                return None

    async def get_file_size(self, session: aiohttp.ClientSession, file_url: str) -> int:
        """
        URL dan fayl hajmini olish

        Args:
            session: aiohttp session
            file_url: Fayl URL

        Returns:
            File size in bytes, 0 if failed
        """
        try:
            # Avval HEAD so'rov bilan sinab ko'ramiz
            async with session.head(file_url) as resp:
                if resp.status == 200 and 'content-length' in resp.headers:
                    content_length = resp.headers.get("Content-Length", "0")
                    if content_length and content_length != "0":
                        return int(content_length)

            # HEAD ishlamasa, GET so'rov bilan range header ishlatamiz
            headers = {'Range': 'bytes=0-0'}
            async with session.get(file_url, headers=headers) as resp:
                if resp.status in [206, 200]:  # 206 = Partial Content, 200 = OK
                    # Content-Range headerdan to'liq hajmni olish
                    content_range = resp.headers.get('Content-Range')
                    if content_range:
                        # Format: "bytes 0-0/total_size"
                        if '/' in content_range:
                            total_size = content_range.split('/')[-1]
                            if total_size.isdigit():
                                return int(total_size)

                    # Content-Length headerdan olish
                    content_length = resp.headers.get("Content-Length", "0")
                    if content_length and content_length != "0":
                        return int(content_length)

            logger.warning(f"⚠️ Fayl hajmini aniqlab bo'lmadi: {file_url}")
            return 0

        except Exception as e:
            logger.error(f"❌ Fayl hajmini olishda xato: {e}")
            return 0

    def check_file_integrity(self, file_path: str, expected_size: int, tolerance_mb: int = 5) -> tuple[bool, str]:
        """
        Fayl butunligini tekshirish

        Args:
            file_path: Tekshiriladigan fayl path
            expected_size: Kutilayotgan hajm (bytes)
            tolerance_mb: Hajm farqi tolerance (MB)

        Returns:
            (is_valid, reason) tuple
        """
        if not os.path.exists(file_path):
            return False, "Fayl mavjud emas"

        local_size = os.path.getsize(file_path)

        if expected_size <= 0:
            return True, "Server hajmi noma'lum, mavjud faylni ishlatamiz"

        size_diff = abs(local_size - expected_size)
        tolerance_bytes = tolerance_mb * 1024 * 1024

        if size_diff <= tolerance_bytes:
            return True, f"Hajm mos keladi (farq: {size_diff/(1024**2):.1f}MB)"
        else:
            return False, f"Hajm farqi katta: {size_diff/(1024**2):.1f}MB"
