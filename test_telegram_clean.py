#!/usr/bin/env python3
import asyncio
import sys
import os

# Path qo'shish
sys.path.append('/home/aicoder/coding/files_project/files_project_scraber')

async def test_telegram_send_clean():
    """Tozalangan caption'ni Telegram'ga yuborish"""
    print("🧪 Telegram clean caption test")
    print("=" * 50)
    
    try:
        from main import send_text_message_to_telegram
        
        # Test message - HTML bilan
        test_message = """#title=Yo'lda Fransiya filmi
#lang=uz
#category_id=37
#actors=Jak Tati,Marsel Franval,Onore Bostel,Fransua Mayzongrosse,Toni Knepper
#year=1971
#country=FRANSIYA, ITALIYA
#categories=comedy
#file_size=2680450492
#url=https://fayllar1.ru/21/kinolar/Yolda 1080p Ozbek tilida (asilmedia.net).mp4
#desc=Eng yangi furgon dizaynida ishtirok etgan Hulot haydovchi, PR ayol va uning iti bilan birga Parijdan Amsterdamga xalqaro korganiga jonaydi. Asta-sekin yol dozaxga aylanadi."""
        
        print("📝 Test message:")
        print(test_message)
        print("-" * 40)
        
        await send_text_message_to_telegram(test_message)
        print("✅ Test tugadi!")
        
    except Exception as e:
        print(f"❌ Xato: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_telegram_send_clean())