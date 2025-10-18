import asyncio
import os
import shutil
from pathlib import Path
from core.FileDB import FileDB
from core.db_info import print_all_file_urls
from filedownloader.legacy_adapter import download
from utils.logger_core import logger
from scraper import scrape, ScrapingOrchestrator, quick_scrape
from core.config import APP_CONFIG, BROWSER_CONFIG, DB_PATH
from core.site_configs import SITE_CONFIGS
from telegramuploader.legacy_adapter import download_and_upload, upload_only_mode
from utils.system_diagnostics import SystemDiagnostics


def safe_input(prompt: str, default: str = "") -> str:
    """Xavfsiz input - automated testing uchun"""
    try:
        return input(prompt).strip()
    except EOFError:
        logger.info(f"[AUTO] {prompt} → {default}")
        return default


async def main():
    logger.info("🚀 Files Project Scraper")
    logger.info("=" * 50)

    # 1️⃣ Avval config tanlaymiz
    logger.info("📋 Mavjud configlar:")
    configs_list = list(SITE_CONFIGS.keys())
    for i, name in enumerate(configs_list, start=1):
        logger.info(f"[{i}] {name}")

    # Special options without config
    logger.info("\n🔧 Sistema rejimlar:")
    logger.info("[info] System Diagnostics")
    logger.info("[clear-cache] Downloads papkasini tozalash")
    logger.info("[clear-db] Database faylini tozalash")

    choice = safe_input("\nTanlang (raqam yoki komanda) → ")

    # Sistema rejimlar - configsiz ishlaydi
    if choice.lower() == "info":
        logger.info("🔍 System Diagnostics ishga tushmoqda...")
        diagnostics = SystemDiagnostics()

        # Verbose mode uchun so'rash
        verbose_choice = safe_input(
            "Batafsil ko'rsatish? (y/n): ", "n").lower()
        verbose = verbose_choice in ['y', 'yes', 'ha']

        success = diagnostics.run_full_diagnostics(verbose=verbose)

        if success:
            logger.info("✅ Tizim tayyor!")
        else:
            logger.warning(
                "⚠️ Ba'zi muammolar topildi. system_diagnostics_report.txt faylini ko'ring.")

        logger.info("🎉 System Diagnostics yakunlandi!")
        return

    elif choice.lower() == "clear-cache":
        await clear_downloads_cache()
        return

    elif choice.lower() == "clear-db":
        await clear_database_file()
        return

    # Config tanlash
    if not choice.isdigit() or not (1 <= int(choice) <= len(configs_list)):
        logger.info("❌ Noto'g'ri tanlov!")
        return

    site_name = configs_list[int(choice) - 1]
    SITE_CONFIG = SITE_CONFIGS[site_name]
    SITE_CONFIG["name"] = site_name

    # Umumiy APP_CONFIG bilan birlashtiramiz
    CONFIG = {**APP_CONFIG, **SITE_CONFIG}

    # 2️⃣ Config tanlangandan keyin rejimlarni ko'rsatamiz
    await show_config_menu(CONFIG, site_name)


async def clear_downloads_cache():
    """Downloads papkasini tozalash"""
    downloads_path = Path("downloads")
    if downloads_path.exists():
        try:
            shutil.rmtree(downloads_path)
            downloads_path.mkdir(exist_ok=True)
            logger.info("✅ Downloads papkasi tozalandi!")
        except Exception as e:
            logger.error(f"❌ Downloads tozalashda xato: {e}")
    else:
        logger.info("📂 Downloads papkasi mavjud emas")

    logger.info("🎉 Cache tozalash yakunlandi!")


async def clear_database_file():
    """Database faylini tozalash"""
    try:
        if os.path.exists(DB_PATH):
            os.remove(DB_PATH)
            logger.info(f"✅ Database fayli o'chirildi: {DB_PATH}")
        else:
            logger.info("📂 Database fayli mavjud emas")
    except Exception as e:
        logger.error(f"❌ Database tozalashda xato: {e}")

    logger.info("🎉 Database tozalash yakunlandi!")


