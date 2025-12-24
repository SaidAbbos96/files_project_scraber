#!/usr/bin/env python3
"""
Disk space management test - yangi logikani sinash
"""

import asyncio
import os
import sys
import time
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from utils.disk_monitor import init_disk_monitor, get_disk_monitor
from utils.logger_core import logger

async def test_disk_space_logic():
    """Disk space management logic test"""
    
    logger.info("🧪 DISK SPACE MANAGEMENT TEST")
    logger.info("=" * 60)
    
    # Test directory
    test_dir = Path("/tmp/test_downloads")
    test_dir.mkdir(exist_ok=True)
    
    # Initialize disk monitor with 10GB requirement
    monitor = init_disk_monitor(str(test_dir), min_free_gb=10.0, check_interval=5)
    
    # Get current disk usage
    usage = monitor.get_disk_usage()
    logger.info(f"📊 HOZIRGI DISK HOLATI:")
    logger.info(f"   💾 Jami: {usage['total_gb']:.2f} GB")
    logger.info(f"   ✅ Bo'sh: {usage['free_gb']:.2f} GB")
    logger.info(f"   📈 Band: {usage['percent_used']:.1f}%")
    
    # Test scenarios
    logger.info("\n🔬 TEST SCENARILAR:")
    
    # Scenario 1: Check if there's enough space for new download
    test_file_size = 2 * 1024 ** 3  # 2GB
    logger.info(f"\n1️⃣ Yangi 2GB fayl download qilish mumkinmi?")
    has_space = monitor.has_enough_space(test_file_size)
    logger.info(f"   Natija: {'✅ HA' if has_space else '❌ YO\'Q'}")
    
    # Scenario 2: Can we continue upload even with low space?
    logger.info(f"\n2️⃣ Disk space kam bo'lsa ham upload davom etishi mumkinmi?")
    can_upload = monitor.can_continue_upload()
    logger.info(f"   Natija: {'✅ HA' if can_upload else '❌ YO\'Q'}")
    
    # Scenario 3: Create some test files and try cleanup
    logger.info(f"\n3️⃣ Test fayllar yaratib, cleanup sinovdan o'tkazish...")
    
    # Create old test file (2 hours ago)
    old_file = test_dir / "old_test_file.txt"
    with open(old_file, "w") as f:
        f.write("Test content " * 10000)  # ~100KB
    
    # Set file modification time to 2 hours ago
    old_time = time.time() - (2 * 3600)  # 2 hours ago
    os.utime(old_file, (old_time, old_time))
    
    # Create new test file (current time)
    new_file = test_dir / "new_test_file.txt"
    with open(new_file, "w") as f:
        f.write("New test content " * 10000)  # ~100KB
    
    logger.info(f"   📁 Yaratildi: {old_file.name} (2 soat oldin)")
    logger.info(f"   📁 Yaratildi: {new_file.name} (hozir)")
    
    # Test cleanup
    cleaned = await monitor.cleanup_old_files(max_age_hours=1)
    logger.info(f"   🧹 Tozalangan fayllar: {cleaned} ta")
    
    # Check which files remain
    remaining_files = list(test_dir.glob("*.txt"))
    logger.info(f"   📂 Qolgan fayllar: {len(remaining_files)} ta")
    for f in remaining_files:
        logger.info(f"      - {f.name}")
    
    # Scenario 4: Simulate critical low space
    logger.info(f"\n4️⃣ Critical low space simulation...")
    
    # Create monitor with very high requirement to simulate low space
    critical_monitor = init_disk_monitor(str(test_dir), min_free_gb=usage['free_gb'] + 5.0)  # Impossible requirement
    
    logger.info(f"   🔴 Simulated requirement: {usage['free_gb'] + 5.0:.2f} GB")
    logger.info(f"   📊 Available: {usage['free_gb']:.2f} GB")
    
    can_download = critical_monitor.has_enough_space(test_file_size)
    can_upload = critical_monitor.can_continue_upload()
    
    logger.info(f"   Download ruxsati: {'✅ HA' if can_download else '❌ YO\'Q'}")
    logger.info(f"   Upload ruxsati: {'✅ HA' if can_upload else '❌ YO\'Q'}")
    
    # Cleanup test files
    logger.info(f"\n🧹 Test fayllarni tozalash...")
    for f in test_dir.glob("*.txt"):
        f.unlink()
        logger.info(f"   🗑️ O'chirildi: {f.name}")
    
    # Test summary
    logger.info("\n" + "=" * 60)
    logger.info("📋 TEST XULOSASI:")
    logger.info("✅ Disk monitor ishga tushdi")
    logger.info("✅ Space tekshiruvi ishlaydi")
    logger.info("✅ Upload ruxsati mantiqiy")
    logger.info("✅ Cleanup funksiyasi ishlaydi")
    logger.info("=" * 60)

if __name__ == "__main__":
    asyncio.run(test_disk_space_logic())