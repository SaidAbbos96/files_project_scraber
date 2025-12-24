# 🛠️ Scripts Directory

Bu papka loyihaning yordamchi scriptlari va asboblarini o'z ichiga oladi.

## 📁 Papka tuzilmasi

### `session_management/`
Session fayllar bilan ishlash uchun scriptlar:
- `session_manager.py` - Asosiy session boshqaruv moduli
- `check_session_status.sh` - Session holatini tekshirish
- `delete_session_files.py` - Session fayllarini o'chirish
- `kill_session_processes.sh` - Session jarayonlarini to'xtatish
- `unlock_session.py` - Session lock ni hal qilish

### `testing/`
Test va sinov faylari:
- `test_session_manager.py` - Session manager testlari
- `minimal_session_test.py` - Minimal session testlari
- `test_database_lock.py` - Database lock testlari

### `diagnostics/`
Tizim diagnostikasi va monitoring:
- `server_test.sh` - Server connectivity testlari

### `git/` - Git bilan ishlash script'lari
- `git-auto.sh` - Avtomatik git commit va push

### `maintenance/` - Tizim maintenance script'lari  
- `download_files_db_from_server.sh` - Serverdan database yuklash
- `fix_system.sh` - Tizimni avtomatik tuzatish
- `test_video_attributes.sh` - Video attributes testlari
- `log_cleanup.sh` - Eski log fayllarni tozalash

## 🚀 Qo'llanish:

```bash
# Session management
./scripts/session_management/kill_session_processes.sh
./scripts/session_management/check_session_status.sh

# Testing
python scripts/testing/test_session_manager.py
python scripts/testing/minimal_session_test.py

# Git avtomatik commit/push
./scripts/git/git-auto.sh

# Tizimni tuzatish
./scripts/maintenance/fix_system.sh
```

## 📋 Eslatma

Har bir papkada o'z README fayli mavjud bo'lib, batafsil yo'riqnomalar beradi.
Barcha script'lar loyiha root papkasidan ishga tushirilishi kerak.