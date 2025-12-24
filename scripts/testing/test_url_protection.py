#!/usr/bin/env python3
"""
URL Protection Test - URL lar buzilmasligini tekshirish
"""

import sys
import os

# Project root'ni sys.path ga qo'shish
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)

from telegramuploader.core.uploader import TelegramUploader

async def test_url_protection():
    """URL himoya qilinishini test qilish"""
    print("🧪 URL Protection Test")
    print("=" * 60)
    
    # Test item with problematic URL
    test_item = {
        "title": "Janob olimpiya / Mister olimpia / Akauka Jo va Ben Vayderlar O'zbekcha",
        "categories": ["biography", "drama", "sport"],
        "year": "2018",
        "country": "SSHA",
        "actors": "Kevin Duran,Di Djey Kuolls,Djulianna Xaf",
        "language": "uz",
        "description": "Jo va Ben Uayder akaukalari — butun hayotini bodibildingni ommalashtirishga bag'ishlagan professional murabbiylar",
        "file_url": "https://fayllar1.ru/37/kinolar/Janob olimpiya 2018 1080p (asilmedia.net).mp4"
    }
    
    uploader = TelegramUploader()
    caption = await uploader._create_caption(test_item, 153 * 1024 * 1024 * 1024)  # 153 GB
    
    print("📝 Generated Caption:")
    print("-" * 60)
    print(caption)
    print("-" * 60)
    
    # URL tekshirish
    original_url = test_item["file_url"]
    print(f"\n🔍 URL Analysis:")
    print(f"Original URL: {original_url}")
    
    if "🔗" in caption:
        url_line = [line for line in caption.split('\n') if '🔗' in line][0]
        caption_url = url_line.replace('🔗 ', '')
        print(f"Caption URL:  {caption_url}")
        
        # URL integrity check
        url_intact = original_url == caption_url
        print(f"URL intact: {'✅' if url_intact else '❌'}")
        
        if not url_intact:
            print(f"❌ URL corruption detected!")
            print(f"   Missing chars: {set(original_url) - set(caption_url)}")
            print(f"   Extra chars:   {set(caption_url) - set(original_url)}")
        
        # Critical URL components check
        critical_parts = ['.ru', '.mp4', '://', '1080p', '(', ')', '.net']
        for part in critical_parts:
            if part in original_url:
                in_caption = part in caption_url
                print(f"   '{part}': {'✅' if in_caption else '❌'}")
    else:
        print("❌ URL not found in caption!")

async def test_different_urls():
    """Turli URL formatlarini test qilish"""
    print(f"\n{'='*60}")
    print("🔗 Different URL Formats Test")
    print("-" * 60)
    
    test_urls = [
        "https://example.com/file.mp4",
        "http://site.org/folder/file (copy).avi",
        "https://domain.net/path-with-dashes/file_name.mkv",
        "ftp://server.com:21/files/movie.2023.1080p.x264.mp4",
        "https://cdn.example.com/v1/files/movie%20name.mp4",
        "https://storage.googleapis.com/bucket/file.mp4?token=abc123"
    ]
    
    base_item = {
        "title": "Test Film",
        "categories": ["test"],
        "language": "test"
    }
    
    uploader = TelegramUploader()
    
    for i, url in enumerate(test_urls, 1):
        test_item = base_item.copy()
        test_item["file_url"] = url
        
        caption = await uploader._create_caption(test_item, 1024*1024*100)
        
        print(f"\n{i}. URL: {url}")
        
        if "🔗" in caption:
            url_line = [line for line in caption.split('\n') if '🔗' in line][0]
            caption_url = url_line.replace('🔗 ', '')
            
            intact = url == caption_url
            print(f"   Caption: {caption_url}")
            print(f"   Intact: {'✅' if intact else '❌'}")
            
            if not intact:
                print(f"   Original length: {len(url)}")
                print(f"   Caption length:  {len(caption_url)}")
        else:
            print(f"   ❌ URL not in caption (length: {len(url)})")

async def test_special_characters_in_urls():
    """URL dagi maxsus belgilarni test qilish"""
    print(f"\n{'='*60}")
    print("🔧 Special Characters in URLs Test")
    print("-" * 60)
    
    # Characters that might be affected by cleaning
    special_chars = ['.', '-', '_', '(', ')', '/', ':', '?', '=', '&', '%', '#']
    
    base_url = "https://example.com/file"
    
    for char in special_chars:
        test_url = f"{base_url}{char}test{char}.mp4"
        
        test_item = {
            "title": "Test",
            "file_url": test_url
        }
        
        uploader = TelegramUploader()
        caption = await uploader._create_caption(test_item, 1024*1024)
        
        if "🔗" in caption:
            url_line = [line for line in caption.split('\n') if '🔗' in line][0]
            caption_url = url_line.replace('🔗 ', '')
            
            char_preserved = char in caption_url
            print(f"'{char}': {'✅' if char_preserved else '❌'} - {test_url} → {caption_url}")
        else:
            print(f"'{char}': ❌ URL not found")

if __name__ == "__main__":
    import asyncio
    asyncio.run(test_url_protection())
    asyncio.run(test_different_urls())
    asyncio.run(test_special_characters_in_urls())