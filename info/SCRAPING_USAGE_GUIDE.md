# 🚀 Yangi Scraping Modulini Main.py da Ishlatish Yo'riqnomasi

## 📋 Main.py da Mavjud Rejimlar

### ✅ **Asosiy Scraping Rejimlari:**

```
[1]  - Scrape (asosiy) - Oddiy scraping, sahifalar tanlash bilan
[1a] - Quick Scrape - Avtomatik scraping, input so'ramasdan  
[1b] - Advanced Scrape - To'liq statistika va boshqaruv bilan
```

---

## 🎯 **1. Asosiy Scraping (Rejim: 1)**

### Ishlatish:
```bash
python main.py
# Keyin:
# 1. Sayt tanlash (1, 2, 3, ...)
# 2. Rejim tanlash: 1
# 3. Sahifalar kiritish: 1-10 yoki *
```

### Natija:
```
📊 SCRAPING NATIJALARI:
   Status: success
   📈 Topilgan: 200
   ✅ Muvaffaqiyatli: 195  
   💾 DB ga qo'shildi: 195
   ⏭️ Tashlab ketildi: 30
   ⏱️ Vaqt: 180.5s
   🏃 Tezlik: 1.08 item/s
   📊 Muvaffaqiyat: 97.5%
```

---

## ⚡ **2. Quick Scraping (Rejim: 1a)**

### Ishlatish:
```bash
python main.py
# Keyin:
# 1. Sayt tanlash: 1
# 2. Rejim tanlash: 1a  
# 3. Sahifalar: 1-5 (yoki enter bosilsa *)
```

### Xususiyatlari:
- ✅ **Tez** - minimal input so'raydi
- ✅ **Avtomatik** - ko'p so'rov bermasdan ishlaydi
- ✅ **Oddiy** - yangi foydalanuvchilar uchun

---

## 🎛️ **3. Advanced Scraping (Rejim: 1b)**

### Ishlatish:
```bash  
python main.py
# Keyin:
# 1. Sayt tanlash: 1
# 2. Rejim tanlash: 1b
# 3. Sahifalar: 1-10
```

### Natija (batafsil):
```
📊 ADVANCED SCRAPING NATIJALARI:
   status: success
   total_found: 200
   successful: 195
   inserted: 195
   skipped: 30
   📈 Performance Stats:
      total_processed: 200
      successful: 195
      errors: 5
      success_rate: 97.5
      duration_seconds: 180.52
      items_per_second: 1.08
```

---

## 💻 **Kod Misollar**

### **Asosiy Kod:**
```python
# main.py dan
if mode == "1":
    if USING_NEW_SCRAPING:
        result = await scrape(CONFIG, BROWSER_CONFIG)
        # result - bu dict bo'lib, to'liq statistika
    else:
        await scrape(CONFIG, BROWSER_CONFIG)  # eski usul
```

### **Quick Scraping:**
```python
elif mode == "1a" and USING_NEW_SCRAPING:
    pages_selection = input("Sahifalar: ").strip() or "*"
    result = await quick_scrape(CONFIG, BROWSER_CONFIG, pages_selection)
```

### **Advanced Scraping:**
```python
elif mode == "1b" and USING_NEW_SCRAPING:
    orchestrator = ScrapingOrchestrator(CONFIG, BROWSER_CONFIG)
    result = await orchestrator.run_scraping_process()
```

---

## 🔧 **Custom Ishlatish (o'z kodingizda)**

### **1. Direct Import:**
```python
from scraping import scrape, ScrapingOrchestrator, quick_scrape
from core.config import APP_CONFIG, BROWSER_CONFIG
from core.site_configs import SITE_CONFIGS

# Config tayyorlash
CONFIG = {**APP_CONFIG, **SITE_CONFIGS['asilmedia']}
CONFIG["name"] = "asilmedia"

# Scraping
result = await scrape(CONFIG, BROWSER_CONFIG)
print(f"Status: {result['status']}")
print(f"Inserted: {result['inserted']} items")
```

### **2. Orchestrator Ishlatish:**
```python
from scraping import ScrapingOrchestrator

orchestrator = ScrapingOrchestrator(CONFIG, BROWSER_CONFIG)
result = await orchestrator.run_scraping_process()

# Custom post-processing
if result['status'] == 'success':
    print(f"✅ {result['inserted']} yangi fayl qo'shildi!")
```

### **3. Quick Mode:**
```python
from scraping import quick_scrape

# Sahifalar avtomatik tanlash
result = await quick_scrape(CONFIG, BROWSER_CONFIG, "1-5")
# yoki barcha sahifalar
result = await quick_scrape(CONFIG, BROWSER_CONFIG, "*")
```

---

## 📊 **Result Structure (Natija Tuzilishi)**

```python
result = {
    "status": "success",           # success/failed/cancelled/error
    "total_found": 200,            # Jami sahifalar
    "successful": 195,             # Muvaffaqiyatli olingan
    "inserted": 195,               # DB ga qo'shilgan
    "skipped": 30,                 # Tashlab ketilgan (DB da bor)
    "processed": 170,              # Qayta ishlangan
    "stats": {                     # Performance statistika
        "total_processed": 200,
        "successful": 195,
        "errors": 5,
        "success_rate": 97.5,
        "duration_seconds": 180.52,
        "items_per_second": 1.08
    }
}
```

---

## 🚀 **Ishga Tushirish:**

### **Terminal orqali:**
```bash
cd /home/aicoder/coding/films_project/files_scraber/scrabe_and_download
python main.py
```

### **Virtual Environment bilan:**
```bash
cd /home/aicoder/coding/films_project/files_scraber/scrabe_and_download  
/home/aicoder/coding/films_project/files_scraber/scrabe_and_download/venv/bin/python main.py
```

---

## 📝 **Foydali Maslahatlar:**

1. **Quick Scraping** - agar tez natija kerak bo'lsa
2. **Advanced Scraping** - agar batafsil statistika kerak bo'lsa  
3. **Asosiy Scraping** - standart ishlatish uchun
4. **Error Handling** - barcha rejimlar xatoliklar bilan ishlaydi
5. **DB Integration** - avtomatik ravishda DB ga saqlaydi
6. **Performance Monitoring** - real-time tezlik va statistika

**Sizning scraping modulingiz endi professional darajada va ishlatishga tayyor! 🎉**