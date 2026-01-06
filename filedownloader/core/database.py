"""
Database operations for file downloader
"""
from typing import List, Dict, Any, Optional

from core.FileDB import FileDB
from utils.logger_core import logger
from utils.telegram import detect_telegram_type


class FileDownloaderDB:
    """Database operations specifically for file downloader"""
    
    def __init__(self):
        self.db = FileDB()
    
    def get_files_for_download(self, site_name: str, limit: Optional[int] = None, last_id: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Download uchun fayllarni olish (faqat yuklanmagan fayllar)
        
        Args:
            site_name: Site name
            limit: Maximum files to return
            
        Returns:
            List of files ready for download
        """
        # To'g'ridan-to'g'ri database'dan yuklanmagan fayllarni olish
        if last_id is not None and limit is not None:
            download_needed = self.db.get_undownloaded_files_paginated(site_name, last_id, limit)
        else:
            download_needed = self.db.get_undownloaded_files(site_name, limit)
        
        logger.info(f"📂 {len(download_needed)} fayl download uchun tayyor (yuklanmagan)")
        return download_needed
    
    def update_download_success(self, file_id: int, local_path: str, file_size: int) -> bool:
        """
        Muvaffaqiyatli download qilingan faylni yangilash
        
        Args:
            file_id: File ID
            local_path: Local file path
            file_size: File size in bytes
            
        Returns:
            True if successful
        """
        try:
            # MIME type detection
            mime_type = "video/mp4"  # Default
            telegram_type = detect_telegram_type(mime_type)
            
            self.db.update_file(
                file_id,
                local_path=local_path,
                file_size=file_size,
                mime=mime_type,
                telegram_type=telegram_type
            )
            
            logger.info(f"💾 DB updated: file_id={file_id}, size={file_size}")
            return True
            
        except Exception as e:
            logger.error(f"❌ DB update failed: file_id={file_id} | {e}")
            return False
    
    def update_download_failed(self, file_id: int, error_reason: str) -> bool:
        """
        Download fail bo'lgan faylni belgilash
        
        Args:
            file_id: File ID
            error_reason: Error reason
            
        Returns:
            True if successful
        """
        try:
            # Hozircha faqat log qilamiz, keyinchalik error tracking qo'shish mumkin
            logger.error(f"❌ Download failed: file_id={file_id} | {error_reason}")
            return True
            
        except Exception as e:
            logger.error(f"❌ DB error logging failed: {e}")
            return False
    
    def get_download_statistics(self, site_name: str) -> Dict[str, Any]:
        """
        Download statistikalarini olish
        
        Args:
            site_name: Site name
            
        Returns:
            Statistics dictionary
        """
        return self.db.get_download_statistics(site_name)