async def show_files_stats(site_name: str):
    """Fayllar statistikasini ko'rsatish"""
    db = FileDB()
    try:
        # Jami fayllar soni
        total_files = db.get_files_count(site_name)

        # Yuklangan fayllar (local_path mavjud)
        downloaded_files = db.get_downloaded_files_count(site_name)

        # Telegramga yuklangan fayllar
        uploaded_files = db.get_uploaded_files_count(site_name)

        # Yuklanmagan fayllar
        not_downloaded = total_files - downloaded_files
        # Manfiy bo'lmaslik uchun
        not_uploaded = max(0, downloaded_files - uploaded_files)

        logger.info("📊 FAYLLAR STATISTIKASI")
        logger.info("=" * 40)
        logger.info(f"📁 Site: {site_name}")
        logger.info(f"📋 Jami fayllar: {total_files}")
        logger.info(f"⬇️ Yuklangan: {downloaded_files}")
        logger.info(f"⬆️ Telegramga yuklangan: {uploaded_files}")
        logger.info(f"⏳ Yuklanmagan: {not_downloaded}")
        logger.info(f"📤 Upload qilinmagan: {not_uploaded}")
        logger.info(
            f"📈 Yuklanish foizi: {(downloaded_files/total_files*100) if total_files > 0 else 0:.1f}%")
        logger.info(
            f"📊 Upload foizi: {(uploaded_files/downloaded_files*100) if downloaded_files > 0 else 0:.1f}%")

    except Exception as e:
        logger.error(f"❌ Statistika olishda xato: {e}")


async def show_config_menu(CONFIG, site_name):
    """Config ichidagi rejimlarni ko'rsatish"""
    logger.info(f"\n🎯 Tanlangan Config: {site_name}")
    logger.info("=" * 50)

    # Fayllar statistikasini ko'rsatish
    await show_files_stats(site_name)

    logger.info("\n🎮 Mavjud rejimlar:")
    logger.info("[1] Scrape - yangi fayllarni topish")
    logger.info("[2] Download - fayllarni yuklash")
    logger.info("[3] Download + Upload - yuklash va Telegramga yuborish")
    logger.info("[4] Upload Only - faqat Telegramga yuborish")
    logger.info("[stats] Fayllar statistikasi")
    logger.info("[search] Fayl qidirish (nom/ID)")
    logger.info("[reset] Upload statusini reset qilish")
    logger.info("[clear] Bu config'dagi barcha fayllarni o'chirish")
    logger.info("[back] Bosh menyuga qaytish")

    mode = safe_input("\nRejimni tanlang → ")

    if mode == "1":
        await handle_scraping(CONFIG, site_name)
    elif mode == "2":
        await download(CONFIG)
    elif mode == "3":
        await download_and_upload(CONFIG)
    elif mode == "4":
        await upload_only_mode(CONFIG)
    elif mode.lower() == "stats":
        await show_files_stats(site_name)
    elif mode.lower() == "search":
        await search_files(site_name)
    elif mode.lower() == "reset":
        await reset_uploaded_status(site_name)
    elif mode.lower() == "clear":
        await clear_config_files(site_name)
    elif mode.lower() == "back":
        return
    else:
        logger.info("❌ Noto'g'ri tanlov!")
        return


async def handle_scraping(CONFIG, site_name):
    """Scraping rejimlarini boshqarish"""
    logger.info("\n🔍 Scraping rejimini tanlang:")
    logger.info("[1] Oddiy scraping")
    logger.info("[2] Quick scraping")

    scrape_mode = safe_input("Scraping turi → ")

    if scrape_mode == "1":
        logger.info("🚀 Scraping boshlandi...")
        result = await scrape(CONFIG, BROWSER_CONFIG)
        await show_scraping_results(result)
    elif scrape_mode == "2":
        pages_selection = safe_input("Sahifalar tanlovi (1-5, *, 1-10): ", "*")
        logger.info("⚡ Quick scraping boshlandi...")
        result = await quick_scrape(CONFIG, BROWSER_CONFIG, pages_selection)
        await show_scraping_results(result)
    else:
        logger.info("❌ Noto'g'ri tanlov!")


