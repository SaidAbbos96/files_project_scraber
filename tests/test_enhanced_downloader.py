#!/usr/bin/env python3
"""
Test script for enhanced FileDownloader with intelligent timeout
"""
import asyncio
import sys
import os
sys.path.append('/home/aicoder/coding/files_project/files_project_scraber')

from filedownloader.core.downloader import FileDownloader
from utils.logger_core import logger


async def test_downloader():
    """Test enhanced downloader functionality"""
    
    downloader = FileDownloader(max_retries=2)
    
    # Test timeout calculation
    test_sizes = [
        (1024 * 1024, "1MB file"),           # 1MB
        (100 * 1024 * 1024, "100MB file"),  # 100MB  
        (1024 * 1024 * 1024, "1GB file"),   # 1GB
        (0, "Unknown size file")             # Unknown
    ]
    
    print("🧪 Testing timeout calculations:")
    for size_bytes, description in test_sizes:
        timeout = downloader.calculate_timeout(size_bytes)
        print(f"  - {description}: {timeout}s ({timeout/60:.1f} min)")
    
    print("\n✅ Timeout calculation tests completed!")
    
    # Test actual download (if you want to test with a real file)
    # Uncomment and provide a real URL for testing
    """
    test_files = [{
        'id': 'test1',
        'title': 'Test File',
        'file_url': 'https://httpbin.org/bytes/1024'  # 1KB test file
    }]
    
    print("\n🚀 Testing actual download:")
    successful, failed = await downloader.download_multiple_files(
        files_data=test_files,
        download_dir='/tmp/test_downloads',
        concurrency=1
    )
    print(f"Download results: {successful} successful, {failed} failed")
    """


if __name__ == "__main__":
    asyncio.run(test_downloader())