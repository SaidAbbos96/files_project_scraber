# 🚀 YANGI SERVER UCHUN MANUAL O'RNATISH QO'LLANMASI

## 📋 TO'LIQ QADAM BA QADAM COMMANDLAR

Bu qo'llanma har bir commandni alohida ko'rsatadi. Copy-paste qiling va ketma-ket bajaring.

---

## 🔧 1-QADAM: SERVER TAYYORLASH

### A. Sistema yangilash va asosiy paketlar

```bash
# Sistema yangilash
sudo apt update
sudo apt upgrade -y
```

```bash
# Asosiy development tools
sudo apt install -y python3 python3-pip python3-venv curl wget git htop screen
```

```bash
# Multimedia va video processing tools
sudo apt install -y ffmpeg libavcodec-extra libavformat-dev libavutil-dev libswscale-dev
```

```bash
# Playwright browser dependencies
sudo apt install -y libnss3 libnspr4 libatk-bridge2.0-0 libdrm2 libxkbcommon0 libxcomposite1 libxdamage1 libxrandr2 libgbm1 libxss1 libasound2 libatspi2.0-0 libgtk-3-0 libgdk-pixbuf2.0-0
```

### B. FFmpeg va FFprobe test qilish

```bash
# FFmpeg version tekshirish
ffmpeg -version
```

```bash
# FFprobe version tekshirish (FFmpeg bilan birga keladi)
ffprobe -version
```

### C. Loyihani clone qilish

```bash
# GitHub'dan clone qilish
git clone https://github.com/SaidAbbos96/files_project_scraber.git
```

```bash
# Loyiha papkasiga kirish
cd files_project_scraber
```

---

## 🐍 2-QADAM: PYTHON ENVIRONMENT

### A. Virtual environment yaratish

```bash
# Virtual environment yaratish
python3 -m venv venv
```

```bash
# Virtual environment faollashtirish
source venv/bin/activate
```

### B. Python requirements o'rnatish

```bash
# pip yangilash
pip install --upgrade pip
```

```bash
# Requirements fayldan o'rnatish
pip install -r requirements.txt
```

---

## 🌐 3-QADAM: PLAYWRIGHT SETUP

### A. Playwright browserlarni o'rnatish

```bash
# Virtual environment faollashtirish (agar faol bo'lmasa)
source venv/bin/activate
```

```bash
# Chromium browser o'rnatish
playwright install chromium
```

```bash
# Firefox browser o'rnatish  
playwright install firefox
```

```bash
# Webkit browser o'rnatish
playwright install webkit
```

### B. Playwright system dependencies

```bash
# System dependencies o'rnatish
playwright install-deps
```

---

## ⚙️ 4-QADAM: LOYIHA SOZLASH

### A. Kerakli papkalar yaratish

```bash
# Downloads papka
mkdir -p downloads
```

```bash
# Results papka
mkdir -p results
```

```bash
# Finish papka  
mkdir -p finish
```

```bash
# Logs papka
mkdir -p logs
```

```bash
# Local database papka
mkdir -p local_db
```

### B. .env fayl yaratish

```bash
# .env fayl yaratish
touch .env
```

```bash
# .env faylini tahrirlash
nano .env
```

**Quyidagi kontent ni .env faylga copy qiling:**

```env
# Database
DB_LOCAL_NAME=local_files

# Telegram API (https://my.telegram.org dan oling!)
TELEGRAM_API_ID=your_api_id_here
TELEGRAM_API_HASH=your_api_hash_here
TELEGRAM_PHONE_NUMBER=+998901234567
FILES_GROUP_LINK=https://t.me/your_files_channel

# Worker nomi (har server uchun boshqacha)
WORKER_NAME=server_001

# Download settings
DOWNLOAD_CONCURRENCY=2
SCRAPE_CONCURRENCY=5
UPLOAD_CONCURRENCY=2
DOWNLOAD_MAX_RETRIES=3
DOWNLOAD_CHUNK_SIZE=262144

# Playwright settings
HEADLESS=1

# Disk monitoring
MIN_FREE_SPACE_GB=1.0
DISK_MONITOR_ENABLED=true

# Logging
LOGGING_ENABLED=true
DEBUG=false

# Timing
SLEEP_MIN=0.5
SLEEP_MAX=2.5
ENABLE_SLEEP=true
```

