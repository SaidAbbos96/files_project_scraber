# ⚙️ SEQUENTIAL MODE KONFIGURATSIYASI

## 📋 Hozirgi Sozlamalar

```python
# Bitta-bitta ishlash rejimi
"download_concurrency": 1      # Bir vaqtda bitta download
"upload_workers": 1            # Bir vaqtda bitta upload
"mode": "sequential"           # Ketma-ket ishlash

# Fayllarni avtomatik o'chirish
"clear_uploaded_files": True   # Upload'dan keyin o'chirish
"keep_files_on_disk": False    # Fayllarni saqlamaslik

# Disk monitoring
"disk_monitor_enabled": True   # Disk joy monitoringi yoqilgan
"min_free_space_gb": 5.0       # Minimal 5GB bo'sh joy kerak
"disk_check_interval": 60      # Har 1 daqiqada tekshirish
"cleanup_old_files": True      # Eski fayllarni avtomatik tozalash
"file_max_age_hours": 1        # 1 soatdan eski fayllarni o'chirish

# Notifications
"notification_quiet_mode": False  # Har bir fayl haqida xabar berish
```

---

## 🔄 Ishlash Jarayoni

### 1. Birinchi Fayl:
```
📥 Download → /downloads/film1.mp4
📤 Upload to Telegram
✅ Success
🗑️ Delete → /downloads/film1.mp4
```

### 2. Ikkinchi Fayl:
```
📥 Download → /downloads/film2.mp4
📤 Upload to Telegram
✅ Success
🗑️ Delete → /downloads/film2.mp4
```

### 3. Va hokazo...

---

## 💾 Disk Joy Monitoring

Agar disk joy kam bo'lsa (< 5GB):

```
⏸️ DISK JOY KAM!
🧹 Eski fayllarni tozalash...
⏳ 60 soniya kutish...
✅ Joy bo'ldi, davom etadi
```

---

## 📊 Afzalliklar

### ✅ Disk Joy Tejash
- Bir vaqtda faqat **bitta fayl** diskda
- Upload tugagach **avtomatik o'chiriladi**
- Eski fayllar **avtomatik tozalanadi**

### ✅ To'liq Nazorat
- Har bir fayl **ketma-ket** qayta ishlanadi
- Xatolarni **oson kuzatish**
- **Real-time** progress tracking

### ✅ Xavfsizlik
- Disk to'lib ketish **xavfi yo'q**
- Xatolarda **to'xtamaydi**, keyingisiga o'tadi
- **Diagnostika** har bir fayl uchun

---

## 🚀 Ishlatish

```bash
python -m main
# Rejim tanlang: 3 (Download + Upload)
# Sayt tanlang: 1 (yoki kerakli raqam)
```

---

## 📈 Jarayon Ko'rinishi

```
🚀 Sequential batch boshlandi: 50 ta fayl

📥 [1/50] Download: film1.mp4 (1.2 GB)
📤 [1/50] Upload: film1.mp4
✅ [1/50] Success
🗑️ [1/50] Deleted

📥 [2/50] Download: film2.mp4 (2.5 GB)
⏸️ DISK JOY KAM! Kutilmoqda...
🧹 Eski fayllar tozalandi: 3 ta, 5.2 GB
✅ Joy bo'ldi
📥 [2/50] Download davom etmoqda...
📤 [2/50] Upload: film2.mp4
✅ [2/50] Success
🗑️ [2/50] Deleted

...

📊 NATIJA:
   ✅ Muvaffaqiyatli: 48
   ❌ Muvaffaqiyatsiz: 2
   ⏱️ Jami vaqt: 2.5 soat
```

---

## ⚠️ Muhim Eslatmalar

1. **Disk Joy**: Kamida 5GB bo'sh joy bo'lishi kerak
2. **Internet**: Barqaror internet talab qilinadi
3. **Telegram API**: Rate limiting avtomatik boshqariladi
4. **Fayllar**: Upload tugagach avtomatik o'chiriladi
5. **Xatolar**: Xato bo'lsa keyingi faylga o'tadi

---

## 🎯 Optimal Sozlamalar

Bu sozlamalar **eng yaxshi**:
- ✅ Disk joy tejash
- ✅ Barqaror ishlash
- ✅ Xatolarni kamaytirish
- ✅ To'liq nazorat

**Tavsiya etiladi production uchun!** 🚀
