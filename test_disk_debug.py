#!/usr/bin/env python3
import sys
import os
sys.path.append('/home/aicoder/coding/files_project/files_project_scraber')

from utils.disk_monitor import init_disk_monitor, get_disk_monitor

def test_disk_space():
    """Disk space muammosini test qilish"""
    print("🧪 Disk space test")
    print("=" * 50)
    
    # Download directory
    download_dir = "/home/aicoder/coding/files_project/files_project_scraber/downloads"
    
    # Initialize monitor with same settings as production
    monitor = init_disk_monitor(download_dir, min_free_gb=10.0)
    
    # Test with different file sizes
    test_sizes = [
        0,                    # No file size
        1 * 1024**3,         # 1 GB
        5 * 1024**3,         # 5 GB
        10 * 1024**3,        # 10 GB  
        50 * 1024**3,        # 50 GB
        100 * 1024**3,       # 100 GB
        200 * 1024**3,       # 200 GB
    ]
    
    for size in test_sizes:
        size_gb = size / (1024**3)
        has_space = monitor.has_enough_space(size)
        print(f"📁 Fayl hajmi: {size_gb:.1f} GB → Yetarlimi: {'✅' if has_space else '❌'}")
    
    print("\n" + "=" * 50)
    print("📊 Current disk status:")
    print(monitor.get_status_message())

if __name__ == "__main__":
    test_disk_space()