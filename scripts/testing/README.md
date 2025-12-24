# 🧪 Testing Scripts

Bu papka loyihaning test va sinov fayllarini o'z ichiga oladi.

## 📋 Test fayllar ro'yxati

### `test_session_manager.py`
- **Maqsad**: Session Manager modulining to'liq testlari
- **Imkoniyatlar**: Session backup, restore, lock detection testlari
- **Foydalanish**: `python scripts/testing/test_session_manager.py`

### `minimal_session_test.py`
- **Maqsad**: Dependencies siz minimal session testlari
- **Imkoniyatlar**: Session va database holatini tekshirish
- **Foydalanish**: `python scripts/testing/minimal_session_test.py`

### `test_database_lock.py`
- **Maqsad**: Database lock holatini simulyatsiya qilish
- **Imkoniyatlar**: Lock yaratish va Session Manager testlari
- **Foydalanish**: `python scripts/testing/test_database_lock.py`

### `test_real_scenario.py`
- **Maqsad**: Real Telegram upload scenariosini test qilish
- **Imkoniyatlar**: Kengaytirilgan diagnostika va manual checks
- **Foydalanish**: `python scripts/testing/test_real_scenario.py`

### `test_session_lock.py`
- **Maqsad**: Session lock holatini simulyatsiya qilish
- **Imkoniyatlar**: Session lock yaratish va 30 soniya ushlab turish
- **Foydalanish**: `python scripts/testing/test_session_lock.py`

## 🚀 Testlarni ishga tushirish

```bash
# Minimal session test (tavsiya etiladi)
python scripts/testing/minimal_session_test.py

# Session manager to'liq test
python scripts/testing/test_session_manager.py

# Real scenario test
python scripts/testing/test_real_scenario.py

# Database lock simulatsiyasi
timeout 15 python scripts/testing/test_database_lock.py

# Session lock simulatsiyasi
timeout 35 python scripts/testing/test_session_lock.py
```

## 📊 Test natijalari

### Kutilayotgan natijalar:
- ✅ Session fayllar topiladi va normal ochiladi
- ✅ Database fayllar to'g'ri formatda
- ✅ Session Manager avtomatik tuzatish ishlaydi
- ✅ Lock detection to'g'ri ishlaydi

### Agar testlar muvaffaqiyatsiz bo'lsa:
1. Dependencies o'rnatilganligini tekshiring
2. Session fayllar mavjudligini tekshiring
3. Database fayllar buzilmaganligini tekshiring
4. Boshqa Python jarayonlar session ishlatmayotganligini tekshiring

## 🔧 Debugging

Test muammolarini hal qilish uchun:

```bash
# Session holatini tekshirish
./scripts/session_management/check_session_status.sh

# Session jarayonlarini to'xtatish
./scripts/session_management/kill_session_processes.sh

# Minimal test qayta ishga tushirish
python scripts/testing/minimal_session_test.py
```

## 📋 Eslatma

- Testlar development muhitida ishlatiladi
- Production serverda ehtiyotkorlik bilan foydalaning
- Ba'zi testlar timeout bilan cheklangan
- Lock simulatsiya testlari ehtiyotkorlik talab qiladi