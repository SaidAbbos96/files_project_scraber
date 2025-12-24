#!/usr/bin/env python3
"""
Database Lock Simulator - Database lock holatini test qilish
"""

import sqlite3
import time
import os
from session_manager import SessionManager

def create_database_lock():
    """Database lock simulatsiyasi"""
    db_path = "local_db/local_files.db"  # Real database
    
    print(f"🔒 Real database lock simulatsiyasi: {db_path}")
    
    if not os.path.exists(db_path):
        print(f"❌ Database fayli mavjud emas: {db_path}")
        return
    
    try:
        # Real database ni lock qilish
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Exclusive lock bilan transaction boshlash
        cursor.execute("BEGIN EXCLUSIVE")
        print("🔒 Database bloklanıdi!")
        
        # Session Manager test qilish
        manager = SessionManager()
        print("\n" + "="*50)
        print("Session Manager test - real database lock:")
        result = manager.auto_fix_session(verbose=True)
        
        if result:
            print("✅ Session Manager muvaffaqiyatli!")
        else:
            print("❌ Session Manager da muammo!")
        
        print("\n⏳ 5 soniya kutish...")
        time.sleep(5)
        
        cursor.execute("ROLLBACK")
        conn.close()
        print("🔓 Database unlock qilindi")
        
    except Exception as e:
        print(f"❌ Database lock simulatsiyasida xatolik: {e}")

if __name__ == "__main__":
    create_database_lock()