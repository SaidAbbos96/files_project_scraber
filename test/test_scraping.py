"""
Test script - yangi scraping modulini test qilish.

Bu script yangi scraping modulining asosiy funksiyalarini
tekshiradi va muammolarni aniqlaydi.
"""
from utils.logger_core import logger
import asyncio
import sys
from pathlib import Path

# Path ni sozlash
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))


async def test_imports():
    """
    Barcha importlarni test qilish.
    """
    print("🧪 Importlarni test qilish...")

    tests = []

    # Asosiy modul
    try:
        import scraper
        tests.append(("✅", "scraping moduli", "OK"))
    except ImportError as e:
        tests.append(("❌", "scraping moduli", f"XATO: {e}"))

    # Browser moduli
    try:
        from scraper import launch_browser, cleanup_browser
        tests.append(("✅", "browser funksiyalari", "OK"))
    except ImportError as e:
        tests.append(("❌", "browser funksiyalari", f"XATO: {e}"))

    # Workers moduli
    try:
        from scraper import collect_items_parallel, WorkerPool
        tests.append(("✅", "workers funksiyalari", "OK"))
    except ImportError as e:
        tests.append(("❌", "workers funksiyalari", f"XATO: {e}"))

    # Parsers moduli
    try:
        from scraper.parsers import scrape_file_page_safe, collect_links
        tests.append(("✅", "parsers funksiyalari", "OK"))
    except ImportError as e:
        tests.append(("❌", "parsers funksiyalari", f"XATO: {e}"))

    # Orchestrator
    try:
        from scraper import ScrapingOrchestrator
        tests.append(("✅", "ScrapingOrchestrator", "OK"))
    except ImportError as e:
        tests.append(("❌", "ScrapingOrchestrator", f"XATO: {e}"))

    # Migration
    try:
        from scraper.migration import migrate_scrape
        tests.append(("✅", "migration funksiyalari", "OK"))
    except ImportError as e:
        tests.append(("❌", "migration funksiyalari", f"XATO: {e}"))

    # Natijalarni chop etish
    print("\n📊 Import test natijalari:")
    for status, module, result in tests:
        print(f"{status} {module}: {result}")

    # Umumiy natija
    failed_count = len([t for t in tests if t[0] == "❌"])
    if failed_count == 0:
        print("\n🎉 Barcha importlar muvaffaqiyatli!")
        return True
    else:
        print(f"\n⚠️ {failed_count} ta import xatosi topildi")
        return False


async def test_browser_functionality():
    """
    Browser funksiyalarini test qilish.
    """
    print("\n🌐 Browser funksiyalarini test qilish...")

    try:
        from scraper.browser import launch_browser, cleanup_browser

        # Test browser config
        test_config = {
            "browser": "chromium",
            "headless": True,
            "slow_mo": 0,
            "viewport": {"width": 1280, "height": 720},
            "user_agent": "Mozilla/5.0 (Test)",
            "locale": "en-US",
            "device_scale_factor": 1,
            "proxy": None,
            "geolocation": None,
            "permissions": []
        }

        print("🚀 Browser ochilmoqda...")
        pw, browser, page = await launch_browser(test_config)

        print("✅ Browser muvaffaqiyatli ochildi")

        # Test sahifaga o'tish
        await page.goto("https://httpbin.org/get", timeout=10000)
        print("✅ Test sahifaga muvaffaqiyatli o'tildi")

        # Browser yopish
        await cleanup_browser(pw, browser)
        print("✅ Browser muvaffaqiyatli yopildi")

        return True

    except Exception as e:
        print(f"❌ Browser test xato: {e}")
        return False


def test_configuration_validation():
    """
    Konfiguratsiya validatsiyasini test qilish.
    """
    print("\n⚙️ Konfiguratsiya validatsiyasini test qilish...")

    # Test config
    test_config = {
        "name": "test_site",
        "base_url": "https://example.com",
        "pagination_link": "https://example.com/page/{page}/",
        "pagination_selector": "a.last",
        "card_selector": ".film-card",
        "scrape_concurrency": 3,
        "fields": {
            "title": "h1.title::text",
            "file_url": "a.download::attr(href)",
            "description": ".description::text"
        }
    }

    required_fields = ["name", "base_url", "fields"]
    missing_fields = []

    for field in required_fields:
        if field not in test_config:
            missing_fields.append(field)

    if missing_fields:
        print(f"❌ Yo'q maydonlar: {missing_fields}")
        return False
    else:
        print("✅ Konfiguratsiya to'liq")
        return True


