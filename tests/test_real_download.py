#!/usr/bin/env python3
"""
Test script with real file download
"""
import asyncio
import sys
import os
sys.path.append('/home/aicoder/coding/files_project/files_project_scraber')

from filedownloader.core.downloader import FileDownloader
from utils.logger_core import logger


async def test_real_download():
    """Test with a real small file"""
    
    downloader = FileDownloader(max_retries=2)
    
    # Small test file (about 1KB JSON data)
    test_files = [{
        'id': 'test_json',
        'title': 'Test JSON Data',
        'file_url': 'https://httpbin.org/json'
    }]
    
    print("🚀 Testing real file download with retry mechanism:")
    
    os.makedirs('/tmp/test_downloads', exist_ok=True)
    
    successful, failed = await downloader.download_multiple_files(
        files_data=test_files,
        download_dir='/tmp/test_downloads',
        concurrency=1
    )
    
    print(f"\n📊 Final results: {successful} successful, {failed} failed")
    
    # Check downloaded file
    if successful > 0:
        files = os.listdir('/tmp/test_downloads')
        print(f"📂 Downloaded files: {files}")
        
        if files:
            file_path = f'/tmp/test_downloads/{files[0]}'
            file_size = os.path.getsize(file_path)
            print(f"📏 File size: {file_size} bytes")
            
            with open(file_path, 'r') as f:
                content = f.read()[:200]  # First 200 chars
                print(f"📄 Content preview: {content}")


if __name__ == "__main__":
    asyncio.run(test_real_download())