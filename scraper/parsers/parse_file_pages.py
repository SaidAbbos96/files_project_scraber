"""
Listing sahifalarni o'qish - ko'p sahifali ro'yxatlarni tahlil qilish moduli.

Bu modul listing sahifalar (pagination) bilan ishlaydi:
- Sahifa linklarini to'plash
- Har bir sahifadan film linklarini ajratish
- Pagination bilan ishlash
"""
import asyncio
import aiohttp
import re
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse

from utils.logger_core import logger


async def fetch_page_html_safe(url: str, timeout: int = 20) -> str | None:
    """
    Xavfsiz ravishda HTML yuklab olish.

    Args:
        url: Yuklab olinadigan URL
        timeout: Timeout sekundlarda

    Returns:
        str | None: HTML matn yoki None
    """
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, timeout=timeout) as resp:
                if resp.status == 200:
                    return await resp.text()
                logger.warning(f"⚠️ HTTP {resp.status}: {url}")
                return None
    except asyncio.TimeoutError:
        logger.warning(f"⚠️ Timeout: {url}")
        return None
    except Exception as e:
        logger.warning(f"⚠️ HTML yuklanmadi: {url} | {e}")
        return None


async def get_last_page_number(config: dict, page) -> int:
    """
    Pagination orqali oxirgi sahifa raqamini aniqlash.

    Args:
        config: Sayt konfiguratsiyasi
        page: Browser page instance

    Returns:
        int: Oxirgi sahifa raqami
    """
    try:
        await page.goto(config["base_url"], timeout=30000)

        # Agar configda aniq sahifa soni berilgan bo'lsa
        if (isinstance(config.get("pagination_pages"), int)
                and config["pagination_pages"] > 1):
            return config["pagination_pages"]

        # Pagination selector orqali oxirgi sahifani topish
        last_page_el = await page.query_selector(config["pagination_selector"])
        if not last_page_el:
            logger.info("📄 Pagination topilmadi, bitta sahifa")
            return 1

        last_href = await last_page_el.get_attribute("href")
        if not last_href:
            return 1

        # URL dan sahifa raqamini ajratish
        match = re.search(r"/page/(\d+)/", last_href)
        last_page = int(match.group(1)) if match else 1

        logger.info(f"📊 Jami sahifalar soni: {last_page}")
        return last_page

    except Exception as e:
        logger.error(f"❌ Oxirgi sahifa raqamini aniqlab bo'lmadi: {e}")
        return 1


async def collect_links(config: dict, page) -> list[str]:
    """
    Pagination linklarini yig'ish.

    Args:
        config: Sayt konfiguratsiyasi
        page: Browser page instance

    Returns:
        list[str]: Sahifa URLlari ro'yxati
    """
    try:
        last_page = await get_last_page_number(config, page)

        # Barcha sahifa linklarini yaratish
        links = [config["base_url"]]

        if last_page > 1:
            for page_num in range(2, last_page + 1):
                link = config["pagination_link"].format(page=page_num)
                links.append(link)

        logger.info(f"🔗 Yaratilgan sahifa linklari: {len(links)}")
        return links

    except Exception as e:
        logger.error(f"❌ Linklarni yig'ishda xato: {e}")
        return [config["base_url"]]


async def parse_page_links_from_html(config: dict, html: str, base_url: str) -> list[dict]:
    """
    HTML dan film linklarini ajratish.

    Args:
        config: Sayt konfiguratsiyasi
        html: HTML matn
        base_url: Asosiy URL

    Returns:
        list[dict]: Film linklari ro'yxati
    """
    try:
        soup = BeautifulSoup(html, "html.parser")
        base_domain = "{uri.scheme}://{uri.netloc}".format(
            uri=urlparse(base_url))

        cards = soup.select(config["card_selector"])
        items = []

        for card in cards:
            link_el = card.select_one("a")
            if not link_el:
                continue

            href = link_el.get("href")
            if not href:
                continue

            # Relative URLni absolute ga aylantirish
            if not href.startswith("http"):
                href = urljoin(base_domain, href)

            items.append({"file_page": href})

        return items

    except Exception as e:
        logger.error(f"❌ HTML dan linklar ajratishda xato: {e}")
        return []


async def scrape_page_list_with_aiohttp(config: dict, url: str) -> list[dict]:
    """
    Aiohttp orqali listing sahifasini tahlil qilish.

    Args:
        config: Sayt konfiguratsiyasi
        url: Sahifa URL

    Returns:
        list[dict]: Film linklari
    """
    html = await fetch_page_html_safe(url)
    if not html:
        return []

    return await parse_page_links_from_html(config, html, url)