def test_utility_functions():
    """
    Yordamchi funksiyalarni test qilish.
    """
    print("\n🛠️ Yordamchi funksiyalarni test qilish...")

    tests = []

    # Workers validatsiyasi
    try:
        from scraper.workers import validate_item

        # Valid item
        valid_item = {
            "file_url": "https://example.com/file.mp4", "title": "Test"}
        if validate_item(valid_item):
            tests.append(("✅", "validate_item (valid)", "OK"))
        else:
            tests.append(("❌", "validate_item (valid)", "False qaytardi"))

        # Invalid item (telegram link)
        invalid_item = {"file_url": "https://t.me/channel", "title": "Test"}
        if not validate_item(invalid_item):
            tests.append(("✅", "validate_item (invalid)", "OK"))
        else:
            tests.append(("❌", "validate_item (invalid)", "True qaytardi"))

    except Exception as e:
        tests.append(("❌", "validate_item", f"XATO: {e}"))

    # Migration compatibility
    try:
        from scraper.migration import check_module_compatibility
        compatibility = check_module_compatibility()
        if isinstance(compatibility, dict):
            tests.append(("✅", "check_module_compatibility", "OK"))
        else:
            tests.append(
                ("❌", "check_module_compatibility", "Dict qaytarmadi"))
    except Exception as e:
        tests.append(("❌", "check_module_compatibility", f"XATO: {e}"))

    # Natijalar
    print("\n📊 Utility test natijalari:")
    for status, func, result in tests:
        print(f"{status} {func}: {result}")

    failed_count = len([t for t in tests if t[0] == "❌"])
    return failed_count == 0


async def run_full_test():
    """
    To'liq test suite ishga tushirish.
    """
    print("🧪 Yangi scraping moduli - To'liq test\n")

    results = []

    # 1. Import testlari
    import_ok = await test_imports()
    results.append(("Import testlari", import_ok))

    # 2. Browser testlari (faqat import muvaffaqiyatli bo'lsa)
    if import_ok:
        try:
            browser_ok = await test_browser_functionality()
            results.append(("Browser testlari", browser_ok))
        except Exception as e:
            print(f"❌ Browser test o'tkazib yuborildi: {e}")
            results.append(("Browser testlari", False))
    else:
        print("⏭️ Browser testlari o'tkazib yuborildi (import xatosi)")
        results.append(("Browser testlari", False))

    # 3. Konfiguratsiya testlari
    config_ok = test_configuration_validation()
    results.append(("Konfiguratsiya testlari", config_ok))

    # 4. Utility testlari
    utility_ok = test_utility_functions()
    results.append(("Utility testlari", utility_ok))

    # Umumiy natijalar
    print("\n" + "="*50)
    print("📋 TO'LIQ TEST NATIJALARI:")
    print("="*50)

    total_tests = len(results)
    passed_tests = len([r for r in results if r[1]])

    for test_name, passed in results:
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"{status} {test_name}")

    print(f"\n📊 Umumiy: {passed_tests}/{total_tests} test o'tdi")

    if passed_tests == total_tests:
        print("🎉 Barcha testlar muvaffaqiyatli o'tdi!")
        print("✅ Yangi scraping moduli ishlatishga tayyor!")
    else:
        print(f"⚠️ {total_tests - passed_tests} ta test muvaffaqiyatsiz")
        print("🔧 Muammolarni hal qilib, qayta test qiling")

    return passed_tests == total_tests


if __name__ == "__main__":
    try:
        # Async testni ishga tushirish
        success = asyncio.run(run_full_test())

        if success:
            print("\n🚀 Modului ishlatish uchun:")
            print("from scraping import scrape")
            print("result = await scrape(CONFIG, BROWSER_CONFIG)")
            sys.exit(0)
        else:
            print("\n🛠️ Muammolarni hal qiling va qayta urinib ko'ring")
            sys.exit(1)

    except KeyboardInterrupt:
        print("\n🚫 Test to'xtatildi")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Test jarayonida xato: {e}")
        sys.exit(1)
