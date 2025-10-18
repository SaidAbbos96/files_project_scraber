#!/usr/bin/env python3
"""
Session fayllarni butunlay o'chirish - database lock 100% hal bo'ladi
Login ma'lumotlari yo'qoladi, qayta kiritish kerak
"""

import os
import time
import subprocess
from pathlib import Path

def kill_main_processes():
    """Main processlarni to'xtatish"""
    try:
        print("🔄 files_project_scraber processlarni to'xtatish...")
        
        # files_project_scraber path bilan processlarni topish
        result = subprocess.run(["ps", "aux"], capture_output=True, text=True, check=True)
        lines = result.stdout.split('\n')
        
        our_processes = []
        for line in lines:
            if 'files_project_scraber' in line and 'python' in line and 'main' in line and 'grep' not in line:
                parts = line.split()
                if len(parts) >= 2:
                    pid = parts[1]
                    our_processes.append((pid, line))
        
        if our_processes:
            print("📤 Main processlar topildi:")
            for pid, proc_line in our_processes:
                print(f"   PID {pid}: {proc_line}")
            
            print(f"\n🔄 {len(our_processes)} ta processni to'xtatish...")
            for pid, _ in our_processes:
                try:
                    subprocess.run(["kill", "-TERM", pid], check=False)
                    print(f"📤 SIGTERM: PID {pid}")
                except Exception as e:
                    print(f"⚠️ SIGTERM xato PID {pid}: {e}")
            
            # 5 soniya kutish
            print("⏳ 5 soniya kutish...")
            time.sleep(5)
            
            # Force kill
            for pid, _ in our_processes:
                try:
                    result = subprocess.run(["kill", "-0", pid], check=False, capture_output=True)
                    if result.returncode == 0:
                        subprocess.run(["kill", "-KILL", pid], check=False)
                        print(f"🔨 SIGKILL: PID {pid}")
                except Exception:
                    pass
                    
            print("✅ Processlar to'xtatildi")
        else:
            print("ℹ️ Main processlar topilmadi")
            
    except Exception as e:
        print(f"❌ Process to'xtatishda xato: {e}")

def delete_all_session_files():
    """Barcha session fayllarni o'chirish"""
    try:
        print("\n🗑️ Barcha session fayllarni qidirish va o'chirish...")
        
        # Barcha session fayllarni topish
        session_patterns = [
            "**/*.session",
            "**/*.session-wal", 
            "**/*.session-shm",
            "**/*.session-journal"
        ]
        
        deleted_count = 0
        backup_dir = Path("deleted_sessions_backup")
        backup_dir.mkdir(exist_ok=True)
        timestamp = int(time.time())
        
        for pattern in session_patterns:
            session_files = list(Path('.').glob(pattern))
            
            for session_file in session_files:
                if session_file.is_file():
                    print(f"📁 Topildi: {session_file}")
                    
                    # Backup yaratish
                    backup_name = f"{session_file.name}_{timestamp}"
                    backup_path = backup_dir / backup_name
                    
                    try:
                        # Backup
                        import shutil
                        shutil.copy2(session_file, backup_path)
                        print(f"📦 Backup: {backup_path}")
                    except Exception as e:
                        print(f"⚠️ Backup xato: {e}")
                    
                    # O'chirish
                    try:
                        session_file.unlink()
                        print(f"🗑️ O'chirildi: {session_file}")
                        deleted_count += 1
                    except Exception as e:
                        print(f"❌ O'chirishda xato {session_file}: {e}")
                        # Force remove
                        try:
                            os.remove(session_file)
                            print(f"🔨 Force o'chirildi: {session_file}")
                            deleted_count += 1
                        except Exception as e2:
                            print(f"❌ Force o'chirib bo'lmadi: {e2}")
        
        if deleted_count > 0:
            print(f"\n✅ {deleted_count} ta session fayl o'chirildi")
            print(f"📦 Backup: {backup_dir}/")
        else:
            print("\nℹ️ Session fayllar topilmadi")
            
        return deleted_count > 0
        
    except Exception as e:
        print(f"❌ Session fayllarni o'chirishda xato: {e}")
        return False

