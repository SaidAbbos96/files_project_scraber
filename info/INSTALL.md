# 📦 Package Installation Guide

Loyiha uchun faqat kerakli package'larni o'rnatish:

## 🔄 Virtual Environment'ni yangilash

```bash
# Current directory'da
cd /home/aicoder/coding/files_project/files_project_scraber

# Venv'ni activate qiling
source venv/bin/activate

# Requirements'ni o'rnating
pip install -r requirements.txt

# Playwright browser'larni o'rnating
playwright install chromium

# Installation'ni tekshiring
python -c "import aiohttp, playwright, telethon, tqdm; print('✅ All packages installed!')"
```

## 📊 Package'lar ro'yxati

1. **aiohttp** - Async HTTP client/server
2. **anyio** - Cross-platform async library  
3. **playwright** - Modern browser automation
4. **beautifulsoup4** - HTML/XML parsing
5. **Telethon** - Telegram client
6. **tqdm** - Progress bars
7. **UzTransliterator** - O'zbek tili transliteratsiya

## 🎯 Optimizations

- Faqat ishlatilayotgan package'lar
- Latest stable versions
- Python 3.12+ compatibility
- Minimal dependencies