#!/usr/bin/env python3
"""
Hashtag Format Test - Caption da hashtag formatini tekshirish
"""

import sys
import os

# Project root'ni sys.path ga qo'shish
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)

from telegramuploader.core.uploader import TelegramUploader

async def test_hashtag_formatting():
    """Hashtag formatini test qilish"""
    print("🧪 Hashtag Format Test")
    print("=" * 60)
    
    # Test item
    test_item = {
        "title": "Janob olimpiya / Mister olimpia / Akauka Jo va Ben Vayderlar O'zbekcha",
        "categories": ["biography", "drama", "sport"],
        "year": "2018",
        "country": "SSHA",
        "actors": "Kevin Duran, Di Djey Kuolls, Djulianna Xaf",
        "language": "uz",
        "description": "Jo va Ben Uayder akaukalari professional murabbiylar",
        "file_url": "https://example.com/file.mp4"
    }
    
    uploader = TelegramUploader()
    caption = await uploader._create_caption(test_item, 153 * 1024 * 1024 * 1024)  # 153 GB
    
    print("📝 Generated Caption:")
    print("-" * 60)
    print(caption)
    print("-" * 60)
    
    # Hashtag tekshirish
    lines = caption.split('\n')
    for line in lines:
        if '🏷️' in line:
            print(f"\n🏷️ Categories line: {line}")
            
            # Hashtag counting
            hashtag_count = line.count('#')
            print(f"   Hashtag count: {hashtag_count}")
            
            if hashtag_count > 0:
                hashtags = [part for part in line.split() if part.startswith('#')]
                print(f"   Hashtags found: {hashtags}")
            else:
                print(f"   ❌ No hashtags found in categories!")

async def test_different_categories():
    """Turli kategoriya formatlarini test qilish"""
    print(f"\n{'='*60}")
    print("🏷️ Different Categories Test")
    print("-" * 60)
    
    test_cases = [
        ["drama", "comedy", "action"],
        ["Sci-Fi", "Adventure", "Family"],
        ["crime thriller", "psychological drama"],
        ["Uzbek Films", "Tarjima Kinolar"],
        ["2023 Films", "HD Quality"],
        ["biography", "drama", "sport"]  # Original case
    ]
    
    base_item = {
        "title": "Test Film",
        "year": "2023",
        "language": "uz"
    }
    
    uploader = TelegramUploader()
    
    for i, categories in enumerate(test_cases, 1):
        test_item = base_item.copy()
        test_item["categories"] = categories
        
        caption = await uploader._create_caption(test_item, 1024*1024*100)
        
        print(f"\n{i}. Categories: {categories}")
        
        # Find categories line
        category_line = None
        for line in caption.split('\n'):
            if '🏷️' in line:
                category_line = line
                break
        
        if category_line:
            print(f"   Result: {category_line}")
            
            # Hashtag analysis
            hashtags = [part for part in category_line.split() if part.startswith('#')]
            print(f"   Hashtags: {hashtags}")
        else:
            print(f"   ❌ Categories line not found!")

async def test_hashtag_cleaning():
    """Hashtag cleaning jarayonini tekshirish"""
    print(f"\n{'='*60}")
    print("🧹 Hashtag Cleaning Test")
    print("-" * 60)
    
    # Problematic categories
    problematic_categories = [
        "Crime & Thriller",
        "Sci-Fi/Fantasy",
        "Action/Adventure",
        "Drama (Psychological)",
        "Comedy - Romantic",
        "Horror & Suspense"
    ]
    
    uploader = TelegramUploader()
    
    print("Category → Hashtag conversion:")
    
    for category in problematic_categories:
        # Simulate cleaning process
        cleaned = uploader._clean_text_for_caption(category)
        hashtag = f"#{cleaned.replace(' ', '_').lower()}"
        
        print(f"  '{category}' → '{cleaned}' → '{hashtag}'")
        
        # Check for problematic characters
        problematic_chars = ['&', '/', '(', ')', '-']
        found_chars = [char for char in hashtag if char in problematic_chars]
        
        if found_chars:
            print(f"    ⚠️  Problematic chars: {found_chars}")
        else:
            print(f"    ✅ Clean hashtag")

if __name__ == "__main__":
    import asyncio
    asyncio.run(test_hashtag_formatting())
    asyncio.run(test_different_categories())
    asyncio.run(test_hashtag_cleaning())