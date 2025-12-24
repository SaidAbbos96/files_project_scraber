#!/usr/bin/env python3
"""
Minimal Session Test - Dependencies siz test
"""

import os
import sys


def minimal_session_check():
    """Minimal session holati tekshiruvi"""
    print("🔍 Minimal Session Tekshiruv")
    print("=" * 40)

    # 1. Session fayli topish
    session_file = None

    # Default telefon raqami bilan
    phone = "+998200089990"
    default_session = f"telegramuploader/session_{phone}.session"

    if os.path.exists(default_session):
        session_file = default_session
        print(f"✅ Session topildi: {session_file}")
    else:
        # telegramuploader papkasida qidirish
        telegram_dir = "telegramuploader"
        if os.path.exists(telegram_dir):
            for file in os.listdir(telegram_dir):
                if file.startswith("session_") and file.endswith(".session"):
                    session_file = os.path.join(telegram_dir, file)
                    print(f"🔍 Session topildi: {session_file}")
                    break

    if not session_file:
        print("❌ Session fayli topilmadi")
        return False

    # 2. Session fayli tekshiruvi
    try:
        file_size = os.path.getsize(session_file)
        print(f"📏 Session hajmi: {file_size} bytes")

        # Faylni ochishga harakat
        with open(session_file, 'rb') as f:
            # Faqat birinchi 10 byte o'qish
            header = f.read(10)
            print(f"📄 Session header: {len(header)} bytes o'qildi")

        print("✅ Session fayli normal ochiladi")
        return True

    except PermissionError:
        print("🔒 Session fayli boshqa process tomonidan ishlatilmoqda")
        return False
    except Exception as e:
        print(f"❌ Session faylida xatolik: {e}")
        return False


def check_database_status():
    """Database holatini tekshirish"""
    print("\n🔍 Database Holati")
    print("=" * 40)

    db_dir = "local_db"
    if not os.path.exists(db_dir):
        print("❌ Database papka mavjud emas")
        return False

    db_files = [f for f in os.listdir(db_dir) if f.endswith('.db')]
    if not db_files:
        print("❌ Database fayllar topilmadi")
        return False

    print(f"📊 Database fayllar: {len(db_files)} ta")

    for db_file in db_files:
        db_path = os.path.join(db_dir, db_file)
        size = os.path.getsize(db_path)
        size_mb = size / 1024 / 1024
        print(f"  • {db_file}: {size_mb:.1f} MB")

        # Database ochishga harakat (dependencies siz)
        try:
            # Faylni read-only ochish
            with open(db_path, 'rb') as f:
                header = f.read(16)  # SQLite header
                if header.startswith(b'SQLite format 3'):
                    print(f"    ✅ Valid SQLite fayl")
                else:
                    print(f"    ⚠️ Noto'g'ri SQLite format")
        except Exception as e:
            print(f"    ❌ Xatolik: {e}")

    return True


def main():
    """Asosiy test funksiyasi"""
    print("🚀 Session va Database Minimal Test")
    print("=" * 50)

    session_ok = minimal_session_check()
    db_ok = check_database_status()

    print("\n📋 NATIJA:")
    print(f"Session: {'✅ OK' if session_ok else '❌ PROBLEM'}")
    print(f"Database: {'✅ OK' if db_ok else '❌ PROBLEM'}")

    if session_ok and db_ok:
        print("\n🎉 Barcha tizimlar normal ishlayapti!")
        print("💡 Agar telegram upload da muammo bo'lsa:")
        print("   1. Internetni tekshiring")
        print("   2. Telegram API kalitlarini tekshiring")
        print("   3. Session faylini qayta yarating")
    else:
        print("\n⚠️ Ba'zi muammolar aniqlandi")
        print("💡 Session Manager avtomatik tuzatish urinishi bo'ladi")


if __name__ == "__main__":
    main()
