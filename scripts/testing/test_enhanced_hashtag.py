#!/usr/bin/env python3
"""
Enhanced Hashtag Test - Yangi hashtag cleaning logikasini test qilish
"""

import sys
import os

# Project root'ni sys.path ga qo'shish
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)

from telegramuploader.core.uploader import TelegramUploader

async def test_problematic_categories():
    """Muammoli kategoriyalarni test qilish"""
    print("🧪 Enhanced Hashtag Cleaning Test")
    print("=" * 60)
    
    # Problematic categories
    test_cases = [
        {
            "categories": ["Crime & Thriller", "Sci-Fi/Fantasy"],
            "description": "Special characters (&, /)"
        },
        {
            "categories": ["Action/Adventure", "Drama (Psychological)"],
            "description": "Slashes and parentheses"
        },
        {
            "categories": ["Comedy - Romantic", "Horror & Suspense"],
            "description": "Dashes and ampersands"
        },
        {
            "categories": ["Biography, Drama", "Sport, Action"],
            "description": "Commas in categories"
        },
        {
            "categories": ["2023 Films", "HD Quality", "Uzbek Films"],
            "description": "Numbers and spaces"
        }
    ]
    
    uploader = TelegramUploader()
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n{i}. {test_case['description']}")
        print(f"   Input: {test_case['categories']}")
        
        test_item = {
            "title": "Test Film",
            "categories": test_case["categories"],
            "language": "uz"
        }
        
        caption = await uploader._create_caption(test_item, 1024*1024*100)
        
        # Find categories line
        category_line = None
        for line in caption.split('\n'):
            if '🏷️' in line:
                category_line = line
                break
        
        if category_line:
            print(f"   Output: {category_line}")
            
            # Extract hashtags
            hashtags = [part for part in category_line.split() if part.startswith('#')]
            print(f"   Hashtags: {hashtags}")
            
            # Check for problematic characters
            problematic_chars = ['&', '/', '(', ')', '-', ',']
            clean_hashtags = []
            for hashtag in hashtags:
                has_problems = any(char in hashtag for char in problematic_chars)
                clean_hashtags.append('✅' if not has_problems else '❌')
            
            print(f"   Clean status: {' '.join(clean_hashtags)}")
        else:
            print(f"   ❌ Categories line not found!")

async def test_original_example():
    """Sizning asl misolingizni test qilish"""
    print(f"\n{'='*60}")
    print("🎬 Original Example Test")
    print("-" * 60)
    
    # Your original example
    original_item = {
        "title": "Janob olimpiya / Mister olimpia / Akauka Jo va Ben Vayderlar O'zbekcha",
        "categories": ["biography", "drama", "sport"],
        "year": "2018",
        "country": "SSHA", 
        "actors": "Kevin Duran,Di Djey Kuolls,Djulianna Xaf,Viktoriya Djastis,Robert Forster",
        "language": "uz",
        "description": "Jo va Ben Uayder akaukalari — butun hayotini bodibildingni ommalashtirishga bag'ishlagan professional murabbiylar 1946yilda ular Xalqaro bodibilding federatsiyasiga asos solishadi va bu tashkilo",
        "file_url": "https://fayllar1.ru/37/kinolar/Janob olimpiya 2018 1080p (asilmedia.net).mp4"
    }
    
    uploader = TelegramUploader()
    caption = await uploader._create_caption(original_item, 153 * 1024**3)  # 153 GB
    
    print("📝 Final Enhanced Caption:")
    print("-" * 60)
    print(caption)
    print("-" * 60)
    
    # Analysis
    lines = caption.split('\n')
    for line in lines:
        if '🏷️' in line:
            print(f"\n🏷️ Categories Analysis:")
            print(f"   Line: {line}")
            
            hashtags = [part for part in line.split() if part.startswith('#')]
            print(f"   Hashtag count: {len(hashtags)}")
            print(f"   Hashtags: {hashtags}")
            
            # Expected vs actual
            expected_hashtags = ["#biography", "#drama", "#sport"]
            print(f"   Expected: {expected_hashtags}")
            print(f"   Match: {'✅' if hashtags == expected_hashtags else '❌'}")

async def test_edge_cases():
    """Edge case'larni test qilish"""
    print(f"\n{'='*60}")
    print("🔧 Edge Cases Test")
    print("-" * 60)
    
    edge_cases = [
        [],  # Empty categories
        [""],  # Empty string category
        ["   "],  # Whitespace only
        ["Category with    multiple   spaces"],
        ["Category/with/many/slashes"],
        ["Category & another & third"],
        ["(Parentheses) - everywhere -"],
        ["UPPERCASE", "lowercase", "MiXeD CaSe"]
    ]
    
    uploader = TelegramUploader()
    
    for i, categories in enumerate(edge_cases, 1):
        print(f"\n{i}. Input: {categories}")
        
        test_item = {
            "title": "Test Film",
            "categories": categories,
            "language": "test"
        }
        
        caption = await uploader._create_caption(test_item, 1024*1024)
        
        # Find categories line
        category_line = None
        for line in caption.split('\n'):
            if '🏷️' in line:
                category_line = line
                break
        
        if category_line:
            print(f"   Output: {category_line}")
        else:
            print(f"   No categories line (expected for empty input)")

if __name__ == "__main__":
    import asyncio
    asyncio.run(test_problematic_categories())
    asyncio.run(test_original_example())
    asyncio.run(test_edge_cases())