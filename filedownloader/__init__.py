"""
Professional File Downloader Package

Bu package fayllarni professional tarzda download qilish uchun yaratilgan.
TelegramUploader package bilan bir xil arxitektura asosida qurilgan.

Components:
- core/: Asosiy business logic (FileDownloader, ProgressTracker, etc.)
- workers/: Producer/Consumer pattern bilan parallel processing
- handlers/: Progress tracking, notifications, va error handling
- utils/: Helper utilities va validators
- orchestrator.py: Main orchestrator
- legacy_adapter.py: Backward compatibility
"""

__version__ = "1.0.0"
__author__ = "AI Assistant"

from .orchestrator import FileDownloaderOrchestrator

__all__ = ["FileDownloaderOrchestrator"]