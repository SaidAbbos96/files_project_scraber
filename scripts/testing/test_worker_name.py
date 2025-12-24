#!/usr/bin/env python3
"""
Worker Name Test - Telegram caption'da worker nomini tekshirish
"""

import sys
import os

# Project root'ni sys.path ga qo'shish
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)

# Set environment variable for testing
os.environ['WORKER_NAME'] = 'test_worker_123'

from telegramuploader.core.uploader import TelegramUploader
from core.config import WORKER_NAME

async def test_worker_name_in_caption():
    """Worker nomining caption'da paydo bo'lishini test qilish"""
    print("🧪 Worker Name Caption Test")
    print("=" * 50)
    
    print(f"🤖 Environment WORKER_NAME: {WORKER_NAME}")
    
    # Test item
    test_item = {
        "title": "Test Film Nomi",
        "categories": ["Drama", "Comedy"],
        "year": "2023",
        "country": "O'zbekiston",
        "actors": "Actor One, Actor Two",
        "language": "O'zbek",
        "description": "Bu test film haqida qisqacha ma'lumot.",
        "file_url": "https://example.com/file.mp4"
    }
    
    # TelegramUploader instance
    uploader = TelegramUploader()
    
    # Caption yaratish
    file_size = 1024 * 1024 * 500  # 500 MB
    caption = await uploader._create_caption(test_item, file_size)
    
    print("\n📝 Generated Caption:")
    print("-" * 50)
    print(caption)
    print("-" * 50)
    
    # Worker name mavjudligini tekshirish
    worker_line = f"🤖 {WORKER_NAME}"
    if worker_line in caption:
        print(f"✅ Worker name topildi: {worker_line}")
    else:
        print(f"❌ Worker name topilmadi!")
        print(f"   Qidirildi: {worker_line}")
    
    # Caption struktura tekshiruvi
    lines = caption.strip().split('\n')
    print(f"\n📊 Caption Struktura ({len(lines)} qator):")
    for i, line in enumerate(lines, 1):
        print(f"  {i:2d}. {line}")
    
    # Worker name qaysi qatorda ekanligini aniqlash
    for i, line in enumerate(lines, 1):
        if "🤖" in line:
            print(f"\n🎯 Worker info {i}-qatorda: {line}")
            break

def test_different_worker_names():
    """Turli worker nomlari bilan test"""
    print(f"\n{'='*50}")
    print("🔄 Multiple Worker Names Test")
    print("-" * 50)
    
    test_workers = [
        "worker_001",
        "scraper_main",
        "server_01",
        "uzbek_films_bot",
        "backup_worker"
    ]
    
    for worker_name in test_workers:
        # Environment'ni o'zgartirish
        os.environ['WORKER_NAME'] = worker_name
        
        # Config'ni qayta yuklash
        from importlib import reload
        import core.config as config_module
        reload(config_module)
        
        # Worker nomini chop etish
        print(f"🤖 Testing: {worker_name}")
        print(f"   Config value: {config_module.WORKER_NAME}")

def test_caption_length_with_worker():
    """Worker name bilan caption uzunligini tekshirish"""
    print(f"\n{'='*50}")
    print("📏 Caption Length Test")
    print("-" * 50)
    
    # Long description bilan test
    long_item = {
        "title": "Juda Uzun Nomli Film - Fantastik Sarguzasht",
        "categories": ["Drama", "Comedy", "Action", "Adventure", "Sci-Fi"],
        "year": "2023",
        "country": "O'zbekiston, AQSh, Yaponiya",
        "actors": "Birinchi Actor Ismi, Ikkinchi Actor Ismi, Uchinchi Actor Ismi, To'rtinchi Actor Ismi",
        "language": "O'zbek, Ingliz, Yapon",
        "description": "Bu juda uzun tavsif. " * 20,  # Long description
        "file_url": "https://very-long-domain-name.example.com/very/long/path/to/file.mp4"
    }
    
    from telegramuploader.core.uploader import TelegramUploader
    uploader = TelegramUploader()
    
    # Different file sizes
    test_sizes = [
        1024 * 1024,        # 1 MB
        1024 * 1024 * 500,  # 500 MB
        1024 * 1024 * 1024 * 2  # 2 GB
    ]
    
    import asyncio
    
    async def test_all_sizes():
        for size in test_sizes:
            caption = await uploader._create_caption(long_item, size)
            print(f"\n📊 Size: {size // (1024*1024)} MB")
            print(f"   Caption length: {len(caption)} characters")
            print(f"   Within Telegram limit: {'✅' if len(caption) <= 4096 else '❌'}")
            
            # Worker name mavjudligini tekshirish
            worker_found = "🤖" in caption
            print(f"   Worker name included: {'✅' if worker_found else '❌'}")
    
    asyncio.run(test_all_sizes())

if __name__ == "__main__":
    import asyncio
    asyncio.run(test_worker_name_in_caption())
    test_different_worker_names()
    test_caption_length_with_worker()