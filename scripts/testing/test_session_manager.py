#!/usr/bin/env python3
"""
Session Manager Test - dependencies siz test
"""

from session_manager import SessionManager

def main():
    print("🔍 Session Manager - Real Test")
    print("=" * 50)
    
    # Session manager yaratish
    manager = SessionManager()
    print(f"📁 Session fayli: {manager.session_file}")
    
    # Avtomatik tekshiruv
    result = manager.auto_fix_session(verbose=True)
    
    if result:
        print("✅ Session Manager muvaffaqiyatli ishladi!")
    else:
        print("❌ Session Manager da muammo!")
    
    # Backup larni ko'rsatish
    backups = manager.list_backups()
    if backups:
        print(f"\n📋 Mavjud backup lar: {len(backups)} ta")
        for backup in backups[:3]:  # Faqat 3 ta ko'rsatish
            size_mb = backup['size'] / 1024 / 1024
            time_str = backup['time'].strftime("%Y-%m-%d %H:%M:%S")
            print(f"  • {backup['name']} ({size_mb:.1f}MB) - {time_str}")

if __name__ == "__main__":
    main()