"""
Scraper oqimi (boshqaruv) - asosiy scraping orchestration moduli.

Bu modul scraping jarayonining asosiy oqimini boshqaradi:
1. Browserni ishga tushirish
2. Sahifalarni tanlash
3. Film linklarini to'plash
4. DB orqali filtrlash
5. Parallel processing
6. Natijalarni saqlash
"""
import asyncio
from typing import List, Dict, Optional, Tuple

from core.FileDB import FileDB
from utils.helpers import parse_page_selection
from utils.logger_core import logger
from tqdm import tqdm

from .browser import launch_browser, cleanup_browser
from .parsers.parse_file_pages import collect_links, scrape_page_list_safe
from .workers import collect_items_parallel, ProcessingStats


class ScrapingOrchestrator:
    """
    Scraping jarayonini boshqaruvchi klass.
    """

    def __init__(self, config: dict, browser_config: dict):
        self.config = config
        self.browser_config = browser_config
        self.db = FileDB()
        self.stats = ProcessingStats()

    async def setup_browser(self) -> Tuple:
        """
        Playwright browserni ishga tushirish.

        Returns:
            Tuple: (playwright_instance, browser, page)
        """
        try:
            pw, browser, page = await launch_browser(self.browser_config)
            logger.info("🚀 Scraper ishga tushdi.")
            return pw, browser, page
        except Exception as e:
            logger.error(f"❌ Browser setup xato: {e}")
            raise

    async def select_pages(self, page) -> Tuple[Optional[List[str]], List[str]]:
        """
        Foydalanuvchidan sahifa tanlashni so'raydi va valid ro'yxat qaytaradi.

        Args:
            page: Browser page instance

        Returns:
            Tuple: (selected_links, all_links)
        """
        try:
            logger.info("🌐 Linklarni yig'ish boshlandi...")
            links = await collect_links(self.config, page)
            total = len(links)
            logger.info(f"🔗 Topilgan sahifalar soni: {total}")

            selection = input(
                "📌 Qaysi sahifalarni ko'rib chiqamiz? (1-10,50,51 yoki *): "
            ).strip()

            selected = parse_page_selection(selection, total)

            if not selected:
                logger.warning("❌ Sahifalar tanlanmadi.")
                return None, links

            if len(selected) > 10:
                selected_info = f"{selected[0]}...{selected[-1]}"
            else:
                selected_info = ", ".join(map(str, selected))

            logger.info(
                f"📑 Tanlangan sahifalar: {selected_info} (jami {len(selected)})"
            )

            selected_links = [links[i - 1] for i in selected]
            return selected_links, links

        except Exception as e:
            logger.error(f"❌ Sahifa tanlashda xato: {e}")
            return None, []

    async def collect_film_links(self, browser, links: List[str]) -> List[dict]:
        """
        Har bir listing sahifadan film linklarini to'playdi.

        Args:
            browser: Browser instance
            links: Listing sahifa linklari

        Returns:
            List[dict]: Film linklari
        """
        try:
            film_links = []

            with tqdm(total=len(links), desc="📄 Listing sahifalar", unit="sahifa") as pbar:
                for link in links:
                    try:
                        items = await scrape_page_list_safe(self.config, browser, link)
                        film_links.extend(items)
                        logger.debug(
                            f"✅ {link} dan {len(items)} ta link topildi")
                    except Exception as e:
                        logger.warning(f"❌ Sahifa o'qilmadi: {link} | {e}")
                    finally:
                        pbar.update(1)

            logger.info(
                f"📊 Umumiy topilgan film sahifalari: {len(film_links)}")
            return film_links

        except Exception as e:
            logger.error(f"❌ Film linklar to'plashda xato: {e}")
            return []

    def filter_existing_files(self, film_links: List[dict]) -> Tuple[List[dict], int]:
        """
        DB'da mavjud fayllarni chiqarib tashlaydi.

        Args:
            film_links: Barcha film linklari

        Returns:
            Tuple: (new_links, skipped_count)
        """
        try:
            new_links, skipped = [], 0

            for item in film_links:
                file_page = item.get("file_page")
                if not file_page:
                    continue

                if self.db.file_exists(self.config["name"], file_page):
                    skipped += 1
                    continue

                new_links.append(item)

            logger.info(f"🧠 DB'da mavjud {skipped} ta sahifa tashlab ketildi.")
            logger.info(f"📥 Yangi sahifalar soni: {len(new_links)}")

            return new_links, skipped

        except Exception as e:
            logger.error(f"❌ DB filtrlashda xato: {e}")
            return film_links, 0

    def insert_new_items(self, all_items: List[dict], skipped: int) -> int:
        """
        Yangi yig'ilgan itemlarni DB ga yozadi.

        Args:
            all_items: Yangi itemlar
            skipped: Tashlab ketilgan itemlar soni

        Returns:
            int: Qo'shilgan itemlar soni
        """
        try:
            inserted = 0

            for item in all_items:
                if not item.get("file_page"):
                    continue

                self.db.insert_file(self.config["name"], item)
                inserted += 1

            logger.info(
                f"📂 {self.config['name']} uchun {inserted} ta yangi item qo'shildi, "
                f"{skipped} ta eskisi tashlab ketildi."
            )

            return inserted

        except Exception as e:
            logger.error(f"❌ DB ga yozishda xato: {e}")
            return 0

    async def run_scraping_process(self) -> Dict:
        """
        To'liq scraping jarayonini ishga tushirish.

        Returns:
            Dict: Scraping natijalari statistikasi
        """
        self.stats.start()
        pw, browser, page = None, None, None

        try:
            # 1. Browser setup
            pw, browser, page = await self.setup_browser()

            # 2. Sahifalarni tanlash
            selected_links, all_links = await self.select_pages(page)
            if not selected_links:
                return {"status": "cancelled", "reason": "No pages selected"}

            # 3. Film linklarini to'plash
            film_links = await self.collect_film_links(browser, selected_links)
            if not film_links:
                return {"status": "failed", "reason": "No film links found"}

            # 4. DB orqali filtrlash
            new_links, skipped = self.filter_existing_files(film_links)
            if not new_links:
                return {"status": "completed", "reason": "No new files to process", "skipped": skipped}

            # 5. Parallel processing
            logger.info(
                f"🚀 Parallel processing boshlandi: {len(new_links)} ta yangi fayl")
            all_items = await collect_items_parallel(self.config, browser, new_links)
            logger.info(f"✅ Yig'ilgan yangi itemlar: {len(all_items)}")

            if not all_items:
                return {"status": "failed", "reason": "No items collected"}

            # 6. DB ga saqlash
            inserted = self.insert_new_items(all_items, skipped)

            self.stats.finish()
            stats_summary = self.stats.get_summary()

            return {
                "status": "success",
                "total_found": len(film_links),
                "skipped": skipped,
                "processed": len(new_links),
                "successful": len(all_items),
                "inserted": inserted,
                "stats": stats_summary
            }

        except Exception as e:
            logger.error(f"❌ Scraping jarayonida xato: {e}")
            return {"status": "error", "error": str(e)}

        finally:
            # Browser va resurslarni tozalash
            if pw and browser:
                await cleanup_browser(pw, browser)


