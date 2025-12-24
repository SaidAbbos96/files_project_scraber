"""
Migration script - eski scraper modulidan yangi scraping moduliga o'tish.

Bu script eski kodlarni yangi struktura bilan ishlatish uchun migration qiladi.
"""
import asyncio
from typing import Dict, Any

from utils.logger_core import logger

# Yangi scraping modulini import qilish
try:
    from scraper import scrape as new_scrape
    NEW_MODULE_AVAILABLE = True
    logger.info("✅ Yangi scraping moduli topildi")
except ImportError as e:
    NEW_MODULE_AVAILABLE = False
    logger.warning(f"⚠️ Yangi scraping moduli topilmadi: {e}")
    
    # Eski modullarni import qilish (fallback)
    try:
        from scraper.scraping import scrape as old_scrape
        logger.info("📦 Eski scraper moduli ishlatilmoqda")
    except ImportError:
        logger.error("❌ Eski scraper moduli ham topilmadi!")
        raise


async def migrate_scrape(config: Dict[str, Any], browser_config: Dict[str, Any]) -> Dict:
    """
    Scraping funksiyasini yangi yoki eski modul orqali ishga tushirish.
    
    Args:
        config: Sayt konfiguratsiyasi
        browser_config: Browser konfiguratsiyasi
        
    Returns:
        Dict: Scraping natijalari
    """
    try:
        if NEW_MODULE_AVAILABLE:
            logger.info("🚀 Yangi scraping moduli ishlatilmoqda...")
            return await new_scrape(config, browser_config)
        else:
            logger.info("📦 Eski scraper moduli ishlatilmoqda...")
            # Eski modul natijasi dict formatida bo'lmasligi mumkin
            await old_scrape(config, browser_config)
            return {"status": "completed", "method": "legacy"}
            
    except Exception as e:
        logger.error(f"❌ Migration scrape xato: {e}")
        return {"status": "error", "error": str(e)}


def check_module_compatibility() -> Dict[str, bool]:
    """
    Modullar mosligi va mavjudligini tekshirish.
    
    Returns:
        Dict: Compatibility ma'lumotlari
    """
    compatibility = {
        "new_scraping_module": False,
        "old_scraper_module": False,
        "can_migrate": False
    }
    
    # Yangi modulni tekshirish
    try:
        import scraper
        compatibility["new_scraping_module"] = True
        logger.info("✅ Yangi scraping moduli mavjud")
    except ImportError:
        logger.warning("⚠️ Yangi scraping moduli mavjud emas")
    
    # Eski modulni tekshirish
    try:
        import scraper
        compatibility["old_scraper_module"] = True
        logger.info("✅ Eski scraper moduli mavjud")
    except ImportError:
        logger.warning("⚠️ Eski scraper moduli mavjud emas")
    
    # Migration imkoniyatini tekshirish
    compatibility["can_migrate"] = (
        compatibility["new_scraping_module"] or 
        compatibility["old_scraper_module"]
    )
    
    return compatibility


def get_migration_recommendations() -> Dict[str, str]:
    """
    Migration tavsiyalari.
    
    Returns:
        Dict: Tavsiyalar
    """
    recommendations = {}
    compatibility = check_module_compatibility()
    
    if compatibility["new_scraping_module"]:
        recommendations["primary"] = "Yangi scraping modulini ishlatish tavsiya etiladi"
        recommendations["action"] = "scraper.runner.py ni scraping.scrape() ga o'tkazing"
        
    elif compatibility["old_scraper_module"]:
        recommendations["primary"] = "Eski scraper moduli ishlatilmoqda"
        recommendations["action"] = "Yangi scraping modulini o'rnating"
        
    else:
        recommendations["primary"] = "Hech qanday scraping moduli topilmadi"
        recommendations["action"] = "Scraping modulini qayta o'rnating"
    
    return recommendations


if __name__ == "__main__":
    # Migration test
    print("🔄 Migration test ishga tushirilmoqda...")
    
    compatibility = check_module_compatibility()
    print(f"📊 Compatibility: {compatibility}")
    
    recommendations = get_migration_recommendations()
    print(f"💡 Tavsiyalar: {recommendations}")
    
    if compatibility["can_migrate"]:
        print("✅ Migration mumkin")
    else:
        print("❌ Migration imkonsiz - modullar mavjud emas")