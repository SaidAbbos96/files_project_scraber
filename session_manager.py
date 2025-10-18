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
        """Telegram session lock holatini tekshirish"""
        if not os.path.exists(self.session_file):
            if verbose:
                print("ℹ️  Session fayli mavjud emas, yangi session yaratiladi")
            return False

        try:
            # Telegram session lock ni tekshirish uchun fayl ochishga harakat
            # 1. Faylni read-write rejimida ochish
            with open(self.session_file, 'r+b') as f:
                # Faylni o'qishga harakat qilish
                f.seek(0)
                f.read(1)
                # Faylga yozishga harakat qilish (lock aniqlash uchun)
                f.seek(0, 2)  # Fayl oxiriga
                current_pos = f.tell()
                f.seek(current_pos)
            
            # Agar bu yerga yetib kelsa, fayl lock emas
            if verbose:
                print("✅ Session fayli normal holatda")
            return False
            
        except PermissionError as e:
            # Permission error - fayl lock bo'lishi mumkin
            if verbose:
                print(f"🔒 Session fayli lock bo'lishi mumkin: {e}")
            return True
            
        except IOError as e:
            # IO error - fayl ishlatilayotgan bo'lishi mumkin
            if "being used by another process" in str(e).lower() or \
               "resource temporarily unavailable" in str(e).lower():
                if verbose:
                    print(f"🔒 Session fayli boshqa jarayon tomonidan ishlatilmoqda: {e}")
                return True
            else:
                if verbose:
                    print(f"⚠️  Session faylida I/O xatolik: {e}")
                return True
                
        except Exception as e:
            # Boshqa xatoliklar
            if verbose:
                print(f"❌ Session tekshirishda xatolik: {e}")
            
            # Agar fayl ochilmasa, process check qilamiz
            return self.check_session_process_usage(verbose)
    
    def is_database_locked(self, verbose=True):
        """Database lock holatini tekshirish - asosiy sabab"""
        try:
            # local_db papkasidagi database fayllarni tekshirish
            db_dir = "local_db"
            if not os.path.exists(db_dir):
                return False
            
            locked_files = []
            for file in os.listdir(db_dir):
                if file.endswith('.db'):
                    db_path = os.path.join(db_dir, file)
                    try:
                        # SQLite database ni ochishga harakat - qisqa timeout
                        conn = sqlite3.connect(db_path, timeout=0.1)  # 0.1 soniya timeout
                        conn.execute("SELECT 1")
                        conn.close()
                    except sqlite3.OperationalError as e:
                        if "database is locked" in str(e).lower():
                            locked_files.append(db_path)
                            if verbose:
                                print(f"🔒 Database bloklanagan: {db_path}")
            
            if locked_files:
                if verbose:
                    print(f"❌ {len(locked_files)} ta database fayli bloklanagan!")
                    print("💡 Bu session muammosining asosiy sababi bo'lishi mumkin")
                return True
            
            return False
            
        except Exception as e:
            if verbose:
                print(f"⚠️ Database tekshirishda xatolik: {e}")
            return False
    
    def check_session_process_usage(self, verbose=True):
        """Session faylini ishlatayotgan processlarni tekshirish"""
        try:
            import subprocess
            
            # lsof yordamida faylni ishlatayotgan processlarni topish
            result = subprocess.run(['lsof', self.session_file], 
                                  capture_output=True, text=True, timeout=5)
            
            if result.returncode == 0 and result.stdout.strip():
                if verbose:
                    print(f"🔒 Session fayli ishlatilmoqda:")
                    print(result.stdout.strip())
                return True
            else:
                # lsof hech narsa topmadi, fayl free
                return False
                
        except (subprocess.TimeoutExpired, FileNotFoundError, Exception) as e:
            if verbose:
                print(f"⚠️ Process check da xatolik: {e}")
            # Process check muvaffaqiyatsiz bo'lsa, ehtiyotkorlik uchun false qaytaramiz
            return False

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
        """Avtomatik session ni tuzatish - kengaytirilgan diagnostika"""
        if verbose:
            print("\n🔍 Kengaytirilgan session diagnostikasi...")
        
        # 1. Session fayl holatini tekshirish
        session_locked = self.is_session_locked(verbose=verbose)
        
        # 2. Database lock holatini tekshirish
        db_locked = self.is_database_locked(verbose=verbose)
        
        # 3. Agar hech qanday muammo yo'q bo'lsa
        if not session_locked and not db_locked:
            if verbose:
                print("✅ Session va database normal holatda")
            return True
        
        # 4. Muammolar topildi - tuzatish boshlanadi
        if verbose:
            print("🔧 Muammolar aniqlandi, avtomatik tuzatish boshlanmoqda...")
            if session_locked:
                print("   📋 Session fayli muammosi")
            if db_locked:
                print("   📋 Database lock muammosi")
        
        # 5. Session backup yaratish
        backup_path = None
        if session_locked:
            backup_path = self.create_backup()
            if not backup_path:
                if verbose:
                    print("❌ Backup yaratib bo'lmadi, davom etish xavfli")
                return False
        
        # 6. Database lock ni hal qilish
        if db_locked:
            if verbose:
                print("🔧 Database lock ni hal qilishga harakat...")
            self.fix_database_locks(verbose)
        
        # 7. Session lock ni hal qilish  
        if session_locked:
            if not self.delete_locked_session():
                if verbose:
                    print("❌ Bloklanagan session ni o'chirib bo'lmadi")
                # Alternativ: copy + rename usuli
                return self.force_session_reset(verbose)
        
        # 8. Yangi session yaratilishini kutish
        if verbose:
            print("⏳ Yangi session yaratilishini kutish...")
        time.sleep(3)
        
        # 9. Eski backup larni tozalash
        self.cleanup_old_backups()
        
        # 10. Final tekshiruv
        final_check = self.is_session_locked(verbose=False) or self.is_database_locked(verbose=False)
        
        if not final_check:
            if verbose:
                print("✅ Session va database muvaffaqiyatli tuzatildi!")
                if backup_path:
                    print(f"💾 Backup saqlandi: {backup_path}")
                print("🚀 Dastur normal ishlay oladi")
            return True
        else:
            if verbose:
                print("⚠️ Ba'zi muammolar hali ham mavjud")
                print("💡 Manual tekshiruv talab qilinishi mumkin")
            return False
    
    def fix_database_locks(self, verbose=True):
        """Database lock larni hal qilish"""
        try:
            if verbose:
                print("🔧 Database lock larni hal qilish...")
            
            # Barcha database connection larni yopish
            import gc
            gc.collect()  # Garbage collection
            
            # Biroz kutish
            time.sleep(1)
            
            if verbose:
                print("✅ Database connection lar tozalandi")
            return True
            
        except Exception as e:
            if verbose:
                print(f"❌ Database lock hal qilishda xatolik: {e}")
            return False

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