async def show_scraping_results(result):
    """Scraping natijalarini ko'rsatish"""
    if isinstance(result, dict):
        logger.info("📊 SCRAPING NATIJALARI:")
        logger.info(f"   Status: {result.get('status', 'unknown')}")
        if result.get('status') == 'success':
            logger.info(f"   📈 Topilgan: {result.get('total_found', 0)}")
            logger.info(f"   ✅ Muvaffaqiyatli: {result.get('successful', 0)}")
            logger.info(f"   � DB ga qo'shildi: {result.get('inserted', 0)}")
            logger.info(f"   ⏭️ Tashlab ketildi: {result.get('skipped', 0)}")

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
            logger.error(f"   ❌ Xato: {result.get('error', 'Unknown error')}")


async def reset_uploaded_status(site_name):
    """Bitta config'ga tegishli barcha fayllarning uploaded statusini reset qilish"""
    confirm = safe_input(
        f"⚠️ {site_name} dagi barcha fayllarning upload statusini reset qilishni tasdiqlaysizmi? (yes/no): ", "no").lower()

    if confirm in ['yes', 'y', 'ha']:
        try:
            db = FileDB()
            reset_count = db.reset_uploaded_status(site_name)
            logger.info(
                f"✅ {site_name} da {reset_count} ta faylning upload statusi reset qilindi")
            logger.info("📤 Endi bu fayllar qayta upload qilinishi mumkin")

            # Yangi statistikani ko'rsatish
            await show_files_stats(site_name)
        except Exception as e:
            logger.error(f"❌ Upload status reset qilishda xato: {e}")
    else:
        logger.info("❌ Bekor qilindi")


async def clear_config_files(site_name):
    """Bitta config'ga tegishli barcha fayllarni o'chirish"""
    confirm = safe_input(
        f"⚠️ {site_name} dagi barcha fayllarni o'chirishni tasdiqlaysizmi? (yes/no): ", "no").lower()

    if confirm in ['yes', 'y', 'ha']:
        try:
            db = FileDB()
            deleted_count = db.delete_files(site_name)
            logger.info(
                f"✅ {site_name} dan {deleted_count} ta fayl o'chirildi")
        except Exception as e:
            logger.error(f"❌ Fayllarni o'chirishda xato: {e}")
    else:
        logger.info("❌ Bekor qilindi")


