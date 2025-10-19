#!/bin/bash
# Telegram session lock fix - serverda ishlatish uchun

echo "🔧 Telegram Session Lock Fix (Server - Xavfsiz)"
echo "================================================"

# Joriy papka va user ma'lumotlarini olish
CURRENT_DIR=$(pwd)
CURRENT_USER=$(whoami)
PROJECT_NAME="files_project_scraber"

echo "📁 Joriy papka: $CURRENT_DIR"
echo "👤 User: $CURRENT_USER"
echo "🎯 Faqat '$PROJECT_NAME' loyihasi processlarini tekshiradi"
echo ""

# 1. Running processlarni tekshirish (faqat bizning loyiha)
echo "1️⃣ Faqat files_project_scraber processlarni tekshirish..."

# Faqat joriy papkadagi python main.py processlarni topish
echo "🔍 Bizning loyiha processlarini qidirish:"
echo "   Path: $CURRENT_DIR"
echo "   Pattern: python.*main"

PYTHON_PROCS=$(ps aux | grep "$CURRENT_DIR" | grep "python.*main" | grep -v grep || echo "")
if [ -n "$PYTHON_PROCS" ]; then
    echo "📤 Bizning loyiha processlar topildi:"
    echo "$PYTHON_PROCS"
    echo ""
    echo "⚠️ Ushbu processlarni o'chirishni xohlaysizmi? (y/n)"
    read -r CONFIRM
    if [ "$CONFIRM" = "y" ] || [ "$CONFIRM" = "Y" ]; then
        # PID larni olish va o'chirish
        PIDS=$(echo "$PYTHON_PROCS" | awk '{print $2}')
        for PID in $PIDS; do
            echo "🔄 Process $PID ni to'xtatish..."
            kill -TERM "$PID" 2>/dev/null || kill -9 "$PID" 2>/dev/null
        done
        sleep 3
        echo "✅ Bizning Python processlar to'xtatildi"
    else
        echo "❌ Process to'xtatish bekor qilindi"
    fi
else
    echo "ℹ️ Bizning Python main.py process ishlamayapti"
fi

# Faqat bizning loyihadagi telethon processlarni tekshirish  
echo ""
echo "🔍 Telethon processlarni tekshirish..."
TELETHON_PROCS=$(ps aux | grep "$CURRENT_DIR" | grep -E "(telethon|telegram)" | grep -v grep || echo "")
if [ -n "$TELETHON_PROCS" ]; then
    echo "📤 Bizning Telethon/Telegram processlar:"
    echo "$TELETHON_PROCS"
    echo ""
    echo "⚠️ Ushbu processlarni o'chirishni xohlaysizmi? (y/n)"
    read -r CONFIRM2
    if [ "$CONFIRM2" = "y" ] || [ "$CONFIRM2" = "Y" ]; then
        PIDS=$(echo "$TELETHON_PROCS" | awk '{print $2}')
        for PID in $PIDS; do
            echo "🔄 Process $PID ni to'xtatish..."
            kill -TERM "$PID" 2>/dev/null
        done
        sleep 2
        echo "✅ Bizning Telethon processlar to'xtatildi"
    else
        echo "❌ Telethon process to'xtatish bekor qilindi"
    fi
else
    echo "ℹ️ Bizning Telethon processlar ishlamayapti"
fi

# 2. Session fayllarni tekshirish
echo ""
echo "2️⃣ Session fayllarni tekshirish..."
cd /var/www/projects/files_project_scraber 2>/dev/null || cd .

SESSION_FILES=$(find . -name "*.session*" 2>/dev/null)
if [ -n "$SESSION_FILES" ]; then
    echo "📁 Session fayllar topildi:"
    echo "$SESSION_FILES"
    
    # Backup yaratish
    BACKUP_DIR="session_backup_$(date +%Y%m%d_%H%M%S)"
    mkdir -p "$BACKUP_DIR"
    echo "📦 Backup yaratilmoqda: $BACKUP_DIR"
    
    # Session fayllarni backup va o'chirish
    find . -name "*.session*" | while read file; do
        if [ -f "$file" ]; then
            echo "📦 Backup: $file"
            cp "$file" "$BACKUP_DIR/$(basename $file)"
            
            echo "🗑️ O'chirish: $file"
            rm -f "$file" 2>/dev/null || {
                echo "🔨 Force remove: $file"
                sudo rm -f "$file" 2>/dev/null || echo "❌ O'chirib bo'lmadi: $file"
            }
        fi
    done
    
    # WAL va journal fayllarni ham o'chirish
    find . -name "*.session-wal" -o -name "*.session-shm" -o -name "*.session-journal" | while read file; do
        if [ -f "$file" ]; then
            echo "🗑️ WAL/Journal o'chirish: $file"
            rm -f "$file" 2>/dev/null
        fi
    done
    
    echo "✅ Session fayllar tozalandi"
else
    echo "ℹ️ Session fayllar topilmadi"
fi

# 3. SQLite processlarni tekshirish
echo ""
echo "3️⃣ SQLite locks tekshirish..."
SQLITE_PROCS=$(pgrep -f sqlite || echo "")
if [ -n "$SQLITE_PROCS" ]; then
    echo "⚠️ SQLite processlar ishlab turibdi"
    ps aux | grep sqlite | grep -v grep
else
    echo "✅ SQLite locks yo'q"
fi

# 4. File locks tekshirish
echo ""
echo "4️⃣ File locks tekshirish..."
if command -v lsof >/dev/null 2>&1; then
    LOCKED_FILES=$(lsof | grep -i session 2>/dev/null || echo "")
    if [ -n "$LOCKED_FILES" ]; then
        echo "⚠️ Locked session fayllar:"
        echo "$LOCKED_FILES"
    else
        echo "✅ Session fayllar lock emas"
    fi
else
    echo "ℹ️ lsof mavjud emas"
fi

echo ""
echo "✅ Session lock fix tugadi!"
echo "📝 Endi main.py ni ishga tushiring"
echo "🔑 Telegram qayta login so'raydi"