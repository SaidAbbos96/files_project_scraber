#!/usr/bin/env python3
"""
Real Session Test - Telegram upload simulatsiyasi
"""

import sys
import os
sys.path.append('/home/aicoder/coding/files_project/files_project_scraber')

from session_manager import SessionManager

def test_real_telegram_scenario():
    """Real Telegram upload scenario test"""
    print("🔍 Real Telegram Upload Scenario Test")
    print("=" * 50)
    
    # 1. Session Manager yaratish
    manager = SessionManager()
    print(f"📁 Session fayli: {manager.session_file}")
    
    # 2. Kengaytirilgan diagnostika
    print("\n🔍 Kengaytirilgan diagnostika:")
    result = manager.auto_fix_session(verbose=True)
    
    # 3. Manual checks
    print("\n🔍 Manual tekshiruvlar:")
    
    # Session fayli mavjudligini tekshirish
    if os.path.exists(manager.session_file):
        file_size = os.path.getsize(manager.session_file)
        print(f"✅ Session fayli mavjud: {file_size} bytes")
    else:
        print("❌ Session fayli mavjud emas")
    
    # Database fayllarini tekshirish
    db_dir = "local_db"
    if os.path.exists(db_dir):
        db_files = [f for f in os.listdir(db_dir) if f.endswith('.db')]
        print(f"📊 Database fayllar: {len(db_files)} ta")
        for db_file in db_files:
            db_path = os.path.join(db_dir, db_file)
            size = os.path.getsize(db_path)
            print(f"  • {db_file}: {size} bytes")
    
    # Process check
    try:
        import subprocess
        result = subprocess.run(['ps', 'aux'], capture_output=True, text=True)
        python_processes = [line for line in result.stdout.split('\n') if 'python' in line.lower()]
        print(f"🔍 Python processlar: {len(python_processes)} ta")
    except Exception as e:
        print(f"⚠️ Process tekshirishda xatolik: {e}")
    
    # Network connections
    try:
        result = subprocess.run(['netstat', '-tuln'], capture_output=True, text=True)
        if result.returncode == 0:
            telegram_connections = [line for line in result.stdout.split('\n') if '443' in line]
            print(f"🌐 Telegram-related connections: {len(telegram_connections)} ta")
    except Exception:
        print("⚠️ Network tekshirib bo'lmadi")
    
    return result

if __name__ == "__main__":
    test_real_telegram_scenario()