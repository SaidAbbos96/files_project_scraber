"""
TelegramUploader - Professional Telegram File Upload System

Modular structure:
- core: Main upload/download logic
- handlers: Request/response handlers  
- utils: Helper utilities
- workers: Background processing workers
"""

from .orchestrator import TelegramUploaderOrchestrator, select_debug_files
from .core.uploader import TelegramUploader
from .core.downloader import FileDownloader
from .handlers.notification import NotificationHandler
from .workers.producer import FileProducer
from .workers.consumer import FileConsumer
from .utils.diagnostics import diagnostics, TelegramDiagnostics

__version__ = "1.0.0"
__all__ = [
    "TelegramUploaderOrchestrator",
    "select_debug_files",
    "TelegramUploader",
    "FileDownloader", 
    "NotificationHandler",
    "FileProducer",
    "FileConsumer",
    "diagnostics",
    "TelegramDiagnostics"
]