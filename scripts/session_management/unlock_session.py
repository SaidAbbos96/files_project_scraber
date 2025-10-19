#!/usr/bin/env python3
"""
Telegram session database lock ni ochish - session faylni o'chirmasdan
Faqat SQLite database lock ni ochadi
"""

import os
import sqlite3
import time
import subprocess
from pathlib import Path

def unlock_sqlite_database(db_path):
    """SQLite database lock ni ochish"""
    try:
        print(f"🔓 SQLite lock ochish: {db_path}")
        
        # WAL mode checkpoint qilish
        conn = sqlite3.connect(db_path, timeout=1.0)
        conn.execute("PRAGMA wal_checkpoint(TRUNCATE)")
        conn.execute("PRAGMA optimize")
        conn.close()
        print(f"✅ WAL checkpoint bajarildi: {db_path}")
        return True
        
    except sqlite3.OperationalError as e:
        if "database is locked" in str(e).lower():
            print(f"🔒 Database hali locked: {db_path}")
            return False
        else:
            print(f"❌ SQLite xato: {e}")
            return False
    except Exception as e:
        print(f"⚠️ Xato: {e}")
        return False

def force_unlock_session(session_path):
    """Session database ni force unlock qilish"""
    try:
        session_file = Path(session_path)
        if not session_file.exists():
            print(f"❌ Session fayl topilmadi: {session_path}")
            return False
            
        print(f"🔧 Force unlock: {session_path}")
        
        # 1. WAL va SHM fayllarni vaqtincha rename qilish
        wal_file = Path(f"{session_path}-wal")
        shm_file = Path(f"{session_path}-shm")
        journal_file = Path(f"{session_path}-journal")
        
        backup_files = []
        
        # WAL faylni backup
        if wal_file.exists():
            backup_wal = Path(f"{session_path}-wal.backup")
            wal_file.rename(backup_wal)
            backup_files.append((backup_wal, wal_file))
            print(f"📦 WAL backup: {backup_wal}")
        
        # SHM faylni backup  
        if shm_file.exists():
            backup_shm = Path(f"{session_path}-shm.backup")
            shm_file.rename(backup_shm)
            backup_files.append((backup_shm, shm_file))
            print(f"📦 SHM backup: {backup_shm}")
            
        # Journal faylni backup
        if journal_file.exists():
            backup_journal = Path(f"{session_path}-journal.backup")
            journal_file.rename(backup_journal)
            backup_files.append((backup_journal, journal_file))
            print(f"📦 Journal backup: {backup_journal}")
        
        # 2. Asosiy session faylni unlock qilish
        time.sleep(1)
        success = unlock_sqlite_database(session_path)
        
        # 3. Backup fayllarni qayta tiklash
        time.sleep(1)
        for backup_file, original_file in backup_files:
            try:
                if backup_file.exists():
                    backup_file.rename(original_file)
                    print(f"🔄 Restored: {original_file}")
            except Exception as e:
                print(f"⚠️ Restore xato {original_file}: {e}")
        
        return success
        
    except Exception as e:
        print(f"❌ Force unlock xato: {e}")
        return False

def kill_main_processes():
    """Faqat bizning loyiha main processlarini to'xtatish"""
    try:
        print("🔄 files_project_scraber main processlarni to'xtatish...")
        
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
            print("📤 Bizning main processlar topildi:")
            for pid, proc_line in our_processes:
                print(f"   PID {pid}: {proc_line}")
            
            print(f"\n⚠️ {len(our_processes)} ta processni to'xtatamiz")
            for pid, _ in our_processes:
                try:
                    # Avval SIGTERM
                    subprocess.run(["kill", "-TERM", pid], check=False)
                    print(f"📤 SIGTERM yuborildi: PID {pid}")
                except Exception as e:
                    print(f"⚠️ SIGTERM xato PID {pid}: {e}")
            
            # 5 soniya kutish
            print("⏳ 5 soniya kutish...")
            time.sleep(5)
            
            # Hali ishlab turganlarni SIGKILL
            for pid, _ in our_processes:
                try:
                    result = subprocess.run(["kill", "-0", pid], check=False, capture_output=True)
                    if result.returncode == 0:  # Process hali ishlab turibdi
                        subprocess.run(["kill", "-KILL", pid], check=False)
                        print(f"🔨 SIGKILL yuborildi: PID {pid}")
                except Exception:
                    pass  # Process allaqachon o'lgan
                    
            print("✅ Main processlar to'xtatildi")
        else:
            print("ℹ️ Bizning main processlar topilmadi")
            
    except Exception as e:
        print(f"❌ Process to'xtatishda xato: {e}")

def main():
    print("🔓 Telegram Session Unlock (Session faylni saqlab)")
    print("=" * 55)
    
    # 1. Main processlarni to'xtatish
    kill_main_processes()
    
    # 2. Session fayllarni topish
    session_files = []
    for root, dirs, files in os.walk('.'):
        for file in files:
            if file.endswith('.session'):
                session_path = os.path.join(root, file)
                session_files.append(session_path)
    
    if not session_files:
        print("❌ Session fayllar topilmadi")
        return
    
    print(f"📁 {len(session_files)} ta session fayl topildi:")
    for session_file in session_files:
        print(f"   {session_file}")
    
    # 3. Har bir session faylni unlock qilish
    print("\n🔓 Session fayllarni unlock qilish...")
    success_count = 0
    
    for session_file in session_files:
        print(f"\n📂 Ishlov berish: {session_file}")
        if force_unlock_session(session_file):
            success_count += 1
            print(f"✅ Unlock muvaffaqiyatli: {session_file}")
        else:
            print(f"❌ Unlock muvaffaqiyatsiz: {session_file}")
    
    print(f"\n📊 Natija: {success_count}/{len(session_files)} session unlock bo'ldi")
    
    if success_count > 0:
        print("✅ Session lock muammosi hal qilindi!")
        print("🔄 Endi main.py ni ishga tushiring")
    else:
        print("❌ Hech qanday session unlock bo'lmadi")
        print("💡 Manual restart kerak bo'lishi mumkin")

if __name__ == "__main__":
    main()