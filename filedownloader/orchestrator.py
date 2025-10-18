"""
File Downloader Orchestrator - Main coordination class
"""
import asyncio
import aiohttp
from typing import Dict, Any, List, Optional
from pathlib import Path

from utils.logger_core import logger
from .core import FileDownloader, ProgressTracker, FileDownloaderDB
from .workers import DownloadProducer, DownloadConsumer
from .handlers import ProgressHandler, ErrorHandler
from .utils import validate_config, FileValidator


class FileDownloaderOrchestrator:
    """Main orchestrator for file download operations"""
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the orchestrator
        
        Args:
            config: Configuration dictionary
        """
        self.config = config
        
        # Validate configuration
        is_valid, reason = validate_config(config)
        if not is_valid:
            raise ValueError(f"Invalid configuration: {reason}")
        
        # Initialize components with enhanced timeout and retry
        self.downloader = FileDownloader(
            base_timeout=None,  # ⚡ Timeout removed - unlimited download time
            chunk_size=config.get("download_chunk_size", 256 * 1024),  # 256KB
            max_retries=config.get("download_max_retries", 3)  # 3 retries
        )
        
        self.db = FileDownloaderDB()
        self.progress_tracker = ProgressTracker()
        self.progress_handler = ProgressHandler()
        self.error_handler = ErrorHandler()
        
        # Workers
        self.producer = DownloadProducer(self.downloader, self.db)
        self.consumer = DownloadConsumer(self.db)
        
        logger.info("🚀 FileDownloaderOrchestrator initialized")
    
    async def download_files(self, site_name: str, limit: Optional[int] = None, 
                           debug_mode: bool = False) -> Dict[str, Any]:
        """
        Main download function
        
        Args:
            site_name: Site name to download files from
            limit: Maximum files to download (None for all)
            debug_mode: Enable debug mode (single file selection)
            
        Returns:
            Download results dictionary
        """
        logger.info(f"📂 Starting download session for: {site_name}")
        
        # Get files to download
        files = self.db.get_files_for_download(site_name, limit)
        
        if not files:
            logger.warning(f"⚠️ No files found for download: {site_name}")
            return {"status": "no_files", "total": 0}
        
        # Debug mode - select single file
        if debug_mode:
            files = await self._debug_file_selection(files)
            if not files:
                return {"status": "cancelled", "total": 0}
        
        # Ensure download directory exists
        download_dir = self.config["download_dir"]
        Path(download_dir).mkdir(parents=True, exist_ok=True)
        
        # Cleanup incomplete downloads
        cleaned = FileValidator.cleanup_incomplete_downloads(download_dir)
        if cleaned > 0:
            logger.info(f"🧹 Cleaned {cleaned} incomplete files")
        
        # Start progress tracking
        self.progress_handler.start_session(len(files))
        
        # Get download concurrency
        concurrency = self.config.get("download_concurrency", 3)
        semaphore = asyncio.Semaphore(concurrency)
        
        logger.info(f"⚡ Download concurrency: {concurrency}")
        
        # Execute downloads
        async with aiohttp.ClientSession() as session:
            results = await self.producer.batch_process(session, semaphore, files, self.config)
        
        # Process results
        stats = self.consumer.batch_process_results(results, self.config)
        
        # Log summaries
        self.progress_handler.log_session_summary()
        self.error_handler.log_error_summary()
        
        # Prepare return data
        return {
            "status": "completed",
            "total": len(files),
            "results": results,
            "statistics": stats,
            "progress": self.progress_handler.get_session_summary(),
            "errors": self.error_handler.get_error_summary()
        }
    
    async def _debug_file_selection(self, files: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Debug mode - fayllarni tanlash
        
        Args:
            files: Barcha fayllar ro'yxati
            
        Returns:
            Tanlangan fayllar ro'yxati
        """
        # Fayllarni hajm bo'yicha saralash
        sorted_files = sorted(files, key=lambda x: x.get("file_size", 0) or 0)
        top10 = sorted_files[:10]
        
        logger.info("\\nDEBUG: Eng kichik 10 fayl:")
        for idx, file_data in enumerate(top10, 1):
            file_size = file_data.get('file_size', 0) or 0
            size_gb = file_size / (1024 ** 3)
            logger.info(
                f"{idx}. {file_data.get('title', 'No title')[:50]} | "
                f"{size_gb:.3f} GB | id={file_data.get('id')}"
            )
        
        try:
            selected = int(input("Qaysi faylni yuklashni tanlaysiz? (1-10): "))
            if not (1 <= selected <= len(top10)):
                logger.info("Noto'g'ri tanlov. Jarayon to'xtatildi.")
                return []
        except (ValueError, KeyboardInterrupt):
            logger.info("Jarayon bekor qilindi.")
            return []
        
        return [top10[selected - 1]]
    
    def get_download_statistics(self, site_name: str) -> Dict[str, Any]:
        """
        Site uchun download statistikalarini olish
        
        Args:
            site_name: Site name
            
        Returns:
            Statistics dictionary
        """
        return self.db.get_download_statistics(site_name)
    
    def log_download_statistics(self, site_name: str):
        """Download statistikalarini log qilish"""
        stats = self.get_download_statistics(site_name)
        
        logger.info("="*60)
        logger.info(f"📊 DOWNLOAD STATISTICS - {site_name}")
        logger.info("="*60)
        logger.info(f"📁 Total files:        {stats['total_files']}")
        logger.info(f"✅ Downloaded:         {stats['downloaded']}")
        logger.info(f"⏳ Pending:            {stats['pending']}")
        logger.info(f"❌ No URL:             {stats['no_url']}")
        logger.info(f"📊 Download rate:      {stats['download_rate']:.1f}%")
        logger.info(f"💾 Total size:         {stats['total_size_gb']:.2f} GB")
        logger.info(f"✅ Downloaded size:    {stats['downloaded_size_gb']:.2f} GB")
        logger.info(f"⏳ Pending size:       {stats['pending_size_gb']:.2f} GB")
        logger.info("="*60)
    
    async def sequential_download(self, site_name: str, limit: Optional[int] = None) -> Dict[str, Any]:
        """
        Sequential (ketma-ket) download mode
        
        Args:
            site_name: Site name
            limit: Maximum files to download
            
        Returns:
            Download results
        """
        logger.info("🔄 Sequential download mode")
        
        # Temporarily set concurrency to 1 for sequential mode
        original_concurrency = self.config.get("download_concurrency", 3)
        self.config["download_concurrency"] = 1
        
        try:
            result = await self.download_files(site_name, limit, debug_mode=False)
            return result
        finally:
            # Restore original concurrency
            self.config["download_concurrency"] = original_concurrency
    
    async def parallel_download(self, site_name: str, limit: Optional[int] = None) -> Dict[str, Any]:
        """
        Parallel download mode
        
        Args:
            site_name: Site name
            limit: Maximum files to download
            
        Returns:
            Download results
        """
        logger.info("⚡ Parallel download mode")
        return await self.download_files(site_name, limit, debug_mode=False)