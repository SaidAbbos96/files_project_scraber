# Scraping Module - Yangi Optimallashtirilgan Struktura

## 📁 Modul Strukturasi

```
scraping/                          # Asosiy scraping moduli
├── __init__.py                    # Modul interface
├── scraping.py                    # Asosiy orchestration
├── browser.py                     # Browser boshqaruvi
├── workers.py                     # Parallel processing
├── migration.py                   # Eski moduldan migration
├── parsers/                       # HTML parsing modullari
│   ├── __init__.py
│   ├── parse_file_page.py         # Bitta sahifa parsing
│   └── parse_file_pages.py        # Ko'p sahifa parsing
```

## 🎯 Asosiy Imkoniyatlar

### 1. Browser Boshqaruvi (`browser.py`)
- Playwright browser yaratish va boshqaruv
- Xavfsiz sahifaga o'tish va retry mexanizmi
- Browser kontekst va resurs boshqaruvi
- Optimallashtirilgan browser konfiguratsiyasi

### 2. HTML Parsing (`parsers/`)
- **Bitta sahifa parsing** (`parse_file_page.py`):
  - Film sahifasidan ma'lumot ajratish
  - Fayl hajmi tekshiruvi va optimallash
  - Ma'lumotlarni normallash va tozalash
  - aiohttp → browser fallback mexanizmi

- **Ko'p sahifa parsing** (`parse_file_pages.py`):
  - Pagination bilan ishlash
  - Listing sahifalardan film linklar ajratish
  - Batch processing
  - Parallel sahifa tahlili

### 3. Parallel Processing (`workers.py`)
- Async workers bilan parallel scraping
- Semaphore orqali concurrency cheklash
- Batch processing va checkpoint
- Xato boshqaruv va statistika
- Advanced worker pool

### 4. Orchestration (`scraping.py`)
- To'liq scraping jarayoni boshqaruvi
- ScrapingOrchestrator klassi
- Scraping statistikasi
- Multiple site scraping
- Quick scrape funksiyasi

## 🚀 Foydalanish

### Asosiy Foydalanish

```python
from scraping import scrape

# CONFIG va BROWSER_CONFIG bilan
result = await scrape(CONFIG, BROWSER_CONFIG)

# Natija dict formatida qaytadi:
# {
#     "status": "success",
#     "total_found": 150,
#     "successful": 145,
#     "inserted": 145,
#     "skipped": 30,
#     "stats": {...}
# }
```

### Kengaytirilgan Foydalanish

```python
from scraping import ScrapingOrchestrator, quick_scrape

# Quick scrape (input so'ramasdan)
result = await quick_scrape(CONFIG, BROWSER_CONFIG, page_selection="1-10")

# To'liq boshqaruv
orchestrator = ScrapingOrchestrator(CONFIG, BROWSER_CONFIG)
result = await orchestrator.run_scraping_process()
```

### Ko'p Saytli Scraping

```python
from scraping import batch_scrape_multiple_sites

sites = [CONFIG1, CONFIG2, CONFIG3]
results = await batch_scrape_multiple_sites(sites, BROWSER_CONFIG)
```

## 🔄 Migration (O'tish Jarayoni)

### Eski Moduldan Yangi Modulga O'tish

1. **Migration scriptini ishlatish**:
```python
from scraping.migration import migrate_scrape

result = await migrate_scrape(CONFIG, BROWSER_CONFIG)
```

2. **Yangi runner.py ishlatish**:
```python
# Eski
from scraper.runner import scrape

# Yangi
from new_runner import run_scraping
result = await run_scraping(CONFIG, BROWSER_CONFIG)
```

### Migration Tekshiruvi

```python
from scraping.migration import check_module_compatibility

compatibility = check_module_compatibility()
print(compatibility)
# {
#     "new_scraping_module": True,
#     "old_scraper_module": True, 
#     "can_migrate": True
# }
```

## 📊 Scraping Statistikasi

Yangi modul har bir scraping jarayoni uchun batafsil statistika beradi:

```python
{
    "status": "success",
    "total_found": 200,           # Topilgan umumiy sahifalar
    "skipped": 50,                # DB da mavjud bo'lganlari
    "processed": 150,             # Yangi tahlil qilinganlar
    "successful": 145,            # Muvaffaqiyatli
    "inserted": 145,              # DB ga qo'shilganlar
    "stats": {
        "total_processed": 150,
        "successful": 145,
        "errors": 5,
        "success_rate": 96.67,
        "duration_seconds": 180.5,
        "items_per_second": 0.83
    }
}
```

## ⚙️ Konfiguratsiya

### Browser Konfiguratsiyasi
```python
BROWSER_CONFIG = {
    "browser": "chromium",        # firefox, webkit
    "headless": True,
    "slow_mo": 50,
    "viewport": {"width": 1920, "height": 1080},
    "user_agent": "...",
    "locale": "uz-UZ",
    "proxy": None,
    # ... boshqa sozlamalar
}
```

### Sayt Konfiguratsiyasi
```python
CONFIG = {
    "name": "site_name",
    "base_url": "https://example.com",
    "pagination_link": "https://example.com/page/{page}/",
    "pagination_selector": "a.last",
    "card_selector": ".film-card",
    "scrape_concurrency": 5,      # Parallel workers soni
    "fields": {
        "title": "h1.title::text",
        "file_url": "a.download::attr(href)",
        # ... boshqalar
    }
}
```

## 🛠️ Advanced Features

### 1. Custom Worker Pool
```python
from scraping.workers import WorkerPool

pool = WorkerPool(max_workers=10)
# Custom parallel processing
```

### 2. Batch Processing
```python
from scraping.workers import process_batch_parallel

results = await process_batch_parallel(
    config, browser, film_links, 
    batch_size=20, 
    checkpoint_interval=100
)
```

### 3. Processing Statistics
```python
from scraping.workers import ProcessingStats

stats = ProcessingStats()
stats.start()
# ... processing
stats.finish()
summary = stats.get_summary()
```

## 🔧 Debugging va Monitoring

### Log Darajalarini Sozlash
```python
from utils.logger_core import logger
import logging

logger.setLevel(logging.DEBUG)  # Batafsil loglar
logger.setLevel(logging.INFO)   # Asosiy ma'lumotlar
```

### Xato Boshqaruv
Yangi modul har qanday xatolikda to'xtamasdan, natijalarni qaytaradi:
```python
result = await scrape(CONFIG, BROWSER_CONFIG)

if result["status"] == "error":
    print(f"Xato: {result['error']}")
elif result["status"] == "failed":
    print(f"Muvaffaqiyatsiz: {result['reason']}")
```

## 📈 Performance Optimizatsiyasi

1. **Concurrency sozlash**: `scrape_concurrency` parametri
2. **Batch processing**: Katta ro'yxatlar uchun batch'lardan foydalanish
3. **aiohttp fallback**: Tez HTML yukash, kerak bo'lsa browser
4. **Memory management**: Context'larni to'g'ri yopish
5. **Checkpoint**: Uzoq jarayonlarda progress saqlash

## 🎉 Afzalliklari

### Eski Modulga Nisbatan:
- ✅ **To'liq statistika** va natija tracking
- ✅ **Professional code structure** va documentation
- ✅ **Advanced error handling** va retry mexanizmi
- ✅ **Modular architecture** - har bir qism alohida
- ✅ **Migration support** - eski kod bilan compatibility
- ✅ **Performance optimizations** - tezroq va samaraliroq
- ✅ **Batch processing** va checkpoint
- ✅ **Multiple site support** - bir vaqtda ko'p sayt
- ✅ **Comprehensive logging** va debugging tools

### Kelajakda Qo'shilishi Mumkin:
- 🔄 **Auto-retry** va exponential backoff
- 📊 **Real-time monitoring** dashboard
- 🔧 **Configuration validation** va suggestions
- 💾 **Database optimizations** va caching
- 🤖 **ML-based content detection** va filtering
- 📱 **Mobile responsiveness** testing