async def scrape(config: dict, browser_config: dict) -> Dict:
    """
    Asosiy scraping funksiyasi (eski interface bilan moslashuv).

    Args:
        config: Sayt konfiguratsiyasi
        browser_config: Browser konfiguratsiyasi

    Returns:
        Dict: Scraping natijalari
    """
    orchestrator = ScrapingOrchestrator(config, browser_config)
    return await orchestrator.run_scraping_process()


# Qo'shimcha helper funksiyalar

async def quick_scrape(config: dict, browser_config: dict, page_selection: str = "*") -> Dict:
    """
    Tez scraping (foydalanuvchi input'isiz).

    Args:
        config: Sayt konfiguratsiyasi
        browser_config: Browser konfiguratsiyasi
        page_selection: Sahifa tanlash (masalan, "1-5" yoki "*")

    Returns:
        Dict: Scraping natijalari
    """
    # Input ni avtomatik qilib qo'yish
    original_input = __builtins__.get('input')
    __builtins__['input'] = lambda _: page_selection

    try:
        result = await scrape(config, browser_config)
        return result
    finally:
        # Input ni qaytarish
        __builtins__['input'] = original_input


async def batch_scrape_multiple_sites(sites_configs: List[dict], browser_config: dict) -> List[Dict]:
    """
    Bir necha saytni ketma-ket scraping qilish.

    Args:
        sites_configs: Saytlar konfiguratsiyasi ro'yxati
        browser_config: Browser konfiguratsiyasi

    Returns:
        List[Dict]: Har bir sayt uchun natijalar
    """
    results = []

    for i, config in enumerate(sites_configs, 1):
        logger.info(
            f"🌐 Sayt {i}/{len(sites_configs)}: {config.get('name', 'Unknown')}")

        try:
            result = await scrape(config, browser_config)
            result["site_name"] = config.get("name", f"Site_{i}")
            results.append(result)

            logger.info(f"✅ Sayt {i} yakunlandi: {result.get('status')}")

            # Saytlar orasida tanaffus
            await asyncio.sleep(5)

        except Exception as e:
            logger.error(f"❌ Sayt {i} da xato: {e}")
            results.append({
                "site_name": config.get("name", f"Site_{i}"),
                "status": "error",
                "error": str(e)
            })

    return results


def get_scraping_summary(results: List[Dict]) -> Dict:
    """
    Scraping natijalarining umumiy xulosasi.

    Args:
        results: Scraping natijalari

    Returns:
        Dict: Umumiy statistika
    """
    total_found = sum(r.get("total_found", 0) for r in results)
    total_successful = sum(r.get("successful", 0) for r in results)
    total_inserted = sum(r.get("inserted", 0) for r in results)
    total_skipped = sum(r.get("skipped", 0) for r in results)

    successful_sites = len(
        [r for r in results if r.get("status") == "success"])
    failed_sites = len([r for r in results if r.get("status") == "error"])

    return {
        "total_sites": len(results),
        "successful_sites": successful_sites,
        "failed_sites": failed_sites,
        "total_found": total_found,
        "total_successful": total_successful,
        "total_inserted": total_inserted,
        "total_skipped": total_skipped,
        "success_rate": (successful_sites / len(results) * 100) if results else 0
    }
