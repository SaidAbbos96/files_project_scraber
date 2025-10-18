#!/usr/bin/env python3
"""
Session Manager - Avtomatik session backup va restore funksiyasi
Agar session bloklanagan bo'lsa, backup yaratib yangi session bilan ishlaydi
"""

import os
import shutil
import sqlite3
import asyncio
import time
from datetime import datetime
from pathlib import Path


class SessionManager:
    def __init__(self, session_file=None):
        # Agar session_file berilmagan bo'lsa, telefon raqami bilan nomi yaratamiz
        if session_file is None:
            self.session_file = self.find_session_file()
        else:
            self.session_file = session_file
        self.backup_dir = "session_backups"
        self.lock_timeout = 5  # 5 soniya timeout

    def find_session_file(self):
        """Mavjud session faylini topish"""
        # 1. Default telefon raqami bilan
        phone = "+998200089990"
        default_session = f"telegramuploader/session_{phone}.session"

        if os.path.exists(default_session):
            return default_session

        # 2. telegramuploader papkasida barcha session fayllarni qidirish
        telegram_dir = "telegramuploader"
        if os.path.exists(telegram_dir):
            for file in os.listdir(telegram_dir):
                if file.startswith("session_") and file.endswith(".session"):
                    session_path = os.path.join(telegram_dir, file)
                    print(f"🔍 Topilgan session fayli: {session_path}")
                    return session_path

        # 3. Agar hech narsa topilmasa, default qaytar
        print(
            f"⚠️ Session fayli topilmadi, default ishlatiladi: {default_session}")
        return default_session

    def ensure_backup_dir(self):
        """Backup papkasini yaratish"""
        if not os.path.exists(self.backup_dir):
            os.makedirs(self.backup_dir)
            print(f"📁 Backup papka yaratildi: {self.backup_dir}")

    def is_session_locked(self, verbose=True):
        """Session bloklanganligini tekshirish"""
        if not os.path.exists(self.session_file):
            if verbose:
                print("ℹ️  Session fayli mavjud emas, yangi session yaratiladi")
            return False

        try:
            # SQLite faylini ochishga harakat qilish
            conn = sqlite3.connect(
                self.session_file, timeout=self.lock_timeout)
            conn.execute("SELECT 1")
            conn.close()
            if verbose:
                print("✅ Session fayli normal holatda")
            return False
        except sqlite3.OperationalError as e:
            if "database is locked" in str(e).lower():
                if verbose:
                    print("🔒 Session fayli bloklanagan!")
                return True
            else:
                if verbose:
                    print(f"⚠️  Session faylida xatolik: {e}")
                return True
        except Exception as e:
            if verbose:
                print(f"❌ Session tekshirishda xatolik: {e}")
            return True

    def create_backup(self):
        """Session faylini backup qilish"""
        if not os.path.exists(self.session_file):
            print("⚠️  Backup qilish uchun session fayli topilmadi")
            return None

        self.ensure_backup_dir()

        # Backup nomi: session_YYYY-MM-DD_HH-MM-SS.session
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        backup_name = f"session_{timestamp}.session"
        backup_path = os.path.join(self.backup_dir, backup_name)

        try:
            shutil.copy2(self.session_file, backup_path)
            print(f"💾 Session backup yaratildi: {backup_path}")
            return backup_path
        except Exception as e:
            print(f"❌ Backup yaratishda xatolik: {e}")
            return None

    def delete_locked_session(self):
        """Bloklanagan session faylini o'chirish"""
        try:
            if os.path.exists(self.session_file):
                os.remove(self.session_file)
                print(
                    f"🗑️  Bloklanagan session fayli o'chirildi: {self.session_file}")
                return True
        except Exception as e:
            print(f"❌ Session faylini o'chirishda xatolik: {e}")
            return False
        return True

    def restore_from_backup(self, backup_path):
        """Backup dan session ni qayta tiklash"""
        try:
            if os.path.exists(backup_path):
                shutil.copy2(backup_path, self.session_file)
                print(f"🔄 Session backup dan tiklandi: {backup_path}")
                return True
        except Exception as e:
            print(f"❌ Backup dan tiklashda xatolik: {e}")
            return False
        return False

    def list_backups(self):
        """Mavjud backup fayllarini ko'rsatish"""
        if not os.path.exists(self.backup_dir):
            print("📁 Backup papka mavjud emas")
            return []

        backups = []
        for file in os.listdir(self.backup_dir):
            if file.startswith("session_") and file.endswith(".session"):
                file_path = os.path.join(self.backup_dir, file)
                file_size = os.path.getsize(file_path)
                file_time = datetime.fromtimestamp(os.path.getmtime(file_path))
                backups.append({
                    'name': file,
                    'path': file_path,
                    'size': file_size,
                    'time': file_time
                })

        # Vaqt bo'yicha saralash (yangidan eskiga)
        backups.sort(key=lambda x: x['time'], reverse=True)
        return backups

    def cleanup_old_backups(self, keep_count=10):
        """Eski backup fayllarini tozalash"""
        backups = self.list_backups()
        if len(backups) <= keep_count:
            return

        old_backups = backups[keep_count:]
        deleted_count = 0

        for backup in old_backups:
            try:
                os.remove(backup['path'])
                deleted_count += 1
            except Exception as e:
                print(f"⚠️  {backup['name']} o'chirishda xatolik: {e}")

        if deleted_count > 0:
            print(f"🧹 {deleted_count} ta eski backup o'chirildi")

    def auto_fix_session(self, verbose=True):
        """Avtomatik session ni tuzatish"""
        if verbose:
            print("\n🔍 Session holatini tekshiruv...")

        if not self.is_session_locked(verbose=False):
            if verbose:
                print("✅ Session normal holatda, hech narsa qilish shart emas")
            return True

        if verbose:
            print("🔧 Avtomatik session tuzatish boshlanmoqda...")

        # 1. Backup yaratish
        backup_path = self.create_backup()
        if not backup_path:
            if verbose:
                print("❌ Backup yaratib bo'lmadi, davom etish xavfli")
            return False

        # 2. Bloklanagan session ni o'chirish
        if not self.delete_locked_session():
            if verbose:
                print("❌ Bloklanagan session ni o'chirib bo'lmadi")
            # Alternativ: copy + rename usuli
            return self.force_session_reset(verbose)

        # 3. Yangi session yaratilishini kutish
        if verbose:
            print("⏳ Yangi session yaratilishini kutish...")
        time.sleep(2)

        # 4. Eski backup larni tozalash
        self.cleanup_old_backups()

        if verbose:
            print("✅ Session avtomatik tuzatildi!")
            print(f"💾 Backup saqlandi: {backup_path}")
            print("🚀 Dastur normal ishlay oladi")

        return True

    def force_session_reset(self, verbose=True):
        """Majburan session reset qilish - copy va rename bilan"""
        try:
            if verbose:
                print("🔄 Majburan session reset qilish...")

            # Yangi nom bilan kopiyalash
            temp_name = f"{self.session_file}.temp_{int(time.time())}"

            if os.path.exists(self.session_file):
                try:
                    # Kopiyalash
                    shutil.copy2(self.session_file, temp_name)

                    # Eski faylni o'chirish
                    os.remove(self.session_file)

                    # Temp faylni qaytarish
                    shutil.move(temp_name, self.session_file)

                    if verbose:
                        print("✅ Session majburan reset qilindi")
                    return True

                except Exception as e:
                    if verbose:
                        print(f"❌ Copy-rename usulida xatolik: {e}")

                    # Eng oxirgi chora - faylni butunlay o'chirish
                    try:
                        os.remove(self.session_file)
                        if verbose:
                            print(
                                "🗑️ Session fayli butunlay o'chirildi, yangi session yaratiladi")
                        return True
                    except Exception as e2:
                        if verbose:
                            print(f"❌ Faylni o'chirishda ham xatolik: {e2}")
                        return False

            return True

        except Exception as e:
            if verbose:
                print(f"❌ Force reset da xatolik: {e}")
            return False

    def interactive_restore(self):
        """Interaktiv backup dan tiklash"""
        backups = self.list_backups()

        if not backups:
            print("📁 Hech qanday backup topilmadi")
            return False

        print(f"\n📋 Mavjud backup fayllar ({len(backups)} ta):")
        for i, backup in enumerate(backups, 1):
            size_mb = backup['size'] / 1024 / 1024
            time_str = backup['time'].strftime("%Y-%m-%d %H:%M:%S")
            print(f"{i}. {backup['name']} ({size_mb:.1f}MB) - {time_str}")

        try:
            choice = input(
                f"\nQaysi backup ni tiklaysiz? (1-{len(backups)}, 0=bekor qilish): ")
            choice = int(choice)

            if choice == 0:
                print("❌ Bekor qilindi")
                return False

            if 1 <= choice <= len(backups):
                selected_backup = backups[choice - 1]

                # Joriy session ni backup qilish
                current_backup = self.create_backup()

                # Tanlangan backup ni tiklash
                if self.restore_from_backup(selected_backup['path']):
                    print("✅ Backup muvaffaqiyatli tiklandi!")
                    return True
                else:
                    print("❌ Backup tiklashda xatolik")
                    return False
            else:
                print("❌ Noto'g'ri tanlov")
                return False

        except ValueError:
            print("❌ Noto'g'ri raqam")
            return False
        except KeyboardInterrupt:
            print("\n❌ Bekor qilindi")
            return False


def main():
    """Test funksiyasi"""
    manager = SessionManager()

    print("🔍 Session Manager Test")
    print("=" * 50)

    # Session holatini tekshirish
    if manager.is_session_locked():
        manager.auto_fix_session()
    else:
        print("✅ Session normal holatda")

    # Backup larni ko'rsatish
    backups = manager.list_backups()
    if backups:
        print(f"\n📋 Mavjud backup fayllar: {len(backups)} ta")
        for backup in backups[:3]:  # Faqat 3 ta yangi backup
            size_mb = backup['size'] / 1024 / 1024
            time_str = backup['time'].strftime("%Y-%m-%d %H:%M:%S")
            print(f"  • {backup['name']} ({size_mb:.1f}MB) - {time_str}")


if __name__ == "__main__":
    main()
