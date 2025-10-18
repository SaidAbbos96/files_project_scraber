# Upload Only Mode - Foydalanish Qo'llanmasi

## 📤 Upload Only Mode Nima?

Upload Only mode - bu downloads papkasida mavjud video fayllarni Telegramga yuklash uchun maxsus rejim. Bu rejim yangi fayllarni internetdan yuklab olmaydi, faqat disk'da mavjud fayllarni Telegramga yuboradi.

## 🎯 Qachon Ishlatish?

- ✅ Downloads papkasida video fayllar bor va ularni Telegramga yuklash kerak
- ✅ Internet bilan bog'lanish yomon lekin Telegram yuklash ishlaydi
- ✅ Disk joy kam, yangi yuklab olmaslik kerak
- ✅ Faqat mavjud fayllarni qayta ishlash kerak

## 🚀 Qanday Ishlatish?

### 1. Asosiy menyu
```
📋 Mavjud configlar:
[1] asilmedia
[2] asilmedia_multfilm
[3] daxshat_net_tarjima
[4] ruhub_me
```

### 2. Config tanlash
Kerakli config raqamini kiriting (masalan: `1`)

### 3. Rejim tanlash
```
🎮 Mavjud rejimlar:
[1] Scrape - yangi fayllarni topish
[2] Download - fayllarni yuklash  
[3] Download + Upload - yuklash va Telegramga yuborish
[4] Upload Only - faqat Telegramga yuborish  👈 SHU REJIMNI TANLANG
```

`4` ni kiriting

## 🔍 Nima Sodir Bo'ladi?

### 1. Fayl Tekshirish
```
📁 Downloads papkasidagi mavjud fayllarni tekshirish...
📁 X ta video fayl topildi downloads papkasida
```

### 2. Database Bilan Solishtirish
```
📤 X ta fayl Telegramga yuklanadi
```
- Faqat database da mavjud va hali Telegramga yuklanmagan fayllar tanlanadi

### 3. Yuklash Jarayoni
```
📤 Yuklanmoqda: fayl_nomi.mp4
✅ Yuklandi: fayl_nomi.mp4
🗑️ O'chirildi: fayl_nomi.mp4  (agar CLEAR_UPLOADED_FILES=true bo'lsa)
```

### 4. Yakuniy Hisobot
```
✅ Upload Only jarayoni tugadi!
📊 Jami: 10 ta fayl
✅ Yuklandi: 8 ta fayl  
❌ Xato: 2 ta fayl
🎉 8 ta fayl muvaffaqiyatli Telegramga yuklandi!
```

## ⚙️ Sozlamalar

### Video Format'lar
Quyidagi formatlar qo'llab-quvvatlanadi:
- `.mp4` - asosiy format
- `.mkv` - yuqori sifat
- `.avi` - eski format
- `.mov` - Apple format
- `.wmv` - Windows format
- `.flv` - Flash format
- `.webm` - Web format

### Fayl Hajmi Tartibi
`.env` faylida `SORT_BY_SIZE=true` qo'ysangiz, kichik fayllar birinchi yuklanadi.

### Avtomatik O'chirish
`.env` faylida `CLEAR_UPLOADED_FILES=true` bo'lsa, yuklangan fayllar avtomatik o'chiriladi.

## 🛡️ Xavfsizlik

### Fayl Tekshirish
- Faqat to'liq yuklangan fayllar ishlatiladi
- Buzuq video fayllar e'tiborga olinmaydi
- Database bilan solishtirish orqali faqat kerakli fayllar tanlanadi

### Xato Ishlash
- Har bir fayl uchun alohida xato qayd etiladi
- Bitta fayl xato bo'lsa, qolgan fayllar davom etadi
- Telegram server bilan bog'lanish xatosi bo'lsa, qayta urinish

## 📊 Foydali Ma'lumotlar

### Statistika Koʻrish
Upload'dan oldin statistikani ko'ring:
```
📊 FAYLLAR STATISTIKASI
📋 Jami fayllar: 100
⬇️ Yuklangan: 50
⬆️ Telegramga yuklangan: 30
📤 Upload qilinmagan: 20  👈 Shular yuklanadi
```

### Log Fayllari
Barcha amallar `logs/` papkasida saqlanadi:
- Upload muvaffaqiyatlari
- Xato hodisalar  
- Vaqt statistikasi

## 🔧 Muammolarni Hal Qilish

### "Video fayllar topilmadi"
- Downloads papkasini tekshiring
- Fayl formatlarini tekshiring
- To'g'ri config tanlanganini tasdiqlang

### "Database bilan bog'lanish xatosi"
- SQLite fayli buzulmagan ekanini tekshiring
- `[clear-db]` rejimi bilan database'ni tiklang

### "Telegram yuklash xatosi"
- Internet bog'lanishini tekshiring
- Telegram bot tokenini tekshiring
- Fayl hajmi cheklovlarini tekshiring (2GB limit)

## 💡 Maslahatlar

1. **Disk Joy**: Upload Only rejimi disk joy tejaydi
2. **Tezlik**: Kichik fayllardan boshlash tezroq natija beradi  
3. **Xavfsizlik**: Muhim fayllarni backup qiling
4. **Monitoring**: Log fayllarini muntazam tekshiring

---

✅ **Upload Only mode** - mavjud fayllarni tez va xavfsiz Telegramga yuklash uchun eng yaxshi yechim!