def check_session_lock():
    """Session lock borligini tekshirish"""
    try:
        import sqlite3
        session_files = list(Path('.').glob("**/*.session"))
        
        if not session_files:
            print("ℹ️ Session fayllar topilmadi")
            return False
            
        print(f"🔍 {len(session_files)} ta session fayl tekshirilmoqda...")
        
        for session_file in session_files:
            try:
                conn = sqlite3.connect(str(session_file), timeout=0.1)
                conn.execute("SELECT name FROM sqlite_master LIMIT 1")
                conn.close()
                print(f"✅ Session OK: {session_file}")
            except sqlite3.OperationalError as e:
                if "database is locked" in str(e).lower():
                    print(f"� Session LOCKED: {session_file}")
                    return True
                else:
                    print(f"⚠️ Session xato: {session_file} - {e}")
            except Exception as e:
                print(f"⚠️ Tekshirishda xato: {session_file} - {e}")
        
        return False
        
    except Exception as e:
        print(f"❌ Session tekshirishda xato: {e}")
        return False

def main():
    print("�🗑️ SESSION FAYLLARNI BUTUNLAY O'CHIRISH")
    print("=" * 45)
    
    # Session lock tekshirish
    session_locked = check_session_lock()
    print()
    
    if not session_locked:
        print("✅ Session lock muammosi yo'q!")
        print("💡 Bu script faqat quyidagi holatlarda kerak:")
        print("   • 'database is locked' xatosi ko'rinanda")
        print("   • Upload Only rejimi ishlamay qolganda") 
        print("   • Telegram connection xatolari bo'lganda")
        print()
        force_confirm = input("❓ Baribir session fayllarni o'chirishni xohlaysizmi? (yes/no): ").strip().lower()
        if force_confirm not in ['yes', 'y']:
            print("❌ Bekor qilindi - session fayllar saqlanib qoldi")
            print("🔄 Oddiy holatda main.py ni ishga tushiring")
            return
        print("⚠️ Majburiy o'chirish rejimi...")
    else:
        print("🔒 SESSION LOCK MUAMMOSI ANIQLANDI!")
        print("   Bu script aynan shu muammo uchun kerak")
    
    print()
    print("⚠️ OGOHLANTIRISH:")
    print("   • Telegram login ma'lumotlari yo'qoladi")
    print("   • Phone number va code qayta kiritish kerak")
    print("   • Database lock 100% hal bo'ladi")
    print("   • Backup yaratiladi")
    print()
    
    confirm = input("❓ Davom etishni xohlaysizmi? (yes/no): ").strip().lower()
    if confirm not in ['yes', 'y', 'ha']:
        print("❌ Bekor qilindi")
        return
    
    print("\n🚀 Jarayon boshlanmoqda...")
    
    # 1. Processlarni to'xtatish
    kill_main_processes()
    
    # 2. Session fayllarni o'chirish
    success = delete_all_session_files()
    
    print("\n" + "=" * 45)
    if success:
        print("✅ SESSION LOCK MUAMMOSI HAL QILINDI!")
        print("📝 Keyingi qadamlar:")
        print("   1. python -m main ishga tushiring")
        print("   2. Upload Only rejimini tanlayman")
        print("   3. Telegram login so'raydi:")
        print("      • Phone number kiriting")
        print("      • SMS code kiriting")
        print("   4. Login muvaffaqiyatli bo'lgandan keyin upload boshlanadi")
        print()
        print("🎯 Database lock endi 100% yo'q!")
    else:
        print("❌ Session fayllar topilmadi yoki o'chirib bo'lmadi")
        print("💡 Manual o'chirish: rm -f **/*.session*")

if __name__ == "__main__":
    main()