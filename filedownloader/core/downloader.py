"""
Core FileDownloader - Enhanced with intelligent timeout and retry
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


class FileDownloader:
    """Professional file downloader with intelligent timeout and retry"""
    
    def __init__(self, base_timeout: int = 1800, chunk_size: int = 256 * 1024, max_retries: int = 3):
        """
        Args:
            base_timeout: Base timeout in seconds (default 30 minutes)
            chunk_size: Download chunk size in bytes (default 256KB)
            max_retries: Maximum retry attempts (default 3)
        """
        self.base_timeout = base_timeout
        self.chunk_size = chunk_size
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
        
        # Minimum 5 minutes, maximum 2 hours
        min_timeout = 300   # 5 minutes
        max_timeout = 7200  # 2 hours
        
        # Assume 100KB/s minimum speed, add 50% buffer
        calculated_timeout = int((file_size / (100 * 1024)) * 1.5)
        
        # Apply bounds
        timeout = max(min_timeout, min(calculated_timeout, max_timeout))
        
        logger.info(f"🕐 Calculated timeout: {timeout}s for {file_size/1024/1024:.1f}MB file")
        return timeout

    async def download_file_with_retry(self, session: aiohttp.ClientSession, semaphore: asyncio.Semaphore,
                           file_url: str, output_path: str, filename: str) -> Optional[int]:
        """
        Bitta faylni download qilish with retry and intelligent timeout
        
        Returns:
            File size in bytes if successful, None if failed
        """
        async with semaphore:
            for attempt in range(self.max_retries):
                try:
                    # Avval HEAD request bilan file size olish
                    file_size = await self.get_file_size(session, file_url)
                    
                    # Intelligent timeout calculation
                    timeout_seconds = self.calculate_timeout(file_size)
                    
                    # sock_read timeout ham intelligent bo'lishi kerak
                    sock_read_timeout = min(timeout_seconds // 4, 1800)  # 1/4 yoki max 30 min
                    
                    timeout = aiohttp.ClientTimeout(
                        total=timeout_seconds,
                        connect=60,  # Connection timeout 1 minute
                        sock_read=sock_read_timeout  # Dynamic socket read timeout
                    )
                    
                    size_mb = file_size / (1024 * 1024) if file_size else 0
                    
                    if attempt > 0:
                        logger.info(f"🔄 Retry {attempt + 1}/{self.max_retries}: {filename}")
                    
                    logger.info(f"⬇️ Downloading: {filename} ({size_mb:.2f} MB)")
                    logger.info(f"⏱️ Timeouts: Total={timeout_seconds}s, SockRead={sock_read_timeout}s")
                    
                    async with session.get(file_url, timeout=timeout) as resp:
                        if resp.status != 200:
                            logger.error(f"❌ HTTP {resp.status}: {file_url}")
                            if attempt == self.max_retries - 1:
                                return None
                            continue
                        
                        # Response'dan actual size
                        actual_total_size = int(resp.headers.get("Content-Length", file_size or 0))
                        
                        # Faylni download qilish
                        with open(output_path, "wb") as f:
                            with tqdm(
                                total=actual_total_size,
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
                        if actual_total_size > 0 and abs(actual_size - actual_total_size) > 1024:  # 1KB tolerance
                            logger.warning(f"⚠️ Size mismatch: expected {actual_total_size}, got {actual_size}")
                        
                        logger.info(f"✅ Downloaded: {filename} ({actual_size / (1024*1024):.2f} MB)")
                        return actual_size
                        
                except asyncio.TimeoutError:
                    logger.error(f"⏰ Download timeout (attempt {attempt + 1}): {filename}")
                    if attempt == self.max_retries - 1:
                        logger.error(f"❌ Final timeout after {self.max_retries} attempts: {filename}")
                        return None
                    
                    # Cleanup partial file
                    if os.path.exists(output_path):
                        os.remove(output_path)
                    
                    # Exponential backoff
                    wait_time = 2 ** attempt
                    logger.info(f"⏳ Waiting {wait_time}s before retry...")
                    await asyncio.sleep(wait_time)
                    
                except Exception as e:
                    logger.error(f"❌ Download error (attempt {attempt + 1}): {filename} | {e}")
                    if attempt == self.max_retries - 1:
                        logger.error(f"❌ Final error after {self.max_retries} attempts: {filename}")
                        return None
                    
                    # Cleanup partial file
                    if os.path.exists(output_path):
                        os.remove(output_path)
                    
                    # Exponential backoff
                    wait_time = 2 ** attempt
                    logger.info(f"⏳ Waiting {wait_time}s before retry...")
                    await asyncio.sleep(wait_time)
            
            return None

    async def download_file(self, session: aiohttp.ClientSession, semaphore: asyncio.Semaphore,
                           file_url: str, output_path: str, filename: str) -> Optional[int]:
        """
        Backward compatibility wrapper - uses new retry logic
        """
        return await self.download_file_with_retry(session, semaphore, file_url, output_path, filename)

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
            timeout = aiohttp.ClientTimeout(total=30)  # Quick timeout for HEAD request
            async with session.head(file_url, timeout=timeout) as resp:
                if resp.status == 200:
                    return int(resp.headers.get("Content-Length", 0))
                return 0
        except Exception as e:
            logger.debug(f"🔍 HEAD request failed: {e}")
            return 0

    def prepare_download_path(self, title: str, file_url: str, download_dir: str) -> Tuple[str, str]:
        """
        Download path va filename tayyorlash

        Args:
            title: File title
            file_url: File URL
            download_dir: Download directory

        Returns:
            (output_path, filename) tuple
        """
        # Extension extraction
        ext = Path(file_url).suffix or ".mp4"

        # Clean title and create filename
        clean_title_str = clean_title(title or "untitled")
        filename = safe_filename(clean_title_str, ext)

        # Full output path
        output_path = os.path.join(download_dir, filename)

        return output_path, filename

    def check_file_exists(self, output_path: str, expected_size: int = 0) -> Tuple[bool, str]:
        """
        Fayl mavjudligini va butunligini tekshirish

        Args:
            output_path: File path
            expected_size: Expected file size (0 = don't check)

        Returns:
            (exists_and_valid, reason) tuple
        """
        if not os.path.exists(output_path):
            return False, "File does not exist"

        actual_size = os.path.getsize(output_path)
        if actual_size == 0:
            return False, "File is empty"

        if expected_size > 0:
            # Size tolerance check (1% or minimum 1MB)
            tolerance = max(expected_size * 0.01, 1024 * 1024)
            if abs(actual_size - expected_size) > tolerance:
                return False, f"Size mismatch: expected {expected_size}, got {actual_size}"

        return True, f"File exists and valid ({actual_size} bytes)"

    async def download_multiple_files(self, files_data: list, download_dir: str, 
                                    concurrency: int = 2) -> Tuple[int, int]:
        """
        Ko'p fayllarni parallel download qilish
        
        Args:
            files_data: List of file dictionaries
            download_dir: Download directory
            concurrency: Number of concurrent downloads
            
        Returns:
            Tuple of (successful_downloads, failed_downloads)
        """
        Path(download_dir).mkdir(parents=True, exist_ok=True)
        
        semaphore = asyncio.Semaphore(concurrency)
        successful = 0
        failed = 0
        
        connector = aiohttp.TCPConnector(
            limit=100,
            limit_per_host=10,
            keepalive_timeout=30,
            enable_cleanup_closed=True
        )
        
        timeout = aiohttp.ClientTimeout(
            total=None,  # No total timeout - handled per file
            connect=60,
            sock_read=300
        )
        
        async with aiohttp.ClientSession(
            connector=connector,
            timeout=timeout,
            headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
        ) as session:
            
            # Create download tasks
            tasks = []
            for file_info in files_data:
                file_url = file_info.get('file_url')
                if not file_url:
                    continue
                
                title = clean_title(file_info.get('title', 'unknown'))
                filename = safe_filename(f"{title}_{file_info.get('id', 'unknown')}")
                output_path = os.path.join(download_dir, filename)
                
                # Skip if already exists
                if os.path.exists(output_path):
                    logger.info(f"⏭️ Skipping existing: {filename}")
                    continue
                
                task = self.download_file(session, semaphore, file_url, output_path, filename)
                tasks.append(task)
            
            # Execute downloads
            if tasks:
                logger.info(f"🚀 Starting {len(tasks)} downloads with {concurrency} concurrency")
                results = await asyncio.gather(*tasks, return_exceptions=True)
                
                for result in results:
                    if isinstance(result, Exception):
                        failed += 1
                        logger.error(f"❌ Download task exception: {result}")
                    elif result is not None:
                        successful += 1
                    else:
                        failed += 1
            
        logger.info(f"📊 Download summary: {successful} successful, {failed} failed")
        return successful, failed


class ProgressTracker:
    """Download progress tracking utility"""

    def __init__(self):
        self.total_files = 0
        self.completed_files = 0
        self.failed_files = 0
        self.total_bytes = 0
        self.downloaded_bytes = 0

    def set_total_files(self, count: int):
        """Set total files to download"""
        self.total_files = count

    def file_completed(self, size: int):
        """Mark file as completed"""
        self.completed_files += 1
        self.downloaded_bytes += size

    def file_failed(self):
        """Mark file as failed"""
        self.failed_files += 1

    def get_progress_info(self) -> Dict[str, Any]:
        """Get current progress information"""
        return {
            "total_files": self.total_files,
            "completed_files": self.completed_files,
            "failed_files": self.failed_files,
            "success_rate": (self.completed_files / self.total_files * 100) if self.total_files else 0,
            "total_bytes": self.total_bytes,
            "downloaded_bytes": self.downloaded_bytes,
            "remaining_files": self.total_files - self.completed_files - self.failed_files
        }
