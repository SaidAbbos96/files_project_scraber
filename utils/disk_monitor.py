"""
Disk Space Monitor - Disk joy monitoringi va boshqaruvi
"""
import os
import shutil
import asyncio
import time
from pathlib import Path
from typing import Optional
from utils.logger_core import logger


class DiskMonitor:
    """Disk joy monitoringi va boshqaruv"""

    def __init__(self, download_dir: str, min_free_gb: float = 5.0, check_interval: int = 60):
        """
        Args:
            download_dir: Download papka
            min_free_gb: Minimal bo'sh joy (GB)
            check_interval: Tekshirish intervali (soniya, default: 60s = 1 daqiqa)
        """
        self.download_dir = Path(download_dir)
        self.min_free_bytes = int(min_free_gb * 1024 ** 3)  # GB → bytes
        self.check_interval = check_interval
        self._last_check_time = 0
        self._is_paused = False

    def get_disk_usage(self) -> dict:
        """Disk ishlatilishini olish"""
        try:
            stat = shutil.disk_usage(self.download_dir)
            return {
                "total_gb": stat.total / (1024 ** 3),
                "used_gb": stat.used / (1024 ** 3),
                "free_gb": stat.free / (1024 ** 3),
                "free_bytes": stat.free,
                "percent_used": (stat.used / stat.total) * 100
            }
        except Exception as e:
            logger.error(f"❌ Disk usage olishda xato: {e}")
            return {
                "total_gb": 0,
                "used_gb": 0,
                "free_gb": 0,
                "free_bytes": 0,
                "percent_used": 0
            }

    def has_enough_space(self, required_bytes: int = 0) -> bool:
        """
        Yetarlicha joy bormi tekshirish

        Args:
            required_bytes: Kerakli joy (bytes), 0 bo'lsa faqat minimal tekshiradi

        Returns:
            True agar yetarli bo'lsa, False aks holda
        """
        current_time = time.time()

        # Har safar tekshirmaslik uchun cache
        if current_time - self._last_check_time < 5:  # 5 soniya cache
            return not self._is_paused

        self._last_check_time = current_time

        usage = self.get_disk_usage()
        free_bytes = usage["free_bytes"]

        # Minimal + required
        needed = self.min_free_bytes + required_bytes

        has_space = free_bytes > needed
        self._is_paused = not has_space

        # Debug log qo'shish - faqat juda katta file uchun
        if not has_space and required_bytes > 10 * 1024**3:  # 10GB dan katta
            logger.debug(
                f"🔍 DISK SPACE DEBUG (katta fayl):\n"
                f"   Bo'sh: {free_bytes / (1024**3):.2f} GB\n"
                f"   Minimal: {self.min_free_bytes / (1024**3):.2f} GB\n"
                f"   Kerak: {required_bytes / (1024**3):.2f} GB\n"
                f"   Jami kerak: {needed / (1024**3):.2f} GB"
            )

        return has_space

    def can_continue_upload(self) -> bool:
        """
        Upload jarayonini davom ettirish mumkinligini tekshirish
        
        Bu method disk space kam bo'lsa ham True qaytaradi,
        chunki mavjud fayllarni telegramga yuklash disk space ni
        bo'shatishga yordam beradi.
        
        Returns:
            True - upload davom etsin (disk space kam bo'lsa ham)
        """
        usage = self.get_disk_usage()
        
        # Agar juda ham kam joy qolgan bo'lsa (1GB dan kam), upload ham to'xtatamiz
        critical_threshold = 1.0 * 1024 ** 3  # 1GB bytes
        
        if usage["free_bytes"] < critical_threshold:
            logger.warning(
                f"🔴 CRITICAL: Disk space juda kam ({usage['free_gb']:.2f} GB), "
                f"upload ham to'xtatildi"
            )
            return False
        
        # 1GB dan ortiq joy bor - upload davom etsin
        if usage["free_bytes"] < self.min_free_bytes:
            logger.info(
                f"⚠️ Disk space kam ({usage['free_gb']:.2f} GB), "
                f"lekin upload davom etadi (fayllar o'chiriladi)"
            )
        
        return True

    async def wait_for_space(self, required_bytes: int = 0, max_wait_minutes: int = 30) -> bool:
        """
        Disk joy bo'lishini kutish

        Args:
            required_bytes: Kerakli joy (bytes)
            max_wait_minutes: Maksimal kutish vaqti (daqiqa)

        Returns:
            True agar joy bo'lsa, False aks holda (timeout)
        """
        start_time = time.time()
        max_wait_seconds = max_wait_minutes * 60
        wait_count = 0

        while not self.has_enough_space(required_bytes):
            wait_count += 1

            # Timeout tekshiruvi
            elapsed = time.time() - start_time
            if elapsed > max_wait_seconds:
                logger.error(
                    f"⏰ Timeout: {max_wait_minutes} daqiqa kutildi, disk joy hali ham kam")
                return False

            usage = self.get_disk_usage()
            logger.warning(
                f"⏸️ DISK JOY KAM! "
                f"Bo'sh: {usage['free_gb']:.2f} GB, "
                f"Kerak: {(self.min_free_bytes + required_bytes) / (1024**3):.2f} GB"
            )
            logger.info(
                f"⏳ {self.check_interval} soniya kutilmoqda... ({wait_count}-kutish)")
            logger.info(
                f"💡 Telegram upload fayllarni o'chirib, joy bo'shatishini kutmoqdamiz")

            # Progress ko'rsatish
            remaining = max_wait_seconds - elapsed
            logger.info(f"⏱️ Qolgan vaqt: {remaining / 60:.1f} daqiqa")

            await asyncio.sleep(self.check_interval)

        logger.info(f"✅ Disk joy yetarli bo'ldi! Download davom etadi.")
        return True

    def get_status_message(self) -> str:
        """Status xabari"""
        usage = self.get_disk_usage()

        status = "🟢 YETARLI" if self.has_enough_space() else "🔴 KAM"

        return (
            f"📊 DISK HOLATI: {status}\n"
            f"   💾 Jami: {usage['total_gb']:.2f} GB\n"
            f"   ✅ Bo'sh: {usage['free_gb']:.2f} GB\n"
            f"   📈 Band: {usage['percent_used']:.1f}%\n"
            f"   ⚠️ Minimal: {self.min_free_bytes / (1024**3):.2f} GB"
        )

    async def cleanup_old_files(self, max_age_hours: int = 24) -> int:
        """
        Eski fayllarni tozalash (agar joy kam bo'lsa)

        Args:
            max_age_hours: Maksimal yoshi (soat)

        Returns:
            O'chirilgan fayllar soni
        """
        if self.has_enough_space():
            return 0

        logger.info(f"🧹 Disk joy kam, eski fayllarni tozalash boshlandi...")

        current_time = time.time()
        max_age_seconds = max_age_hours * 3600
        deleted_count = 0
        freed_bytes = 0

        try:
            for file_path in self.download_dir.glob("*"):
                if not file_path.is_file():
                    continue

                # Fayl yoshini tekshirish
                file_age = current_time - file_path.stat().st_mtime

                if file_age > max_age_seconds:
                    file_size = file_path.stat().st_size
                    try:
                        file_path.unlink()
                        deleted_count += 1
                        freed_bytes += file_size
                        logger.info(
                            f"🗑️ O'chirildi: {file_path.name} ({file_size / (1024**2):.2f} MB)")
                    except Exception as e:
                        logger.warning(
                            f"⚠️ O'chirib bo'lmadi: {file_path.name} - {e}")

            if deleted_count > 0:
                logger.info(
                    f"✅ {deleted_count} ta fayl o'chirildi, "
                    f"{freed_bytes / (1024**3):.2f} GB bo'shatildi"
                )
            else:
                logger.info("ℹ️ Eski fayllar topilmadi")

        except Exception as e:
            logger.error(f"❌ Cleanup xatosi: {e}")

        return deleted_count


# Global monitor instance
disk_monitor: Optional[DiskMonitor] = None


def init_disk_monitor(download_dir: str, min_free_gb: float = 5.0, check_interval: int = 60):
    """
    Disk monitor'ni initsializatsiya qilish

    Args:
        download_dir: Download papka
        min_free_gb: Minimal bo'sh joy (GB, default: 5GB)
        check_interval: Tekshirish intervali (soniya, default: 60s)
    """
    global disk_monitor
    disk_monitor = DiskMonitor(download_dir, min_free_gb, check_interval)

    logger.info("💾 Disk monitor ishga tushirildi")
    logger.info(disk_monitor.get_status_message())

    return disk_monitor


def get_disk_monitor() -> Optional[DiskMonitor]:
    """Global disk monitor'ni olish"""
    return disk_monitor
