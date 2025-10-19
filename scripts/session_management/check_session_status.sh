#!/bin/bash
# Session lock checker - qachon session o'chirish kerak ekanligini aniqlaydi

echo "🔍 SESSION LOCK DIAGNOSTIC"
echo "========================="

# 1. Running processlarni tekshirish
echo "1️⃣ Running processlar:"
MAIN_PROCS=$(ps aux | grep "python.*main" | grep -v grep)
if [ -n "$MAIN_PROCS" ]; then
    echo "📤 Python main processlar ishlab turibdi:"
    echo "$MAIN_PROCS"
    echo "⚠️ Multiple processlar session conflict yaratishi mumkin"
else
    echo "✅ Python main processlar ishlamayapti"
fi

echo ""

# 2. Session fayllarni tekshirish
echo "2️⃣ Session fayllar holati:"
SESSION_FILES=$(find . -name "*.session" 2>/dev/null)
if [ -n "$SESSION_FILES" ]; then
    LOCKED_COUNT=0
    TOTAL_COUNT=0
    
    for SESSION_FILE in $SESSION_FILES; do
        TOTAL_COUNT=$((TOTAL_COUNT + 1))
        echo "📁 Tekshirilmoqda: $SESSION_FILE"
        
        # SQLite lock tekshirish
        LOCK_CHECK=$(python3 -c "
import sqlite3
try:
    conn = sqlite3.connect('$SESSION_FILE', timeout=0.1)
    conn.execute('SELECT name FROM sqlite_master LIMIT 1')
    conn.close()
    print('OK')
except sqlite3.OperationalError as e:
    if 'database is locked' in str(e).lower():
        print('LOCKED')
    else:
        print('ERROR')
except:
    print('ERROR')
" 2>/dev/null)

        if [ "$LOCK_CHECK" = "OK" ]; then
            echo "   ✅ Normal"
        elif [ "$LOCK_CHECK" = "LOCKED" ]; then
            echo "   🔒 LOCKED"
            LOCKED_COUNT=$((LOCKED_COUNT + 1))
        else
            echo "   ⚠️ Xato yoki access muammosi"
        fi
    done
    
    echo ""
    echo "📊 Natija: $LOCKED_COUNT/$TOTAL_COUNT session fayl locked"
    
    if [ $LOCKED_COUNT -gt 0 ]; then
        echo ""
        echo "🚨 SESSION LOCK MUAMMOSI BOR!"
        echo "💡 Hal qilish yo'llari:"
        echo "   [1] unlock_session.py - session ni unlock qilish (login saqlanadi)"
        echo "   [2] delete_session_files.py - session ni o'chirish (login yo'qoladi)"
        echo ""
        echo "🔧 Tavsiya qilingan buyruqlar:"
        echo "   python3 unlock_session.py      # Avval buni sinang"
        echo "   python3 delete_session_files.py # Agar unlock ishlamasa"
    else
        echo ""
        echo "✅ Session fayllar normal holatda"
        echo "💡 Session o'chirish kerak emas"
        echo "🔄 Oddiy holatda main.py ni ishga tushiring"
    fi
    
else
    echo "ℹ️ Session fayllar topilmadi"
    echo "🔄 Birinchi marta ishga tushirganda login so'raydi"
fi

echo ""

# 3. Xatolik belgilari tekshirish
echo "3️⃣ Keng uchraydigan xatolik belgilari:"
echo "   🔒 'database is locked' - session lock muammosi"
echo "   🔌 'Connection failed' - network yoki auth muammosi"  
echo "   📤 'Upload timeout' - fayl yuklash muammosi"
echo "   🔄 'Multiple connections' - bir nechta process muammosi"

echo ""
echo "📋 XULOSA:"
if [ -n "$SESSION_FILES" ] && [ $LOCKED_COUNT -gt 0 ]; then
    echo "🚨 SESSION O'CHIRISH KERAK - database locked!"
    echo "   Buyruq: ./delete_session_server.sh"
elif [ -n "$MAIN_PROCS" ]; then
    echo "⚠️ PROCESSLARNI TO'XTATISH KERAK - multiple instance"
    echo "   Buyruq: pkill -f 'python.*main'"
else
    echo "✅ HAMMASI NORMAL - oddiy ishga tushiring"
    echo "   Buyruq: python -m main"
fi