#!/usr/bin/env python3
import asyncio
import sys
import os

# Path qo'shish
sys.path.append('/home/aicoder/coding/files_project/files_project_scraber')

async def test_main_menu():
    """Main menu test message rejimini sinash"""
    print("🧪 Main menu test-message rejimi")
    print("=" * 50)
    
    try:
        from main import test_message_demo
        
        print("📝 test_message_demo funksiyasini chaqirish...")
        await test_message_demo()
        print("✅ Test tugadi!")
        
    except Exception as e:
        print(f"❌ Xato: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_main_menu())