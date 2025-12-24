"""
Progress Handler - Download progress tracking and reporting
"""
import time
from typing import Dict, Any, List
from utils.logger_core import logger


class ProgressHandler:
    """Download progress tracking and reporting"""
    
    def __init__(self):
        self.start_time = None
        self.total_files = 0
        self.completed_files = 0
        self.failed_files = 0
        self.skipped_files = 0
        self.existing_files = 0
        self.total_bytes = 0
        self.downloaded_bytes = 0
        self.current_file = ""
    
    def start_session(self, total_files: int):
        """Download session boshlash"""
        self.start_time = time.time()
        self.total_files = total_files
        self.reset_counters()
        logger.info(f"🚀 Download session started: {total_files} files")
    
    def reset_counters(self):
        """Counters'larni reset qilish"""
        self.completed_files = 0
        self.failed_files = 0
        self.skipped_files = 0
        self.existing_files = 0
        self.downloaded_bytes = 0
        self.current_file = ""
    
    def file_started(self, filename: str):
        """Fayl download boshlanganda"""
        self.current_file = filename
        logger.debug(f"⬇️ Starting: {filename}")
    
    def file_completed(self, filename: str, file_size: int):
        """Fayl muvaffaqiyatli download bo'lganda"""
        self.completed_files += 1
        self.downloaded_bytes += file_size
        size_mb = file_size / (1024 * 1024)
        logger.info(f"✅ Completed: {filename} ({size_mb:.2f} MB)")
        self._log_progress()
    
    def file_failed(self, filename: str, reason: str):
        """Fayl download fail bo'lganda"""
        self.failed_files += 1
        logger.error(f"❌ Failed: {filename} - {reason}")
        self._log_progress()
    
    def file_skipped(self, filename: str, reason: str):
        """Fayl skip qilinganda"""
        self.skipped_files += 1
        logger.info(f"⏭️ Skipped: {filename} - {reason}")
        self._log_progress()
    
    def file_exists(self, filename: str, file_size: int):
        """Fayl allaqachon mavjud bo'lganda"""
        self.existing_files += 1
        self.downloaded_bytes += file_size
        logger.info(f"♻️ Exists: {filename}")
        self._log_progress()
    
    def _log_progress(self):
        """Progress ma'lumotlarini log qilish"""
        if not self.start_time:
            return
        
        processed = self.completed_files + self.failed_files + self.skipped_files + self.existing_files
        progress_percent = (processed / self.total_files * 100) if self.total_files else 0
        
        elapsed = time.time() - self.start_time
        if processed > 0:
            avg_time_per_file = elapsed / processed
            eta_seconds = avg_time_per_file * (self.total_files - processed)
            eta_str = f"ETA: {eta_seconds/60:.1f}m"
        else:
            eta_str = "ETA: --"
        
        logger.info(
            f"📊 Progress: {processed}/{self.total_files} ({progress_percent:.1f}%) | "
            f"✅{self.completed_files} ♻️{self.existing_files} ❌{self.failed_files} ⏭️{self.skipped_files} | "
            f"{eta_str}"
        )
    
    def get_session_summary(self) -> Dict[str, Any]:
        """Session summary statistikalarini olish"""
        if not self.start_time:
            return {"status": "not_started"}
        
        elapsed = time.time() - self.start_time
        processed = self.completed_files + self.failed_files + self.skipped_files + self.existing_files
        
        return {
            "status": "completed" if processed == self.total_files else "in_progress",
            "total_files": self.total_files,
            "completed": self.completed_files,
            "failed": self.failed_files,
            "skipped": self.skipped_files,
            "existing": self.existing_files,
            "processed": processed,
            "remaining": self.total_files - processed,
            "success_rate": (self.completed_files / processed * 100) if processed else 0,
            "total_size_gb": self.downloaded_bytes / (1024**3),
            "elapsed_minutes": elapsed / 60,
            "avg_speed_mbps": (self.downloaded_bytes / (1024*1024) / elapsed) if elapsed > 0 else 0,
            "files_per_minute": (processed / elapsed * 60) if elapsed > 0 else 0
        }
    
    def log_session_summary(self):
        """Session summary'ni log qilish"""
        summary = self.get_session_summary()
        
        if summary["status"] == "not_started":
            return
        
        logger.info("="*60)
        logger.info("📊 DOWNLOAD SESSION SUMMARY")
        logger.info("="*60)
        logger.info(f"📁 Total files:      {summary['total_files']}")
        logger.info(f"✅ Completed:        {summary['completed']}")
        logger.info(f"♻️ Already existed:  {summary['existing']}")
        logger.info(f"❌ Failed:           {summary['failed']}")
        logger.info(f"⏭️ Skipped:          {summary['skipped']}")
        logger.info(f"📊 Success rate:     {summary['success_rate']:.1f}%")
        logger.info(f"💾 Total size:       {summary['total_size_gb']:.2f} GB")
        logger.info(f"⏱️ Duration:         {summary['elapsed_minutes']:.1f} minutes")
        logger.info(f"🚀 Average speed:    {summary['avg_speed_mbps']:.2f} MB/s")
        logger.info(f"📈 Files/minute:     {summary['files_per_minute']:.1f}")
        logger.info("="*60)


class ErrorHandler:
    """Download error handling and recovery"""
    
    def __init__(self):
        self.errors = []
        self.retry_count = {}
        self.max_retries = 3
    
    def handle_error(self, file_id: int, filename: str, error: Exception) -> bool:
        """
        Error handling va retry logic
        
        Args:
            file_id: File ID
            filename: Filename
            error: Exception object
            
        Returns:
            True if should retry, False if max retries reached
        """
        error_info = {
            "file_id": file_id,
            "filename": filename,
            "error": str(error),
            "error_type": type(error).__name__,
            "timestamp": time.time()
        }
        self.errors.append(error_info)
        
        # Retry logic
        retry_key = f"{file_id}_{filename}"
        current_retries = self.retry_count.get(retry_key, 0)
        
        if current_retries < self.max_retries:
            self.retry_count[retry_key] = current_retries + 1
            logger.warning(f"🔄 Retry {current_retries + 1}/{self.max_retries}: {filename}")
            return True
        else:
            logger.error(f"💀 Max retries reached: {filename}")
            return False
    
    def get_error_summary(self) -> Dict[str, Any]:
        """Error summary statistiklari"""
        if not self.errors:
            return {"total_errors": 0}
        
        error_types = {}
        for error in self.errors:
            error_type = error["error_type"]
            error_types[error_type] = error_types.get(error_type, 0) + 1
        
        return {
            "total_errors": len(self.errors),
            "error_types": error_types,
            "most_common_error": max(error_types.items(), key=lambda x: x[1])[0] if error_types else None,
            "retry_attempts": sum(self.retry_count.values()),
            "files_with_retries": len(self.retry_count)
        }
    
    def log_error_summary(self):
        """Error summary'ni log qilish"""
        summary = self.get_error_summary()
        
        if summary["total_errors"] == 0:
            logger.info("✅ No errors occurred during download session")
            return
        
        logger.warning("="*60)
        logger.warning("⚠️ ERROR SUMMARY")
        logger.warning("="*60)
        logger.warning(f"Total errors: {summary['total_errors']}")
        logger.warning(f"Retry attempts: {summary['retry_attempts']}")
        logger.warning(f"Files with retries: {summary['files_with_retries']}")
        logger.warning(f"Most common error: {summary['most_common_error']}")
        logger.warning("Error types:")
        for error_type, count in summary["error_types"].items():
            logger.warning(f"  - {error_type}: {count}")
        logger.warning("="*60)