"""
Browser boshqaruvi va kontekst yaratish moduli.

Bu modul Playwright orqali browser sesssiyalarini boshqaradi va
optimal browser konfiguratsiyasini ta'minlaydi.
"""
import asyncio
from playwright.async_api import async_playwright, Browser, BrowserContext, Page
from utils.logger_core import logger


async def launch_browser(browser_config: dict) -> tuple:
    """
    Playwright browser ochish va asosiy sahifa yaratish.
    
    Args:
        browser_config: Browser konfiguratsiyasi
        
    Returns:
        tuple: (playwright_instance, browser, page)
    """
    try:
        pw = await async_playwright().start()
        browser_type = getattr(pw, browser_config["browser"])
        
        browser = await browser_type.launch(
            headless=browser_config["headless"], 
            slow_mo=browser_config["slow_mo"]
        )
        
        context = await browser.new_context(
            viewport=browser_config["viewport"],
            user_agent=browser_config["user_agent"],
            locale=browser_config["locale"],
            device_scale_factor=browser_config["device_scale_factor"],
            proxy=browser_config["proxy"],
            geolocation=browser_config["geolocation"],
            permissions=browser_config["permissions"],
        )
        
        page = await context.new_page()
        logger.info("🌐 Browser muvaffaqiyatli ishga tushirildi")
        
        return pw, browser, page
        
    except Exception as e:
        logger.error(f"❌ Browser ochishda xato: {e}")
        raise


async def create_browser_context(browser: Browser, config: dict = None) -> BrowserContext:
    """
    Yangi browser kontekst yaratish.
    
    Args:
        browser: Playwright browser instance
        config: Qo'shimcha kontekst konfiguratsiyasi
        
    Returns:
        BrowserContext: Yangi kontekst
    """
    try:
        context_config = config or {}
        context = await browser.new_context(**context_config)
        return context
    except Exception as e:
        logger.error(f"❌ Browser kontekst yaratishda xato: {e}")
        raise


async def create_new_page(browser: Browser, url: str = None) -> Page:
    """
    Yangi sahifa yaratish va ixtiyoriy URL ga o'tish.
    
    Args:
        browser: Browser instance
        url: O'tish uchun URL (ixtiyoriy)
        
    Returns:
        Page: Yangi sahifa
    """
    try:
        context = await browser.new_context()
        page = await context.new_page()
        
        if url:
            await page.goto(url, timeout=0)
            
        return page
    except Exception as e:
        logger.error(f"❌ Yangi sahifa yaratishda xato: {e}")
        raise


async def safe_page_goto(page: Page, url: str, retries: int = 3) -> bool:
    """
    Sahifaga xavfsiz o'tish va retry mexanizmi.
    
    Args:
        page: Page instance
        url: O'tish uchun URL
        retries: Qayta urinish soni
        
    Returns:
        bool: Muvaffaqiyatli yoki yo'q
    """
    for attempt in range(retries):
        try:
            await page.goto(url, timeout=30000)
            return True
        except Exception as e:
            logger.warning(f"⚠️ Sahifaga o'tishda xato (urinish {attempt + 1}/{retries}): {url} | {e}")
            if attempt < retries - 1:
                await asyncio.sleep(2)
            else:
                logger.error(f"❌ Sahifaga o'tib bo'lmadi: {url}")
                return False
    return False


async def cleanup_browser(pw, browser: Browser) -> None:
    """
    Browser va playwright resurslarini tozalash.
    
    Args:
        pw: Playwright instance
        browser: Browser instance
    """
    try:
        if browser:
            await browser.close()
        if pw:
            await pw.stop()
        logger.info("🧹 Browser resurslari tozalandi")
    except Exception as e:
        logger.error(f"❌ Browser tozalashda xato: {e}")