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
    
    # Test data - sizning misolingiz kabi
    test_item = {
        "title": "Burulish Mosfilm SSSR kinosi",
        "categories": "36",  # Drama
        "year": "1978",
        "country": "SSSR", 
        "actors": "Oleg Yankovskiy,Irina Kupchenko,Anatoliy Solonisыn,Lyubov Strijenova,Oleg Anofriyev,Natalya Velichko,Mixail Dadыko",
        "language": "uz",
        "description": "Yangi turmush qurganlarning Qora dengizdagi sayohati baxtli yakunlanmoqda. Oldinda - Moskva, qiziqarli ish va oilaviy hayotning farovonligi. Ammo fojiali baxtsiz hodisa Vedeneevlarning umidlarini yo'q qiladi - Viktor jinoyatda ayblanadi. Tergov boshlanadi...Счастливо завершается круиз молодоженов по Черному морю. Впереди - Москва, интересная работа и уют семейной жизни. Но трагическая случайность рушит надежды Веденеевых - Виктора обвиняют в преступлении. Начинается следствие...",
        "file_url": "https://fayllar1.ru/21/kinolar/Burulish 480p O'zbek tilida (asilmedia.net).mp4"
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
        else:
            print("\n❌ Hashtag formatda muammo bor!")
            
    except Exception as e:
        print(f"❌ Test xatosi: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_category_fix())