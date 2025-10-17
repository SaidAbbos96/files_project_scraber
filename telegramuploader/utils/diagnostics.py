"""
Telegram upload diagnostika va monitoring utilitalari
"""
import json
import time
import re
from pathlib import Path
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict
from utils.logger_core import logger


@dataclass
class UploadError:
    """Upload xatosi haqida ma'lumot"""
    timestamp: float
    filename: str
    file_size: int
    error_type: str
    error_message: str
    full_traceback: str
    duration_seconds: float
    retry_count: int = 0


@dataclass
class UploadStats:
    """Upload statistikalari"""
    total_attempts: int = 0
    successful_uploads: int = 0
    failed_uploads: int = 0
    rate_limit_errors: int = 0
    flood_limit_errors: int = 0
    corruption_errors: int = 0
    auth_errors: int = 0
    connection_errors: int = 0
    unknown_errors: int = 0
    total_wait_time: float = 0.0
    average_upload_time: float = 0.0


class TelegramDiagnostics:
    """Telegram upload diagnostika va monitoring"""

    def __init__(self, log_file: str = "telegram_diagnostics.json"):
        self.log_file = Path(log_file)
        self.errors: List[UploadError] = []
        self.stats = UploadStats()
        self.session_start = time.time()

    def categorize_error(self, error_msg: str) -> str:
        """Xato turini aniqlash"""
        error_msg = str(error_msg).lower()

        if "wait of" in error_msg and "seconds" in error_msg:
            return "rate_limit"
        elif "peer_flood" in error_msg:
            return "flood_limit"
        elif "file_parts_invalid" in error_msg:
            return "file_corruption"
        elif "auth_key_invalid" in error_msg:
            return "auth_error"
        elif "connection_not_inited" in error_msg:
            return "connection_error"
        elif "timeout" in error_msg:
            return "timeout_error"
        elif "network" in error_msg or "connection" in error_msg:
            return "network_error"
        else:
            return "unknown_error"

    def extract_wait_time(self, error_msg: str) -> Optional[float]:
        """Rate limit error dan kutish vaqtini ajratib olish"""
        match = re.search(r"wait of (\d+)", error_msg)
        if match:
            return float(match.group(1))
        return None

    def log_error(self, filename: str, file_size: int, error_msg: str,
                  full_traceback: str, duration: float, retry_count: int = 0):
        """Xatoni qayd qilish"""
        error_type = self.categorize_error(error_msg)

        error = UploadError(
            timestamp=time.time(),
            filename=filename,
            file_size=file_size,
            error_type=error_type,
            error_message=error_msg,
            full_traceback=full_traceback,
            duration_seconds=duration,
            retry_count=retry_count
        )

        self.errors.append(error)
        self.update_stats(error)
        self.save_to_file()

        # Wait time ni aniqlash
        if error_type == "rate_limit":
            wait_time = self.extract_wait_time(error_msg)
            if wait_time:
                self.stats.total_wait_time += wait_time
                logger.warning(
                    f"⏰ Rate limit: {wait_time} soniya kutish kerak")

        logger.error(f"📊 Xato qayd qilindi: {error_type} - {filename}")

    def log_success(self, filename: str, duration: float):
        """Muvaffaqiyatli uploadni qayd qilish"""
        self.stats.total_attempts += 1
        self.stats.successful_uploads += 1

        # Average upload time ni yangilash
        total_time = (self.stats.average_upload_time *
                      (self.stats.successful_uploads - 1) + duration)
        self.stats.average_upload_time = total_time / self.stats.successful_uploads

        logger.info(
            f"✅ Muvaffaqiyat qayd qilindi: {filename} ({duration:.1f}s)")

    def update_stats(self, error: UploadError):
        """Statistikalarni yangilash"""
        self.stats.total_attempts += 1
        self.stats.failed_uploads += 1

        if error.error_type == "rate_limit":
            self.stats.rate_limit_errors += 1
        elif error.error_type == "flood_limit":
            self.stats.flood_limit_errors += 1
        elif error.error_type == "file_corruption":
            self.stats.corruption_errors += 1
        elif error.error_type == "auth_error":
            self.stats.auth_errors += 1
        elif error.error_type == "connection_error":
            self.stats.connection_errors += 1
        else:
            self.stats.unknown_errors += 1

    def get_error_summary(self) -> Dict:
        """Xatolar xulosasi"""
        if not self.errors:
            return {"message": "Hech qanday xato qayd qilinmagan"}

        recent_errors = self.errors[-10:]  # So'nggi 10 ta xato

        error_types = {}
        for error in recent_errors:
            error_types[error.error_type] = error_types.get(
                error.error_type, 0) + 1

        return {
            "total_errors": len(self.errors),
            "recent_errors": len(recent_errors),
            "error_types": error_types,
            "most_common_error": max(error_types.items(), key=lambda x: x[1])[0] if error_types else None,
            "total_wait_time": self.stats.total_wait_time,
            "session_duration": time.time() - self.session_start
        }

    def get_recommendations(self) -> List[str]:
        """Tavsiyalar berish"""
        recommendations = []

        if self.stats.rate_limit_errors > 3:
            recommendations.append(
                "🔄 Rate limit ko'p - upload tezligini pasaytiring")

        if self.stats.flood_limit_errors > 1:
            recommendations.append("⏸️ Flood limit - bir oz kutib turing")

        if self.stats.corruption_errors > 2:
            recommendations.append(
                "🔍 Fayl corruption ko'p - download qilish jarayonini tekshiring")

        if self.stats.auth_errors > 0:
            recommendations.append(
                "🔑 Auth error - Telegram client ni qayta ulang")

        if self.stats.connection_errors > 2:
            recommendations.append(
                "🌐 Connection error ko'p - internetni tekshiring")

        if self.stats.failed_uploads > self.stats.successful_uploads:
            recommendations.append(
                "⚠️ Muvaffaqiyatsizlik ko'p - konfiguratsiyani tekshiring")

        return recommendations

    def save_to_file(self):
        """Diagnostika ma'lumotlarini faylga saqlash"""
        try:
            data = {
                "session_start": self.session_start,
                "stats": asdict(self.stats),
                # So'nggi 50 ta
                "recent_errors": [asdict(error) for error in self.errors[-50:]],
                "summary": self.get_error_summary(),
                "recommendations": self.get_recommendations()
            }

            with open(self.log_file, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)

        except Exception as e:
            logger.error(f"❌ Diagnostika faylini saqlashda xato: {e}")

    def print_report(self):
        """Hisobot chop etish"""
        print("\n" + "="*60)
        print("📊 TELEGRAM UPLOAD DIAGNOSTIKA HISOBOTI")
        print("="*60)

        print(
            f"⏱️ Session davomiyligi: {(time.time() - self.session_start)/60:.1f} daqiqa")
        print(f"📈 Jami urinishlar: {self.stats.total_attempts}")
        print(f"✅ Muvaffaqiyatli: {self.stats.successful_uploads}")
        print(f"❌ Muvaffaqiyatsiz: {self.stats.failed_uploads}")

        if self.stats.total_attempts > 0:
            success_rate = (self.stats.successful_uploads /
                            self.stats.total_attempts) * 100
            print(f"📊 Muvaffaqiyat darajasi: {success_rate:.1f}%")

        if self.stats.successful_uploads > 0:
            print(
                f"⏱️ O'rtacha upload vaqti: {self.stats.average_upload_time:.1f}s")

        if self.stats.total_wait_time > 0:
            print(
                f"⏰ Jami kutish vaqti: {self.stats.total_wait_time/60:.1f} daqiqa")

        print("\n🔍 XATO TURLARI:")
        print(f"   ⏰ Rate limit: {self.stats.rate_limit_errors}")
        print(f"   🚫 Flood limit: {self.stats.flood_limit_errors}")
        print(f"   💔 File corruption: {self.stats.corruption_errors}")
        print(f"   🔑 Auth errors: {self.stats.auth_errors}")
        print(f"   🔌 Connection errors: {self.stats.connection_errors}")
        print(f"   ❓ Unknown errors: {self.stats.unknown_errors}")

        recommendations = self.get_recommendations()
        if recommendations:
            print("\n💡 TAVSIYALAR:")
            for rec in recommendations:
                print(f"   {rec}")

        print("\n" + "="*60)


# Global diagnostics instance
diagnostics = TelegramDiagnostics()
