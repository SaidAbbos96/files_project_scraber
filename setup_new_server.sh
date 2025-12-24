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

print_step "System dependencies o'rnatish (Playwright uchun - ixtiyoriy)..."
# Playwright dependencies - ba'zilari server muhitida bo'lmasligi mumkin
print_warning "Ba'zi paketlar server muhitida mavjud bo'lmasligi mumkin, lekin bu normal."

# Core dependencies (asosiy)
sudo apt install -y \
    libnss3 \
    libnspr4 \
    libdrm2 \
    libxkbcommon0 \
    libxcomposite1 \
    libxdamage1 \
    libxrandr2 \
    libgbm1 \
    libxss1 || print_warning "Ba'zi core dependencies o'rnatilmadi"

# Optional dependencies (server muhitida bo'lmasligi mumkin)
print_step "Ixtiyoriy dependencies o'rnatish..."
sudo apt install -y \
    libatk-bridge2.0-0 \
    libatspi2.0-0 \
    libgtk-3-0 \
    libgdk-pixbuf2.0-0 2>/dev/null || print_warning "GUI dependencies o'rnatilmadi (server muhitida normal)"

# Audio dependencies (server muhitida shart emas)
sudo apt install -y libasound2 2>/dev/null || \
sudo apt install -y libasound2t64 2>/dev/null || \
print_warning "Audio dependencies o'rnatilmadi (server muhitida shart emas)"

print_step "Playwright browserlarni o'rnatish (faqat Chromium)..."
playwright install chromium || handle_error "Playwright chromium o'rnatish"
# Faqat Chromium ishlatamiz, qolganlar shart emas
# playwright install firefox || handle_error "Playwright firefox o'rnatish"
# playwright install webkit || handle_error "Playwright webkit o'rnatish"

print_step "Playwright system dependencies o'rnatish..."
playwright install-deps || print_warning "playwright install-deps ba'zi xatoliklar bilan yakunlandi (bu normal)"

print_step "FFmpeg va multimedia tools o'rnatish (ixtiyoriy)..."
# FFmpeg server muhitida bo'lmasligi yoki o'rnatilmasligi mumkin
if sudo apt install -y ffmpeg ffprobe 2>/dev/null; then
    print_success "FFmpeg muvaffaqiyatli o'rnatildi"
else
    print_warning "FFmpeg o'rnatilmadi - video processing ishlamaydi"
    print_warning "Agar video kerak bo'lsa: sudo apt update && sudo apt install ffmpeg"
fi

# Additional multimedia packages (optional)
sudo apt install -y \
    libavcodec-extra \
    libavformat-dev \
    libavutil-dev \
    libswscale-dev \
    libavresample-dev 2>/dev/null || print_warning "Qo'shimcha multimedia kutubxonalar o'rnatilmadi"

print_step "Loyiha papkalarini yaratish..."
mkdir -p downloads results finish logs || handle_error "papkalar yaratish"

print_step ".env fayl sozlash..."
if [ ! -f ".env" ]; then
    if [ -f ".env.example" ]; then
        cp .env.example .env
        print_success ".env fayl .env.example dan nusxalandi"
    else
        print_warning ".env.example fayl yo'q, .env yaratish..."
        cat > .env << 'EOF'
# ========================================
# DATABASE CONFIGURATION
# ========================================
# PostgreSQL Database (Remote Server)
DB_HOST=your_db_host
DB_PORT=5432
DB_NAME=files_scraber_db
DB_USER=postgres
DB_PASSWORD="your_password"

# Local Database (Legacy - for backup)
DB_LOCAL_NAME=local_files

# ========================================
# TELEGRAM API CONFIGURATION
# ========================================
TELEGRAM_API_ID=your_api_id
TELEGRAM_API_HASH=your_api_hash
TELEGRAM_PHONE_NUMBER=+998901234567
FILES_GROUP_ID=-1002699309226
FILES_GROUP_LINK=https://t.me/your_group
TELEGRAM_USER_IS_PREMIUM=true

# ========================================
# WORKER CONFIGURATION
# ========================================
WORKER_NAME=worker_001

# ========================================
# CONCURRENCY SETTINGS
# ========================================
DOWNLOAD_CONCURRENCY=2
SCRAPE_CONCURRENCY=5
UPLOAD_CONCURRENCY=2
UPLOAD_WORKERS=2

# ========================================
# BROWSER SETTINGS
# ========================================
HEADLESS=1

