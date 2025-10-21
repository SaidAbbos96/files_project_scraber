#!/usr/bin/env python3
import asyncio
import sys
import os

# Path qo'shish
sys.path.append('/home/aicoder/coding/files_project/files_project_scraber')

async def quick_test():
    """Tez test - telegram yuborish"""
    print("🧪 Telegram test message")
    print("=" * 40)
    
    try:
        from main import send_text_message_to_telegram
        
        # Test message
        test_message = """#title=Test Hashtag Format
#lang=uz
#category_id=36
#actors=Test Actor 1,Test Actor 2
#year=2024
#country=Test Country
#categories=drama
#file_size=123456789
#url=https://test.example.com/video.mp4
#desc=Bu test message hashtag formatida yuborilmoqda"""
        
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
    asyncio.run(quick_test())