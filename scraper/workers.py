"""
Fayllarni parallel yig'ish - multithreading va async workers moduli.

Bu modul parallel processing orqali ko'p sahifalarni 
bir vaqtda tahlil qilish imkonini beradi.
"""
import asyncio
import json
from pathlib import Path
from typing import List, Dict, Optional
from concurrent.futures import ThreadPoolExecutor

from tqdm.asyncio import tqdm
from utils.logger_core import logger
from .parsers.parse_file_page import scrape_file_page_safe


class WorkerPool:
    """
    Async worker pool boshqaruvchisi.
    """

    def __init__(self, max_workers: int = 5):
        self.max_workers = max_workers
        self.semaphore = asyncio.Semaphore(max_workers)
        self.results = []
        self.errors = []

    async def add_task(self, coro):
        """Task qo'shish va semaphore bilan cheklash."""
        async with self.semaphore:
            try:
                result = await coro
                if result:
                    self.results.append(result)
                return result
            except Exception as e:
                self.errors.append(e)
                logger.error(f"❌ Worker task xatosi: {e}")
                return None


def validate_item(details: dict) -> bool:
    """
    Film itemni tekshiradi — noto'g'ri bo'lsa False qaytaradi.

    Args:
        details: Film ma'lumotlari

    Returns:
        bool: Valid yoki yo'q
    """
    if not details:
        return False
    if not isinstance(details, dict):
        return False

    file_url = details.get("file_url")
    if not file_url:
        return False
    if "https://t.me/" in file_url:
        return False

    return True


def save_checkpoint(config: dict, results: list, idx: int, batch_size: int) -> None:
    """
    Har N ta elementda checkpoint faylini saqlaydi.

    Args:
        config: Sayt konfiguratsiyasi
        results: Natijalar ro'yxati
        idx: Joriy indeks
        batch_size: Batch hajmi
    """
    try:
        checkpoint_dir = Path(config.get("results_dir", "results"))
        checkpoint_dir.mkdir(parents=True, exist_ok=True)

        checkpoint_path = checkpoint_dir / \
            f"{config.get('name')}_checkpoint_{idx}.json"

        with open(checkpoint_path, "w", encoding="utf-8") as f:
            json.dump(results[-batch_size:], f, ensure_ascii=False, indent=2)

        logger.info(f"💾 Checkpoint saqlandi: {checkpoint_path}")

    except Exception as e:
        logger.error(f"❌ Checkpoint saqlashda xato: {e}")


async def single_worker(config: dict, browser, semaphore: asyncio.Semaphore,
                        film: dict, pbar) -> Optional[dict]:
    """
    Bitta film sahifasini scrap qiladi.

    Args:
        config: Sayt konfiguratsiyasi
        browser: Browser instance
        semaphore: Concurrency cheklash
        film: Film ma'lumotlari
        pbar: Progress bar

    Returns:
        dict | None: Film ma'lumotlari yoki None
    """
    file_page = film.get("file_page")
    if not file_page:
        pbar.update(1)
        return None

    async with semaphore:
        try:
            details = await scrape_file_page_safe(config, browser, file_page)

            if not validate_item(details):
                pbar.update(1)
                return None

            pbar.update(1)
            return details

        except Exception as e:
            logger.warning(f"❌ Worker xato: {file_page} | {e}")
            pbar.update(1)
            return None


async def batch_worker(config: dict, browser, films_batch: List[dict]) -> List[dict]:
    """
    Film batch'ini parallel tahlil qilish.

    Args:
        config: Sayt konfiguratsiyasi
        browser: Browser instance
        films_batch: Film batch'i

    Returns:
        List[dict]: Tahlil qilingan filmlar
    """
    semaphore = asyncio.Semaphore(config.get("scrape_concurrency", 3))
    results = []

    with tqdm(total=len(films_batch), desc="🎬 Batch", unit="film") as pbar:
        tasks = [
            single_worker(config, browser, semaphore, film, pbar)
            for film in films_batch
        ]

        for coro in asyncio.as_completed(tasks):
            result = await coro
            if result:
                results.append(result)

    return results


