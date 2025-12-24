#!/usr/bin/env python3
"""
Hashtag Test - # belgisi qayerda yo'qolayotganini tekshirish
"""

import sys
import os

# Project root'ni sys.path ga qo'shish
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)

from telegramuploader.core.uploader import TelegramUploader

async def test_hashtag_preservation():
    """# belgisining saqlanishini test qilish"""
    print("🧪 Hashtag Preservation Test")
    print("=" * 50)
    
    # Test cases with hashtags
    test_cases = [
        "Film #drama #comedy #action",
        "#uzbekfilm #tarjima #HD",
        "Film haqida #info va #tavsif",
        "#2023 #yangi #film",
        "Kategoriya: Drama #drama, Comedy #comedy",
        "#hashtag #test #saqlanishi #kerak"
    ]
    
    uploader = TelegramUploader()
    
    print("📋 Text cleaning tests:")
    print("-" * 50)
    
    for i, text in enumerate(test_cases, 1):
        print(f"\n{i}. Original: '{text}'")
        
        # _clean_text_for_caption orqali tozalash
        cleaned = uploader._clean_text_for_caption(text)
        print(f"   Cleaned:  '{cleaned}'")
        
        # Hashtag mavjudligini tekshirish
        original_hashtags = text.count('#')
        cleaned_hashtags = cleaned.count('#')
        
        if original_hashtags == cleaned_hashtags:
            print(f"   ✅ Hashtags saqlandin: {original_hashtags}")
        else:
            print(f"   ❌ Hashtags yo'qoldi: {original_hashtags} → {cleaned_hashtags}")

async def test_full_caption_with_hashtags():
    """To'liq caption'da hashtag test"""
    print(f"\n{'='*50}")
    print("📝 Full Caption Hashtag Test")
    print("-" * 50)
    
    # Hashtag'li test item
    test_item = {
        "title": "Ajoyib Film #yangi #2023",
        "categories": ["#drama", "#comedy"],
        "year": "2023",
        "country": "O'zbekiston #uzbek",
        "actors": "Actor One #star, Actor Two #famous",
        "language": "O'zbek #tilida",
        "description": "Bu film #ajoyib va #qiziq #tavsiya #drama #comedy"
    }
    
    uploader = TelegramUploader()
    caption = await uploader._create_caption(test_item, 1024*1024*100)
    
    print("Generated caption:")
    print("-" * 50)
    print(caption)
    print("-" * 50)
    
    # Hashtag hisobi
    original_hashtags = sum(str(value).count('#') for value in test_item.values() if isinstance(value, str))
    original_hashtags += sum(cat.count('#') for cat in test_item.get('categories', []) if isinstance(cat, str))
    
    caption_hashtags = caption.count('#')
    
    print(f"📊 Hashtag statistics:")
    print(f"   Original: {original_hashtags} hashtag")
    print(f"   Caption:  {caption_hashtags} hashtag")
    print(f"   Preserved: {'✅' if caption_hashtags > 0 else '❌'}")

async def test_step_by_step_cleaning():
    """Step-by-step cleaning process"""
    print(f"\n{'='*50}")
    print("🔧 Step-by-Step Cleaning Test")
    print("-" * 50)
    
    test_text = "Bu <b>film</b> #drama #comedy haqida #info"
    
    print(f"Original: '{test_text}'")
    
    uploader = TelegramUploader()
    
    # Manual step-by-step cleaning simulation
    import html
    import re
    
    # Step 1: HTML decode
    step1 = html.unescape(test_text)
    print(f"Step 1 (HTML decode): '{step1}'")
    
    # Step 2: Remove script/style
    step2 = re.sub(r'<script[^>]*>.*?</script>', '', step1, flags=re.DOTALL | re.IGNORECASE)
    step2 = re.sub(r'<style[^>]*>.*?</style>', '', step2, flags=re.DOTALL | re.IGNORECASE)
    print(f"Step 2 (Remove script/style): '{step2}'")
    
    # Step 3: Remove HTML tags
    step3 = re.sub(r'<[^>]+>', '', step2)
    print(f"Step 3 (Remove HTML tags): '{step3}'")
    
    # Step 4: Replace entities
    step4 = step3.replace('&amp;', '&').replace('&lt;', '<').replace('&gt;', '>')
    print(f"Step 4 (Replace entities): '{step4}'")
    
    # Step 5: Whitespace cleanup
    step5 = re.sub(r'\s+', ' ', step4).strip()
    print(f"Step 5 (Whitespace cleanup): '{step5}'")
    
    # Compare with function result
    function_result = uploader._clean_text_for_caption(test_text)
    print(f"Function result: '{function_result}'")
    
    print(f"\nHashtag count comparison:")
    print(f"  Original: {test_text.count('#')}")
    print(f"  Step 5:   {step5.count('#')}")
    print(f"  Function: {function_result.count('#')}")

if __name__ == "__main__":
    import asyncio
    asyncio.run(test_hashtag_preservation())
    asyncio.run(test_full_caption_with_hashtags())
    asyncio.run(test_step_by_step_cleaning())