**MUHIM:** Quyidagi qiymatlarni o'zgartiring:
- `TELEGRAM_API_ID` - o'z API ID ngiz
- `TELEGRAM_API_HASH` - o'z API hash ingiz  
- `TELEGRAM_PHONE_NUMBER` - o'z telefon raqamingiz
- `FILES_GROUP_LINK` - o'z Telegram channel/group linkingiz
- `WORKER_NAME` - server nomi (masalan: server_001, server_002, etc.)

---

## 🧪 5-QADAM: TESTLAR

### A. Python modules test

```bash
# Virtual environment faollashtirish
source venv/bin/activate
```

```bash
# Python modullarni test qilish
python -c "import aiohttp, playwright, telethon, ffmpeg, tqdm; print('✅ Barcha modullar import qilindi')"
```

### B. Playwright browser test

```bash
# Browser test
python -c "
import asyncio
from playwright.async_api import async_playwright

async def test():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        await page.goto('https://google.com')
        title = await page.title()
        print(f'✅ Browser test muvaffaqiyatli: {title}')
        await browser.close()

asyncio.run(test())
"
```

### C. FFmpeg test

```bash
# FFmpeg python module test
python -c "import ffmpeg; print('✅ FFmpeg Python module ishlaydi')"
```

---

## 📺 6-QADAM: SCREEN SESSION VA ISHGA TUSHIRISH

### A. Screen session yaratish

```bash
# Yangi screen session yaratish
screen -S files_project
```

### B. Virtual environment faollashtirish (screen ichida)

```bash
# Screen ichida virtual environment faollashtirish
source venv/bin/activate
```

### C. Loyihani ishga tushirish

```bash
# Loyihani ishga tushirish
python main.py
```

### D. Screen session boshqarish

**Screen'dan chiqish (loyiha ishlash davom etadi):**
```
Ctrl + A, so'ngra D
```

**Screen'ga qayta kirish:**
```bash
screen -r files_project
```

**Screen sessionlarni ko'rish:**
```bash
screen -ls
```

**Screen sessionni to'xtatish:**
```bash
screen -S files_project -X quit
```

---

## 📊 7-QADAM: MONITORING VA LOG KUZATISH

### A. Logs kuzatish

```bash
# Realtime log kuzatish (yangi terminal'da)
tail -f logs/app.log
```

```bash
# Xatoliklarni ko'rish
grep ERROR logs/app.log
```

```bash
# Muvaffaqiyatli yuklashlarni sanash
grep "Download tugadi\|muvaffaqiyatli yuklandi" logs/app.log | wc -l
```

### B. Sistema monitoring

```bash
# CPU va RAM kuzatish
htop
```

```bash
# Disk joy kuzatish
df -h
```

```bash
# Network usage
iftop
```

### C. Process management

```bash
# Background process sifatida ishlatish (screen o'rniga)
nohup python main.py > output.log 2>&1 &
```

```bash
# Process'ni topish
ps aux | grep python
```

```bash
# Process'ni to'xtatish (PID ni almashtiring)
kill PID_NUMBER
```

---

## ⚠️ KENG UCHRAYDIGAN MUAMMOLAR VA YECHIMLAR

### 🌐 Playwright Browser Muammosi

**Agar bu xato chiqsa:**
```
BrowserType.launch: Executable doesn't exist at /home/user/.cache/ms-playwright/chromium...
```

**Yechim:**
```bash
# Virtual environment faollashtirish
source venv/bin/activate
```

```bash
# Browserlarni qayta o'rnatish
playwright install chromium
```

```bash
# System dependencies
playwright install-deps
```

### 🎬 FFprobe/FFmpeg Muammosi

**Agar bu warning chiqsa:**
```
WARNING | main | ⚠️ FFprobe ishlamadi, basic validation
```

**Yechim:**
```bash
# FFmpeg qayta o'rnatish (ffprobe ham birga keladi)
sudo apt install -y ffmpeg libavcodec-extra
```

```bash
# Path tekshirish
which ffprobe
```

```bash
# Version tekshirish
ffprobe -version
```

### 🐍 Python Module Import Xatoligi

**Agar bu xato chiqsa:**
```
ModuleNotFoundError: No module named 'playwright'
```

**Yechim:**
```bash
# Virtual environment faollashtirish
source venv/bin/activate
```

```bash
# Requirements qayta o'rnatish
pip install -r requirements.txt
```

### 📁 Permission Denied Xatoligi

