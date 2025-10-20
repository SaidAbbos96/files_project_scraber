#!/usr/bin/env python3
"""
Final Cleanup Hashtag Test - _final_caption_cleanup da # yo'qolishi
"""

import sys
import os

# Project root'ni sys.path ga qo'shish
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)

from telegramuploader.core.uploader import TelegramUploader

def test_final_cleanup_hashtags():
    """_final_caption_cleanup da hashtag yo'qolishini test qilish"""
    print("🧪 Final Cleanup Hashtag Test")
    print("=" * 50)
    
    uploader = TelegramUploader()
    
    # Test captions with hashtags
    test_captions = [
        "📄 Film #drama #comedy\n🏷️ Action\n💾 100 MB",
        "📄 Test Film\n🏷️ #uzbek #yangi\n🤖 worker_001",
        "📝 Bu film #ajoyib va #qiziq #drama #comedy",
        "#hashtag1 #hashtag2 #hashtag3",
        "Text with #hash and other symbols * _ [ ]"
    ]
    
    print("📋 Final cleanup tests:")
    print("-" * 50)
    
    for i, caption in enumerate(test_captions, 1):
        print(f"\n{i}. Original:")
        print(f"   '{caption}'")
        
        # _final_caption_cleanup orqali tozalash
        cleaned = uploader._final_caption_cleanup(caption)
        print(f"   Final cleanup:")
        print(f"   '{cleaned}'")
        
        # Hashtag comparison
        original_hashtags = caption.count('#')
        cleaned_hashtags = cleaned.count('#')
        
        print(f"   Hashtags: {original_hashtags} → {cleaned_hashtags}")
        
        if original_hashtags == cleaned_hashtags:
            print(f"   ✅ Hashtags saqlandin")
        else:
            print(f"   ❌ {original_hashtags - cleaned_hashtags} ta hashtag yo'qoldi!")

def test_telegram_special_chars():
    """Telegram special characterlarni tekshirish"""
    print(f"\n{'='*50}")
    print("🔧 Telegram Special Characters Test")
    print("-" * 50)
    
    # Current telegram_special list from code
    telegram_special = ['*', '_', '`', '[', ']', '~', '|', '+', '-', '=', '.', '!']
    
    print("Current telegram_special list:")
    print(telegram_special)
    print(f"'#' in list: {'#' in telegram_special}")
    
    # Test with all special characters
    test_text = "Text with #hash *bold* _italic_ `code` [link] +plus -minus =equal .dot !exclamation"
    
    print(f"\nTest text: '{test_text}'")
    
    # Simulate cleaning
    cleaned = test_text
    for char in telegram_special:
        cleaned = cleaned.replace(char, '')
    
    print(f"After removing telegram_special: '{cleaned}'")
    print(f"Hashtag preserved: {'✅' if '#' in cleaned else '❌'}")

if __name__ == "__main__":
    test_final_cleanup_hashtags()
    test_telegram_special_chars()