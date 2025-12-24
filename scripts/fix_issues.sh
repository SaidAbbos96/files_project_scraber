#!/bin/bash

echo "🔧 FILES PROJECT SCRAPER - MUAMMOLARNI HAL QILISH"
echo "================================================="

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

print_step() {
    echo -e "${BLUE}[FIX]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

echo "Qaysi muammoni hal qilmoqchisiz?"
echo ""
echo "1. 🌐 Playwright browser muammosi"
echo "2. 🎬 FFmpeg/FFprobe muammosi"  
echo "3. 🐍 Python virtual environment muammosi"
echo "4. 📁 Permissions muammosi"
echo "5. ⚙️ .env konfiguratsiya muammosi"
echo "6. 🧪 Barcha testlarni qayta o'tkazish"
echo "7. 🗑️ To'liq tozalash va qayta o'rnatish"
echo ""
read -p "Tanlang (1-7): " choice

case $choice in
    1)
        print_step "Playwright browserlarni qayta o'rnatish..."
        source venv/bin/activate 2>/dev/null || { echo "Virtual env faollashtirish mumkin emas"; exit 1; }
        
        print_step "Eski browserlarni o'chirish..."
        rm -rf ~/.cache/ms-playwright/
        
        print_step "Yangi browserlarni o'rnatish..."
        playwright install chromium
        playwright install firefox
        playwright install webkit
        playwright install-deps
        
        print_step "Browser test..."
        python -c "
import asyncio
from playwright.async_api import async_playwright

async def test():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        await page.goto('https://google.com')
        print('✅ Browser test muvaffaqiyatli')
        await browser.close()

asyncio.run(test())
" && print_success "Playwright muammosi hal qilindi!" || print_error "Playwright hali ham ishlamayapti"
        ;;
        
    2)
        print_step "FFmpeg va FFprobe o'rnatish..."
        sudo apt update
        sudo apt install -y ffmpeg ffprobe libavcodec-extra libavformat-dev libavutil-dev
        
        print_step "Test qilish..."
        ffmpeg -version > /dev/null 2>&1 && print_success "FFmpeg ishlaydi" || print_error "FFmpeg ishlamayapti"
        ffprobe -version > /dev/null 2>&1 && print_success "FFprobe ishlaydi" || print_error "FFprobe ishlamayapti"
        
        print_step "Python ffmpeg module test..."
        source venv/bin/activate 2>/dev/null || { echo "Virtual env yo'q"; exit 1; }
        python -c "import ffmpeg; print('✅ Python ffmpeg module ishlaydi')" || print_error "Python ffmpeg module muammosi"
        ;;
        
    3)
        print_step "Virtual environment qayta yaratish..."
        rm -rf venv
        python3 -m venv venv
        source venv/bin/activate
        pip install --upgrade pip
        pip install -r requirements.txt
        print_success "Virtual environment qayta yaratildi"
        ;;
        
    4)
        print_step "Ruxsatlarni to'g'irlash..."
        chmod +x *.sh
        chmod 755 .
        chmod -R 755 downloads/ results/ finish/ logs/ local_db/ 2>/dev/null || mkdir -p downloads results finish logs local_db
        print_success "Ruxsatlar to'g'irlandi"
        ;;
        
    5)
        print_step ".env fayl sozlash..."
        if [ ! -f ".env" ]; then
            if [ -f ".env.example" ]; then
                cp .env.example .env
                print_success ".env fayl yaratildi"
            else
                print_step "Yangi .env fayl yaratish..."
                cat > .env << 'EOF'
# Database
DB_LOCAL_NAME=local_files

# Telegram API (O'z qiymatlaringizni kiriting!)
TELEGRAM_API_ID=your_api_id
TELEGRAM_API_HASH=your_api_hash
TELEGRAM_PHONE_NUMBER=+998901234567
FILES_GROUP_LINK=https://t.me/your_group

# Worker name
WORKER_NAME=worker_001

# Download settings
DOWNLOAD_CONCURRENCY=2
SCRAPE_CONCURRENCY=5
UPLOAD_CONCURRENCY=2

# Playwright settings
HEADLESS=1

# Disk monitoring
MIN_FREE_SPACE_GB=1.0

# Logging
LOGGING_ENABLED=True
DEBUG=false
EOF
                print_success ".env fayl yaratildi - tahrirlash kerak!"
            fi
        else
            print_success ".env fayl allaqachon mavjud"
        fi
        
        echo ""
        echo "📝 .env faylidagi majburiy maydonlar:"
        echo "- TELEGRAM_API_ID"
        echo "- TELEGRAM_API_HASH" 
        echo "- TELEGRAM_PHONE_NUMBER"
        echo "- FILES_GROUP_LINK"
        echo ""
        read -p ".env faylini hozir tahrirlamoqchimisiz? (y/n): " edit_env
        if [ "$edit_env" = "y" ]; then
            nano .env
        fi
        ;;
        
    6)
        print_step "Barcha testlarni o'tkazish..."
        
        print_step "1. Virtual environment test..."
        source venv/bin/activate && print_success "Virtual env OK" || print_error "Virtual env muammosi"
        
        print_step "2. Python modules test..."
        python -c "
try:
    import aiohttp, playwright, telethon, ffmpeg, tqdm
    print('✅ Python modules OK')
except ImportError as e:
    print(f'❌ Import muammosi: {e}')
"
        
        print_step "3. Playwright test..."
        python -c "
import asyncio
from playwright.async_api import async_playwright

async def test():
    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()
            await page.goto('https://google.com')
            await browser.close()
            print('✅ Playwright OK')
    except Exception as e:
        print(f'❌ Playwright muammosi: {e}')

asyncio.run(test())
"
        
        print_step "4. FFmpeg test..."
        ffmpeg -version > /dev/null 2>&1 && print_success "FFmpeg OK" || print_error "FFmpeg muammosi"
        ffprobe -version > /dev/null 2>&1 && print_success "FFprobe OK" || print_error "FFprobe muammosi"
        
        print_step "5. .env test..."
        [ -f ".env" ] && print_success ".env mavjud" || print_error ".env yo'q"
        
        print_step "6. Papkalar test..."
        for dir in downloads results finish logs local_db; do
            [ -d "$dir" ] && print_success "$dir papka mavjud" || { mkdir -p "$dir"; print_success "$dir papka yaratildi"; }
        done
        ;;
        
    7)
        print_step "To'liq tozalash va qayta o'rnatish..."
        read -p "Haqiqatan ham to'liq tozalab qayta o'rnatmoqchimisiz? (yes/no): " confirm
        if [ "$confirm" = "yes" ]; then
            print_step "Virtual environment o'chirish..."
            rm -rf venv
            
            print_step "Cache lar o'chirish..."
            rm -rf ~/.cache/ms-playwright/
            rm -rf __pycache__/
            find . -name "*.pyc" -delete
            
            print_step "Log fayllar o'chirish..."
            rm -rf logs/*
            
            print_step "Qayta o'rnatishni boshlash..."
            ./setup_new_server.sh
        else
            echo "Bekor qilindi"
        fi
        ;;
        
    *)
        print_error "Noto'g'ri tanlov: $choice"
        exit 1
        ;;
esac

echo ""
echo "✅ Muammo hal qilish yakunlandi!"
echo ""
echo "🧪 Loyihani ishga tushirish uchun:"
echo "source venv/bin/activate"
echo "python main.py"