# ========================================
# SYSTEM SETTINGS
# ========================================
MIN_FREE_SPACE_GB=1.0
LOGGING_ENABLED=true
DEBUG=false
MODE=parallel
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
    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()
            await page.goto('https://www.google.com', timeout=10000)
            title = await page.title()
            print(f'✅ Browser test muvaffaqiyatli: {title}')
            await browser.close()
    except Exception as e:
        print(f'⚠️ Browser test muvaffaqiyatsiz: {e}')
        print('💡 Chromium o\'rnatilmagan yoki server muhitida GUI yo\'q')

asyncio.run(test_browser())
" 2>/dev/null || print_warning "Playwright browser test o'tkazib yuborildi"

print_step "FFmpeg test qilish..."
if command -v ffmpeg >/dev/null 2>&1; then
    ffmpeg -version > /dev/null 2>&1 && print_success "FFmpeg muvaffaqiyatli o'rnatildi" || print_warning "FFmpeg o'rnatilgan lekin ishlamayapti"
else
    print_warning "FFmpeg o'rnatilmagan - video processing ishlamaydi"
fi

if command -v ffprobe >/dev/null 2>&1; then
    ffprobe -version > /dev/null 2>&1 && print_success "FFprobe muvaffaqiyatli o'rnatildi" || print_warning "FFprobe o'rnatilgan lekin ishlamayapti"
else
    print_warning "FFprobe o'rnatilmagan - video metadata extraction ishlamaydi"
fi

print_step "Python importlarni va PostgreSQL ulanishini test qilish..."
python -c "
try:
    import aiohttp
    import playwright
    import telethon
    import ffmpeg
    import tqdm
    import sqlalchemy
    import psycopg2
    import alembic
    print('✅ Barcha Python kutubxonalar import bo\'ldi')
    
    # PostgreSQL ulanishini test qilish
    from core.config import get_database_url
    from sqlalchemy import create_engine
    
    try:
        db_url = get_database_url()
        print(f'🔗 Database URL yaratildi (parol yashirin)')
        
        # Ulanishni test qilish (agar DB sozlangan bo'lsa)
        if 'your_db_host' not in db_url and 'your_password' not in db_url:
            engine = create_engine(db_url)
            engine.connect()
            print('✅ PostgreSQL ulanishi muvaffaqiyatli!')
        else:
            print('⚠️  PostgreSQL sozlamalari to\'ldirilmagan (.env da)')
    except Exception as e:
        print(f'⚠️  PostgreSQL ulanish xatoligi: {e}')
        print('💡 .env faylidagi DB_* parametrlarni to\'ldiring')
        
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
echo "   - DB_HOST, DB_NAME, DB_USER, DB_PASSWORD ni kiriting (PostgreSQL server)"
echo "   - TELEGRAM_API_ID va TELEGRAM_API_HASH ni kiriting"
echo "   - TELEGRAM_PHONE_NUMBER ni kiriting"
echo "   - FILES_GROUP_ID va FILES_GROUP_LINK ni kiriting"
echo ""
echo "2. 🗄️ PostgreSQL migration ishga tushiring:"
echo "   source venv/bin/activate"
echo "   alembic upgrade head"
echo ""
echo "3. 🧪 Loyihani test qiling:"
echo "   python main.py"
echo ""
echo "4. 📊 Loglarni kuzating:"
echo "   tail -f logs/app.log"
echo ""
echo "🎯 MUHIM ESLATMALAR:"
echo "- Database REMOTE serverda joylashgan, local SQLite emas"
echo "- Virtual environment har doim faollashtirilgan bo'lishi kerak: source venv/bin/activate"
echo "- .env faylidagi PostgreSQL va Telegram sozlamalarni to'ldirish majburiy"
echo "- Birinchi ishga tushirishda Telegram autentifikatsiyasi kerak bo'ladi"
echo "- Faqat Chromium browser ishlatiladi (~100MB)"
echo "- Alembic migration bilan database table yaratiladi"
echo "- FFmpeg ixtiyoriy - video processing uchun kerak bo'lsa o'rnatish mumkin"
echo "- Server muhitida GUI paketlar shart emas, headless mode ishlatiladi"
echo ""
echo "❓ Muammo bo'lsa:"
echo "- Loglarni tekshiring: cat logs/app.log"
echo "- Database ulanishini tekshiring: python -c 'from core.FileDB import FileDB; db=FileDB()'"
echo "- Browser test: python -c 'from playwright.async_api import async_playwright'"
echo "- FFmpeg test: ffmpeg -version"
echo "- Alembic status: alembic current"
echo ""
print_success "Loyiha ishga tushirishga tayyor!"