async def search_files(site_name):
    """Fayl qidirish funksiyasi - nom yoki ID bo'yicha"""
    try:
        logger.info(f"\n🔍 {site_name} da kengaytirilgan fayl qidirish")
        logger.info("📋 Qidirish imkoniyatlari:")
        logger.info("   • Fayl ID (masalan: 123)")
        logger.info("   • Fayl nomi (masalan: Oila)")
        logger.info("   • Fayl path (masalan: downloads/film.mp4)")
        logger.info("   • Kategoriya, aktyorlar, mamlakat, til, yil")
        logger.info("   • Tavsif yoki URL qismi")
        
        search_query = safe_input("\n🔍 Qidiruv matnini kiriting → ").strip()
        if not search_query:
            logger.info("❌ Qidiruv so'zi kiritilmadi")
            return
            
        db = FileDB()
        files = db.get_files(site_name)
        
        # Kengaytirilgan qidiruv - ID, nom, filepath, description va boshqalar
        found_files = []
        search_lower = search_query.lower()
        
        # ID bo'yicha qidirish (raqam bo'lsa)
        if search_query.isdigit():
            file_id = int(search_query)
            for file in files:
                if file.get("id") == file_id:
                    found_files.append(file)
                    
        # Barcha fieldlar bo'yicha qidirish (oxshashlik)
        for file in files:
            # Faylni qo'shmaslik uchun tekshirish (ID bo'yicha allaqachon qo'shilgan bo'lishi mumkin)
            if file in found_files:
                continue
                
            # Qidirish fieldlari va ularning nomlari
            fields_to_search = [
                ("title", file.get("title", ""), "📄 Nom"),
                ("local_path", file.get("local_path", ""), "📁 Path"),
                ("description", file.get("description", ""), "📝 Tavsif"),
                ("categories", file.get("categories", ""), "🏷️ Kategoriya"),
                ("actors", file.get("actors", ""), "🎭 Aktyorlar"),
                ("country", file.get("country", ""), "🌍 Mamlakat"),
                ("language", file.get("language", ""), "🌐 Til"),
                ("year", file.get("year", ""), "📅 Yil"),
                ("file_url", file.get("file_url", ""), "🔗 URL"),
            ]
            
            # Har bir field da qidiruv
            for field_name, field_value, field_display in fields_to_search:
                if field_value and search_lower in str(field_value).lower():
                    # Topilgan fieldni saqlab qo'yamiz
                    file["_matched_field"] = field_display
                    file["_matched_value"] = str(field_value)
                    found_files.append(file)
                    break  # Bitta field da topilsa, boshqa fieldlarni tekshirmaslik
                
        if not found_files:
            logger.info(f"❌ '{search_query}' bo'yicha hech narsa topilmadi")
            return
            
        logger.info(f"✅ {len(found_files)} ta fayl topildi:")
        
        for i, file in enumerate(found_files, 1):
            logger.info(f"\n📁 [{i}] Fayl #{file.get('id', 'N/A')}")
            logger.info(f"📄 Nomi: {file.get('title', 'No title')}")
            
            # Qaysi field da topilganligini ko'rsatish
            if file.get("_matched_field"):
                matched_value = file.get("_matched_value", "")
                # Uzun matnni qisqartirish
                if len(matched_value) > 100:
                    matched_value = matched_value[:100] + "..."
                logger.info(f"🔍 Topildi: {file.get('_matched_field')} -> {matched_value}")
            
            logger.info(f"🏷️ Kategoriya: {file.get('categories', 'N/A')}")
            logger.info(f"🌐 Til: {file.get('language', 'N/A')}")
            logger.info(f"📅 Yil: {file.get('year', 'N/A')}")
            logger.info(f"🎭 Aktyorlar: {file.get('actors', 'N/A')}")
            
            # Path ma'lumotini ham ko'rsatish
            if file.get('local_path'):
                path_short = file.get('local_path')
                if len(path_short) > 80:
                    path_short = "..." + path_short[-77:]
                logger.info(f"📂 Path: {path_short}")
            
            # Status ma'lumotlari
            local_path = file.get('local_path')
            uploaded = file.get('uploaded', False)
            file_size = file.get('file_size', 0)
            
            if local_path and os.path.exists(local_path):
                logger.info(f"💾 Local: ✅ Yuklab olingan ({file_size} bytes)")
                logger.info(f"📁 Path: {local_path}")
            else:
                logger.info(f"💾 Local: ❌ Yuklanmagan")
                
            telegram_status = "✅ Yuklangan" if uploaded else "❌ Yuklanmagan"
            logger.info(f"📤 Telegram: {telegram_status}")
            
        # Fayl tanlash
        if len(found_files) == 1:
            selected_file = found_files[0]
        else:
            choice = safe_input(f"\nQaysi faylni tanlaysiz? (1-{len(found_files)}) → ")
            try:
                index = int(choice) - 1
                if 0 <= index < len(found_files):
                    selected_file = found_files[index]
                else:
                    logger.info("❌ Noto'g'ri raqam")
                    return
            except ValueError:
                logger.info("❌ Raqam kiriting")
                return
                
        # Tanlangan fayl uchun amallar
        await file_actions_menu(selected_file, site_name)
        
    except Exception as e:
        logger.error(f"❌ Qidirishda xato: {e}")


async def file_actions_menu(file_data, site_name):
    """Tanlangan fayl uchun amallar menyusi"""
    try:
        logger.info(f"\n🔧 Fayl #{file_data.get('id')} uchun amallar:")
        logger.info("[1] Ma'lumotlarni ko'rsatish")
        logger.info("[2] Telegram statusini RESET qilish (uploaded=False)")
        logger.info("[3] Telegram YUKLANGAN qilish (uploaded=True)")
        logger.info("[4] Faylni DATABASE dan o'chirish")
        logger.info("[5] Local faylni o'chirish (disk dan)")
        logger.info("[back] Orqaga")
        
        choice = safe_input("Amalni tanlang → ")
        
        if choice == "1":
            await show_file_details(file_data)
        elif choice == "2":
            await reset_file_upload_status(file_data)
        elif choice == "3":
            await mark_file_uploaded(file_data)
        elif choice == "4":
            await delete_file_from_db(file_data)
        elif choice == "5":
            await delete_local_file(file_data)
        elif choice.lower() == "back":
            return
        else:
            logger.info("❌ Noto'g'ri tanlov")
            
    except Exception as e:
        logger.error(f"❌ Amallar menyusida xato: {e}")


