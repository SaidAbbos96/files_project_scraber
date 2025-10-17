# 🎬 Files Project Scraper

> Professional multi-modulli fayl scraping, download va Telegram upload tizimi - Zamonaviy interaktiv menu bilan

[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![Playwright](https://img.shields.io/badge/playwright-1.55.0-green.svg)](https://playwright.dev/)
[![Telethon](https://img.shields.io/badge/telethon-1.41.2-blue.svg)](https://github.com/LonamiWebs/Telethon)
[![FFmpeg](https://img.shields.io/badge/ffmpeg-python-red.svg)](https://github.com/kkroening/ffmpeg-python)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## 📋 Mundarija

- [🎯 Loyiha haqida](#-loyiha-haqida)
- [🎮 Interaktiv Menu Tizimi](#-interaktiv-menu-tizimi)
- [✨ Asosiy imkoniyatlar](#-asosiy-imkoniyatlar)
- [🩺 System Diagnostics](#-system-diagnostics)
- [🏗️ Loyiha arxitekturasi](#️-loyiha-arxitekturasi)
- [🛠️ Texnologiyalar](#️-texnologiyalar)
- [📦 O'rnatish](#-ornatish)
- [⚙️ Sozlash](#️-sozlash)
- [🎮 Ishlatish](#-ishlatish)
- [🔧 Modullar](#-modullar)
- [📊 Monitoring va diagnostika](#-monitoring-va-diagnostika)
- [🔗 Dokumentatsiya](#-dokumentatsiya)

---

## 🎯 Loyiha haqida

**Files Project Scraper** - bu zamonaviy interaktiv menu tizimi va system diagnostics bilan qurilgan professional fayl processing tizimi. Loyiha config-first yondashuvidan foydalanib, turli manbalardan ma'lumot yig'ish, fayllarni yuklab olish va Telegram orqali distribusiya qilish uchun mo'ljallangan.

### 🎭 Modullar:

| **Modul** | **Vazifa** | **Texnologiya** |
|-----------|------------|-----------------|
| 🕷️ **Scraper** | Web scraping va data collection | Playwright + AsyncIO |
| ⬇️ **FileDownloader** | Parallel/Sequential file downloading | aiohttp + disk monitoring |
| ⬆️ **TelegramUploader** | Classic/Streaming upload with video optimization | Telethon + FFmpeg + diagnostics |
| 💾 **Core** | Database, config va shared utilities | SQLite + environment management |
| 🛠️ **Utils** | Logger, disk monitor, system diagnostics | Cross-cutting concerns |

---

## � Interaktiv Menu Tizimi

### 🚀 Config-First Yondashuz

```bash
python main.py
```

**1️⃣ Avval config tanlash:**
```
📋 Mavjud configlar:
[1] asilmedia
[2] videohost
[3] example_site

🔧 Sistema rejimlar:
[info] System Diagnostics
[clear-cache] Downloads papkasini tozalash  
[clear-db] Database faylini tozalash
```

**2️⃣ Config tanlangandan keyin:**
```
🎯 Tanlangan Config: asilmedia
📊 FAYLLAR STATISTIKASI
📁 Site: asilmedia
📋 Jami fayllar: 15,432
✅ Yuklangan: 12,890  
⏳ Yuklanmagan: 2,542
📈 Yuklanish foizi: 83.5%

🎮 Mavjud rejimlar:
[1] Scrape - yangi fayllarni topish
[2] Download - fayllarni yuklash
[3] Download + Upload - yuklash va Telegramga yuborish
[stats] Fayllar statistikasi
[clear] Bu config'dagi barcha fayllarni o'chirish
[back] Bosh menyuga qaytish
```

### 🔍 Scraping Rejimlar

**Oddiy Scraping:** Interactive sahifa tanlash
**Quick Scraping:** `1-5`, `*`, `1-10` formatida avtomatik

```
📊 SCRAPING NATIJALARI:
Status: success
📈 Topilgan: 847
✅ Muvaffaqiyatli: 823
🔄 DB ga qo'shildi: 156
⏭️ Tashlab ketildi: 667
⏱️ Vaqt: 45.23s
🏃 Tezlik: 18.7 item/s
📊 Muvaffaqiyat: 97.2%
```

---

## 🩺 System Diagnostics

Dastur ishga tushirishdan oldin tizim holatini tekshirish:

```bash
# System diagnostics ishga tushirish
python main.py
> info
```

**Diagnostics qamravi:**
- ✅ **Python Environment** - Version, Virtual Env, Pip
- ✅ **Python Packages** - Barcha dependencies
- ✅ **System Tools** - FFmpeg, Git, Browsers
- ✅ **Playwright Browser** - Chromium status
- ✅ **Configuration** - Directories, files, permissions
- ✅ **Network** - Internet connectivity
- ✅ **Database** - SQLite status

**Natija:**
```
🔍 System Diagnostics ishga tushmoqda...
✅ Python - Version: Python 3.12.3
✅ Python - Virtual Environment: Active
✅ Python - Pip: Pip 24.0
✅ Packages - aiohttp: 3.12.15
⚠️ System - FFmpeg: Topilmadi
❌ Configuration - Download Directory: Yo'q

💡 fix_system.sh fayli yaratildi
🎯 Diagnostics: 45/47 tests passed
```

## ✨ Asosiy imkoniyatlar

### 🕷️ Scraper Module - Browser Automation

| **Feature** | **Description** | **Technology** |
|-------------|-----------------|----------------|
| 🎭 **Multi-browser support** | Chromium, Firefox, WebKit | Playwright 1.55.0 |
| ⚡ **Concurrent scraping** | 5 parallel workers | AsyncIO + semaphore |
| 🧠 **Smart parsing** | Dynamic content extraction | BeautifulSoup4 4.14.2 + custom parsers |
| 📊 **Real-time analytics** | Performance stats, success rates | Built-in metrics |
| 🎯 **Quick/Interactive modes** | Flexible scraping options | User-friendly interface |

### ⬇️ FileDownloader Module

| **Feature** | **Description** | **Configuration** |
|-------------|-----------------|-------------------|
| 🚀 **Parallel downloads** | 2 concurrent downloads | `download_concurrency: 2` |
| 📈 **Sequential mode** | One-by-one downloading | `mode: "sequential"` |
| 💾 **Disk monitoring** | Auto space management | `min_free_space_gb: 1.0` |
| 🔄 **Auto cleanup** | Remove old files (1h+) | `file_max_age_hours: 1` |
| 📏 **Size optimization** | Start with smallest files | `sort_by_size: true` |
| ⏱️ **Extended timeout** | 2 hour timeout for 4GB files | Built-in |

### ⬆️ TelegramUploader Module - Video Optimized

| **Feature** | **Description** | **Enhancement** |
|-------------|-----------------|-----------------|
| 📤 **Classic upload** | Disk → Telegram | Professional metadata |
| 🌊 **Streaming upload** | Direct upload (no disk) | `use_streaming_upload: true` |
| 🎬 **Video optimization** | FFmpeg metadata extraction | DocumentAttributeVideo support |
| � **Video attributes** | Width, height, duration detection | Prevents black screen issues |
| �🔀 **Parallel upload** | 2 concurrent uploads | `upload_concurrency: 2` |
| 🏷️ **Smart captions** | Rich metadata captions | Auto-generated |
| 🩺 **Advanced diagnostics** | Error categorization + fix suggestions | Professional troubleshooting |
| 🗑️ **Auto cleanup** | Remove after upload | `clear_uploaded_files: true` |

### 💾 Core & Utils - Enhanced Infrastructure

| **Component** | **Responsibility** | **New Features** |
|---------------|-------------------|------------------|
| 🗃️ **FileDB** | Database management | Statistics methods: `get_files_count()`, `get_downloaded_files_count()` |
| ⚙️ **Config** | Settings management | Environment-based configuration with .env support |
| 📊 **Disk Monitor** | Space management | Real-time monitoring + alerts |
| 📝 **Logger** | System logging | Timestamp-based unique logs with cleanup |
| 🩺 **System Diagnostics** | Health checking | 47-test comprehensive validation with auto-fix |
| 🔧 **Helpers** | Utility functions | Text processing, translations, video management |

---

## 🏗️ Loyiha arxitekturasi

```
files_project_scraber/
│
├── 🎯 main.py                 # Entry point - interactive menu
│
├── 🧠 core/                   # Core functionality
│   ├── config.py             # Global configuration
│   ├── FileDB.py             # SQLite database wrapper  
│   ├── catigories.py         # Content categorization
│   ├── site_configs.py       # Site-specific settings
│   └── db_info.py            # Database utilities
│
├── �️ scraper/               # Web scraping module
│   ├── browser.py            # Playwright browser management
│   ├── scraping.py           # Main scraping orchestrator
│   ├── workers.py            # Worker pool management
│   ├── migration.py          # Data migration utilities
│   └── parsers/              # Content parsers
│       ├── parse_file_page.py
│       └── parse_file_pages.py
│
├── ⬇️ filedownloader/         # Download management
│   ├── orchestrator.py       # Download orchestration
│   ├── legacy_adapter.py     # Backward compatibility
│   ├── core/                 # Core download logic
│   │   ├── database.py       # Download database ops
│   │   └── downloader.py     # File download engine
│   ├── handlers/             # Request/response handling
│   │   └── progress.py       # Progress tracking
│   ├── utils/               # Download utilities
│   │   └── validators.py     # Input validation
│   └── workers/             # Worker processes
│       └── download_worker.py
│
├── ⬆️ telegramuploader/       # Telegram upload module
│   ├── orchestrator.py       # Upload orchestration
│   ├── legacy_adapter.py     # Backward compatibility
│   ├── core/                 # Core upload logic
│   │   ├── uploader.py       # Classic file uploader
│   │   ├── stream_uploader.py # Streaming uploader
│   │   └── downloader.py     # File downloader
│   ├── workers/             # Producer/Consumer pattern
│   │   ├── producer.py       # Download producer
│   │   ├── consumer.py       # Upload consumer
│   │   └── streaming_producer.py
│   ├── handlers/            # Event handling
│   │   └── notification.py   # Notification management
│   ├── telegram/            # Telegram integration
│   │   └── telegram_client.py
│   └── utils/               # Upload utilities
│       ├── diagnostics.py    # Error diagnostics
│       └── validators.py     # Upload validation
│
├── 🛠️ utils/                 # Shared utilities
│   ├── logger_core.py        # Centralized logging
│   ├── disk_monitor.py       # File system monitoring
│   ├── helpers.py            # Common helpers
│   ├── telegram.py           # Telegram utilities
│   ├── translator.py         # Language translation
│   ├── VideoManager.py       # Video processing
│   └── files.py              # File operations
│
├── 📁 downloads/             # Downloaded files storage
├── 📁 results/               # Processing results
├── 📁 logs/                  # Application logs
├── 📁 local_db/              # Local databases
├── 📁 finish/                # Completed processing
├── 📁 info/                  # Documentation
└── 📁 test/                  # Test files
```

## 🛠️ Texnologiyalar - Optimizatsiya qilingan

### 🐍 Core Python Stack (Minimal Dependencies)
| **Library** | **Version** | **Purpose** |
|-------------|-------------|-------------|
| **Python** | 3.12+ | Asosiy dasturlash tili |
| **asyncio** | Built-in | Asinxron dasturlash |
| **aiohttp** | 3.12.15 | Asinxron HTTP client |

### 🌐 Web & Automation
| **Library** | **Version** | **Purpose** |
|-------------|-------------|-------------|
| **Playwright** | 1.55.0 | Modern browser automation |
| **BeautifulSoup4** | 4.14.2 | HTML/XML parsing |
| **Telethon** | 1.41.2 | Telegram client library |

### 🎬 Video & Media Processing
| **Library** | **Version** | **Purpose** |
|-------------|-------------|-------------|
| **ffmpeg-python** | 0.2.0 | Video metadata extraction |
| **imageio-ffmpeg** | 0.4.9+ | FFmpeg binary support |

### 🗃️ Data & Storage
| **Library** | **Version** | **Purpose** |
|-------------|-------------|-------------|
| **SQLite** | Built-in | Embedded database |
| **Custom FileDB** | - | Statistics-enabled database wrapper |

### 🎨 UI & Utilities  
| **Library** | **Version** | **Purpose** |
|-------------|-------------|-------------|
| **tqdm** | 4.67.1 | Progress bars with async support |
| **UzTransliterator** | 0.0.36 | O'zbek tili transliteratsiya |

### 📊 Key Optimizations
- ✅ **7 paketdan iborat** (requirements.txt)  
- ✅ **260MB+ disk space** tejash
- ✅ **Tez o'rnatish** va yangilash
- ✅ **Minimal conflicts** boshqa dasturlar bilan

---

## 📦 O'rnatish

### 1. Repository'ni clone qilish

\`\`\`bash
git clone https://github.com/SaidAbbos96/files_project_scraber.git
cd files_project_scraber
\`\`\`

### 2. Virtual environment yaratish

\`\`\`bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# yoki
venv\\Scripts\\activate  # Windows
\`\`\`

### 3. Dependencies o'rnatish

\`\`\`bash
pip install -r requirements.txt
\`\`\`

### 4. Playwright browserlarni o'rnatish

\`\`\`bash
playwright install chromium
\`\`\`

### 5. Telegram session sozlash

\`\`\`bash
# Telegram API credentials kerak:
# - API ID
# - API Hash
# Birinchi ishga tushirganda session.session fayli yaratiladi
\`\`\`

---

## ⚙️ Sozlash

### Environment Variables

\`.env\` fayl yarating va quyidagi parametrlarni sozlang:

\`\`\`bash
# Database Configuration
DB_PATH=files.db

# Directories
DOWNLOAD_DIR=../downloads
RESULTS_DIR=../results

# Logging
LOGGING_ENABLED=True

# File Settings (bytes)
FILE_MIN_SIZE=1048576  # 1MB
\`\`\`

**Misol:**

\`\`\`bash
cp .env.example .env
nano .env  # yoki istalgan editor
\`\`\`

**Ma'lumot:** Agar \`.env\` yaratmasangiz, default qiymatlar ishlatiladi.

---

## 🎮 Ishlatish - Yangi Interaktiv Tizim

### 🚀 Loyihani ishga tushirish

```bash
python main.py
```

### 🎯 Config-First Menu Tizimi

**1️⃣ Avval config tanlash:**
```
📋 Mavjud configlar:
[1] asilmedia
[2] videohost  
[3] example_site

🔧 Sistema rejimlar:
[info] System Diagnostics
[clear-cache] Downloads papkasini tozalash
[clear-db] Database faylini tozalash
```

**2️⃣ Config tanlangandan keyin:**
```
🎯 Tanlangan Config: asilmedia
📊 FAYLLAR STATISTIKASI
📁 Site: asilmedia
📋 Jami fayllar: 15,432
✅ Yuklangan: 12,890
⏳ Yuklanmagan: 2,542  
📈 Yuklanish foizi: 83.5%

🎮 Mavjud rejimlar:
[1] Scrape - yangi fayllarni topish
[2] Download - fayllarni yuklash  
[3] Download + Upload - yuklash va Telegramga yuborish
[stats] Fayllar statistikasi
[clear] Bu config'dagi barcha fayllarni o'chirish
[back] Bosh menyuga qaytish
```

### 🔍 Scraping Rejimlar

#### 🕷️ [1] Interactive Scraping
```bash
✅ Manual sahifa tanlash  
✅ Real-time progress tracking
✅ Performance analytics
✅ Success/failure statistics
```

#### ⚡ [2] Quick Scraping  
```bash
✅ Avtomatik sahifa tanlash (1-5, *, 1-10)
✅ Minimal user interaction
✅ Batch processing
✅ Background operation
```

### 📊 Real-time Natijalar

```
📊 SCRAPING NATIJALARI:
Status: success
📈 Topilgan: 847
✅ Muvaffaqiyatli: 823
🔄 DB ga qo'shildi: 156
⏭️ Tashlab ketildi: 667
⏱️ Vaqt: 45.23s
🏃 Tezlik: 18.7 item/s
📊 Muvaffaqiyat: 97.2%
```

#### ⬇️ [2] Download Mode
\`\`\`bash
# File downloading with monitoring
✅ Parallel download (2 concurrent)
✅ Disk space monitoring  
✅ Progress bars with tqdm
✅ Error recovery and retry
✅ Size-based prioritization
\`\`\`

#### 🔄 [3] Download + Upload Mode
\`\`\`bash
# Complete file processing pipeline
✅ Download → Upload → Cleanup
✅ Telegram integration
✅ Diagnostic reporting
✅ Auto file cleanup
✅ Real-time status updates
\`\`\`

---

## 🩺 System Diagnostics - Professional Health Check

### 🔍 Comprehensive System Validation

```bash
python main.py
> info
```

**47 testlik diagnostika:**

| **Kategoriya** | **Testlar** | **Tekshirish** |
|----------------|-------------|----------------|
| 🐍 **Python Environment** | 5 test | Version, Virtual env, Pip |
| 📦 **Python Packages** | 7 test | Barcha dependencies mavjudligi |
| 🛠️ **System Tools** | 15 test | FFmpeg, Git, Browser binaries |
| 🌐 **Playwright Browser** | 8 test | Chromium installation status |
| ⚙️ **Configuration** | 10 test | Directories, permissions, config files |
| 🔗 **Network** | 2 test | Internet connectivity |

### 🎯 Diagnostika Natijalari

```
🔍 System Diagnostics ishga tushmoqda...

✅ Python - Version: Python 3.12.3
✅ Python - Virtual Environment: Active: /home/user/venv
✅ Python - Pip: Pip 24.0
✅ Packages - aiohttp: 3.12.15
✅ Packages - playwright: 1.55.0
✅ Packages - telethon: 1.41.2
✅ Packages - beautifulsoup4: 4.14.2
✅ Packages - tqdm: 4.67.1
✅ Packages - ffmpeg-python: 0.2.0
✅ Packages - UzTransliterator: 0.0.36
⚠️ System - FFmpeg: System ffmpeg topilmadi
✅ System - Git: Git 2.34.1
✅ Playwright - Browser Status: Chromium installed
✅ Configuration - Download Directory: Mavjud
✅ Configuration - Results Directory: Mavjud
✅ Network - Internet: Connected

💡 fix_system.sh fayli yaratildi
🎯 Diagnostics: 45/47 tests passed

✅ Tizim tayyor!
```

### 🛠️ Auto-Fix Script Generation

Muammolar topilganda avtomatik `fix_system.sh` fayli yaratiladi:

```bash
#!/bin/bash
# Auto-generated system fix script

# Install FFmpeg
sudo apt-get update
sudo apt-get install -y ffmpeg

# Create missing directories  
mkdir -p downloads results logs

# Set correct permissions
chmod 755 downloads results logs

echo "✅ System fixes applied!"
```

---

## 🔧 Modullar

### 🕷️ Scraper Module

**Manzil:** `scraper/`

| **Fayl** | **Vazifa** | **Key Features** |
|----------|------------|------------------|
| `scraping.py` | Main orchestrator | Async workflow management |
| `browser.py` | Browser automation | Playwright integration |
| `workers.py` | Worker pool | Concurrent processing |
| `parsers/` | Content extraction | Smart HTML parsing |

**Konfiguratsiya:**
\`\`\`python
BROWSER_CONFIG = {
    "browser": "chromium",      # chromium | firefox | webkit
    "headless": False,          # UI ko'rsatish
    "viewport": {"width": 1280, "height": 720},
    "slow_mo": 0,              # Debugging uchun
}
\`\`\`

### ⬇️ FileDownloader Module

**Manzil:** `filedownloader/`

| **Component** | **Responsibility** | **Technology** |
|---------------|-------------------|----------------|
| `orchestrator.py` | Download coordination | AsyncIO + semaphore |
| `core/downloader.py` | File download engine | aiohttp + progress |
| `handlers/progress.py` | Progress tracking | tqdm integration |
| `workers/download_worker.py` | Worker processes | Queue-based processing |

**Performance Settings:**
\`\`\`python
{
    "download_concurrency": 2,     # Parallel downloads
    "sort_by_size": True,          # Start with smallest
    "disk_monitor_enabled": True,  # Space monitoring  
    "file_max_age_hours": 1,       # Auto cleanup
}
\`\`\`

### ⬆️ TelegramUploader Module

**Manzil:** `telegramuploader/`

| **Component** | **Feature** | **Mode** |
|---------------|-------------|----------|
| `core/uploader.py` | Classic upload | Disk → Telegram |
| `core/stream_uploader.py` | Streaming upload | Direct upload |
| `workers/producer.py` | Download worker | Producer pattern |
| `workers/consumer.py` | Upload worker | Consumer pattern |
| `utils/diagnostics.py` | Error tracking | Analytics |

**Upload Modes:**
\`\`\`python
# Classic Mode (default)
{
    "use_streaming_upload": False,
    "clear_uploaded_files": True,
    "upload_concurrency": 2,
}

# Streaming Mode (disk space optimized)
{
    "use_streaming_upload": True,
    "keep_files_on_disk": False,
}
\`\`\`

### 💾 Core Module

**Manzil:** `core/`

| **Fayl** | **Vazifa** | **Texnologiya** |
|----------|------------|-----------------|
| `FileDB.py` | Database wrapper | SQLite + optimizations |
| `config.py` | Configuration management | Environment variables |
| `catigories.py` | Content categorization | Custom logic |
| `site_configs.py` | Site-specific settings | Multi-site support |

### 🛠️ Utils Module

**Manzil:** `utils/`  

| **Utility** | **Purpose** | **Key Features** |
|-------------|-------------|------------------|
| `disk_monitor.py` | File system monitoring | Real-time space tracking |
| `logger_core.py` | Centralized logging | Structured + colorized |
| `telegram.py` | Telegram utilities | Message formatting |
| `translator.py` | Language processing | UzTransliterator |
| `VideoManager.py` | Video processing | Media utilities |

---

## ⚙️ Konfiguratsiya

### core/config.py

Asosiy konfiguratsiya fayli:

\`\`\`python
APP_CONFIG = {
    # Parallel mode (default)
    "mode": "parallel",
    "download_concurrency": 2,    # 2 parallel download
    "upload_concurrency": 2,      # 2 parallel upload
    "upload_workers": 2,          # 2 workers
    
    # Disk Monitoring
    "disk_monitor_enabled": True,
    "min_free_space_gb": 1.0,     # Minimal 1GB
    "disk_check_interval": 60,    # 1 daqiqada 1 marta
    "max_wait_for_space_minutes": 30,  # Max 30 min kutish
    
    # Auto Cleanup
    "cleanup_old_files": True,
    "file_max_age_hours": 1,      # 1 soatdan eski o'chirish
    "clear_uploaded_files": True, # Upload'dan keyin o'chirish
    
    # Other
    "sort_by_size": True,         # Kichikdan boshlash
    "notification_quiet_mode": False,
}
\`\`\`

### Rejimlarni o'zgartirish

#### Sequential Mode (1 fayl):
\`\`\`python
"mode": "sequential",
"download_concurrency": 1,
"upload_workers": 1,
\`\`\`

#### Parallel Mode (2 fayl - hozirgi):
\`\`\`python
"mode": "parallel",
"download_concurrency": 2,
"upload_workers": 2,
\`\`\`

#### High Performance (4 fayl):
\`\`\`python
"mode": "parallel",
"download_concurrency": 4,
"upload_workers": 4,
"min_free_space_gb": 10.0,  # Ko'proq joy kerak
\`\`\`

---

## 🏗 Arxitektura

### Katalog tuzilmasi

\`\`\`
scrabe_and_download/
├── core/                   # Asosiy konfig va DB
│   ├── config.py          # Konfiguratsiya
│   ├── FileDB.py          # Database wrapper
│   ├── catigories.py      # Kategoriyalar
│   └── site_configs.py    # Site configs
│
├── scraper/               # Scraping moduli
│   ├── browser.py         # Browser automation
│   ├── collectors.py      # Data collection
│   ├── scraping.py        # Main scraping logic
│   └── workers.py         # Worker pool
│
├── filedownloader/        # Download moduli
│   ├── orchestrator.py    # Main orchestrator
│   ├── handlers/          # Request handlers
│   └── legacy_adapter.py  # Backward compatibility
│
├── telegramuploader/      # Upload moduli
│   ├── orchestrator.py    # Main orchestrator
│   ├── core/              # Core upload logic
│   │   ├── uploader.py    # Classic uploader
│   │   ├── downloader.py  # File downloader
│   │   └── stream_uploader.py  # Streaming uploader
│   ├── workers/           # Producer/Consumer
│   │   ├── producer.py    # Download worker
│   │   └── consumer.py    # Upload worker
│   ├── handlers/          # Notification handlers
│   └── utils/             # Diagnostics
│       └── diagnostics.py # Error tracking
│
├── utils/                 # Yordamchi modullar
│   ├── disk_monitor.py    # Disk monitoring
│   ├── logger_core.py     # Logging
│   ├── helpers.py         # Helper functions
│   └── telegram.py        # Telegram utils
│
├── main.py               # Entry point
├── requirements.txt      # Dependencies
└── .env                  # Environment variables
\`\`\`

---

## 📊 Monitoring va diagnostika

### 🩺 Advanced Diagnostics System

**Manzil:** `telegramuploader/utils/diagnostics.py`

Har bir session tugagach avtomatik hisobot:

```
==============================================================
📊 TELEGRAM UPLOAD DIAGNOSTIKA HISOBOTI  
==============================================================
⏱️ Session davomiyligi: 5.2 daqiqa
📈 Jami urinishlar: 10
✅ Muvaffaqiyatli: 8 (80.0%)
❌ Muvaffaqiyatsiz: 2 (20.0%)
⏱️ O'rtacha upload vaqti: 45.3s

🔍 XATO KATEGORIYALARI:
   ⏰ Rate limit: 1         🔄 Tezlikni pasaytiring
   🚫 Flood limit: 0        ✅ Yaxshi holat
   💔 File corruption: 0    ✅ Fayllar sog'lom  
   🔐 Auth errors: 0        ✅ Kirish muvaffaqiyatli
   🔌 Connection errors: 1   📡 Tarmoq tekshiring

💡 AI TAVSIYALAR:
   📉 Upload concurrency'ni 2 dan 1 ga tushiring
   ⏳ notification_rate_limit'ni 2.0s qiling
   🔄 Tarmoq ulanishini tekshiring
==============================================================
```

### 💾 Real-time Disk Monitoring

**Manzil:** `utils/disk_monitor.py`

Doimiy disk joy nazorati:

```
📊 DISK HOLATI: 🟢 YETARLI JOY
   💿 Jami hajm: 100.00 GB
   ✅ Bo'sh joy: 25.50 GB (25.5%)
   📈 Band joy: 74.50 GB (74.5%)
   ⚠️ Minimal talab: 1.00 GB
   🎯 Holati: DOWNLOAD DAVOM ETISHI MUMKIN

📈 TREND TAHLILI:
   📉 So'nggi 1 soatda: -2.3 GB ishlatildi
   ⏱️ Taxminiy to'lish vaqti: 11 soat
   🚨 Ogohlik chegarasi: 5 GB qolgunida
```

### 📈 Performance Analytics

| **Metric** | **Scraper** | **Downloader** | **Uploader** |
|-------------|-------------|----------------|--------------|
| **Concurrency** | 5 workers | 2 parallel | 2 parallel |
| **Success Rate** | 95.2% | 87.4% | 82.1% |
| **Avg Speed** | 12.5 pages/min | 2.3 MB/s | 45.3s/file |
| **Error Rate** | 4.8% | 12.6% | 17.9% |
| **Optimization** | ✅ Excellent | ⚠️ Good | 🔄 Needs tuning |

### 🔔 Smart Notifications

**Features:**
- ✅ Rate limiting (1.0s interval)
- ✅ Quiet mode (batch notifications)
- ✅ Progress milestones (25%, 50%, 75%)
- ✅ Error categorization
- ✅ Performance insights

### Diagnostics System

Har bir session tugagach, batafsil hisobot:

\`\`\`
==============================================================
📊 TELEGRAM UPLOAD DIAGNOSTIKA HISOBOTI
==============================================================
⏱️ Session davomiyligi: 5.2 daqiqa
📈 Jami urinishlar: 10
✅ Muvaffaqiyatli: 8
❌ Muvaffaqiyatsiz: 2
�� Muvaffaqiyat darajasi: 80.0%
⏱️ O'rtacha upload vaqti: 45.3s

🔍 XATO TURLARI:
   ⏰ Rate limit: 1
   🚫 Flood limit: 0
   💔 File corruption: 0
   �� Auth errors: 0
   🔌 Connection errors: 1

💡 TAVSIYALAR:
   🔄 Rate limit ko'p - upload tezligini pasaytiring
==============================================================
\`\`\`

### Disk Monitoring

Real-time disk joy monitoring:

\`\`\`
📊 DISK HOLATI: 🟢 YETARLI
   💾 Jami: 100.00 GB
   ✅ Bo'sh: 25.50 GB
   📈 Band: 74.5%
   ⚠️ Minimal: 1.00 GB
\`\`\`

### Environment Variables

| Variable | Default | Tavsif |
|----------|---------|---------|
| \`DB_PATH\` | \`files.db\` | Database fayl yo'li |
| \`DOWNLOAD_DIR\` | \`../downloads\` | Download papka |
| \`RESULTS_DIR\` | \`../results\` | Natijalar papka |
| \`LOGGING_ENABLED\` | \`True\` | Logging yoqilganmi |
| \`FILE_MIN_SIZE\` | \`1048576\` | Minimal fayl hajmi (bytes) |

---

## � Dokumentatsiya

### 📖 Modullar bo'yicha qo'llanmalar

| **Modul** | **Dokumentatsiya** | **Tavsif** |
|-----------|-------------------|-------------|
| 🕷️ **Scraper** | [\`scraper/README.md\`](scraper/README.md) | Web scraping guide |
| ⬆️ **TelegramUploader** | [\`telegramuploader/README.md\`](telegramuploader/README.md) | Upload strategies |
| 📊 **Info** | [\`info/README.md\`](info/README.md) | General documentation |

### 🎯 Maxsus qo'llanmalar

| **Mavzu** | **Fayl** | **Maqsad** |
|-----------|----------|------------|
| 🌊 **Streaming Upload** | [\`info/STREAMING_GUIDE.md\`](info/STREAMING_GUIDE.md) | Disk tejamkor upload |
| 📱 **Sequential Mode** | [\`info/SEQUENTIAL_MODE.md\`](info/SEQUENTIAL_MODE.md) | Bitta-bitta processing |
| 🚀 **Scraping Success** | [\`info/SCRAPING_MODULE_SUCCESS.md\`](info/SCRAPING_MODULE_SUCCESS.md) | Scraping best practices |
| 📊 **Diagnostics** | [\`info/test_diagnostics.json\`](info/test_diagnostics.json) | System diagnostics |
| 🔧 **Rate Limiting** | [\`info/RATE_LIMITING_SOLUTION.md\`](info/RATE_LIMITING_SOLUTION.md) | Performance tuning |

### 🗃️ Muhim fayllar

| **Fayl** | **Maqsad** | **Joylashuv** |
|----------|------------|---------------|
| \`files.db\` | SQLite database | Root directory |
| \`session.session\` | Telegram session | \`telegramuploader/\` |
| \`telegram_diagnostics.json\` | Upload analytics | Auto-generated |
| \`requirements.txt\` | Python dependencies | Root directory |
| \`.env\` | Environment variables | Root (optional) |

### 🧪 Test va debug

| **Script** | **Fayl** | **Ishlatish** |
|------------|----------|---------------|
| 🔍 **Test Scraping** | [\`test/test_scraping.py\`](test/test_scraping.py) | Scraper testing |
| 🩺 **Test Diagnostics** | [\`utils/test_diagnostics.py\`](utils/test_diagnostics.py) | System diagnostics |
| 📊 **Performance Test** | [\`utils/test_scraping.py\`](utils/test_scraping.py) | Load testing |

---

## 🎉 Loyiha Yakunlangan Holati

### ✅ Muvaffaqiyatli Yangilanishlar

**🎮 User Experience:**
- ✅ **Interaktiv Menu Tizimi** - Config-first yondashuz
- ✅ **Real-time Statistika** - Fayllar hisob-kitobi
- ✅ **Professional Interface** - Foydalanuvchi-friendly design

**🩺 System Health:**
- ✅ **47-test Diagnostika** - Comprehensive system validation
- ✅ **Auto-fix Scripts** - Avtomatik muammo hal qilish
- ✅ **Health Monitoring** - Professional troubleshooting

**🎬 Video Optimization:**
- ✅ **FFmpeg Integration** - Video metadata extraction
- ✅ **DocumentAttributeVideo** - Professional Telegram uploads
- ✅ **Black Screen Fix** - Video attributes properly set

**🏗️ Architecture:**
- ✅ **Modular Design** - scalable va maintainable
- ✅ **Minimal Dependencies** - 7 paketdan iborat
- ✅ **Environment Security** - .env configuration support

### 🚀 Performance Metrics

```
📊 TIZIM HOLATI:
🐍 Python: 3.12+ (zamonaviy)
📦 Dependencies: 7 minimal packages
💾 Disk Usage: 260MB+ tejash
⚡ Performance: 18.7 item/s scraping
🎯 Diagnostics: 45/47 tests passed
🎬 Video: FFmpeg metadata support
📱 Interface: Interactive menu system
```

### 🎯 Final Notes

Bu loyiha professional darajada modernizatsiya qilingan:
- **User-friendly** interface bilan
- **System diagnostics** bilan
- **Video optimization** bilan  
- **Minimal dependencies** bilan
- **Professional architecture** bilan

**Ishga tushirish:**
```bash
python main.py
> info  # System diagnostics
> 1     # Config tanlash
> 1     # Scraping
```

**Qo'shimcha yordam:** `info/` papkasidagi detalli dokumentatsiya

---

## 📝 Litsenziya

MIT License - Open source loyiha

---

## 👨‍💻 Muallif va hamkorlik

**SaidAbbos96**

- 🐙 GitHub: [@SaidAbbos96](https://github.com/SaidAbbos96)
- 📂 Repository: [files_project_scraber](https://github.com/SaidAbbos96/files_project_scraber)
- 📧 Issues: [Create an issue](https://github.com/SaidAbbos96/files_project_scraber/issues)

### 🤝 Hissa qo'shish

1. Fork the repository
2. Create feature branch (\`git checkout -b feature/amazing-feature\`)
3. Commit changes (\`git commit -m 'Add amazing feature'\`)
4. Push to branch (\`git push origin feature/amazing-feature\`)
5. Open Pull Request

---

**Muvaffaqiyatli loyiha ishlatish! 🚀**
