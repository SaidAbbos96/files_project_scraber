#!/bin/bash
#
# Session Killer Script (No Sudo) - Python jarayonlarini foydalanuvchi huquqida to'xtatish
# Muallif: Session Manager
# Maqsad: .session fayllarni ishlatayotgan Python jarayonlarini topish va to'xtatish
#

set -e

echo "🔍 Session fayllarni ishlatayotgan Python jarayonlarini qidiryapman..."

# Foydalanuvchi jarayonlarini tekshirish
echo "📋 Joriy Python jarayonlar:"
ps aux | grep python | grep -v grep | while read line; do
    echo "  • $line"
done

echo ""
echo "🔍 Session fayllarni kim ishlatyapti:"

# Session fayllarni topish
SESSION_FILES=$(find . -name "*.session" -type f 2>/dev/null || true)

if [ -z "$SESSION_FILES" ]; then
    echo "❌ Hech qanday .session fayli topilmadi"
    exit 1
fi

echo "📁 Topilgan session fayllar:"
echo "$SESSION_FILES"

echo ""
echo "🔍 Bu fayllarni ishlatayotgan jarayonlarni tekshirish..."

# lsof o'rniga fuser ishlatish (sudo talab qilmaydi)
PIDS=""
for session_file in $SESSION_FILES; do
    if [ -f "$session_file" ]; then
        echo "🔍 Tekshirish: $session_file"
        
        # fuser bilan tekshirish
        file_pids=$(fuser "$session_file" 2>/dev/null || true)
        
        if [ -n "$file_pids" ]; then
            echo "  🔒 Fayl ishlatilmoqda, PID'lar: $file_pids"
            PIDS="$PIDS $file_pids"
        else
            echo "  ✅ Fayl erkin"
        fi
    fi
done

# PID'larni tozalash
PIDS=$(echo "$PIDS" | tr ' ' '\n' | grep -E '^[0-9]+$' | sort -u | tr '\n' ' ')

if [ -z "$PIDS" ]; then
    echo "✅ Hech qanday jarayon session fayllarni ishlatmayapti"
    echo "🚀 Session fayllar erkin holatda"
    exit 0
fi

echo ""
echo "🔒 Session fayllarni ishlatayotgan PID'lar: $PIDS"

# PID'larning Python jarayonlari ekanligini tekshirish
PYTHON_PIDS=""
for pid in $PIDS; do
    if [ -n "$pid" ]; then
        process_cmd=$(ps -p "$pid" -o cmd --no-headers 2>/dev/null || echo "")
        if echo "$process_cmd" | grep -q python; then
            echo "  🐍 PID $pid: Python jarayoni - $process_cmd"
            PYTHON_PIDS="$PYTHON_PIDS $pid"
        else
            echo "  ℹ️  PID $pid: Python emas - $process_cmd"
        fi
    fi
done

if [ -z "$PYTHON_PIDS" ]; then
    echo "✅ Python jarayonlari session fayllarni ishlatmayapti"
    exit 0
fi

echo ""
echo "💀 Python jarayonlarini to'xtatyapman..."

killed_count=0
for pid in $PYTHON_PIDS; do
    if [ -n "$pid" ] && [ "$pid" -gt 0 ] 2>/dev/null; then
        echo "  🎯 PID $pid ni to'xtatish..."
        if kill -9 "$pid" 2>/dev/null; then
            echo "    ✅ PID $pid to'xtatildi"
            killed_count=$((killed_count + 1))
        else
            echo "    ⚠️  PID $pid to'xtatib bo'lmadi"
        fi
    fi
done

echo ""
echo "📊 Natija: $killed_count ta Python jarayoni to'xtatildi"

# Final tekshiruv
sleep 1
echo "🔍 Final tekshiruv..."

still_running=0
for session_file in $SESSION_FILES; do
    if [ -f "$session_file" ]; then
        remaining_pids=$(fuser "$session_file" 2>/dev/null || true)
        if [ -n "$remaining_pids" ]; then
            echo "  ⚠️  $session_file hali ham ishlatilmoqda: $remaining_pids"
            still_running=1
        fi
    fi
done

if [ $still_running -eq 0 ]; then
    echo "✅ All session-locked processes have been killed successfully."
    echo "🚀 Barcha session fayllar endi erkin holatda"
else
    echo "⚠️  Ba'zi session fayllar hali ham band"
    echo "💡 Sudo bilan qayta urinib ko'ring: sudo ./kill_session_processes.sh"
fi

echo ""
echo "🎉 Session killer script yakunlandi!"