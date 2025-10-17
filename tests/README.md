# Tests Directory

Bu papkada loyihaning barcha test fayllari joylashgan.

## 📁 Test fayllari:

### Core Tests
- `test_diagnostics.py` - Tizim diagnostika testlari
- `test_scraping.py` - Scraping moduli testlari  
- `test_video_attributes.py` - Video attributes testlari

### Feature Tests
- `test_enhanced_downloader.py` - Enhanced FileDownloader testlari
- `test_real_download.py` - Haqiqiy fayl download testlari

## 🚀 Testlarni ishga tushirish:

```bash
# Python environment faollashtirish
source venv/bin/activate

# Barcha testlar
python -m pytest tests/

# Bitta test fayl
python tests/test_enhanced_downloader.py

# Real download test
python tests/test_real_download.py

# System diagnostics test
python tests/test_diagnostics.py
```

## 📊 Test coverage:

- ✅ FileDownloader with intelligent timeout
- ✅ Video attributes extraction  
- ✅ System diagnostics validation
- ✅ Scraping functionality
- ✅ Real download scenarios

## ⚠️ Eslatma:
Testlar loyiha root papkasidan ishga tushirilishi kerak va Python environment faollashtirilgan bo'lishi kerak.