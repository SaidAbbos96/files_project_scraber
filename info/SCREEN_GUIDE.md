# 📘 screen qo‘llanmasi

## 🔧 1. screen o‘rnatish

Ubuntu/Debian serverlarda:

```bash
sudo apt update
sudo apt install screen -y
```

## 🔧 2. Yangi sessiya yaratish

```bash
screen -S scraper
```

`scraper` — sessiya nomi (xohlagancha berishingiz mumkin).

Bu yangi terminal oynasini ochadi va siz odatdagidek buyruqlarni yozishingiz mumkin.

## 🔧 3. Scraper dasturini ishga tushirish

```bash
source venv/bin/activate
python main.py
```

Endi scraper ishlay boshlaydi.

## 🔧 4. Sessiyadan chiqib ketish (dastur to‘xtamasdan)

`Ctrl + A` keyin `D`

👉 Endi siz SSH terminalni yopishingiz mumkin — scraper ishlashda davom etadi.

## 🔧 5. Sessiyaga qaytish

Serverga qaytib ulanib, mavjud sessiyalarni ko‘rish:

```bash
screen -ls
```

Misol:

```
There is a screen on:
    12345.scraper   (Detached)
```

Sessiyaga qaytish:

```bash
screen -r scraper
```

yoki ID bilan:

```bash
screen -r 12345
```

## 🔧 6. Sessiyani butunlay yopish

Agar scraper tugagan bo‘lsa yoki chiqishni istasangiz:

Sessiyaga kiring (`screen -r scraper`)

Ichida `exit` yozing yoki `Ctrl + D` bosing.

---

## ✅ Foydali komandalar

**Yangi sessiya yaratish:**

```bash
screen -S nomi
```

**Sessiyalar ro‘yxatini ko‘rish:**

```bash
screen -ls
```

**Sessiyaga qaytish:**

```bash
screen -r nomi
```

**Sessiyani butunlay o'chirish:**
```bash
screen -X -S 14086 quit
# yoki sessiya ichida
exit
```

---

## 🚨 Muammolar va Hal qilish yo'llari

### ❌ **1. SSH terminalni yopib qo'ydim, sessiya detach qilmadim**

**Belgilar:**
- SSH ulanish uzildi
- `screen -ls` da sessiya ko'rinmaydi yoki `(Dead)` holatida

**Hal qilish:**
```bash
# 1. Barcha screen sessiyalarini ko'rish
screen -ls

# 2. Agar (Dead) sessiyalar bo'lsa, ularni tozalash
screen -wipe

# 3. Yangi sessiya yaratish
screen -S scraper_yangi
```

### ❌ **2. Sessiya "Attached" holatida, lekin men ulana olmayapman**

**Xato:**
```
There is a screen on:
    12345.scraper   (Attached)
Cannot attach to a multi display session.
```

**Hal qilish:**
```bash
# Majburiy qayta ulanish
screen -d -r scraper

# yoki ID bilan
screen -d -r 12345
```

### ❌ **3. Screen jarayoni "zombi" holatida**

**Belgilar:**
- `screen -ls` ko'rsatadi lekin ulana olmaysiz
- Sessiya javob bermaydi

**Hal qilish:**
```bash
# 1. Screen jarayonini topish
ps aux | grep screen

# 2. Jarayonni to'xtatish
kill -9 [PID_RAQAMI]

# 3. Tozalash
screen -wipe

# 4. Yangi sessiya yaratish
screen -S scraper_yangi
```

### ❌ **4. Ko'p sessiyalar bir xil nom bilan**

**Xato:**
```
There are several suitable screens on:
    12345.scraper   (Detached)
    12346.scraper   (Detached)
```

**Hal qilish:**
```bash
# ID bilan aniq sessiyani tanlash
screen -r 12345

# yoki barchani ko'rish va kerakli sessiyani tanlash
screen -ls
screen -r 12345.scraper
```

### ❌ **5. "No screen session found" xatosi**

**Sabab:**
- Sessiya yaratilmagan yoki o'chirilgan
- Noto'g'ri nom kiritilgan

**Hal qilish:**
```bash
# 1. Mavjud sessiyalarni tekshirish
screen -ls

# 2. Agar bo'sh bo'lsa, yangi yaratish
screen -S scraper

# 3. Agar bor bo'lsa, to'g'ri nom bilan ulanish
screen -r [to'g'ri_nom]
```

### ❌ **6. Scraper dasturi to'xtab qolgan**

**Belgilar:**
- Sessiyaga ulanish mumkin lekin dastur ishlamaydi
- Terminal "qotib qolgan"

**Hal qilish:**
```bash
# 1. Sessiyaga ulanish
screen -r scraper

# 2. Dasturni to'xtatish
Ctrl + C

# 3. Qaytadan ishga tushirish
python main.py

# 4. Yoki yangi sessiya yaratish
# Ctrl + A, keyin D (detach)
# screen -S scraper_yangi
```

---

## 💡 **Qo'shimcha maslahatlar**

**Sessiya ichida yangi oyna ochish:**
```bash
Ctrl + A, keyin C
```

**Oynalar orasida o'tish:**
```bash
Ctrl + A, keyin raqam (0, 1, 2...)
```

**Sessiya ichida scrollback ko'rish:**
```bash
Ctrl + A, keyin [
# Keyin yuqoriga/pastga o'tish uchun ko'rsatkich tugmalarini ishlating
# Chiqish uchun ESC
```

**Majburiy qayta ulanish (agar attached bo'lsa):**
```bash
screen -d -r nomi
```

**Barcha "dead" sessiyalarni tozalash:**
```bash
screen -wipe
```

**Screen sessiya logini saqlash:**
```bash
# Sessiya yaratishda log fayl belgilash
screen -L -S scraper
# Log fayl: screenlog.0 da saqlanadi
```
