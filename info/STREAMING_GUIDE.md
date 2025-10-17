# 🚀 Streaming Upload Mode

## 📖 Nima bu?

**Streaming Upload** - bu fayllarni **disk ga to'liq saqlamasdan**, to'g'ridan-to'g'ri Telegram ga yuklash usuli.

### 🎯 Afzalliklar

1. **💾 Disk joy tejash** - Fayllar faqat vaqtinchalik (temporary) papkada saqlanadi
2. **⚡ Tezroq ishlash** - Download va upload jarayonlari ketma-ket bajariladi
3. **🔄 Avtomatik tozalash** - Upload tugagach, temporary fayllar avtomatik o'chiriladi
4. **📊 Monitoring** - Har bir fayl uchun batafsil diagnostika

---

## ⚙️ Konfiguratsiya

`core/config.py` faylida quyidagi parametrlarni o'zgartiring:

```python
APP_CONFIG = {
    # ... boshqa parametrlar ...
    
    # --- Streaming Settings ---
    "use_streaming_upload": True,   # ✅ Streaming rejimini yoqish
    "keep_files_on_disk": False,    # ❌ Fayllarni saqlamaslik
}
```

### Parametrlar tushuntirishi:

| Parametr | Qiymat | Tavsif |
|----------|--------|--------|
| `use_streaming_upload` | `True` | Streaming rejimini yoqish (tavsiya etiladi) |
| `use_streaming_upload` | `False` | Klassik rejim (download → disk → upload) |
| `keep_files_on_disk` | `True` | Upload'dan keyin fayllarni saqlab qolish |
| `keep_files_on_disk` | `False` | Upload muvaffaqiyatli bo'lsa, faylni o'chirish (tavsiya etiladi) |

---

## 🔄 Ishlash jarayoni

### Streaming Mode (`use_streaming_upload=True`):

```
1. 📥 Faylni download qilish → Temporary papkaga
2. 📤 Telegramga yuklash → To'g'ridan-to'g'ri
3. ✅ Muvaffaqiyatli → Temporary faylni o'chirish
4. ❌ Xato → Temporary faylni o'chirish va retry
```

### Klassik Mode (`use_streaming_upload=False`):

```
1. 📥 Faylni download qilish → Downloads papkaga
2. 📤 Telegramga yuklash → Downloads dan
3. ✅ Muvaffaqiyatli → Fayl saqlanadi (agar keep_files_on_disk=True)
4. 🗑️ Faylni o'chirish → (agar clear_uploaded_files=True)
```

---

## 💡 Foydalanish

### 1. Scraping qilish

```bash
python -m main
# Rejim: 1 - Scraping
```

### 2. Streaming upload

```bash
python -m main
# Rejim: 3 - Download + Upload
```

Avtomatik ravishda streaming rejim ishlatiladi (agar `use_streaming_upload=True` bo'lsa)

---

## 📊 Diagnostika

Har bir sessiya tugagach, batafsil hisobot ko'rsatiladi:

```
==============================================================
📊 TELEGRAM UPLOAD DIAGNOSTIKA HISOBOTI
==============================================================
⏱️ Session davomiyligi: 5.2 daqiqa
📈 Jami urinishlar: 10
✅ Muvaffaqiyatli: 8
❌ Muvaffaqiyatsiz: 2
📊 Muvaffaqiyat darajasi: 80.0%
⏱️ O'rtacha upload vaqti: 45.3s

🔍 XATO TURLARI:
   ⏰ Rate limit: 1
   🚫 Flood limit: 0
   💔 File corruption: 0
   🔑 Auth errors: 0
   🔌 Connection errors: 1
   ❓ Unknown errors: 0

💡 TAVSIYALAR:
   🔄 Rate limit ko'p - upload tezligini pasaytiring
==============================================================
```

---

## 🗂️ Fayl tuzilishi

```
telegramuploader/
├── core/
│   ├── uploader.py              # Klassik upload
│   ├── downloader.py            # Klassik download  
│   └── stream_uploader.py       # 🆕 Streaming upload
├── workers/
│   ├── producer.py              # Klassik producer
│   ├── consumer.py              # Klassik consumer
│   └── streaming_producer.py   # 🆕 Streaming producer
├── utils/
│   └── diagnostics.py           # 🆕 Diagnostika sistеmasi
└── orchestrator.py              # Asosiy boshqaruvchi
```

---

## ⚠️ Muhim eslatmalar

1. **Temporary fayllar**: `/tmp/telegram_stream/` papkasida saqlanadi
2. **Disk joy**: Temporary papka uchun kamida 5GB joy bo'lishi kerak
3. **Rate limiting**: Telegram API cheklashlari mavjud, tez-tez xato bo'lsa `download_concurrency` ni kamaytiring
4. **Monitoring**: `telegram_diagnostics.json` faylida batafsil loglar saqlanadi

---

## 🐛 Troubleshooting

### Xato: "Temporary file not found"

**Sabab**: Disk yo'qi yoki ruxsat muammosi

**Yechim**:
```bash
# Temporary papkani tekshirish
ls -la /tmp/telegram_stream/

# Ruxsat berish
chmod 755 /tmp/telegram_stream/
```

### Xato: "Rate limit"

**Sabab**: Juda ko'p parallel upload

**Yechim**: `core/config.py` da `download_concurrency` ni kamaytiring:
```python
"download_concurrency": 2,  # 3 o'rniga 2
```

### Xato: "Upload failed"

**Sabab**: Telegram API xatolari

**Yechim**: Diagnostika hisobotini tekshiring va tavsiyalarga amal qiling

---

## 📈 Performance Tuning

### Optimal sozlamalar (production):

```python
APP_CONFIG = {
    "download_concurrency": 2,       # 2-3 optimal
    "upload_workers": 2,             # 2 optimal (Telegram API safe)
    "mode": "parallel",              # Parallel tezroq
    "use_streaming_upload": True,    # ✅ Yoqilgan
    "keep_files_on_disk": False,     # ❌ O'chirilgan (disk tejash)
    "sort_by_size": True,            # Kichikdan boshlash
}
```

### Test sozlamalar (debug):

```python
APP_CONFIG = {
    "download_concurrency": 1,       # Bitta fayl
    "upload_workers": 1,             # Bitta upload
    "mode": "sequential",            # Ketma-ket
    "use_streaming_upload": True,    # ✅ Yoqilgan
    "keep_files_on_disk": True,      # ✅ Fayllarni saqlab qolish
    "debug": True,                   # Debug rejim
}
```

---

## 🎓 Qo'shimcha ma'lumot

- Streaming rejim **HTTP download** va **Telegram upload** ni birlashtiradi
- Fayllar `aiohttp` orqali chunk bo'lib yuklanadi (1MB chunks)
- Upload jarayoni `tqdm` bilan visualizatsiya qilinadi
- Xatolar avtomatik kategoriyalashtiriladi va loglanadi

---

## 📞 Qo'llab-quvvatlash

Savollar yoki muammolar bo'lsa:
1. `telegram_diagnostics.json` faylini tekshiring
2. Logger output'ni o'qing
3. Diagnostika hisobotidagi tavsiyalarga amal qiling

**Muvaffaqiyatli yuklashlar! 🚀**
