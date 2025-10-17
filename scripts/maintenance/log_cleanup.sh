#!/bin/bash
"""
Log cleanup script - Eski log fayllarni tozalash
"""

LOG_DIR="logs"
DAYS_TO_KEEP=30

echo "🧹 Log cleanup script"
echo "===================="

if [ ! -d "$LOG_DIR" ]; then
    echo "❌ $LOG_DIR papkasi topilmadi"
    exit 1
fi

echo "📁 Log papkasi: $LOG_DIR"
echo "📅 Saqlash muddati: $DAYS_TO_KEEP kun"

# System diagnostics fayllarni tozalash
echo "🔍 System diagnostics fayllarni tekshirish..."
OLD_DIAGNOSTICS=$(find "$LOG_DIR" -name "system_diagnostics_*.txt" -mtime +$DAYS_TO_KEEP)

if [ -n "$OLD_DIAGNOSTICS" ]; then
    echo "🗑️ Eski fayllar topildi:"
    echo "$OLD_DIAGNOSTICS"
    
    read -p "Bu fayllarni o'chirishni tasdiqlaysizmi? (y/N): " confirm
    if [ "$confirm" = "y" ] || [ "$confirm" = "Y" ]; then
        find "$LOG_DIR" -name "system_diagnostics_*.txt" -mtime +$DAYS_TO_KEEP -delete
        echo "✅ Eski diagnostics fayllar o'chirildi"
    else
        echo "⏭️ Tozalash bekor qilindi"
    fi
else
    echo "✅ O'chiriladigan eski fayllar yo'q"
fi

# Log papkasi statistikasi
echo ""
echo "📊 LOG PAPKASI STATISTIKASI"
echo "=========================="
echo "📁 Jami fayllar: $(find "$LOG_DIR" -type f | wc -l)"
echo "📏 Jami hajm: $(du -sh "$LOG_DIR" | cut -f1)"
echo "📅 Eng eski fayl: $(find "$LOG_DIR" -type f -printf '%T@ %p\n' | sort -n | head -1 | cut -d' ' -f2-)"
echo "📅 Eng yangi fayl: $(find "$LOG_DIR" -type f -printf '%T@ %p\n' | sort -n | tail -1 | cut -d' ' -f2-)"

echo ""
echo "🎉 Log cleanup yakunlandi!"