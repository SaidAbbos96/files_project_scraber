# 🔧 Session Killer Guide - Python Jarayonlarini To'xtatish Qo'llanmasi

Bu qo'llanma `.session` fayllarni band qilib turgan Python jarayonlarini topish va zo'rlik bilan to'xtatish uchun mo'ljallangan.

## 📋 Maqsad

Telegram session fayllarini ishlatayotgan Python jarayonlarni aniqlash va ularni to'xtatish orqali "database is locked" xatolarini hal qilish.

## 🚀 Bosqichma-bosqich yo'riqnoma

### 1️⃣ Session fayllarni ishlatayotgan jarayonlarni topish

```bash
sudo lsof | grep .session
```

Bu buyruq barcha ochiq fayllarni ko'rsatadi va `.session` so'zi bor qatorlarni filtrlaydi.

### 2️⃣ Faqat Python jarayonlarini aniqlash

```bash
sudo lsof | grep .session | grep python
```

Yoki batafsil ma'lumot uchun:

```bash
sudo lsof | grep .session | grep python | awk '{print $1, $2, $9}'
```

Bu buyruq quyidagi formatda natija beradi:
```
python 16743 /path/to/session_+998200089990.session
python 16745 /path/to/session_+998200089990.session
python 16746 /path/to/session_+998200089990.session
```

### 3️⃣ PID raqamlarini ajratib olish

```bash
sudo lsof | grep .session | grep python | awk '{print $2}' | sort -u
```

Bu buyruq faqat PID raqamlarini ko'rsatadi:
```
16743
16745
16746
16751
```

### 4️⃣ Jarayonlarni zo'rlik bilan to'xtatish

Manual usul:
```bash
sudo kill -9 16743 16745 16746 16751
```

Yoki avtomatik usul:
```bash
sudo lsof | grep .session | grep python | awk '{print $2}' | sort -u | xargs sudo kill -9
```

## 🔄 Avtomatik Script

Barcha bosqichlarni avtomatik bajarish uchun quyidagi scriptni ishlating:

```bash
#!/bin/bash

echo "🔍 Session fayllarni ishlatayotgan Python jarayonlarini qidiryapman..."

# Session ishlatayotgan python jarayonlarni topish
PIDS=$(sudo lsof | grep .session | grep python | awk '{print $2}' | sort -u)

if [ -z "$PIDS" ]; then
    echo "✅ Hech qanday Python jarayoni session fayllarni ishlatmayapti"
    exit 0
fi

echo "🔒 Topilgan Python PID'lar:"
echo "$PIDS"

echo "💀 Jarayonlarni to'xtatyapman..."
echo "$PIDS" | xargs sudo kill -9

echo "✅ All session-locked processes have been killed successfully."
```

## 📝 Qo'shimcha Buyruqlar

### Session fayllarni ko'rish
```bash
find . -name "*.session" -type f
```

### Session fayllar hajmini tekshirish
```bash
find . -name "*.session" -type f -exec ls -lah {} \;
```

### Python jarayonlarini ko'rish
```bash
ps aux | grep python
```

### Session fayllarni ishlatayotgan barcha jarayonlar
```bash
sudo lsof | grep session
```

## ⚠️ Muhim Eslatmalar

1. **Ehtiyotkorlik**: `kill -9` buyrug'i jarayonni zo'rlik bilan to'xtatadi
2. **Ma'lumot yo'qotish**: Ochiq tranzaksiyalar yo'qolishi mumkin
3. **Backup**: Muhim ma'lumotlarni avval backup qiling
4. **Qayta ishga tushirish**: Session faylini o'chirib qayta yaratish kerak bo'lishi mumkin

## 🔧 Muammolarni bartaraf etish

### Agar jarayonlar to'xtamasa:

```bash
# SIGTERM dan keyin SIGKILL
sudo kill -15 <PID>
sleep 2
sudo kill -9 <PID>
```

### Session faylini qayta yaratish:

```bash
# Eski session ni backup qilish
cp telegramuploader/session_+998200089990.session session_backup_$(date +%Y%m%d_%H%M%S).session

# Session faylini o'chirish
rm telegramuploader/session_+998200089990.session

# Dasturni qayta ishga tushirib yangi session yaratish
python main.py
```

## 📊 Natijalarni tekshirish

Script tugagandan keyin quyidagi buyruqni bajaring:

```bash
sudo lsof | grep .session | grep python
```

Agar hech narsa chiqmasa, barcha jarayonlar muvaffaqiyatli to'xtatilgan.

## 🚨 Favqulodda holat

Agar hamma usullar ishlamasa:

```bash
# Kompyuterni qayta ishga tushirish
sudo reboot
```

---

**Muallif**: Session Manager  
**Sana**: $(date +%Y-%m-%d)  
**Versiya**: 1.0