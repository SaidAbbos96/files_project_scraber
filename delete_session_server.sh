#!/bin/bash
# Session fayllarni butunlay o'chirish - serverda ishlatish uchun

echo "🗑️ SESSION FAYLLARNI BUTUNLAY O'CHIRISH (SERVER)"
echo "=============================================="

# Session lock borligini tekshirish
echo "🔍 Session lock tekshirilmoqda..."
SESSION_LOCKED=false

# Session fayllarni topish
SESSION_FILES=$(find . -name "*.session" 2>/dev/null)
if [ -n "$SESSION_FILES" ]; then
    for SESSION_FILE in $SESSION_FILES; do
        # SQLite database lock tekshirish
        if python3 -c "
import sqlite3
import sys
try:
    conn = sqlite3.connect('$SESSION_FILE', timeout=0.1)
    conn.execute('SELECT name FROM sqlite_master LIMIT 1')
    conn.close()
    print('OK')
except sqlite3.OperationalError as e:
    if 'database is locked' in str(e).lower():
        print('LOCKED')
        sys.exit(1)
    else:
        print('ERROR')
except:
    print('ERROR')
" 2>/dev/null; then
            echo "✅ Session fayl OK: $SESSION_FILE"
        else
            echo "🔒 Session fayl LOCKED: $SESSION_FILE"
            SESSION_LOCKED=true
            break
        fi
    done
else
    echo "ℹ️ Session fayllar topilmadi"
fi

echo ""

if [ "$SESSION_LOCKED" = false ]; then
    echo "✅ Session lock muammosi yo'q!"
    echo "💡 Bu script faqat quyidagi holatlarda kerak:"
    echo "   • 'database is locked' xatosi ko'rinanda"
    echo "   • Upload Only rejimi ishlamay qolganda"
    echo "   • Telegram connection xatolari bo'lganda"
    echo ""
    read -p "❓ Baribir session fayllarni o'chirishni xohlaysizmi? (yes/no): " FORCE_CONFIRM
    if [ "$FORCE_CONFIRM" != "yes" ] && [ "$FORCE_CONFIRM" != "y" ]; then
        echo "❌ Bekor qilindi - session fayllar saqlanib qoldi"
        echo "🔄 Oddiy holatda main.py ni ishga tushiring"
        exit 0
    fi
    echo "⚠️ Majburiy o'chirish rejimi..."
else
    echo "🔒 SESSION LOCK MUAMMOSI ANIQLANDI!"
    echo "   Bu script aynan shu muammo uchun kerak"
fi

echo ""
echo "⚠️ OGOHLANTIRISH:"
echo "   • Telegram login ma'lumotlari yo'qoladi"
echo "   • Phone number va code qayta kiritish kerak"
echo "   • Database lock 100% hal bo'ladi"
echo ""

# Confirm
read -p "❓ Davom etishni xohlaysizmi? (yes/no): " CONFIRM
if [ "$CONFIRM" != "yes" ] && [ "$CONFIRM" != "y" ]; then
    echo "❌ Bekor qilindi"
    exit 0
fi

echo ""
echo "🚀 Jarayon boshlanmoqda..."

# Joriy papka
CURRENT_DIR="/var/www/projects/files_project_scraber"
cd "$CURRENT_DIR" 2>/dev/null || cd .

# 1. Main processlarni to'xtatish
echo "1️⃣ files_project_scraber processlarni to'xtatish..."
MAIN_PROCS=$(ps aux | grep files_project_scraber | grep "python.*main" | grep -v grep)
if [ -n "$MAIN_PROCS" ]; then
    echo "📤 Main processlar topildi:"
    echo "$MAIN_PROCS"
    
    PIDS=$(echo "$MAIN_PROCS" | awk '{print $2}')
    echo ""
    echo "🔄 Processlarni to'xtatish:"
    
    for PID in $PIDS; do
        echo "📤 SIGTERM: PID $PID"
        kill -TERM "$PID" 2>/dev/null
    done
    
    echo "⏳ 5 soniya kutish..."
    sleep 5
    
    for PID in $PIDS; do
        if kill -0 "$PID" 2>/dev/null; then
            echo "🔨 SIGKILL: PID $PID"
            kill -KILL "$PID" 2>/dev/null
        fi
    done
    
    echo "✅ Processlar to'xtatildi"
else
    echo "ℹ️ Main processlar topilmadi"
fi

echo ""

# 2. Session fayllarni o'chirish
echo "2️⃣ Barcha session fayllarni qidirish va o'chirish..."

# Backup papka yaratish
BACKUP_DIR="deleted_sessions_backup_$(date +%Y%m%d_%H%M%S)"
mkdir -p "$BACKUP_DIR"
echo "📦 Backup papka: $BACKUP_DIR"

DELETED_COUNT=0

# Session fayllarni topish va o'chirish
find . -name "*.session" -o -name "*.session-wal" -o -name "*.session-shm" -o -name "*.session-journal" | while read SESSION_FILE; do
    if [ -f "$SESSION_FILE" ]; then
        echo "📁 Topildi: $SESSION_FILE"
        
        # Backup yaratish
        BACKUP_NAME="$(basename $SESSION_FILE)_$(date +%s)"
        cp "$SESSION_FILE" "$BACKUP_DIR/$BACKUP_NAME" 2>/dev/null
        echo "📦 Backup: $BACKUP_DIR/$BACKUP_NAME"
        
        # O'chirish
        if rm -f "$SESSION_FILE" 2>/dev/null; then
            echo "🗑️ O'chirildi: $SESSION_FILE"
            DELETED_COUNT=$((DELETED_COUNT + 1))
        else
            echo "❌ O'chirib bo'lmadi: $SESSION_FILE"
            # Force remove with sudo
            sudo rm -f "$SESSION_FILE" 2>/dev/null && {
                echo "🔨 Sudo o'chirildi: $SESSION_FILE"
                DELETED_COUNT=$((DELETED_COUNT + 1))
            }
        fi
    fi
done

# Natija
echo ""
echo "=============================================="
if [ $DELETED_COUNT -gt 0 ]; then
    echo "✅ SESSION LOCK MUAMMOSI HAL QILINDI!"
    echo "📊 $DELETED_COUNT ta session fayl o'chirildi"
    echo "📦 Backup: $BACKUP_DIR/"
    echo ""
    echo "📝 Keyingi qadamlar:"
    echo "   1. python -m main"
    echo "   2. Upload Only rejimini tanlang"
    echo "   3. Telegram login:"
    echo "      • Phone number: +998XXXXXXXXX"
    echo "      • SMS code: XXXXX"
    echo "   4. Upload boshlanadi"
    echo ""
    echo "🎯 Database lock endi 100% yo'q!"
else
    echo "ℹ️ Session fayllar topilmadi"
    echo "💡 Manual tekshirish: ls -la **/*.session*"
fi