async def collect_items_parallel(config: dict, browser, film_links: List[dict]) -> List[dict]:
    """
    Filmlarni parallel ravishda to'plash (asosiy worker funksiya).

    Args:
        config: Sayt konfiguratsiyasi
        browser: Browser instance
        film_links: Film linklari ro'yxati

    Returns:
        List[dict]: To'plangan filmlar ro'yxati
    """
    if not film_links:
        logger.warning("⚠️ collect_items_parallel: bo'sh film_links keldi.")
        return []

    concurrency = config.get("scrape_concurrency", 3)
    semaphore = asyncio.Semaphore(concurrency)
    results = []

    try:
        logger.info(
            f"🚀 Parallel scraping boshlandi: {len(film_links)} ta film, {concurrency} concurrent")

        with tqdm(total=len(film_links), desc="🎬 Film sahifalari", unit="film") as pbar:

            async def worker(film):
                file_url = film.get("file_page")
                if not file_url:
                    pbar.update(1)
                    return None

                async with semaphore:
                    try:
                        details = await scrape_file_page_safe(config, browser, file_url)
                        pbar.update(1)

                        if not details or not details.get("file_url"):
                            return None

                        return details
                    except Exception as e:
                        logger.error(f"❌ Worker xato: {file_url} | {e}")
                        pbar.update(1)
                        return None

            # Barcha tasklar yaratish
            tasks = [asyncio.create_task(worker(f)) for f in film_links]

            # Natijalarni to'plash
            for coro in asyncio.as_completed(tasks):
                result = await coro
                if result:
                    results.append(result)

    except Exception as e:
        logger.error(f"❌ collect_items_parallel xato: {e}")

    logger.info(
        f"✅ Parallel scraping yakunlandi: {len(results)} ta muvaffaqiyatli")
    return results


async def process_batch_parallel(config: dict, browser, film_links: List[dict],
                                 batch_size: int = 10, checkpoint_interval: int = 50) -> List[dict]:
    """
    Filmlarni batch'larda parallel tahlil qilish (checkpoint bilan).

    Args:
        config: Sayt konfiguratsiyasi
        browser: Browser instance
        film_links: Film linklari
        batch_size: Batch hajmi
        checkpoint_interval: Checkpoint saqlash oralig'i

    Returns:
        List[dict]: Barcha natijalar
    """
    all_results = []
    total_batches = (len(film_links) + batch_size - 1) // batch_size

    logger.info(
        f"📦 Batch processing: {total_batches} ta batch, har birida {batch_size} ta film")

    for i in range(0, len(film_links), batch_size):
        batch_num = i // batch_size + 1
        batch = film_links[i:i + batch_size]

        logger.info(
            f"📦 Batch {batch_num}/{total_batches}: {len(batch)} ta film")

        try:
            batch_results = await batch_worker(config, browser, batch)
            all_results.extend(batch_results)

            logger.info(
                f"✅ Batch {batch_num} yakunlandi: {len(batch_results)} ta natija")

            # Checkpoint saqlash
            if len(all_results) % checkpoint_interval == 0:
                save_checkpoint(config, all_results, len(
                    all_results), checkpoint_interval)

        except Exception as e:
            logger.error(f"❌ Batch {batch_num} xato: {e}")

        # Batch orasida tanaffus
        await asyncio.sleep(2)

    logger.info(
        f"🎯 Batch processing yakunlandi: {len(all_results)} ta umumiy natija")
    return all_results


async def advanced_parallel_processing(config: dict, browser, film_links: List[dict]) -> List[dict]:
    """
    Murakkab parallel processing strategiyasi.

    Args:
        config: Sayt konfiguratsiyasi
        browser: Browser instance
        film_links: Film linklari

    Returns:
        List[dict]: Natijalar
    """
    pool = WorkerPool(max_workers=config.get("scrape_concurrency", 5))

    logger.info(f"🚀 Advanced parallel processing: {len(film_links)} ta film")

    # Barcha tasklar yaratish
    tasks = []
    for film in film_links:
        task = scrape_file_page_safe(config, browser, film.get("file_page"))
        tasks.append(pool.add_task(task))

    # Progress bar bilan kuzatish
    with tqdm(total=len(tasks), desc="🎬 Advanced processing", unit="film") as pbar:
        for coro in asyncio.as_completed(tasks):
            await coro
            pbar.update(1)

    logger.info(
        f"✅ Processing yakunlandi: {len(pool.results)} ta natija, {len(pool.errors)} ta xato")

    return pool.results


class ProcessingStats:
    """
    Processing statistikasini kuzatish.
    """

    def __init__(self):
        self.total_processed = 0
        self.successful = 0
        self.errors = 0
        self.start_time = None
        self.end_time = None

    def start(self):
        """Processing boshlanishi."""
        import time
        self.start_time = time.time()

    def finish(self):
        """Processing tugashi."""
        import time
        self.end_time = time.time()

    def add_success(self):
        """Muvaffaqiyatli processing."""
        self.successful += 1
        self.total_processed += 1

    def add_error(self):
        """Xatolik."""
        self.errors += 1
        self.total_processed += 1

    def get_summary(self) -> dict:
        """Statistika xulosasi."""
        duration = (
            self.end_time - self.start_time) if self.end_time and self.start_time else 0

        return {
            "total_processed": self.total_processed,
            "successful": self.successful,
            "errors": self.errors,
            "success_rate": (self.successful / self.total_processed * 100) if self.total_processed > 0 else 0,
            "duration_seconds": duration,
            "items_per_second": (self.total_processed / duration) if duration > 0 else 0
        }
