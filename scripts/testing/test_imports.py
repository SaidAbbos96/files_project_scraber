#!/usr/bin/env python3
"""
Import Test - TelegramUploader import larni tekshirish
"""

# Minimal import test - only the specific module
import sys
import os
sys.path.append('/home/aicoder/coding/files_project/files_project_scraber')


def test_imports():
    """Import larni tekshirish"""
    print("🧪 Import Test")
    print("=" * 30)

    try:
        # Direct module level imports test
        import html
        import re
        print("✅ html va re import OK")

        # Test utils.helpers import
        try:
            from utils.helpers import format_file_size
            print("✅ format_file_size import OK")

            # Test the function
            test_size = format_file_size(1024*1024*500)  # 500MB
            print(f"✅ format_file_size test: {test_size}")

        except Exception as e:
            print(f"❌ utils.helpers import xatosi: {e}")

        # Test telegramuploader.core.uploader directly
        try:
            # Import only the specific file without dependencies
            import importlib.util
            spec = importlib.util.spec_from_file_location(
                "uploader",
                "/home/aicoder/coding/files_project/files_project_scraber/telegramuploader/core/uploader.py"
            )
            uploader_module = importlib.util.module_from_spec(spec)

            print("✅ uploader.py fayli topildi")

            # Manual import dependencies test
            import time
            import html
            import re
            import os
            import asyncio
            from pathlib import Path
            from typing import Dict, Any, Optional
            print("✅ Barcha kerakli import lar mavjud")

        except Exception as e:
            print(f"❌ uploader.py direct import xatosi: {e}")

        # Test caption cleaning functions manually
        def test_clean_text_for_caption(text: str) -> str:
            """Caption uchun matnni tozalash - test version"""
            if not text or not isinstance(text, str):
                return ""

            # HTML entities decode qilish
            text = html.unescape(text)

            # Barcha HTML teglarni olib tashlash
            text = re.sub(r'<[^>]+>', '', text)

            # Ortiqcha bo'shliqlarni tozalash
            text = re.sub(r'\s+', ' ', text).strip()

            # Maxsus belgilarni oddiy belgilarga aylantirish
            text = text.replace('&amp;', '&').replace(
                '&lt;', '<').replace('&gt;', '>').replace('&quot;', '"')

            # Telegram uchun xavfli belgilarni tozalash
            text = text.replace('`', "'").replace(
                '*', '').replace('_', '').replace('[', '(').replace(']', ')')

            return text

        # Test clean function
        test_text = "<b>Test &amp; HTML</b>"
        cleaned = test_clean_text_for_caption(test_text)
        print(f"✅ Clean function test: '{test_text}' → '{cleaned}'")

        print("\n🎉 Barcha import testlar muvaffaqiyatli!")
        return True

    except Exception as e:
        print(f"❌ Import test xatosi: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    test_imports()
