#!/usr/bin/env python3
import asyncio
import sys
import os

# Path qo'shish
sys.path.append('/home/aicoder/coding/files_project/files_project_scraber')

from telegramuploader.core.uploader import TelegramUploader

async def test_html_clean():
    """HTML tozalash muammosini test qilish"""
    print("🧪 HTML tozalash test")
    print("=" * 50)
    
    # Test data - HTML bilan
    test_item = {
        "title": "Yo'lda Fransiya filmi",
        "categories": "37",  # Comedy
        "year": "1971",
        "country": "FRANSIYA, ITALIYA", 
        "actors": "Jak Tati,Marsel Franval,Onore Bostel,Fransua Mayzongrosse,Toni Knepper",
        "language": "uz",
        "description": "Eng yangi furgon dizaynida ishtirok etgan Hulot haydovchi, PR ayol va uning iti bilan birga <class='test'>Parijdan</class> Amsterdamga xalqaro ko'rgazmaga jo'naydi. Asta-sekin yo'l do'zaxga aylanadi.Юло, принявший участие в конструировании новейшего автофургона, отправляется из Парижа в Амстердам на международную выставку вместе с водителем, пиарщицей и ее собачкой. Постепенно дорога превращается в ад.",
        "file_url": "https://fayllar1.ru/21/kinolar/Yo'lda 1080p O'zbek tilida (asilmedia.net).mp4"
    }
    
    # Test hajm
    file_size = 2680450492  # 2.5GB
    
    try:
        uploader = TelegramUploader()
        caption = await uploader._create_caption(test_item, file_size)
        
        print("✅ Caption yaratildi!")
        print("\n📄 Generated Caption:")
        print("=" * 50)
        print(caption)
        print("=" * 50)
        
        # HTML teglarni tekshirish
        if '<class' in caption or '<' in caption or '>' in caption:
            print("\n❌ HTML teglar hali ham bor!")
        else:
            print("\n✅ HTML teglar tozalandi!")
            
        # URL tekshirish
        if '#url=' in caption and '"' not in caption.split('#url=')[1].split('\n')[0]:
            print("✅ URL qo'shtirnoqsiz!")
        else:
            print("❌ URL'da hali ham qo'shtirnoq bor!")
            
    except Exception as e:
        print(f"❌ Test xatosi: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_html_clean())