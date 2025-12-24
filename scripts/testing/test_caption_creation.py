#!/usr/bin/env python3
"""
Caption Test - HTML-siz caption yaratishni test qilish
"""

import sys
import os
sys.path.append('/home/aicoder/coding/files_project/files_project_scraber')

def test_caption_creation():
    """HTML-siz caption yaratishni test qilish"""
    print("🧪 Caption Creation Test (HTML-siz)")
    print("=" * 50)
    
    # Test ma'lumotlari HTML belgila bilan
    test_item = {
        "title": "<b>Ajoyib Film</b> &amp; <i>Drama</i>",
        "categories": ["Drama", "Comedy", "Action"],
        "year": "2023",
        "country": "<span>O'zbekiston</span>",
        "actors": "Actor <strong>One</strong>, Actor Two &quot;Three&quot;",
        "language": "O'zbek",
        "description": "Bu <em>ajoyib</em> film haqida <u>batafsil</u> ma'lumot. HTML &lt;teglar&gt; bilan to'la matn...",
        "file_url": "https://example.com/file.mp4",
        "image": "https://example.com/poster.jpg"
    }
    
    # Uploader yaratish
    try:
        from telegramuploader.core.uploader import TelegramUploader
        uploader = TelegramUploader()
        
        # Caption yaratish
        import asyncio
        
        async def test_caption():
            caption = await uploader._create_caption(test_item, 1024*1024*500)  # 500MB
            return caption
        
        caption = asyncio.run(test_caption())
        
        print("📝 Yaratilgan caption:")
        print("-" * 30)
        print(caption)
        print("-" * 30)
        
        # HTML mavjudligini tekshirish
        html_patterns = ['<', '>', '&lt;', '&gt;', '&amp;', '&quot;']
        html_found = any(pattern in caption for pattern in html_patterns)
        
        if html_found:
            print("❌ Caption da HTML belgilar topildi!")
            for pattern in html_patterns:
                if pattern in caption:
                    print(f"   • Topildi: {pattern}")
        else:
            print("✅ Caption da HTML belgilar yo'q - to'liq tozalangan!")
        
        # Caption uzunligini tekshirish
        print(f"📏 Caption uzunligi: {len(caption)} belgi")
        
        if len(caption) <= 4096:
            print("✅ Caption uzunligi Telegram limitiga mos")
        else:
            print("⚠️ Caption juda uzun - kesib olinadi")
        
        # Clean text funksiyasini alohida test qilish
        print(f"\n🧪 _clean_text_for_caption test:")
        test_texts = [
            "<b>Bold matn</b>",
            "Normal &amp; &quot;qo'shtirnoq&quot;",
            "<script>alert('xss')</script>Normal matn",
            "Emoji 🎬 va *markdown* `kod`"
        ]
        
        for test_text in test_texts:
            cleaned = uploader._clean_text_for_caption(test_text)
            print(f"   Original: {test_text}")
            print(f"   Cleaned:  {cleaned}")
            print()
        
        return True
        
    except Exception as e:
        print(f"❌ Test xatosi: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_caption_creation()