async def show_file_details(file_data):
    """Fayl haqida batafsil ma'lumot"""
    logger.info(f"\n📋 Fayl #{file_data.get('id')} - Batafsil ma'lumot:")
    logger.info("=" * 50)
    
    for key, value in file_data.items():
        if key == "description" and len(str(value)) > 100:
            logger.info(f"{key}: {str(value)[:100]}...")
        else:
            logger.info(f"{key}: {value}")


async def reset_file_upload_status(file_data):
    """Fayl upload statusini reset qilish"""
    try:
        file_id = file_data.get('id')
        title = file_data.get('title', 'No title')
        
        confirm = safe_input(f"⚠️ '{title}' ni RESET qilishni tasdiqlaysizmi? (y/n) → ")
        if confirm.lower() in ['y', 'yes', 'ha']:
            db = FileDB()
            db.update_file(file_id, uploaded=False, uploaded_at=None)
            logger.info(f"✅ Fayl #{file_id} upload statusi RESET qilindi")
        else:
            logger.info("❌ Bekor qilindi")
            
    except Exception as e:
        logger.error(f"❌ Reset qilishda xato: {e}")


async def mark_file_uploaded(file_data):
    """Faylni yuklangan deb belgilash"""
    try:
        file_id = file_data.get('id')
        title = file_data.get('title', 'No title')
        
        confirm = safe_input(f"✅ '{title}' ni YUKLANGAN qilishni tasdiqlaysizmi? (y/n) → ")
        if confirm.lower() in ['y', 'yes', 'ha']:
            db = FileDB()
            db.update_file(file_id, uploaded=True)
            logger.info(f"✅ Fayl #{file_id} YUKLANGAN deb belgilandi")
        else:
            logger.info("❌ Bekor qilindi")
            
    except Exception as e:
        logger.error(f"❌ Belgilashda xato: {e}")


async def delete_file_from_db(file_data):
    """Faylni database dan o'chirish"""
    try:
        file_id = file_data.get('id')
        title = file_data.get('title', 'No title')
        
        confirm = safe_input(f"⚠️ '{title}' ni DATABASE dan o'chirishni tasdiqlaysizmi? (y/n) → ")
        if confirm.lower() in ['y', 'yes', 'ha']:
            db = FileDB()
            # FileDB da delete_file methodi yo'q, manual SQL qilamiz
            conn = db._connect()
            c = conn.cursor()
            c.execute("DELETE FROM files WHERE id = ?", (file_id,))
            conn.commit()
            conn.close()
            
            logger.info(f"✅ Fayl #{file_id} DATABASE dan o'chirildi")
        else:
            logger.info("❌ Bekor qilindi")
            
    except Exception as e:
        logger.error(f"❌ Database dan o'chirishda xato: {e}")


async def delete_local_file(file_data):
    """Local faylni disk dan o'chirish"""
    try:
        local_path = file_data.get('local_path')
        title = file_data.get('title', 'No title')
        
        if not local_path:
            logger.info("❌ Local path mavjud emas")
            return
            
        if not os.path.exists(local_path):
            logger.info(f"❌ Fayl topilmadi: {local_path}")
            return
            
        confirm = safe_input(f"⚠️ '{title}' ni DISK dan o'chirishni tasdiqlaysizmi? (y/n) → ")
        if confirm.lower() in ['y', 'yes', 'ha']:
            os.remove(local_path)
            
            # Database da local_path ni None qilish
            db = FileDB()
            db.update_file(file_data.get('id'), local_path=None)
            
            logger.info(f"✅ Fayl disk dan o'chirildi: {local_path}")
        else:
            logger.info("❌ Bekor qilindi")
            
    except Exception as e:
        logger.error(f"❌ Faylni o'chirishda xato: {e}")


if __name__ == "__main__":
    asyncio.run(main())
    logger.info("🎉 Dastur yakunlandi !")
