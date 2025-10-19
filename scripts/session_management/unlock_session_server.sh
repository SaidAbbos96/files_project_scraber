#!/bin/bash
# Session unlock - session faylni o'chirmasdan lock ni ochish

echo "🔓 Telegram Session Unlock (Session saqlanadi)"
echo "=============================================="

# Joriy papka
CURRENT_DIR="/var/www/projects/files_project_scraber"
cd "$CURRENT_DIR" 2>/dev/null || cd .

echo "📁 Joriy papka: $(pwd)"
echo ""

# 1. Main processlarni topish va to'xtatish
echo "1️⃣ files_project_scraber main processlarni to'xtatish..."

MAIN_PROCS=$(ps aux | grep files_project_scraber | grep "python.*main" | grep -v grep)
if [ -n "$MAIN_PROCS" ]; then
    echo "📤 Main processlar topildi:"
    echo "$MAIN_PROCS"
    
    # PID larni olish
    PIDS=$(echo "$MAIN_PROCS" | awk '{print $2}')
    echo ""
    echo "🔄 Processlarni to'xtatish:"
    
    for PID in $PIDS; do
        echo "📤 SIGTERM yuborish: PID $PID"
        kill -TERM "$PID" 2>/dev/null
    done
    
    echo "⏳ 5 soniya kutish..."
    sleep 5
    
    # Hali ishlab turganlarni force kill
    for PID in $PIDS; do
        if kill -0 "$PID" 2>/dev/null; then
            echo "🔨 SIGKILL yuborish: PID $PID"
            kill -KILL "$PID" 2>/dev/null
        fi
    done
    
    echo "✅ Main processlar to'xtatildi"
else
    echo "ℹ️ Main processlar topilmadi"
fi

echo ""

# 2. Session fayllarni topish
echo "2️⃣ Session fayllarni topish..."
SESSION_FILES=$(find . -name "*.session" 2>/dev/null)

if [ -z "$SESSION_FILES" ]; then
    echo "❌ Session fayllar topilmadi"
    exit 1
fi

echo "📁 Session fayllar topildi:"
echo "$SESSION_FILES"
echo ""

# 3. Har bir session faylni unlock qilish
echo "3️⃣ Session fayllarni unlock qilish..."

for SESSION_FILE in $SESSION_FILES; do
    echo "📂 Ishlov berish: $SESSION_FILE"
    
    # WAL, SHM, Journal fayllarni vaqtincha ko'chirish
    WAL_FILE="${SESSION_FILE}-wal"
    SHM_FILE="${SESSION_FILE}-shm"
    JOURNAL_FILE="${SESSION_FILE}-journal"
    
    # Backup yaratish
    if [ -f "$WAL_FILE" ]; then
        mv "$WAL_FILE" "${WAL_FILE}.backup" 2>/dev/null
        echo "📦 WAL backup: ${WAL_FILE}.backup"
    fi
    
    if [ -f "$SHM_FILE" ]; then
        mv "$SHM_FILE" "${SHM_FILE}.backup" 2>/dev/null
        echo "📦 SHM backup: ${SHM_FILE}.backup"
    fi
    
    if [ -f "$JOURNAL_FILE" ]; then
        mv "$JOURNAL_FILE" "${JOURNAL_FILE}.backup" 2>/dev/null
        echo "📦 Journal backup: ${JOURNAL_FILE}.backup"
    fi
    
    # 1 soniya kutish
    sleep 1
    
    # Python orqali SQLite unlock
    python3 -c "
import sqlite3
import sys
try:
    conn = sqlite3.connect('$SESSION_FILE', timeout=2.0)
    conn.execute('PRAGMA wal_checkpoint(TRUNCATE)')
    conn.execute('PRAGMA optimize')
    conn.close()
    print('✅ SQLite unlock muvaffaqiyatli: $SESSION_FILE')
    sys.exit(0)
except Exception as e:
    print('❌ SQLite unlock xato: $SESSION_FILE - ' + str(e))
    sys.exit(1)
"
    
    # Backup fayllarni qayta tiklash
    sleep 1
    
    if [ -f "${WAL_FILE}.backup" ]; then
        mv "${WAL_FILE}.backup" "$WAL_FILE" 2>/dev/null
        echo "🔄 WAL restored: $WAL_FILE"
    fi
    
    if [ -f "${SHM_FILE}.backup" ]; then
        mv "${SHM_FILE}.backup" "$SHM_FILE" 2>/dev/null
        echo "🔄 SHM restored: $SHM_FILE"
    fi
    
    if [ -f "${JOURNAL_FILE}.backup" ]; then
        mv "${JOURNAL_FILE}.backup" "$JOURNAL_FILE" 2>/dev/null
        echo "🔄 Journal restored: $JOURNAL_FILE"
    fi
    
    echo ""
done

echo "✅ Session unlock jarayoni tugadi!"
echo "📝 Session fayllar saqlanib qoldi"
echo "🔄 Endi main.py ni ishga tushiring"