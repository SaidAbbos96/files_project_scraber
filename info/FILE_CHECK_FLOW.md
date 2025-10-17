# 📁 Fayl Mavjudligini Tekshirish Flow

## 🔍 Qayerda va Qanday Tekshiriladi

### 1️⃣ **Producer.py - process_file() - 73-qator**
```python
# workers/producer.py:73
output_path = os.path.join(config["download_dir"], filename)

# Fayl mavjudligini va hajmini tekshirish
if os.path.exists(output_path):  # ← ASOSIY TEKSHIRISH
    is_valid, reason = self.downloader.check_file_integrity(output_path, url_size)
    
    if is_valid:
        # Mavjud faylni ishlatamiz
        size = os.path.getsize(output_path)
        file_needs_download = False
        logger.info(f"♻️ Fayl mavjud va to'liq: {filename}")
    else:
        # Faylni qayta yuklaymiz
        logger.warning(f"⚠️ {reason}: {filename}. Qayta yuklanadi.")
        os.remove(output_path)  # Noto'g'ri faylni o'chirish
        file_needs_download = True
```

### 2️⃣ **Downloader.py - check_file_integrity() - 128-qator**
```python
# core/downloader.py:128
def check_file_integrity(self, file_path: str, expected_size: int, tolerance_mb: int = 5):
    # 1. Fayl mavjudligini tekshirish
    if not os.path.exists(file_path):
        return False, "Fayl mavjud emas"
    
    # 2. Local fayl hajmini olish
    local_size = os.path.getsize(file_path)
    
    # 3. Server hajmi bilan solishtirish
    if expected_size <= 0:
        return True, "Server hajmi noma'lum, mavjud faylni ishlatamiz"
    
    # 4. Hajm farqini tekshirish (5MB tolerance)
    size_diff = abs(local_size - expected_size)
    tolerance_bytes = tolerance_mb * 1024 * 1024
    
    if size_diff <= tolerance_bytes:
        return True, f"Hajm mos keladi (farq: {size_diff/(1024**2):.1f}MB)"
    else:
        return False, f"Hajm farqi katta: {size_diff/(1024**2):.1f}MB"
```

## 🚦 Qaror Qabul Qilish Logic

### ✅ **Fayl Ishlatiladi (file_needs_download = False):**
- `os.path.exists(output_path) == True`
- `check_file_integrity() == (True, reason)`
- Hajm farqi 5MB dan kam
- Log: `♻️ Fayl mavjud va to'liq`

### 🔄 **Fayl Qayta Yuklanadi (file_needs_download = True):**
- `os.path.exists(output_path) == False` YOKI
- `check_file_integrity() == (False, reason)`
- Hajm farqi 5MB dan ko'p
- Log: `⚠️ Hajm farqi katta: X MB. Qayta yuklanadi.`
- Action: `os.remove(output_path)` - noto'g'ri faylni o'chirish

## 📊 Real Misollar

### Scenario 1: Fayl yo'q
```
os.path.exists("/downloads/film.mp4") → False
↓
file_needs_download = True (download qiladi)
```

### Scenario 2: Fayl bor, hajm mos
```
os.path.exists("/downloads/film.mp4") → True
local_size: 1.5GB, server_size: 1.51GB (farq: 10MB)
↓ 
check_file_integrity() → (False, "Hajm farqi katta: 10MB")
↓
os.remove() + file_needs_download = True (qayta download)
```

### Scenario 3: Fayl bor, hajm mos
```
os.path.exists("/downloads/film.mp4") → True  
local_size: 1.5GB, server_size: 1.502GB (farq: 2MB)
↓
check_file_integrity() → (True, "Hajm mos keladi")
↓
file_needs_download = False (mavjud faylni ishlatadi)
```

## ⚙️ Sozlamalar

### Tolerance Settings:
- **Default tolerance**: 5MB
- **Location**: `downloader.check_file_integrity(tolerance_mb=5)`
- **Customizable**: Funksiya parameter orqali o'zgartirish mumkin

### Download Directory:
- **Config**: `config["download_dir"]` (default: "../downloads")
- **Full path**: `os.path.join(config["download_dir"], filename)`

---

**Xulosa**: Fayl tekshirish `producer.py:73` da `os.path.exists()` bilan boshlanadi, keyin `downloader.py:128` da hajm tekshiriladi.