#!/usr/bin/env python3
"""
Full Download Test - Haqiqiy faylni yuklash test
"""

import sys
import os
import asyncio
import aiohttp
import aiofiles
from pathlib import Path

# Project root'ni sys.path ga qo'shish
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)

async def test_download_only():
    """Faqat fayl yuklab olishni test qilish"""
    print("⬇️ Download Test Boshlandi")
    print("=" * 50)
    
    demo_url = "https://videocdn.cdnpk.net/videos/63eef08b-9d49-401c-b357-2bc259bdeebd/horizontal/downloads/720p.mp4?filename=1472728_People_Business_1280x720.mp4&token=exp=1761025908~hmac=826fbb5931aaad2d89665a12f60211691a94aba9cc07c3e26aa388215e77bc37"
    
    try:
        # Download directory
        download_dir = Path("downloads/test_demo")
        download_dir.mkdir(parents=True, exist_ok=True)
        
        # File name
        filename = "demo_test_video.mp4"
        file_path = download_dir / filename
        
        print(f"📁 Download path: {file_path}")
        print(f"🔗 URL: {demo_url[:100]}...")
        
        # Download process
        print("⬇️ Yuklab olish boshlandi...")
        
        # Timeout va headers bilan
        timeout = aiohttp.ClientTimeout(total=300)  # 5 minut
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        async with aiohttp.ClientSession(timeout=timeout, headers=headers) as session:
            print("📡 HTTP so'rov yuborilmoqda...")
            async with session.get(demo_url) as response:
                print(f"📊 HTTP Status: {response.status}")
                print(f"📏 Content-Length: {response.headers.get('content-length', 'Unknown')}")
                print(f"📋 Content-Type: {response.headers.get('content-type', 'Unknown')}")
                
                if response.status == 200:
                    total_size = int(response.headers.get('content-length', 0))
                    print(f"📏 Fayl hajmi: {total_size / (1024*1024):.1f} MB")
                    
                    downloaded = 0
                    chunk_size = 8192
                    
                    async with aiofiles.open(file_path, 'wb') as f:
                        async for chunk in response.content.iter_chunked(chunk_size):
                            await f.write(chunk)
                            downloaded += len(chunk)
                            
                            # Progress har 5MB da
                            if downloaded % (5*1024*1024) == 0 or downloaded == total_size:
                                progress = (downloaded / total_size) * 100 if total_size > 0 else 0
                                print(f"📊 Progress: {progress:.1f}% ({downloaded / (1024*1024):.1f} MB)")
                    
                    print(f"✅ Fayl muvaffaqiyatli yuklandi: {file_path}")
                    
                    # Fayl ma'lumotlarini tekshirish
                    actual_size = file_path.stat().st_size
                    print(f"📏 Final hajm: {actual_size / (1024*1024):.1f} MB")
                    
                    if total_size > 0 and actual_size != total_size:
                        print(f"⚠️ Hajm farqi: expected {total_size}, got {actual_size}")
                    else:
                        print("✅ Hajm mos keldi")
                    
                    return str(file_path)
                    
                elif response.status == 403:
                    print("❌ Access Denied (403) - Token yaroqsiz yoki muddati tugagan")
                elif response.status == 404:
                    print("❌ File Not Found (404) - Fayl topilmadi")
                else:
                    print(f"❌ HTTP xato: {response.status}")
                    
    except asyncio.TimeoutError:
        print("❌ Timeout xato - Fayl juda katta yoki ulanish sekin")
    except aiohttp.ClientError as e:
        print(f"❌ HTTP xato: {e}")
    except Exception as e:
        print(f"❌ Download test da xato: {e}")
        import traceback
        traceback.print_exc()
    
    return None

async def test_url_availability():
    """URL mavjudligini tekshirish"""
    print("\n🔍 URL Availability Test")
    print("=" * 50)
    
    demo_url = "https://videocdn.cdnpk.net/videos/63eef08b-9d49-401c-b357-2bc259bdeebd/horizontal/downloads/720p.mp4?filename=1472728_People_Business_1280x720.mp4&token=exp=1761025908~hmac=826fbb5931aaad2d89665a12f60211691a94aba9cc07c3e26aa388215e77bc37"
    
    try:
        timeout = aiohttp.ClientTimeout(total=30)
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        async with aiohttp.ClientSession(timeout=timeout, headers=headers) as session:
            print("🔍 HEAD request...")
            async with session.head(demo_url) as response:
                print(f"📊 Status: {response.status}")
                print(f"📏 Content-Length: {response.headers.get('content-length', 'Unknown')}")
                print(f"📋 Content-Type: {response.headers.get('content-type', 'Unknown')}")
                print(f"🕐 Last-Modified: {response.headers.get('last-modified', 'Unknown')}")
                print(f"🔐 Server: {response.headers.get('server', 'Unknown')}")
                
                if response.status == 200:
                    print("✅ URL mavjud va fayl yuklash mumkin")
                    return True
                else:
                    print(f"❌ URL muammoli: {response.status}")
                    return False
                    
    except Exception as e:
        print(f"❌ URL tekshirishda xato: {e}")
        return False

async def test_alternative_urls():
    """Muqobil URL larni test qilish"""
    print("\n🔄 Alternative URLs Test")
    print("=" * 50)
    
    # Ba'zi ochiq test URL lar
    test_urls = [
        "https://sample-videos.com/zip/10/mp4/SampleVideo_1280x720_1mb.mp4",
        "https://file-examples.com/storage/fe86c865cd8c0fa9d56083a/2017/10/file_example_MP4_480_1_5MG.mp4",
        "https://www.learningcontainer.com/wp-content/uploads/2020/05/sample-mp4-file.mp4",
        "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/BigBuckBunny.mp4"
    ]
    
    for i, url in enumerate(test_urls, 1):
        print(f"\n{i}. Testing: {url[:60]}...")
        
        try:
            timeout = aiohttp.ClientTimeout(total=30)
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.head(url) as response:
                    if response.status == 200:
                        size = response.headers.get('content-length', 'Unknown')
                        content_type = response.headers.get('content-type', 'Unknown')
                        print(f"   ✅ Available - Size: {size}, Type: {content_type}")
                    else:
                        print(f"   ❌ Status: {response.status}")
        except Exception as e:
            print(f"   ❌ Error: {e}")

if __name__ == "__main__":
    async def main():
        await test_url_availability()
        
        print("\n" + "="*60)
        choice = input("Yuklashni davom ettirish? (y/n): ").lower()
        
        if choice in ['y', 'yes', 'ha']:
            downloaded_file = await test_download_only()
            
            if downloaded_file:
                print(f"\n✅ Download test muvaffaqiyatli!")
                print(f"📁 Fayl joylashuvi: {downloaded_file}")
            else:
                print("\n❌ Download test muvaffaqiyatsiz")
                await test_alternative_urls()
        else:
            print("Download bekor qilindi")
    
    asyncio.run(main())