**Yechim:**
```bash
# Loyiha papkasiga ruxsat berish
chmod -R 755 .
```

```bash
# Virtual environment ga ruxsat
chmod -R 755 venv/
```

### ⚙️ .env Fayl Muammosi

**Agar .env o'qilmayotgan bo'lsa:**
```bash
# .env fayl joylashuvini tekshirish
ls -la .env
```

```bash
# .env fayl mazmunini tekshirish
cat .env
```

**Masalan, TELEGRAM_API_ID to'ldirilmaganligini tekshirish:**
```bash
grep "your_api_id_here" .env
```

---

## � 8-QADAM: QAYTA ISHGA TUSHIRISH (SERVER RESTART KEYIN)

Server restart bo'lgandan keyin loyihani qayta ishga tushirish uchun:

### A. Loyiha papkasiga o'tish

```bash
cd files_project_scraber
```

### B. Screen session yaratish

```bash
screen -S files_project
```

### C. Virtual environment faollashtirish

```bash
source venv/bin/activate
```

### D. Loyihani ishga tushirish

```bash
python main.py
```

### E. Screen'dan chiqish

```
Ctrl + A, keyin D
```

---

## 🎯 PRODUCTION UCHUN SYSTEMD SERVICE (IXTIYORIY)

Agar loyiha avtomatik ishga tushishini istasangiz:

### A. Service fayl yaratish

```bash
sudo nano /etc/systemd/system/files-scraper.service
```

**Quyidagi kontent ni copy qiling (path larni o'zgartiring):**

```ini
[Unit]
Description=Files Project Scraper
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/files_project_scraber
Environment=PATH=/home/ubuntu/files_project_scraber/venv/bin
ExecStart=/home/ubuntu/files_project_scraber/venv/bin/python main.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

### B. Service faollashtirish

```bash
sudo systemctl daemon-reload
```

```bash
sudo systemctl enable files-scraper
```

```bash
sudo systemctl start files-scraper
```

### C. Service statusini tekshirish

```bash
sudo systemctl status files-scraper
```

### D. Service loglarini kuzatish

```bash
journalctl -u files-scraper -f
```

---

## ✅ OXIRGI TEKSHIRISH VA TASDIQ

O'rnatish tugagach quyidagi commandlarni ishga tushirib tekshiring:

### Final Test Commands

```bash
# 1. Virtual environment faollashtirish
source venv/bin/activate
```

```bash
# 2. Python modules test
python -c "import playwright, telethon, aiohttp, ffmpeg, tqdm; print('✅ Modules OK')"
```

```bash
# 3. Playwright version
playwright --version
```

```bash
# 4. FFmpeg test
ffmpeg -version && ffprobe -version
```

```bash
# 5. .env fayl tekshirish
grep -E "TELEGRAM_API_ID|TELEGRAM_API_HASH|WORKER_NAME" .env
```

```bash
# 6. Papkalar tekshirish
ls -la downloads/ results/ finish/ logs/ local_db/
```

**Agar barcha testlar muvaffaqiyatli bo'lsa, loyihani ishga tushiring:**

```bash
screen -S files_project
source venv/bin/activate
python main.py
```

---

## 📋 TEZKOR REFERENCE (Copy-Paste uchun)

**Har kuni ishlatish uchun:**

```bash
# Loyiha papkasiga o'tish
cd files_project_scraber

# Screen session yaratish
screen -S files_project

# Virtual env faollashtirish
source venv/bin/activate

# Loyiha ishga tushirish
python main.py

# Screen'dan chiqish: Ctrl+A, keyin D
```

**Screen'ga qaytish:**
```bash
screen -r files_project
```

**Loglarni kuzatish:**
```bash
tail -f logs/app.log
```

**Virtual environment har doim faol bo'lishi kerak!**

---

## 🎉 O'RNATISH YAKUNLANDI!

Agar barcha qadam lar muvaffaqiyatli bajarilsa, loyihangiz ishga tushishga tayyor! 

**Muhim eslatmalar:**
- ✅ Virtual environment har doim faollashtiring
- ✅ .env faylidagi API ma'lumotlarni to'ldiring  
- ✅ Screen session ishlatib background'da ishlating
- ✅ Loglarni vaqti-vaqti bilan tekshiring

**Muammo bo'lsa, yuqoridagi "MUAMMOLAR VA YECHIMLAR" bo'limiga qarang.**