#!/bin/bash

echo "🚀 YANGI SERVER UCHUN FILES PROJECT SCRAPER O'RNATISH"
echo "======================================================"
echo "Bu script barcha kerakli dasturlarni o'rnatadi va loyihani ishga tushiradi"
echo ""

# Color codes for better output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_step() {
    echo -e "${BLUE}[STEP]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Error handling function
handle_error() {
    print_error "Xatolik yuz berdi: $1"
    echo "O'rnatishni to'xtatish..."
    exit 1
}

print_step "Sistema yangilanishi va asosiy paketlar o'rnatilishi..."
sudo apt update || handle_error "apt update"
sudo apt install -y python3 python3-pip python3-venv curl wget git || handle_error "asosiy paketlar o'rnatish"

print_step "Python virtual environment yaratish..."
if [ -d "venv" ]; then
    print_warning "Virtual environment allaqachon mavjud, o'chirish..."
    rm -rf venv
fi
python3 -m venv venv || handle_error "virtual environment yaratish"
source venv/bin/activate || handle_error "virtual environment faollashtirish"

print_step "Python requirements o'rnatish..."
pip install --upgrade pip || handle_error "pip yangilash"
pip install -r requirements.txt || handle_error "requirements o'rnatish"

print_step "System dependencies o'rnatish (Playwright uchun)..."
# Playwright dependencies
sudo apt install -y \
    libnss3 \
    libnspr4 \
    libatk-bridge2.0-0 \
    libdrm2 \
    libxkbcommon0 \
    libxcomposite1 \
    libxdamage1 \
    libxrandr2 \
    libgbm1 \
    libxss1 \
    libasound2 \
    libatspi2.0-0 \
    libgtk-3-0 \
    libgdk-pixbuf2.0-0 || handle_error "system dependencies o'rnatish"

print_step "Playwright browserlarni o'rnatish (bu biroz vaqt olishi mumkin)..."
playwright install chromium || handle_error "Playwright chromium o'rnatish"
playwright install firefox || handle_error "Playwright firefox o'rnatish"
playwright install webkit || handle_error "Playwright webkit o'rnatish"

print_step "Playwright system dependencies o'rnatish..."
playwright install-deps || print_warning "playwright install-deps ba'zi xatoliklar bilan yakunlandi (bu normal)"

print_step "FFmpeg va multimedia tools o'rnatish..."
sudo apt install -y \
    ffmpeg \
    ffprobe \
    libavcodec-extra \
    libavformat-dev \
    libavutil-dev \
    libswscale-dev \
    libavresample-dev || handle_error "FFmpeg o'rnatish"

print_step "Loyiha papkalarini yaratish..."
mkdir -p downloads results finish logs local_db || handle_error "papkalar yaratish"

print_step ".env fayl sozlash..."
if [ ! -f ".env" ]; then
    if [ -f ".env.example" ]; then
        cp .env.example .env
        print_success ".env fayl .env.example dan nusxalandi"
    else
        print_warning ".env.example fayl yo'q, .env yaratish..."
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
        print_success ".env fayl yaratildi"
    fi
else
    print_success ".env fayl allaqachon mavjud"
fi

print_step "Script fayllariga ruxsat berish..."
chmod +x *.sh || print_warning "ba'zi script fayllarga ruxsat berib bo'lmadi"

print_step "Playwright browser test qilish..."
python -c "
import asyncio
from playwright.async_api import async_playwright

async def test_browser():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        await page.goto('https://www.google.com')
        title = await page.title()
        print(f'Browser test muvaffaqiyatli: {title}')
        await browser.close()

asyncio.run(test_browser())
" || print_error "Playwright browser test muvaffaqiyatsiz"

print_step "FFmpeg test qilish..."
ffmpeg -version > /dev/null 2>&1 && print_success "FFmpeg muvaffaqiyatli o'rnatildi" || print_error "FFmpeg o'rnatishda muammo"
ffprobe -version > /dev/null 2>&1 && print_success "FFprobe muvaffaqiyatli o'rnatildi" || print_error "FFprobe o'rnatishda muammo"

print_step "Python importlarni test qilish..."
python -c "
try:
    import aiohttp
    import playwright
    import telethon
    import ffmpeg
    import tqdm
    print('✅ Barcha Python kutubxonalar import bo\'ldi')
except ImportError as e:
    print(f'❌ Import xatoligi: {e}')
    exit(1)
" || handle_error "Python import test"

echo ""
echo "======================================================"
print_success "O'RNATISH MUVAFFAQIYATLI YAKUNLANDI!"
echo "======================================================"
echo ""
echo "📝 KEYINGI QADAMLAR:"
echo ""
echo "1. 🔧 .env faylini to'ldiring:"
echo "   nano .env"
echo "   - TELEGRAM_API_ID va TELEGRAM_API_HASH ni kiriting"
echo "   - TELEGRAM_PHONE_NUMBER ni kiriting"
echo "   - FILES_GROUP_LINK ni kiriting"
echo ""
echo "2. 🧪 Loyihani test qiling:"
echo "   source venv/bin/activate"
echo "   python main.py"
echo ""
echo "3. 📊 Loglarni kuzating:"
echo "   tail -f logs/app.log"
echo ""
echo "🎯 MUHIM ESLATMALAR:"
echo "- Virtual environment har doim faollashtirilgan bo'lishi kerak: source venv/bin/activate"
echo "- .env faylidagi Telegram sozlamalarni to'ldirish majburiy"
echo "- Birinchi ishga tushirishda Telegram autentifikatsiyasi kerak bo'ladi"
echo "- Playwright browserlari ~200MB joy egallaydi"
echo "- FFmpeg video processing uchun zarur"
echo ""
echo "❓ Muammo bo'lsa:"
echo "- Loglarni tekshiring: cat logs/app.log"
echo "- Browser test: python -c 'from playwright.async_api import async_playwright'"
echo "- FFmpeg test: ffmpeg -version"
echo ""
print_success "Loyiha ishga tushirishga tayyor!"