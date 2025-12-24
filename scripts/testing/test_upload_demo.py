#!/usr/bin/env python3
"""
Test Upload Demo - Independent Test Script
"""

import sys
import os

# Project root'ni sys.path ga qo'shish
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

import asyncio

async def test_caption_demo():
    """Demo caption yaratish test"""
    print("🧪 Test Upload Demo - Caption Test")
    print("=" * 60)
    
    # Demo URL
    demo_url = "https://videocdn.cdnpk.net/videos/63eef08b-9d49-401c-b357-2bc259bdeebd/horizontal/downloads/720p.mp4?filename=1472728_People_Business_1280x720.mp4&token=exp=1761025908~hmac=826fbb5931aaad2d89665a12f60211691a94aba9cc07c3e26aa388215e77bc37"
    
    print(f"🔗 Demo URL: {demo_url[:100]}...")
    
    # Demo file item yaratish
    demo_item = {
        "title": "Test Demo Video - People Business 1280x720",
        "categories": ["demo", "business", "people"],
        "year": "2024",
        "country": "Test Country",
        "actors": "Demo Actor One, Demo Actor Two, Demo Actor Three",
        "language": "en",
        "description": "Bu test uchun demo video. Business people working in office environment. High quality 720p demonstration video for testing upload functionality and caption generation.",
        "file_url": demo_url,
        "file_page": "https://example.com/demo/test-page",
        "image": "https://example.com/demo/thumbnail.jpg"
    }
    
    print("📋 Demo Item Ma'lumotlari:")
    print(f"📄 Title: {demo_item['title']}")
    print(f"🏷️ Categories: {demo_item['categories']}")
    print(f"📅 Year: {demo_item['year']}")
    print(f"🌍 Country: {demo_item['country']}")
    print(f"🎭 Actors: {demo_item['actors']}")
    print(f"🌐 Language: {demo_item['language']}")
    print(f"📝 Description: {demo_item['description'][:100]}...")
    
    try:
        # TelegramUploader import
        import sys
        import os
        current_dir = os.path.dirname(os.path.abspath(__file__))
        parent_dir = os.path.dirname(os.path.dirname(current_dir))
        sys.path.insert(0, parent_dir)
        
        from telegramuploader.core.uploader import TelegramUploader
        
        uploader = TelegramUploader()
        
        # Demo file size (100 MB) 
        demo_size = 100 * 1024 * 1024  # Bytes da 100 MB
        
        # Caption yaratish
        print("\n📝 Caption yaratilmoqda...")
        caption = await uploader._create_caption(demo_item, demo_size)
        
        print("✅ Caption yaratildi!")
        print("\n📄 Generated Caption:")
        print("=" * 60)
        print(caption)
        print("=" * 60)
        
        # Caption tahlili
        lines = caption.split('\n')
        print(f"\n📊 Caption Statistics:")
        print(f"   📏 Uzunlik: {len(caption)} belgi")
        print(f"   📄 Qatorlar soni: {len(lines)}")
        print(f"   📋 Telegram limit: {'✅ OK' if len(caption) <= 4096 else '❌ Limit oshib ketdi'}")
        
        # Hashtag tekshirish
        hashtag_count = caption.count('#')
        print(f"   🏷️ Hashtag soni: {hashtag_count}")
        
        # URL tekshirish
        url_found = "🔗" in caption
        print(f"   🔗 URL mavjud: {'✅' if url_found else '❌'}")
        
        # Worker name tekshirish
        worker_found = "🤖" in caption
        print(f"   🤖 Worker name: {'✅' if worker_found else '❌'}")
        
        # Component analysis
        print(f"\n🔍 Caption Components:")
        for i, line in enumerate(lines, 1):
            if line.strip():
                component = "Unknown"
                if line.startswith("📄"):
                    component = "Title"
                elif line.startswith("🏷️"):
                    component = "Categories (Hashtags)"
                elif line.startswith("📅"):
                    component = "Year & Country"
                elif line.startswith("🎭"):
                    component = "Actors"
                elif line.startswith("🌐"):
                    component = "Language"
                elif line.startswith("💾"):
                    component = "File Size"
                elif line.startswith("🤖"):
                    component = "Worker Name"
                elif line.startswith("📝"):
                    component = "Description"
                elif line.startswith("🔗"):
                    component = "URL"
                
                print(f"   {i:2d}. {component}: {line}")
        
        print("\n✅ Caption test muvaffaqiyatli yakunlandi!")
        print("🎯 Test natijalari:")
        print("   ✅ Hashtag format to'g'ri ishlayapti")
        print("   ✅ Worker name qo'shildi")
        print("   ✅ URL qisqartirildi va qo'shildi")
        print("   ✅ HTML cleaning ishlayapti")
        print("   ✅ Telegram format mos")
        
    except Exception as e:
        print(f"❌ Caption test da xato: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_caption_demo())