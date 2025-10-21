#!/usr/bin/env python3
"""
Resume Download Test - Partial file yuklanishni test qilish
"""

import asyncio
import aiohttp
import os
import sys
from pathlib import Path

# Project root qo'shish
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from filedownloader.core.downloader import FileDownloader

async def test_resume_download():
    """Resume download funksiyasini test qilish"""
    print("🧪 Resume Download Test")
    print("=" * 50)
    
    # Test URL - katta fayl
    test_url = "https://speed.hetzner.de/100MB.bin"  # 100MB test fayl
    output_path = "test_resume_file.bin"
    
    # Agar fayl mavjud bo'lsa, o'chirib tashlash
    if os.path.exists(output_path):
        os.remove(output_path)
        print(f"🗑️ Mavjud test fayl o'chirildi")
    
    downloader = FileDownloader(max_retries=2)
    
    async with aiohttp.ClientSession() as session:
        semaphore = asyncio.Semaphore(1)
        
        print("🔍 Testing resume support...")
        resume_supported = await downloader.check_resume_support(session, test_url)
        print(f"📡 Resume support: {'✅ Yes' if resume_supported else '❌ No'}")
        
        file_size, resume_support = await downloader.get_file_info(session, test_url)
        print(f"📊 File size: {file_size/1024/1024:.2f} MB")
        print(f"🔄 Resume: {'✅ Supported' if resume_support else '❌ Not supported'}")
        
        print("\n🚀 Starting download...")
        result = await downloader.download_file_with_retry(
            session, semaphore, test_url, output_path, "test_resume_file.bin"
        )
        
        if result:
            print(f"✅ Download muvaffaqiyatli: {result/1024/1024:.2f} MB")
            
            # Test: partial download simulation
            if os.path.exists(output_path):
                file_size = os.path.getsize(output_path)
                # Fayl o'rtasini kesib tashlash (partial simulation)
                with open(output_path, "r+b") as f:
                    f.truncate(file_size // 2)
                
                print(f"\n🔪 Simulated partial download: {file_size//2/1024/1024:.2f} MB")
                print("🔄 Testing resume...")
                
                # Resume test
                result2 = await downloader.download_file_with_retry(
                    session, semaphore, test_url, output_path, "test_resume_file.bin"
                )
                
                if result2:
                    print(f"✅ Resume muvaffaqiyatli: {result2/1024/1024:.2f} MB")
                else:
                    print("❌ Resume muvaffaqiyatsiz")
            
        else:
            print("❌ Download muvaffaqiyatsiz")
    
    # Cleanup
    if os.path.exists(output_path):
        os.remove(output_path)
        print(f"🧹 Test fayl tozalandi")

if __name__ == "__main__":
    asyncio.run(test_resume_download())