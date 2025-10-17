"""
Core FileDownloader - Asosiy fayl download qilish moduli
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
    """Professional file downloader with progress tracking and error handling"""
    
    def __init__(self, timeout: int = 600, chunk_size: int = 256 * 1024):
        """
        Args:
            timeout: Download timeout in seconds (default 10 minutes)
            chunk_size: Download chunk size in bytes (default 256KB)
        """
        self.timeout = timeout
        self.chunk_size = chunk_size
    
    async def download_file(self, session: aiohttp.ClientSession, semaphore: asyncio.Semaphore,
                           file_url: str, output_path: str, filename: str) -> Optional[int]:
        """
        Bitta faylni download qilish
        
        Args:
            session: aiohttp session
            semaphore: Concurrency limiter
            file_url: Download URL
            output_path: Output file path
            filename: Display filename
            
        Returns:
            File size in bytes if successful, None if failed
        """
        async with semaphore:
            try:
                timeout = aiohttp.ClientTimeout(total=self.timeout)
                async with session.get(file_url, timeout=timeout) as resp:
                    if resp.status != 200:
                        logger.error(f"❌ HTTP {resp.status}: {file_url}")
                        return None
                    
                    total_size = int(resp.headers.get("Content-Length", 0))
                    size_mb = total_size / (1024 * 1024) if total_size else 0
                    
                    logger.info(f"⬇️ Downloading: {filename} ({size_mb:.2f} MB)")
                    
                    # Faylni download qilish
                    with open(output_path, "wb") as f:
                        with tqdm(
                            total=total_size,
                            unit="B",
                            unit_scale=True,
                            desc=f"⬇️ {filename[:30]}"
                        ) as progress_bar:
                            
                            async for chunk in resp.content.iter_chunked(self.chunk_size):
                                f.write(chunk)
                                progress_bar.update(len(chunk))
                    
                    # File size validation
                    actual_size = os.path.getsize(output_path)
                    if total_size > 0 and abs(actual_size - total_size) > 1024:  # 1KB tolerance
                        logger.warning(f"⚠️ Size mismatch: expected {total_size}, got {actual_size}")
                    
                    logger.info(f"✅ Downloaded: {filename} ({actual_size / (1024*1024):.2f} MB)")
                    return actual_size
                    
            except asyncio.TimeoutError:
                logger.error(f"⏰ Download timeout: {filename}")
                return None
            except Exception as e:
                logger.error(f"❌ Download error: {filename} | {e}")
                return None
    
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
            async with session.head(file_url) as resp:
                if resp.status == 200:
                    return int(resp.headers.get("Content-Length", 0))
                return 0
        except Exception as e:
            logger.error(f"❌ HEAD request failed: {e}")
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