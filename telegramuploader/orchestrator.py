"""
Main Orchestrator - Barcha komponentlarni boshqarish uchun
"""
import asyncio
import aiohttp
from typing import List, Dict, Any

from core.FileDB import FileDB
from utils.logger_core import logger
from .core.downloader import FileDownloader
from .core.uploader import TelegramUploader
from .core.stream_uploader import StreamingUploader
from .handlers.notification import NotificationHandler
from .workers.producer import FileProducer
from .workers.consumer import FileConsumer
from .workers.streaming_producer import StreamingProducer
from .utils.diagnostics import diagnostics


class TelegramUploaderOrchestrator:
    """TelegramUploader sistemasining asosiy orchestrator class"""

    def __init__(self, config: Dict[str, Any]):
        """
        Args:
            config: System configuration
        """
        self.config = config

        # Core components
        self.downloader = FileDownloader(base_timeout=7200, max_retries=3)  # Enhanced downloader
        self.uploader = TelegramUploader()   # Timeout yo'q - muvaffaqiyatli yuklashni to'xtatmaymiz
        # StreamingUploader - agar config da telegram_group bo'lmasa, default ishlatadi
        self.stream_uploader = StreamingUploader(
            # None bo'lsa default ishlatadi
            default_group=config.get("telegram_group") or None
        )
        self.notifier = NotificationHandler()

        # Workers
        self.producer = FileProducer(
            self.downloader, self.notifier, orchestrator=self)
        self.consumer = FileConsumer(
            self.uploader, self.notifier, orchestrator=self)
        self.streaming_producer = StreamingProducer(
            self.stream_uploader, self.notifier, orchestrator=self
        )

        # Batch tracking
        self._total_files = 0
        self._completed_files = 0
        self._successful_files = 0
        self._failed_files = 0

    async def process_files_sequential(self, items: List[Dict[str, Any]], session: aiohttp.ClientSession,
                                       semaphore: asyncio.Semaphore, db: FileDB) -> None:
        """
        Sequential mode - fayllarni ketma-ket qayta ishlash

        Args:
            items: Qayta ishlanadigan fayllar ro'yxati
            session: aiohttp session
            semaphore: Download semaphore
            db: Database connection
        """
        # Batch tracking'ni boshlash
        self.set_total_files(len(items))
        logger.info(f"🚀 Sequential batch boshlandi: {len(items)} ta fayl")

        for row in items:
            queue = asyncio.Queue()
            await self.producer.process_file(session, semaphore, queue, row, self.config)

            while not queue.empty():
                item = await queue.get()
                await self.consumer.process_single_item(item, self.config, db)
                queue.task_done()

        # Batch yakunlanishi haqida xabar
        await self.notifier.notify_batch_complete(
            self._total_files, self._successful_files, self._failed_files
        )

        # Diagnostics hisobotini chop etish
        logger.info("\n" + "="*60)
        diagnostics.print_report()
        logger.info("="*60 + "\n")

    async def process_files_parallel(self, items: List[Dict[str, Any]], session: aiohttp.ClientSession,
                                     semaphore: asyncio.Semaphore, db: FileDB) -> None:
        """
        Parallel mode - fayllarni parallel qayta ishlash

        Args:
            items: Qayta ishlanadigan fayllar ro'yxati  
            session: aiohttp session
            semaphore: Download semaphore
            db: Database connection
        """
        # Batch tracking'ni boshlash
        self.set_total_files(len(items))
        logger.info(f"🚀 Batch boshlandi: {len(items)} ta fayl")

        queue = asyncio.Queue()

        # Consumer'larni ishga tushirish (agar upload_workers > 0 bo'lsa)
        upload_workers = self.config.get(
            "upload_workers", self.config.get("upload_concurrency", 1))

        consumers = []
        if upload_workers > 0:
            consumers = [
                asyncio.create_task(
                    self.consumer.consume_queue(queue, self.config, db))
                for _ in range(upload_workers)
            ]
            logger.info(
                f"📤 {upload_workers} ta upload worker ishga tushirildi")
        else:
            logger.info("📥 Faqat download mode: Upload workers o'chirilgan")

        # Producer'larni ishga tushirish
        producers = [
            self.producer.process_file(
                session, semaphore, queue, row, self.config)
            for row in items
        ]

        # Barcha producer'lar tugashini kutish
        await asyncio.gather(*producers)

        # Upload workers bor bo'lsa queue'ni kutish
        if upload_workers > 0:
            # Queue bo'sh bo'lishini kutish
            await queue.join()

            # Barcha consumer'larni to'xtatish
            for c in consumers:
                c.cancel()
        else:
            logger.info("📥 Download tugadi - Upload queue yo'q")

        # Batch yakunlanishi haqida xabar
        await self.notifier.notify_batch_complete(
            self._total_files, self._successful_files, self._failed_files
        )

        # Diagnostics hisobotini chop etish
        logger.info("\n" + "="*60)
        diagnostics.print_report()
        logger.info("="*60 + "\n")

    async def process_files_streaming(self, items: List[Dict[str, Any]], session: aiohttp.ClientSession,
                                      semaphore: asyncio.Semaphore, db: FileDB) -> None:
        """
        Streaming mode - fayllarni disk ga saqlamasdan to'g'ridan-to'g'ri Telegram ga yuklash

        Args:
            items: Qayta ishlanadigan fayllar ro'yxati
            session: aiohttp session
            semaphore: Download semaphore
            db: Database connection
        """
        # Batch tracking'ni boshlash
        self.set_total_files(len(items))
        logger.info(f"🚀 Streaming batch boshlandi: {len(items)} ta fayl")
        logger.info(
            f"💡 Fayllar disk ga saqlanmaydi, to'g'ridan-to'g'ri Telegram ga yuklanadi")

        # Parallel yoki sequential
        concurrency = self.config.get("download_concurrency", 3)

        if concurrency > 1:
            # Parallel streaming
            tasks = [
                self.streaming_producer.process_file_streaming(
                    session, semaphore, row, self.config, db
                )
                for row in items
            ]
            await asyncio.gather(*tasks)
        else:
            # Sequential streaming
            for row in items:
                await self.streaming_producer.process_file_streaming(
                    session, semaphore, row, self.config, db
                )

        # Batch yakunlanishi haqida xabar
        await self.notifier.notify_batch_complete(
            self._total_files, self._successful_files, self._failed_files
        )

        # Diagnostics hisobotini chop etish
        logger.info("\n" + "="*60)
        diagnostics.print_report()
        logger.info("="*60 + "\n")

    async def update_progress(self, completed: bool, successful: bool, current_filename: str = ""):
        """Progress'ni yangilash va batch notification yuborish"""
        if completed:
            self._completed_files += 1
            if successful:
                self._successful_files += 1
            else:
                self._failed_files += 1

        # Progress notification yuborish (faqat milestone'larda)
        await self.notifier.notify_batch_progress(
            self._completed_files, self._total_files, current_filename
        )

    def set_total_files(self, total: int):
        """Jami fayllar sonini o'rnatish"""
        self._total_files = total
        self._completed_files = 0
        self._successful_files = 0
        self._failed_files = 0


async def select_debug_files(items: List[Dict[str, Any]], config: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Debug rejimida fayllarni tanlash

    Args:
        items: Barcha fayllar
        config: Konfiguratsiya

    Returns:
        Tanlangan fayllar ro'yxati
    """
    # Fayllarni hajm bo'yicha saralash
    sorted_items = sorted(items, key=lambda x: x.get("file_size", 0) or 0)
    top10 = sorted_items[:10]

    logger.info("\\nDEBUG: Eng kichik 10 fayl:")
    for idx, row in enumerate(top10, 1):
        size_bytes = row.get('file_size', 0) or 0
        size_gb = size_bytes / (1024 ** 3)
        logger.info(
            f"{idx}. {row.get('title', 'No title')} | {size_gb:.3f} GB | id={row.get('id')}")

    try:
        selected = int(input("Qaysi faylni yuklashni tanlaysiz? (1-10): "))
        if not (1 <= selected <= len(top10)):
            logger.info("Noto'g'ri tanlov. Jarayon to'xtatildi.")
            return []
    except Exception:
        logger.info("Noto'g'ri kiritildi. Jarayon to'xtatildi.")
        return []

    return [top10[selected - 1]]
