#!/usr/bin/env python3
"""
Timeout olib tashlash testlari
"""

import asyncio
import os
import sys
import time
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from telegramuploader.orchestrator import TelegramUploaderOrchestrator
from telegramuploader.core.uploader import TelegramUploader
from utils.logger_core import logger

async def test_no_timeout_upload():
    """Timeout yo'q upload test"""
    
    logger.info("🧪 Timeout yo'q upload test boshlandi")
    
    try:
        # Test config
        config = {
            "telegram_group": "@tech_files_io",  # Test group
        }
        
        # Orchestrator yaratish
        orchestrator = TelegramUploaderOrchestrator(config)
        
        # Test file yaratish (50MB)
        test_file = Path("/tmp/test_upload_50mb.txt")
        logger.info(f"📁 Test file yaratilmoqda: {test_file}")
        
        # 50MB test file yaratish
        with open(test_file, "w") as f:
            for i in range(50 * 1024):  # 50MB ≈ 50*1024 lines * 1KB/line
                f.write(f"Test line {i:08d} " + "x" * 1000 + "\n")
        
        file_size = test_file.stat().st_size
        logger.info(f"📏 Test file size: {file_size / (1024*1024):.1f} MB")
        
        # Direct uploader test
        uploader = TelegramUploader()
        
        start_time = time.time()
        logger.info("🚀 Upload boshlandi - timeout yo'q!")
        
        # Upload qilish uchun item va config tayyorlash
        item = {
            "title": "Test Upload File 50MB",
            "local_path": str(test_file),  # Bu key kerak
            "file_url": f"file://{test_file}",
            "file_size": file_size
        }
        
        config = {
            "telegram_group": "@tech_files_io"
        }
        
        result = await uploader.upload_file(item, config)
        
        duration = time.time() - start_time
        logger.info(f"⏱️ Upload vaqti: {duration:.1f} soniya ({duration/60:.1f} daqiqa)")
        
        if result:
            logger.info("✅ TEST MUVAFFAQIYATLI: Timeout yo'q upload ishladi!")
        else:
            logger.error("❌ TEST FAILED: Upload xatolik")
            
        # Test file ni o'chirish
        test_file.unlink()
        logger.info("🗑️ Test file o'chirildi")
        
        return result
        
    except Exception as e:
        logger.error(f"❌ Test xatolik: {e}")
        return False

async def test_large_file_upload():
    """Katta file (300MB ga yaqin) upload test"""
    
    logger.info("🧪 Katta file upload test boshlandi")
    
    try:
        # 200MB test file yaratish
        test_file = Path("/tmp/test_large_upload_200mb.txt")
        logger.info(f"📁 Katta test file yaratilmoqda: {test_file}")
        
        # 200MB test file yaratish
        with open(test_file, "w") as f:
            for i in range(200 * 1024):  # 200MB
                f.write(f"Large test line {i:08d} " + "x" * 1000 + "\n")
        
        file_size = test_file.stat().st_size
        logger.info(f"📏 Katta test file size: {file_size / (1024*1024):.1f} MB")
        
        uploader = TelegramUploader()
        
        start_time = time.time()
        logger.info("🚀 Katta file upload boshlandi - timeout yo'q!")
        
        # Upload qilish uchun item va config tayyorlash
        item = {
            "title": "Test Large Upload File 200MB",
            "local_path": str(test_file),  # Bu key kerak
            "file_url": f"file://{test_file}",
            "file_size": file_size
        }
        
        config = {
            "telegram_group": "@tech_files_io"
        }
        
        result = await uploader.upload_file(item, config)
        
        duration = time.time() - start_time
        logger.info(f"⏱️ Katta file upload vaqti: {duration:.1f} soniya ({duration/60:.1f} daqiqa)")
        
        if result:
            logger.info("✅ KATTA FILE TEST MUVAFFAQIYATLI!")
        else:
            logger.error("❌ KATTA FILE TEST FAILED")
            
        # Test file ni o'chirish
        test_file.unlink()
        logger.info("🗑️ Katta test file o'chirildi")
        
        return result
        
    except Exception as e:
        logger.error(f"❌ Katta file test xatolik: {e}")
        return False

async def main():
    """Main test runner"""
    
    logger.info("=" * 60)
    logger.info("🧪 TIMEOUT YO'Q UPLOAD TESTLARI")
    logger.info("=" * 60)
    
    # Test 1: Kichik file
    logger.info("\n📋 TEST 1: 50MB file upload")
    result1 = await test_no_timeout_upload()
    
    # Test 2: Katta file  
    logger.info("\n📋 TEST 2: 200MB file upload")
    result2 = await test_large_file_upload()
    
    # Natijalar
    logger.info("\n" + "=" * 60)
    logger.info("📊 TEST NATIJALARI:")
    logger.info(f"  50MB upload:  {'✅ PASS' if result1 else '❌ FAIL'}")
    logger.info(f"  200MB upload: {'✅ PASS' if result2 else '❌ FAIL'}")
    
    if result1 and result2:
        logger.info("🎉 BARCHA TESTLAR MUVAFFAQIYATLI - TIMEOUT MUAMMOSI HAL QILINDI!")
    else:
        logger.error("⚠️ Ba'zi testlar failed")
    
    logger.info("=" * 60)

if __name__ == "__main__":
    asyncio.run(main())