"""
Enhanced FileDownloader with Resume Support - Partial download qo'llab-quvvatlash
"""
import os
import asyncio
import aiohttp
from pathlib import Path
from typing import Optional, Dict, Any, Tuple
from tqdm.asyncio import tqdm

from utils.logger_core import logger
from utils.files import safe_filename
from utils.text import clean_title


class FileDownloaderResume:
    """Professional file downloader with resume support"""

    def __init__(self, base_timeout: int = None, chunk_size: int = 256 * 1024, max_retries: int = 3):
        """
        Args:
            base_timeout: Base timeout in seconds (None = unlimited)
            chunk_size: Download chunk size in bytes (default 256KB)
            max_retries: Maximum retry attempts (default 3)
        """
        self.base_timeout = base_timeout
        self.chunk_size = chunk_size
        self.max_retries = max_retries

    def calculate_timeout(self, file_size: int) -> int:
        """
        ⚡ TIMEOUT REMOVED - always returns None for unlimited download time

        Args:
            file_size: File size in bytes

        Returns:
            None (unlimited timeout)
        """
        # ⚡ Always return None - no timeout limits!
        logger.info(
            f"⚡ UNLIMITED download time for {file_size/1024/1024:.1f}MB file")
        return None

    async def check_resume_support(self, session: aiohttp.ClientSession, file_url: str) -> bool:
        """
        Server resume qo'llab-quvvatlaydimi tekshirish

        Args:
            session: aiohttp session
            file_url: File URL

        Returns:
            True if resume supported, False otherwise
        """
        try:
            timeout = aiohttp.ClientTimeout(total=30)
            headers = {"Range": "bytes=0-0"}  # Test range request
            async with session.get(file_url, headers=headers, timeout=timeout) as resp:
                # 206 Partial Content yoki Accept-Ranges header mavjudligi
                return resp.status == 206 or "bytes" in resp.headers.get("Accept-Ranges", "")
        except Exception as e:
            logger.warning(f"⚠️ Resume support check failed: {e}")
            return False

    async def get_file_info(self, session: aiohttp.ClientSession, file_url: str) -> Tuple[int, bool]:
        """
        File haqida ma'lumot olish (size va resume support)

        Args:
            session: aiohttp session
            file_url: File URL

        Returns:
            Tuple[file_size, resume_supported]
        """
        try:
            # Head request bilan file size olish
            timeout = aiohttp.ClientTimeout(total=30)
            async with session.head(file_url, timeout=timeout) as resp:
                if resp.status == 200:
                    file_size = int(resp.headers.get("Content-Length", 0))
                    resume_supported = "bytes" in resp.headers.get(
                        "Accept-Ranges", "")
                    return file_size, resume_supported
                return 0, False
        except Exception as e:
            logger.warning(f"⚠️ Get file info failed: {e}")
            return 0, False

    async def download_file_with_resume(self, session: aiohttp.ClientSession, semaphore: asyncio.Semaphore,
                                        file_url: str, output_path: str, filename: str) -> Optional[int]:
        """
        Bitta faylni download qilish with resume support

        Returns:
            File size in bytes if successful, None if failed
        """
        async with semaphore:
            for attempt in range(self.max_retries):
                try:
                    # File info olish
                    total_size, resume_supported = await self.get_file_info(session, file_url)

                    # Mavjud partial file tekshirish
                    start_byte = 0
                    if os.path.exists(output_path):
                        existing_size = os.path.getsize(output_path)

                        if existing_size >= total_size and total_size > 0:
                            logger.info(
                                f"✅ File already complete: {filename} ({existing_size} bytes)")
                            return existing_size

                        if resume_supported and existing_size > 0:
                            start_byte = existing_size
                            logger.info(
                                f"🔄 Resuming download from {start_byte} bytes: {filename}")
                        else:
                            # Resume qo'llab-quvvatlanmasa, qayta boshlash
                            if existing_size > 0:
                                logger.info(
                                    f"🗑️ Removing partial file (no resume support): {filename}")
                                os.remove(output_path)

                    # Timeout settings - unlimited
                    timeout = aiohttp.ClientTimeout(
                        total=None,          # Total timeout yo'q - cheksiz
                        connect=60,          # Connection timeout 1 minute
                        sock_read=None       # Socket read timeout yo'q - cheksiz
                    )

                    size_mb = total_size / (1024 * 1024) if total_size else 0

                    if attempt > 0:
                        logger.info(
                            f"🔄 Retry {attempt + 1}/{self.max_retries}: {filename}")

                    logger.info(
                        f"⬇️ Downloading: {filename} ({size_mb:.2f} MB)")
                    if start_byte > 0:
                        logger.info(
                            f"📍 Resume from: {start_byte/1024/1024:.2f} MB")
                    logger.info(
                        f"⚡ Timeout REMOVED - unlimited download time!")

                    # Headers setup
                    headers = {}
                    if start_byte > 0 and resume_supported:
                        headers["Range"] = f"bytes={start_byte}-"

                    async with session.get(file_url, headers=headers, timeout=timeout) as resp:
                        # Status code tekshirish
                        expected_status = 206 if start_byte > 0 else 200
                        if resp.status not in [200, 206]:
                            logger.error(f"❌ HTTP {resp.status}: {file_url}")
                            if attempt == self.max_retries - 1:
                                return None
                            continue

                        # Response'dan actual size
                        if resp.status == 206:
                            # Partial content - Content-Range header'dan size olish
                            content_range = resp.headers.get(
                                "Content-Range", "")
                            if content_range:
                                # Format: "bytes start-end/total"
                                total_from_range = content_range.split("/")[-1]
                                if total_from_range.isdigit():
                                    actual_total_size = int(total_from_range)
                                else:
                                    actual_total_size = total_size
                            else:
                                actual_total_size = total_size
                        else:
                            actual_total_size = int(resp.headers.get(
                                "Content-Length", total_size or 0))

                        # File mode - append agar resume, yoqsa yangi
                        file_mode = "ab" if start_byte > 0 else "wb"

                        # Faylni download qilish
                        with open(output_path, file_mode) as f:
                            # Progress bar setup
                            remaining_bytes = actual_total_size - start_byte
                            with tqdm(
                                total=remaining_bytes,
                                initial=0,
                                unit="B",
                                unit_scale=True,
                                desc=f"⬇️ {filename[:30]}"
                            ) as progress_bar:

                                downloaded = 0
                                async for chunk in resp.content.iter_chunked(self.chunk_size):
                                    f.write(chunk)
                                    downloaded += len(chunk)
                                    progress_bar.update(len(chunk))

                        # File size validation
                        actual_size = os.path.getsize(output_path)
                        # 1KB tolerance
                        if actual_total_size > 0 and abs(actual_size - actual_total_size) > 1024:
                            logger.warning(
                                f"⚠️ Size mismatch: expected {actual_total_size}, got {actual_size}")

                        logger.info(
                            f"✅ Downloaded: {filename} ({actual_size / (1024*1024):.2f} MB)")
                        return actual_size

                except Exception as e:
                    logger.error(
                        f"❌ Download error (attempt {attempt + 1}): {filename} | {e}")
                    if attempt == self.max_retries - 1:
                        logger.error(
                            f"❌ Final error after {self.max_retries} attempts: {filename}")
                        return None

                    # Partial file'ni saqlab qolish (resume uchun)
                    # Faqat kritik xatoliklarda o'chirish
                    if "Connection" in str(e) or "Timeout" in str(e):
                        logger.info(
                            f"💾 Keeping partial file for resume: {output_path}")
                    else:
                        # Boshqa xatoliklarda o'chirish
                        if os.path.exists(output_path):
                            os.remove(output_path)
                            logger.info(
                                f"🗑️ Removed corrupted partial file: {output_path}")

                    # Exponential backoff
                    wait_time = 2 ** attempt
                    logger.info(f"⏳ Waiting {wait_time}s before retry...")
                    await asyncio.sleep(wait_time)

            return None

    async def download_file_with_retry(self, session: aiohttp.ClientSession, semaphore: asyncio.Semaphore,
                                       file_url: str, output_path: str, filename: str) -> Optional[int]:
        """
        Backward compatibility wrapper - uses new resume logic
        """
        return await self.download_file_with_resume(session, semaphore, file_url, output_path, filename)

    async def download_file(self, session: aiohttp.ClientSession, semaphore: asyncio.Semaphore,
                            file_url: str, output_path: str, filename: str) -> Optional[int]:
        """
        Backward compatibility wrapper
        """
        return await self.download_file_with_resume(session, semaphore, file_url, output_path, filename)

    async def get_file_size(self, session: aiohttp.ClientSession, file_url: str) -> int:
        """
        URL dan fayl hajmini olish (HEAD request bilan)

        Args:
            session: aiohttp session
            file_url: File URL

        Returns:
            File size in bytes, 0 if failed
        """
        try:
            # Quick timeout for HEAD request
            timeout = aiohttp.ClientTimeout(total=30)
            async with session.head(file_url, timeout=timeout) as resp:
                if resp.status == 200:
                    return int(resp.headers.get("Content-Length", 0))
                return 0
        except Exception as e:
            logger.error(f"❌ Get file size error: {e}")
            return 0
