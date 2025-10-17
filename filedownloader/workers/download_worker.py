"""
Download Worker - Producer pattern for file downloads
"""
import os
import asyncio
import aiohttp
from typing import Dict, Any, List

from utils.logger_core import logger
from ..core.downloader import FileDownloader
from ..core.database import FileDownloaderDB


class DownloadProducer:
    """File download producer - manages download tasks"""
    
    def __init__(self, downloader: FileDownloader, db: FileDownloaderDB):
        self.downloader = downloader
        self.db = db
    
    async def process_file(self, session: aiohttp.ClientSession, semaphore: asyncio.Semaphore,
                          file_data: Dict[str, Any], config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Bitta faylni download qilish
        
        Args:
            session: aiohttp session
            semaphore: Concurrency semaphore
            file_data: File information from database
            config: Configuration
            
        Returns:
            Result dictionary with download status
        """
        file_id = file_data["id"]
        title = file_data.get("title", "Untitled")
        file_url = file_data.get("file_url")
        
        if not file_url or "https://t.me/" in file_url:
            logger.warning(f"⏭️ Invalid URL skipped: {title}")
            return {"status": "skipped", "file_id": file_id, "reason": "Invalid URL"}
        
        try:
            # Prepare download path
            output_path, filename = self.downloader.prepare_download_path(
                title, file_url, config["download_dir"]
            )
            
            # Check if file already exists
            expected_size = await self.downloader.get_file_size(session, file_url)
            exists, reason = self.downloader.check_file_exists(output_path, expected_size)
            
            if exists:
                logger.info(f"♻️ File already exists: {filename}")
                # Update database with existing file
                actual_size = os.path.getsize(output_path)
                self.db.update_download_success(file_id, output_path, actual_size)
                return {
                    "status": "exists",
                    "file_id": file_id,
                    "local_path": output_path,
                    "file_size": actual_size
                }
            
            # Download file
            logger.info(f"🚀 Starting download: {title}")
            file_size = await self.downloader.download_file(
                session, semaphore, file_url, output_path, filename
            )
            
            if file_size:
                # Update database
                self.db.update_download_success(file_id, output_path, file_size)
                logger.info(f"✅ Download completed: {filename}")
                return {
                    "status": "success",
                    "file_id": file_id,
                    "local_path": output_path,
                    "file_size": file_size,
                    "title": title
                }
            else:
                # Download failed
                self.db.update_download_failed(file_id, "Download failed")
                logger.error(f"❌ Download failed: {title}")
                return {
                    "status": "failed",
                    "file_id": file_id,
                    "reason": "Download failed"
                }
                
        except Exception as e:
            logger.error(f"❌ Process file error: {title} | {e}")
            self.db.update_download_failed(file_id, str(e))
            return {
                "status": "error",
                "file_id": file_id,
                "reason": str(e)
            }
    
    async def batch_process(self, session: aiohttp.ClientSession, semaphore: asyncio.Semaphore,
                           files: List[Dict[str, Any]], config: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Batch file download processing
        
        Args:
            session: aiohttp session
            semaphore: Concurrency semaphore
            files: List of files to download
            config: Configuration
            
        Returns:
            List of download results
        """
        logger.info(f"📦 Starting batch download: {len(files)} files")
        
        # Create download tasks
        tasks = [
            self.process_file(session, semaphore, file_data, config)
            for file_data in files
        ]
        
        # Execute downloads
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Process results
        successful = len([r for r in results if isinstance(r, dict) and r.get("status") == "success"])
        failed = len([r for r in results if isinstance(r, dict) and r.get("status") == "failed"])
        skipped = len([r for r in results if isinstance(r, dict) and r.get("status") == "skipped"])
        existing = len([r for r in results if isinstance(r, dict) and r.get("status") == "exists"])
        errors = len([r for r in results if isinstance(r, Exception)])
        
        logger.info(f"📊 Batch completed: ✅{successful} ❌{failed} ⏭️{skipped} ♻️{existing} 🚨{errors}")
        
        return [r for r in results if isinstance(r, dict)]


class DownloadConsumer:
    """Download consumer - processes download results"""
    
    def __init__(self, db: FileDownloaderDB):
        self.db = db
    
    def process_result(self, result: Dict[str, Any], config: Dict[str, Any]) -> None:
        """
        Download natijasini qayta ishlash
        
        Args:
            result: Download result
            config: Configuration
        """
        status = result.get("status")
        file_id = result.get("file_id")
        
        if status == "success":
            logger.info(f"📄 File processed successfully: ID={file_id}")
            
            # Optional: File cleanup or post-processing
            if config.get("clear_after_process", False):
                local_path = result.get("local_path")
                if local_path and os.path.exists(local_path):
                    try:
                        os.remove(local_path)
                        logger.info(f"🗑️ File cleaned up: {local_path}")
                    except Exception as e:
                        logger.error(f"❌ Cleanup failed: {e}")
        
        elif status == "failed":
            logger.warning(f"⚠️ File processing failed: ID={file_id}")
        
        elif status == "skipped":
            logger.info(f"⏭️ File skipped: ID={file_id}")
    
    def batch_process_results(self, results: List[Dict[str, Any]], config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Batch natijalarni qayta ishlash
        
        Args:
            results: List of download results
            config: Configuration
            
        Returns:
            Summary statistics
        """
        for result in results:
            self.process_result(result, config)
        
        # Statistics
        stats = {
            "total": len(results),
            "success": len([r for r in results if r.get("status") == "success"]),
            "failed": len([r for r in results if r.get("status") == "failed"]),
            "skipped": len([r for r in results if r.get("status") == "skipped"]),
            "exists": len([r for r in results if r.get("status") == "exists"]),
            "total_size": sum(r.get("file_size", 0) for r in results if r.get("file_size")),
        }
        
        stats["success_rate"] = (stats["success"] / stats["total"] * 100) if stats["total"] else 0
        stats["total_size_gb"] = stats["total_size"] / (1024**3)
        
        return stats