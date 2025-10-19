#!/usr/bin/env python3
"""
Session Lock Simulator - Session lock holatini test qilish uchun
"""

import sqlite3
import time
import os
from session_manager import SessionManager

def create_locked_session():
    """Test uchun session lock simulatsiyasi"""
    manager = SessionManager()
    session_file = manager.session_file
    
    print(f"🔒 Session lock simulatsiyasi: {session_file}")
    
    # Session faylini lock qilish uchun ulanish
    try:
        conn = sqlite3.connect(session_file)
        # Uzun muddatli tranzaksiya boshlash
        conn.execute("BEGIN EXCLUSIVE")
        
        print("🔒 Session fayli lock qilindi!")
        print("⏳ 30 soniya kutish...")
        time.sleep(30)  # 30 soniya lock holatida ushlab turish
        
        conn.rollback()
        conn.close()
        print("🔓 Session fayli unlock qilindi")
        
    except Exception as e:
        print(f"❌ Lock simulatsiyasida xatolik: {e}")

if __name__ == "__main__":
    create_locked_session()