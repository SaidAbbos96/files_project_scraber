#!/usr/bin/env python3
"""
Telegram session database lock muammosini hal qilish
Usage: python fix_session_lock.py
"""

import os
import time
import subprocess
import shutil
from pathlib import Path

def kill_telegram_processes():
    """Faqat joriy loyiha Telegram processlarini to'xtatish"""
    try:
        print("🔄 Faqat files_project_scraber processlarni to'xtatish...")
        
        # Joriy papka path
        current_dir = os.getcwd()
        print(f"📁 Joriy papka: {current_dir}")
        
        # Faqat joriy papkadagi python main.py processlarni topish
        try:
            result = subprocess.run(
                ["ps", "aux"], 
                capture_output=True, text=True, check=True
            )
            
            lines = result.stdout.split('\n')
            our_processes = []
            
            for line in lines:
                if current_dir in line and 'python' in line and 'main' in line and 'grep' not in line:
                    our_processes.append(line)
            
            if our_processes:
                print("📤 Bizning loyiha processlar topildi:")
                for proc in our_processes:
                    print(f"   {proc}")
                
                confirm = input("\n⚠️ Ushbu processlarni o'chirishni xohlaysizmi? (y/n): ").strip().lower()
                if confirm in ['y', 'yes', 'ha']:
                    for proc_line in our_processes:
                        try:
                            pid = proc_line.split()[1]
                            subprocess.run(["kill", "-TERM", pid], check=False)
                            print(f"📤 Process {pid} to'xtatildi")
                        except Exception as e:
                            print(f"⚠️ Process {pid} ni to'xtatishda xato: {e}")
                else:
                    print("❌ Process to'xtatish bekor qilindi")
            else:
                print("ℹ️ Bizning Python main.py process ishlamayapti")
                
        except Exception as e:
            print(f"⚠️ Process qidirishda xato: {e}")
        
        # 3 soniya kutish
        time.sleep(3)
        print("✅ Process tekshiruvi tugadi")
        
    except Exception as e:
        print(f"⚠️ Process to'xtatishda xato: {e}")

def backup_and_remove_session_files():
    """Session fayllarini backup qilib o'chirish"""
    try:
        print("📦 Session fayllarini backup qilish...")
        
        # Session fayllar ro'yxati
        session_files = [
            "telegramuploader/session.session",
            "telegramuploader/session.session-journal", 
            "telegramuploader/session.session-wal",
            "telegramuploader/session.session-shm"
        ]
        
        # Backup papka yaratish
        backup_dir = Path("session_backup")
        backup_dir.mkdir(exist_ok=True)
        timestamp = int(time.time())
        
        removed_count = 0
        
        for session_file in session_files:
            session_path = Path(session_file)
            if session_path.exists():
                # Backup qilish
                backup_name = f"{session_path.name}_{timestamp}"
                backup_path = backup_dir / backup_name
                
                try:
                    shutil.copy2(session_path, backup_path)
                    print(f"📦 Backup: {session_file} -> {backup_path}")
                except Exception as e:
                    print(f"⚠️ Backup xato {session_file}: {e}")
                
                # Original faylni o'chirish
                try:
                    session_path.unlink()
                    print(f"🗑️ O'chirildi: {session_file}")
                    removed_count += 1
                except Exception as e:
                    print(f"❌ O'chirishda xato {session_file}: {e}")
                    # Force remove
                    try:
                        os.remove(session_path)
                        print(f"🔨 Force o'chirildi: {session_file}")
                        removed_count += 1
                    except Exception as e2:
                        print(f"❌ Force o'chirishda ham xato: {e2}")
        
        if removed_count > 0:
            print(f"✅ {removed_count} ta session fayl o'chirildi")
        else:
            print("ℹ️ Session fayllar topilmadi")
            
    except Exception as e:
        print(f"❌ Session fayllarni o'chirishda xato: {e}")

def main():
    print("🔧 Telegram Session Lock Fix")
    print("=" * 40)
    
    # 1. Processlarni to'xtatish
    kill_telegram_processes()
    
    # 2. Session fayllarni o'chirish
    backup_and_remove_session_files()
    
    print("\n✅ Session lock muammosi hal qilindi!")
    print("📝 Keyingi ishga tushirishda Telegram qayta login so'raydi")
    print("🔄 Endi main.py ni ishga tushiring")

if __name__ == "__main__":
    main()