#!/bin/bash
#
# Session Killer Script - Python jarayonlarini avtomatik to'xtatish
# Muallif: Session Manager
# Maqsad: .session fayllarni ishlatayotgan Python jarayonlarini topish va to'xtatish
#

set -e  # Xato bo'lsa to'xtash

echo "🔍 Session fayllarni ishlatayotgan Python jarayonlarini qidiryapman..."

# Session ishlatayotgan python jarayonlarni topish
PIDS=$(sudo lsof 2>/dev/null | grep .session | grep python | awk '{print $2}' | sort -u || true)

if [ -z "$PIDS" ]; then
    echo "✅ Hech qanday Python jarayoni session fayllarni ishlatmayapti"
    echo "ℹ️  Session fayllar erkin holatda"
    exit 0
fi

echo "🔒 Topilgan session-locked Python PID'lar:"
echo "$PIDS" | while read pid; do
    if [ -n "$pid" ]; then
        process_info=$(ps -p "$pid" -o pid,ppid,cmd --no-headers 2>/dev/null || echo "$pid ? ?")
        echo "  • PID $pid: $process_info"
    fi
done

echo ""
echo "💀 Jarayonlarni zo'rlik bilan to'xtatyapman..."

# Har bir PID ni alohida to'xtatish
killed_count=0
for pid in $PIDS; do
    if [ -n "$pid" ] && [ "$pid" -gt 0 ] 2>/dev/null; then
        if sudo kill -9 "$pid" 2>/dev/null; then
            echo "  ✅ PID $pid to'xtatildi"
            killed_count=$((killed_count + 1))
        else
            echo "  ⚠️  PID $pid to'xtatib bo'lmadi (allaqachon to'xtagan bo'lishi mumkin)"
        fi
    fi
done

echo ""
echo "📊 Natija: $killed_count ta jarayon to'xtatildi"

# Final tekshiruv
echo "🔍 Final tekshiruv..."
sleep 1

REMAINING_PIDS=$(sudo lsof 2>/dev/null | grep .session | grep python | awk '{print $2}' | sort -u || true)

if [ -z "$REMAINING_PIDS" ]; then
    echo "✅ All session-locked processes have been killed successfully."
    echo "🚀 Session fayllar endi erkin holatda"
else
    echo "⚠️  Ba'zi jarayonlar hali ham qolgan:"
    echo "$REMAINING_PIDS"
    echo "💡 Qo'lda tekshirish talab qilinadi"
    exit 1
fi

echo ""
echo "🎉 Session lock muammosi hal qilindi!"
echo "💡 Endi dasturingizni qayta ishga tushirishingiz mumkin"