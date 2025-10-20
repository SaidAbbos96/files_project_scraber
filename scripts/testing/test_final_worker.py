#!/usr/bin/env python3
"""
Final Worker Name Test - Real config dan worker nomini tekshirish
"""

import sys
import os

# Project root'ni sys.path ga qo'shish
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)

from core.config import WORKER_NAME
from telegramuploader.core.uploader import TelegramUploader

async def test_final_worker_caption():
    """Final worker name test"""
    print("🧪 Final Worker Name Test")
    print("=" * 50)
    
    print(f"🤖 Current WORKER_NAME from config: '{WORKER_NAME}'")
    
    # Sample item
    test_item = {
        "title": "Ajoyib Film",
        "categories": ["Drama"],
        "year": "2023", 
        "country": "O'zbekiston",
        "language": "O'zbek",
        "description": "Test tavsif"
    }
    
    uploader = TelegramUploader()
    caption = await uploader._create_caption(test_item, 1024*1024*100)  # 100MB
    
    print("\n📝 Real Caption:")
    print("-" * 50)
    print(caption)
    print("-" * 50)
    
    # Worker line tekshirish
    lines = caption.split('\n')
    worker_found = False
    
    for line in lines:
        if '🤖' in line:
            print(f"✅ Worker info topildi: {line}")
            worker_found = True
            break
    
    if not worker_found:
        print("❌ Worker info topilmadi!")
    
    print(f"\n📊 Caption uzunligi: {len(caption)} belgi")
    print(f"📊 Telegram limit: {'✅ OK' if len(caption) <= 4096 else '❌ Limit oshib ketdi'}")
    
    # Multi-worker scenario simulation
    print(f"\n{'='*50}")
    print("🔄 Multi-Worker Scenario")
    print("-" * 50)
    
    scenarios = [
        ("server_01", "Birinchi server"),
        ("backup_worker", "Backup server"),
        ("mobile_bot", "Mobil bot"),
        ("uzbek_films_main", "Asosiy Uzbek Films bot")
    ]
    
    for worker_name, description in scenarios:
        print(f"\n🤖 {worker_name} ({description})")
        
        # Simulate caption with this worker name
        simulated_caption = caption.replace(f"🤖 {WORKER_NAME}", f"🤖 {worker_name}")
        worker_line = [line for line in simulated_caption.split('\n') if '🤖' in line][0]
        print(f"   Caption da: {worker_line}")

if __name__ == "__main__":
    import asyncio
    asyncio.run(test_final_worker_caption())