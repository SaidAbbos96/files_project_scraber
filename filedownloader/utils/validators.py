"""
Validation utilities for file downloader
"""
import os
from pathlib import Path
from typing import Tuple, Optional
from urllib.parse import urlparse

from utils.logger_core import logger


def validate_download_url(url: str) -> Tuple[bool, str]:
    """
    Download URL ni validatsiya qilish
    
    Args:
        url: URL to validate
        
    Returns:
        (is_valid, reason) tuple
    """
    if not url:
        return False, "Empty URL"
    
    if "https://t.me/" in url:
        return False, "Telegram URL not supported for download"
    
    try:
        parsed = urlparse(url)
        if not parsed.scheme or not parsed.netloc:
            return False, "Invalid URL format"
        
        if parsed.scheme not in ["http", "https"]:
            return False, f"Unsupported protocol: {parsed.scheme}"
        
        return True, "Valid URL"
        
    except Exception as e:
        return False, f"URL parse error: {e}"


def validate_download_directory(directory: str) -> Tuple[bool, str]:
    """
    Download directory ni validatsiya qilish
    
    Args:
        directory: Directory path
        
    Returns:
        (is_valid, reason) tuple
    """
    if not directory:
        return False, "Empty directory path"
    
    try:
        # Directory yaratishga harakat qilish
        Path(directory).mkdir(parents=True, exist_ok=True)
        
        # Yozish huquqini tekshirish
        if not os.access(directory, os.W_OK):
            return False, "Directory not writable"
        
        return True, "Valid directory"
        
    except Exception as e:
        return False, f"Directory validation error: {e}"


def validate_file_size(file_path: str, expected_size: Optional[int] = None) -> Tuple[bool, str]:
    """
    Download qilingan faylning hajmini validatsiya qilish
    
    Args:
        file_path: File path
        expected_size: Expected file size (optional)
        
    Returns:
        (is_valid, reason) tuple
    """
    if not os.path.exists(file_path):
        return False, "File does not exist"
    
    actual_size = os.path.getsize(file_path)
    
    if actual_size == 0:
        return False, "File is empty"
    
    if expected_size:
        # 1% tolerance or minimum 1MB
        tolerance = max(expected_size * 0.01, 1024 * 1024)
        size_diff = abs(actual_size - expected_size)
        
        if size_diff > tolerance:
            return False, f"Size mismatch: expected {expected_size}, got {actual_size} (diff: {size_diff})"
    
    return True, f"File valid ({actual_size} bytes)"


def validate_config(config: dict) -> Tuple[bool, str]:
    """
    Configuration'ni validatsiya qilish
    
    Args:
        config: Configuration dictionary
        
    Returns:
        (is_valid, reason) tuple
    """
    required_keys = ["download_dir", "download_concurrency"]
    
    for key in required_keys:
        if key not in config:
            return False, f"Missing required config key: {key}"
    
    # Download directory validatsiya
    is_valid, reason = validate_download_directory(config["download_dir"])
    if not is_valid:
        return False, f"Invalid download_dir: {reason}"
    
    # Concurrency validatsiya
    concurrency = config.get("download_concurrency", 1)
    if not isinstance(concurrency, int) or concurrency < 1 or concurrency > 20:
        return False, f"Invalid download_concurrency: {concurrency} (must be 1-20)"
    
    return True, "Config valid"


class FileValidator:
    """File validation utilities"""
    
    @staticmethod
    def is_media_file(file_path: str) -> bool:
        """Check if file is a media file based on extension"""
        media_extensions = {'.mp4', '.avi', '.mkv', '.mov', '.wmv', '.flv', '.webm', '.m4v'}
        ext = Path(file_path).suffix.lower()
        return ext in media_extensions
    
    @staticmethod
    def get_file_info(file_path: str) -> dict:
        """Get file information"""
        if not os.path.exists(file_path):
            return {"exists": False}
        
        stat = os.stat(file_path)
        return {
            "exists": True,
            "size": stat.st_size,
            "size_mb": stat.st_size / (1024 * 1024),
            "size_gb": stat.st_size / (1024 * 1024 * 1024),
            "modified": stat.st_mtime,
            "is_media": FileValidator.is_media_file(file_path),
            "extension": Path(file_path).suffix.lower()
        }
    
    @staticmethod
    def cleanup_incomplete_downloads(download_dir: str) -> int:
        """
        Incomplete download fayllarini tozalash
        
        Args:
            download_dir: Download directory
            
        Returns:
            Number of files cleaned up
        """
        if not os.path.exists(download_dir):
            return 0
        
        cleaned = 0
        try:
            for file_path in Path(download_dir).glob("*"):
                if file_path.is_file():
                    # Bo'sh yoki juda kichik fayllarni o'chirish
                    file_size = file_path.stat().st_size
                    if file_size < 1024:  # 1KB dan kichik
                        file_path.unlink()
                        logger.info(f"🗑️ Cleaned incomplete file: {file_path.name}")
                        cleaned += 1
        
        except Exception as e:
            logger.error(f"❌ Cleanup error: {e}")
        
        return cleaned