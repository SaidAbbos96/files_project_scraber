#!/usr/bin/env python3
from telegramuploader.core.downloader import FileDownloader
import sys
import asyncio
import aiohttp
sys.path.append('/home/aicoder/coding/files_project/files_project_scraber')


async def test_file_size():
    """File size olish funksiyasini test qilish"""
    print("🧪 File size test")
    print("=" * 50)

    downloader = FileDownloader()

    # Test URLs - ba'zi haqiqiy URL lar
    test_urls = [
        "https://example.com/test.mp4",  # Mavjud emas
        "https://httpbin.org/bytes/1000",  # 1000 bytes
        "https://www.google.com",  # HTML page
    ]

    async with aiohttp.ClientSession() as session:
        for url in test_urls:
            try:
                size = await downloader.get_file_size(session, url)
                size_gb = size / (1024**3) if size > 0 else 0
                print(f"📁 {url[:50]}... → {size:,} bytes ({size_gb:.3f} GB)")
            except Exception as e:
                print(f"❌ {url[:50]}... → Error: {e}")

    print("\n" + "=" * 50)
    print("✅ Test tugadi")

if __name__ == "__main__":
    asyncio.run(test_file_size())
