"""
Scraping module - Veb sahifalardan ma'lumotlarni yig'ish moduli.

Bu modul quyidagi komponentlardan iborat:
- browser: Playwright browser boshqaruvi
- workers: Parallel processing va multithreading
- scraping: Asosiy scraping orchestration
- parsers: HTML parsing va ma'lumot ajratish
"""

from .scraping import scrape, quick_scrape, batch_scrape_multiple_sites, ScrapingOrchestrator
from .browser import launch_browser, create_browser_context, cleanup_browser
from .workers import collect_items_parallel, process_batch_parallel, WorkerPool

__all__ = [
    'scrape',
    'quick_scrape',
    'batch_scrape_multiple_sites',
    'ScrapingOrchestrator',
    'launch_browser', 
    'create_browser_context',
    'cleanup_browser',
    'collect_items_parallel',
    'process_batch_parallel',
    'WorkerPool'
]