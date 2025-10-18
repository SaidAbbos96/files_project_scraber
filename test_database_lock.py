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
    db_path = "local_db/local_files.db"
    
    # Database papkasini yaratish
    os.makedirs("local_db", exist_ok=True)
    
    print(f"🔒 Database lock simulatsiyasi: {db_path}")
    
    try:
        # Database yaratish
        conn = sqlite3.connect(db_path)
        conn.execute("CREATE TABLE IF NOT EXISTS test (id INTEGER)")
        conn.execute("INSERT INTO test (id) VALUES (1)")
        
        # Uzun muddatli transaction
        conn.execute("BEGIN EXCLUSIVE")
        print("🔒 Database bloklanıdi!")
        
        # Session Manager test qilish
        manager = SessionManager()
        print("\n" + "="*50)
        print("Session Manager test - database lock holatida:")
        result = manager.auto_fix_session(verbose=True)
        
        if result:
            print("✅ Session Manager muvaffaqiyatli!")
        else:
            print("❌ Session Manager da muammo!")
        
        print("\n⏳ 10 soniya kutish...")
        time.sleep(10)
        
        conn.rollback()
        conn.close()
        print("🔓 Database unlock qilindi")
        
    except Exception as e:
        print(f"❌ Database lock simulatsiyasida xatolik: {e}")

if __name__ == "__main__":
    create_database_lock()