async def scrape_page_list_with_browser(config: dict, page, url: str) -> list[dict]:
    """
    Browser orqali listing sahifasini tahlil qilish.

    Args:
        config: Sayt konfiguratsiyasi
        page: Browser page instance
        url: Sahifa URL

    Returns:
        list[dict]: Film linklari
    """
    try:
        await page.goto(url, timeout=30000)
        cards = await page.query_selector_all(config["card_selector"])
        items = []

        for card in cards:
            link_el = await card.query_selector("a")
            if not link_el:
                continue

            file_page = await link_el.get_attribute("href")
            if not file_page:
                continue

            # Relative URLni absolute ga aylantirish
            if not file_page.startswith("http"):
                base_domain = f"{page.url.split('/')[0]}//{page.url.split('/')[2]}"
                file_page = urljoin(base_domain, file_page)

            items.append({"file_page": file_page})

        return items

    except Exception as e:
        logger.error(f"❌ Browser orqali sahifa tahlilida xato: {url} | {e}")
        return []


async def scrape_page_list_safe(config: dict, browser, url: str) -> list[dict]:
    """
    Xavfsiz ravishda listing sahifasini tahlil qilish (aiohttp → browser fallback).

    Args:
        config: Sayt konfiguratsiyasi
        browser: Browser instance (fallback uchun)
        url: Sahifa URL

    Returns:
        list[dict]: Film linklari
    """
    try:
        # Birinchi aiohttp orqali urinish
        items = await scrape_page_list_with_aiohttp(config, url)

        if items:
            logger.debug(
                f"✅ Aiohttp orqali {len(items)} ta link topildi: {url}")
            return items

        # Agar aiohttp bilan natija bo'lmasa, browser ishlatish
        logger.info(f"🔄 Browser fallback: {url}")
        context = await browser.new_context()
        page = await context.new_page()

        try:
            items = await scrape_page_list_with_browser(config, page, url)
            logger.debug(
                f"✅ Browser orqali {len(items)} ta link topildi: {url}")
            return items
        finally:
            await page.close()
            await context.close()

    except Exception as e:
        logger.error(f"❌ Sahifa tahlilida xato: {url} | {e}")
        return []


async def collect_all_film_links(config: dict, browser, page_urls: list[str]) -> list[dict]:
    """
    Barcha listing sahifalardan film linklarini yig'ish.

    Args:
        config: Sayt konfiguratsiyasi
        browser: Browser instance
        page_urls: Listing sahifa URLlari

    Returns:
        list[dict]: Barcha film linklari
    """
    all_links = []

    for url in page_urls:
        try:
            links = await scrape_page_list_safe(config, browser, url)
            all_links.extend(links)
            logger.info(f"📄 {url} dan {len(links)} ta link topildi")
        except Exception as e:
            logger.error(f"❌ Sahifani o'qishda xato: {url} | {e}")

    logger.info(f"📊 Jami topilgan film linklari: {len(all_links)}")
    return all_links


async def batch_collect_links(config: dict, browser, page_urls: list[str],
                              batch_size: int = 5) -> list[dict]:
    """
    Listing sahifalarni batch'larda parallel tahlil qilish.

    Args:
        config: Sayt konfiguratsiyasi
        browser: Browser instance
        page_urls: Sahifa URLlari
        batch_size: Parallel tahlil uchun batch hajmi

    Returns:
        list[dict]: Barcha film linklari
    """
    all_links = []

    for i in range(0, len(page_urls), batch_size):
        batch = page_urls[i:i + batch_size]
        logger.info(f"📦 Batch {i//batch_size + 1}: {len(batch)} sahifa")

        # Batch ichidagi sahifalarni parallel tahlil qilish
        tasks = [
            scrape_page_list_safe(config, browser, url)
            for url in batch
        ]

        try:
            batch_results = await asyncio.gather(*tasks, return_exceptions=True)

            for j, result in enumerate(batch_results):
                if isinstance(result, Exception):
                    logger.error(
                        f"❌ Batch sahifada xato: {batch[j]} | {result}")
                elif isinstance(result, list):
                    all_links.extend(result)

        except Exception as e:
            logger.error(f"❌ Batch tahlilida xato: {e}")

        # Batch orasida kichik tanaffus
        await asyncio.sleep(1)

    logger.info(f"📊 Batch jarayoni yakunlandi: {len(all_links)} ta link")
    return all_links
