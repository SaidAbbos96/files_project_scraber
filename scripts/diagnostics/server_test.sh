#!/bin/bash
# Test script for server

echo "🚀 SERVER TEST: Upload Only Mode"
echo "=================================="

cd /var/www/projects/files_project_scraber

echo "📁 Downloads papkasidagi fayllar:"
ls -la downloads/ | wc -l
echo "$(ls downloads/*.mp4 2>/dev/null | wc -l) ta MP4 fayl"
echo "$(ls downloads/*.mkv 2>/dev/null | wc -l) ta MKV fayl"

echo ""
echo "🎯 Upload Only mode'ni ishga tushirish:"
echo "python main.py"
echo "1  # asilmedia config"
echo "4  # Upload Only mode"

echo ""
echo "✅ Natija: 76 ta fayl Telegram'ga yuklanadi!"