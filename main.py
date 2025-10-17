import asyncio
from core.FileDB import FileDB
from core.db_info import print_all_file_urls
from filedownloader.legacy_adapter import download
from utils.logger_core import logger
from scraper import scrape, ScrapingOrchestrator, quick_scrape
from core.config import APP_CONFIG, BROWSER_CONFIG
from core.site_configs import SITE_CONFIGS
from telegramuploader.legacy_adapter import download_and_upload
from utils.system_diagnostics import SystemDiagnostics


async def main():
    # 1️⃣ Avval rejimni tanlaymiz
    logger.info("🚀 Files Project Scraper")
    logger.info("=" * 50)
    logger.info("Rejimni tanlang:")
    logger.info("[0] Files list ni ko'rsatish")
    logger.info("[1] Scrape (asosiy)")
    logger.info("[1a] Quick Scrape (avtomatik)")
    logger.info("[2] Download (faqat yuklash)")
    logger.info("[3] Download + Upload (Telegramga yuborish)")
    logger.info("[info/test] System Diagnostics (tizimni tekshirish)")
    logger.info("[x] Delete files from DB")

    mode = input("Rejimni tanlang → ").strip()

    # 🔍 System Diagnostics - configsiz ishlaydi
    if mode.lower() in ["info", "test", "diagnostics"]:
        logger.info("🔍 System Diagnostics ishga tushmoqda...")
        diagnostics = SystemDiagnostics()
        success = diagnostics.run_full_diagnostics()

        if success:
            logger.info("\n✅ Tizim tayyor!")
        else:
            logger.warning(
                "\n⚠️ Ba'zi muammolar topildi. fix_system.sh faylini ishga tushiring.")

        # Dasturni yakunlaymiz
        logger.info("🎉 System Diagnostics yakunlandi!")
        return

    # 2️⃣ Keyin config tanlaymize (faqat zarur bo'lsa)
    logger.info("\n📋 Mavjud configlar:")
    configs_list = list(SITE_CONFIGS.keys())
    for i, name in enumerate(configs_list, start=1):
        logger.info(f"[{i}] {name}")

    choice = input("Qaysi configni ishlatamiz? raqamini kiriting → ").strip()

    if not choice.isdigit() or not (1 <= int(choice) <= len(configs_list)):
        logger.info("❌ Noto'g'ri tanlov!")
        return

    site_name = configs_list[int(choice) - 1]
    SITE_CONFIG = SITE_CONFIGS[site_name]
    SITE_CONFIG["name"] = site_name

    # Umumiy APP_CONFIG bilan birlashtiramiz
    CONFIG = {**APP_CONFIG, **SITE_CONFIG}

    # 3️⃣ Tanlangan rejimni bajaramiz
    logger.info(f"\n🎯 Rejim: {mode} | Config: {site_name}")
    logger.info("=" * 50)

    if mode == "1":
        # Asosiy scraping
        logger.info("🚀 Yangi scraping moduli ishlatilmoqda...")
        result = await scrape(CONFIG, BROWSER_CONFIG)

        # Natijalarni ko'rsatish
        if isinstance(result, dict):
            logger.info("📊 SCRAPING NATIJALARI:")
            logger.info(f"   Status: {result.get('status', 'unknown')}")
            if result.get('status') == 'success':
                logger.info(f"   📈 Topilgan: {result.get('total_found', 0)}")
                logger.info(
                    f"   ✅ Muvaffaqiyatli: {result.get('successful', 0)}")
                logger.info(
                    f"   💾 DB ga qo'shildi: {result.get('inserted', 0)}")
                logger.info(
                    f"   ⏭️ Tashlab ketildi: {result.get('skipped', 0)}")

                # Performance statistika
                stats = result.get('stats', {})
                if stats:
                    logger.info(
                        f"   ⏱️ Vaqt: {stats.get('duration_seconds', 0):.2f}s")
                    logger.info(
                        f"   🏃 Tezlik: {stats.get('items_per_second', 0):.2f} item/s")
                    logger.info(
                        f"   📊 Muvaffaqiyat: {stats.get('success_rate', 0):.1f}%")
            elif result.get('status') == 'cancelled':
                logger.info("   🚫 Foydalanuvchi tomonidan bekor qilindi")
            elif result.get('status') == 'failed':
                logger.warning(
                    f"   ⚠️ Muvaffaqiyatsiz: {result.get('reason', 'Unknown')}")
            else:
                logger.error(
                    f"   ❌ Xato: {result.get('error', 'Unknown error')}")

    elif mode == "1a":
        # Quick scraping (input so'ramasdan)
        logger.info("⚡ Quick scraping boshlandi...")
        pages_selection = input(
            "Sahifalar tanlovi (1-5, *, 1-10): ").strip() or "*"
        result = await quick_scrape(CONFIG, BROWSER_CONFIG, pages_selection)
        logger.info(f"✅ Quick scraping yakunlandi: {result.get('status')}")

    elif mode == "1b":
        # Advanced scraping with orchestrator
        logger.info("🎛️ Advanced scraping boshlandi...")
        orchestrator = ScrapingOrchestrator(CONFIG, BROWSER_CONFIG)
        result = await orchestrator.run_scraping_process()

        # Detailed results display
        logger.info("📊 ADVANCED SCRAPING NATIJALARI:")
        for key, value in result.items():
            if key == 'stats' and isinstance(value, dict):
                logger.info("   📈 Performance Stats:")
                for stat_key, stat_value in value.items():
                    logger.info(f"      {stat_key}: {stat_value}")
            else:
                logger.info(f"   {key}: {value}")
    elif mode == "2":
        await download(CONFIG)
    elif mode == "3":
        await download_and_upload(CONFIG)

    elif mode == "0":
        await print_all_file_urls(site_name)
    elif mode == "x":
        db = FileDB()
        db.delete_files(site_name)
        logger.info(f"❌ Files in {site_name} deleted from DB.")
    else:
        logger.info("❌ Noto'g'ri tanlov!")
        exit(1)


if __name__ == "__main__":
    asyncio.run(main())
    logger.info("🎉 Dastur yakunlandi !")
