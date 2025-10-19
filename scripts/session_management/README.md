# 🔧 Session Management Scripts

Bu papka Telegram session fayllar bilan ishlash uchun scriptlarni o'z ichiga oladi.

## 📋 Fayllar ro'yxati

### `session_manager.py`
- **Maqsad**: Asosiy session boshqaruv moduli
- **Imkoniyatlar**: Avtomatik session backup, restore, lock detection
- **Foydalanish**: `from scripts.session_management.session_manager import SessionManager`

### `kill_session_processes.sh`
- **Maqsad**: Session fayllarni ishlatayotgan Python jarayonlarini to'xtatish
- **Imkoniyatlar**: Avtomatik PID aniqlash va zo'rlik bilan to'xtatish
- **Foydalanish**: `./scripts/session_management/kill_session_processes.sh`

### `kill_session_no_sudo.sh`
- **Maqsad**: Sudo huquqlarisiz session jarayonlarini to'xtatish
- **Imkoniyatlar**: fuser va kill ishlatish
- **Foydalanish**: `./scripts/session_management/kill_session_no_sudo.sh`

### `check_session_status.sh`
- **Maqsad**: Session holatini tekshirish va tavsiyalar berish
- **Imkoniyatlar**: Lock detection, process analysis
- **Foydalanish**: `./scripts/session_management/check_session_status.sh`

### `delete_session_files.py`
- **Maqsad**: Session fayllarini xavfsiz o'chirish
- **Imkoniyatlar**: Backup yaratish, tasdiqlash
- **Foydalanish**: `python scripts/session_management/delete_session_files.py`

### `delete_session_server.sh`
- **Maqsad**: Server muhitida session fayllarini o'chirish
- **Imkoniyatlar**: Server-specific logic
- **Foydalanish**: `./scripts/session_management/delete_session_server.sh`

### `unlock_session.py`
- **Maqsad**: Session lock ni hal qilish
- **Imkoniyatlar**: Database lock hal qilish
- **Foydalanish**: `python scripts/session_management/unlock_session.py`

### `unlock_session_server.sh`
- **Maqsad**: Server muhitida session unlock
- **Imkoniyatlar**: Server processes management
- **Foydalanish**: `./scripts/session_management/unlock_session_server.sh`

### `fix_session_lock.py`
- **Maqsad**: Session lock muammolarini hal qilish
- **Imkoniyatlar**: Comprehensive session repair
- **Foydalanish**: `python scripts/session_management/fix_session_lock.py`

### `fix_session_server.sh`
- **Maqsad**: Server muhitida session tuzatish
- **Imkoniyatlar**: Server-side session management
- **Foydalanish**: `./scripts/session_management/fix_session_server.sh`

## 🚀 Tez ishlatish

```bash
# Session holatini tekshirish
./scripts/session_management/check_session_status.sh

# Session jarayonlarini to'xtatish
./scripts/session_management/kill_session_processes.sh

# Session fayllarini o'chirish
python scripts/session_management/delete_session_files.py

# Session lock ni hal qilish
python scripts/session_management/unlock_session.py
```

## 📁 Backup Directory

`session_backup/` papkasida avtomatik yaratilgan session backup fayllar saqlanadi.

## ⚠️ Muhim eslatmalar

1. Backup fayllar avtomatik yaratiladi
2. Ba'zi scriptlar sudo huquqlarini talab qiladi
3. Scriptlar loyiha root papkasidan ishga tushirilishi kerak
4. Session fayllarini o'chirishdan oldin backup yaratiladi