#!/usr/bin/env python3
import asyncio
import sys
import os

# Path qo'shish
sys.path.append('/home/aicoder/coding/files_project/files_project_scraber')

from telegramuploader.core.uploader import TelegramUploader

async def test_category_fix():
    """Kategoriya muammosini test qilish"""
    print("🧪 Kategoriya tuzatilishini test qilish")
    print("=" * 50)
    
    # Test data - ko'p kategoriyali
    test_item = {
        "title": "Nafas olma 3: Muqaddima",
        "categories": "1,5,20",  # Multiple categories: other, thriller, crime
        "year": "2022",
        "country": "SSHA", 
        "actors": "Stiven Leng,Mark Senter,Patrik Darro,Liana RaytMark",
        "language": "uz",
        "description": "Dashtdagi yolg'iz uyda g'alati bir chol yashaydi Bir kuni adashgan sayyoh uning ichiga kirib ketadi va darhol uy egasida shubha uyg'otadi Chol bosqinchiga qurol ko'rsatadi va savol bera boshlaydi",
        "file_url": "https://fayllar1.ru/21/kinolar/Nafas olma 3 1080p O'zbek tilida (asilmedia.net).mp4"
    }
    
    # Test hajm
    file_size = 312651474  # 312 MB
    
    try:
        uploader = TelegramUploader()
        caption = await uploader._create_caption(test_item, file_size)
        
        print("✅ Caption yaratildi!")
        print("\n📄 Generated Caption:")
        print("=" * 50)
        print(caption)
        print("=" * 50)
        
        # Hashtag format tekshirish
        if "#title=" in caption and "#category_id=" in caption and "#categories=" in caption:
            print("\n✅ Hashtag format to'g'ri!")
            
            # Ko'p kategoriyali format tekshirish
            if "category_id=1,5,20" in caption and "categories=other,thriller,crime" in caption:
                print("✅ Ko'p kategoriyali format ham to'g'ri!")
            else:
                print("❌ Ko'p kategoriyali formatda muammo")
        else:
            print("\n❌ Hashtag formatda muammo bor!")
            
    except Exception as e:
        print(f"❌ Test xatosi: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_category_fix())