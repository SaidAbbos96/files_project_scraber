"""
Sahifa ichidagi parsing - bitta film sahifasini tahlil qilish moduli.

Bu modul bitta film sahifasidan barcha kerakli ma'lumotlarni ajratib oladi:
- Film nomi, kategoriyalar, til
- Fayl URL va rasm
- Tavsif va boshqa meta-ma'lumotlar
"""
import asyncio
import aiohttp
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup

from core.config import FILE_MIN_SIZE, MAX_SIZE_BYTES
from utils.files import get_file_size, get_small_url
from utils.helpers import normalize_item_categories, normalize_category
from utils.logger_core import logger
from utils.text import (
    clean_title,
    normalize_description,
    normalize_item_fields,
    normalize_item_title,
)


async def fetch_page_html(url: str, timeout: int = 20) -> str | None:
    """
    Aiohttp orqali sahifani olish.

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
                logger.warning(f"⚠️ HTTP status {resp.status}: {url}")
                return None
    except asyncio.TimeoutError:
        logger.warning(f"⚠️ Timeout: {url}")
        return None
    except Exception as e:
        logger.warning(f"⚠️ aiohttp bilan yuklab bo'lmadi: {url} | {e}")
        return None


async def fetch_page_with_browser(browser, url: str) -> str | None:
    """
    Playwright orqali sahifani ochib HTML qaytaradi.

    Args:
        browser: Browser instance
        url: Yuklab olinadigan URL

    Returns:
        str | None: HTML matn yoki None
    """
    context = await browser.new_context()
    page = await context.new_page()
    try:
        await page.goto(url, timeout=30000)
        html = await page.content()
        return html
    except Exception as e:
        logger.warning(f"❌ Browser orqali ochilmadi: {url} | {e}")
        return None
    finally:
        await page.close()
        await context.close()


def parse_page_fields(config: dict, html: str, base_url: str) -> dict:
    item = {
        "file_page": base_url,
        "title": None,
        "categories": None,
        "language": None,
        "description": None,
        "file_url": None,
        "image": None,
    }

    soup = BeautifulSoup(html, "html.parser")
    base_domain = "{uri.scheme}://{uri.netloc}".format(uri=urlparse(base_url))

    # 🧾 Avval meta matnni oldindan ajratamiz
    meta_text = None
    if config["fields"].get("meta"):
        sel = config["fields"]["meta"].replace("::text", "").strip()
        el = soup.select_one(sel)
        if el:
            # Faqat ichki textni olish, HTML taglarni olib tashlash
            meta_text = el.get_text("\n", strip=True)

    # 🔹 meta_textni key-value dictionaryga ajratamiz
    meta_data = {}
    if meta_text:
        # Har bir qatorni parse qilamiz
        for line in meta_text.split("\n"):
            # Masalan: "Mamlakat: AQSh, Xorvatiya"
            parts = line.split(":", 1)
            if len(parts) == 2:
                key = parts[0].strip()
                val = parts[1].strip()
                meta_data[key] = val

    # 🧠 Endi boshqa fieldlarni qayta ishlaymiz
    for key, sel in config["fields"].items():
        if not sel or key == "meta":
            continue

        # Agar meta:Key ko‘rinishida bo‘lsa
        if sel.startswith("meta:"):
            meta_key = sel.split("meta:")[1].strip()
            value = meta_data.get(meta_key)
        else:
            # Standart selector ishlaydi
            selectors = [s.strip() for s in sel.split("|")]
            value = None
            for s in selectors:
                if "::text" in s:
                    el = soup.select_one(s.replace("::text", "").strip())
                    if el:
                        # Faqat ichki textni olish, HTML taglarni olib tashlash, bo'shliqlarni saqlash
                        value = el.get_text(" ", strip=True)
                elif "::attr(" in s:
                    q = s.split("::attr(")[0].strip()
                    attr = s.split("::attr(")[1].replace(")", "").strip()
                    el = soup.select_one(q)
                    if el:
                        value = el.get(attr)
                else:
                    el = soup.select_one(s)
                    if el:
                        # Faqat ichki textni olish, HTML taglarni olib tashlash, bo'shliqlarni saqlash
                        value = el.get_text(" ", strip=True)
                if value:
                    break

            # URL larni to‘liq URLga aylantirish
            if value and key in ["image", "file_url", "file_picture"]:
                if not value.startswith("http"):
                    value = urljoin(base_domain, value)

        item[key] = value
    return item


async def validate_and_optimize_file(item: dict) -> dict:
    """
    Fayl hajmini tekshiradi, kerak bo'lsa kichikroq variantni topadi.

    Args:
        item: Film ma'lumotlari

    Returns:
        dict: Optimallashtirilgan ma'lumotlar
    """
    if not item.get("file_url"):
        item["file_size"] = None
        return item

    try:
        async with aiohttp.ClientSession() as session:
            size = await get_file_size(session, item["file_url"])
            item["file_size"] = size  # Fayl hajmini saqlash

            # Faqat 1 MB dan katta fayllarni log qilamiz
            if size > FILE_MIN_SIZE:
                pass
                # logger.warning(
                #     f"📏 Fayl hajmi: ({size}) {size / (1024**3):.5f} GB")
            else:
                # Barcha variantlar katta
                # logger.warning(
                #     "❌ File juda 1mbdan ham kichkina, o'tkazib yuboramiz.")
                item["file_url"] = None
                return item

            # Agar fayl katta bo'lsa, kichikroq variantni izlaymiz
            if size > MAX_SIZE_BYTES:
                # logger.warning("🔍 Kichikroq variant izlanmoqda...")

                for attempt, quality in enumerate(["1080p", "720p", "480p"], start=1):
                    small_url = await get_small_url(item["file_page"], attempt)
                    if not small_url:
                        continue

                    new_size = await get_file_size(session, small_url)
                    if new_size > FILE_MIN_SIZE:
                        logger.info(
                            f"🔁 {quality} variant hajmi: {new_size / (1024**3):.2f} GB")

                        if new_size < MAX_SIZE_BYTES:
                            item["file_url"] = small_url
                            # Yangi fayl hajmini saqlash
                            item["file_size"] = new_size
                            logger.warning(
                                f"✅ Kichikroq fayl tanlandi: {quality}")
                            return item

                # Barcha variantlar katta
                # logger.warning(
                #     "❌ Barcha variantlar juda katta yoki mavjud emas.")
                item["file_url"] = None

    except Exception as e:
        logger.error(f"❌ Fayl hajmini tekshirishda xato: {e}")
        item["file_size"] = None

    return item


def clean_and_normalize_categories(raw_categories: str) -> str:
    """
    Kategoriyalarni tozalash va normalize qilish (uniq_categoies.py dan olingan logika).

    Args:
        raw_categories: Xom kategoriyalar string (vergul bilan ajratilgan)

    Returns:
        str: Tozalangan va normalize qilingan kategoriyalar
    """
    if not raw_categories:
        return "other"

    try:
        # Kategoriyalarni ajratish
        cats = raw_categories.split(",")
        mapped = set()

        for raw in cats:
            raw = raw.strip()
            if raw:
                normalized = normalize_category(raw)
                mapped.add(normalized)

        # Agar hech qanday kategoriya topilmasa
        if not mapped:
            mapped.add("other")

        # Sorted qilib qaytarish
        return ", ".join(sorted(mapped))

    except Exception as e:
        logger.error(f"❌ Kategoriyalarni tozalashda xato: {e}")
        return "other"


async def normalize_extracted_data(item: dict) -> dict:
    """
    Ajratilgan ma'lumotlarni normallash va tozalash.

    Args:
        item: Xom ma'lumotlar

    Returns:
        dict: Normallashtirilgan ma'lumotlar
    """
    try:
        # Title ni normallash
        item = normalize_item_title(item)

        # Maydonlarni normallash
        item = normalize_item_fields(
            item,
            keys_to_translate=["country", "actors", "categories"]
        )

        # ✅ YANGI: Kategoriyalarni uniq_categoies.py logikasi bilan tozalash
        if item.get("categories"):
            item["categories"] = clean_and_normalize_categories(
                item["categories"])
            logger.debug(f"🏷️ Kategoriyalar tozalandi: {item['categories']}")

        # Eski kategoriya normalizatsiyasi (fallback)
        item = normalize_item_categories(item)

        # Tavsifni normallash
        item = normalize_description(
            item,
            lang=item.get("language", "uz")
        )

        return item
    except Exception as e:
        logger.error(f"❌ Ma'lumotlarni normallashda xato: {e}")
        return item


async def scrape_file_page_safe(config: dict, browser, file_url: str) -> dict:
    """
    Sahifani yuklab, ma'lumotlarni ajratadi (aiohttp → browser fallback).

    Args:
        config: Sayt konfiguratsiyasi
        browser: Browser instance
        file_url: Film sahifa URL

    Returns:
        dict: Ajratilgan va normallashtirilgan ma'lumotlar
    """
    try:
        # Birinchi aiohttp orqali urinish
        html = await fetch_page_html(file_url)

        # Agar aiohttp bilan yuklanmasa, browser ishlatish
        if not html:
            html = await fetch_page_with_browser(browser, file_url)

        # Agar hali ham HTML topilmasa
        if not html:
            logger.error(f"❌ HTML yuklab olinmadi: {file_url}")
            return {"file_page": file_url, "file_url": None}

        # HTML dan ma'lumotlarni ajratish
        item = parse_page_fields(config, html, file_url)

        # Ma'lumotlarni normallash
        item = await normalize_extracted_data(item)

        # Fayl hajmini tekshirish va optimallash
        item = await validate_and_optimize_file(item)

        return item

    except Exception as e:
        logger.error(f"❌ Sahifani parsing qilishda xato: {file_url} | {e}")
        return {"file_page": file_url, "file_url": None, "error": str(e)}
