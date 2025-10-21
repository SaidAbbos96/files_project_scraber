#!/bin/bash

echo "🚀 Yangi server uchun Files Project Scraper o'rnatish"
echo "===================================================="

# 1. Python virtual environment yaratish va faollashtirish
echo "📦 Virtual environment yaratish..."
python3 -m venv venv
source venv/bin/activate

# 2. Requirements o'rnatish
echo "📋 Requirements o'rnatish..."
pip install -r requirements.txt

# 3. Playwright browserlarni o'rnatish (MUHIM!)
echo "🌐 Playwright browserlarni o'rnatish..."
playwright install

# 4. System dependencies o'rnatish (agar kerak bo'lsa)
echo "🛠️ System dependencies tekshirish..."
playwright install-deps

# 5. FFmpeg o'rnatish (video processing uchun)
echo "🎬 FFmpeg o'rnatish..."
sudo apt update
sudo apt install -y ffmpeg

# 6. Kerakli papkalar yaratish
echo "📁 Kerakli papkalar yaratish..."
mkdir -p downloads
mkdir -p results
mkdir -p finish
mkdir -p logs
mkdir -p local_db

# 7. .env faylni nusxalash (agar mavjud bo'lmasa)
if [ ! -f ".env" ]; then
    echo "⚙️ .env fayl yaratish..."
    if [ -f ".env.example" ]; then
        cp .env.example .env
        echo "✅ .env fayl .env.example dan nusxalandi"
        echo "⚠️ .env faylini sozlashni unutmang!"
    else
        echo "❌ .env.example fayl topilmadi"
    fi
fi

# 8. Ruxsatlar berish
chmod +x *.sh

echo ""
echo "✅ O'rnatish yakunlandi!"
echo ""
echo "📝 Keyingi qadamlar:"
echo "1. .env faylini sozlang (Telegram API, database, va boshqa sozlamalar)"
echo "2. python main.py - dasturni ishga tushiring"
echo ""
echo "🧪 Test uchun:"
echo "python main.py"
echo ""