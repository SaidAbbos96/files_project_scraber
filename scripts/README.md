# Scripts Directory

Bu papkada loyihaning turli shell script'lari joylashgan.

## 📁 Papka tuzilishi:

### `git/` - Git bilan ishlash script'lari
- `git-auto.sh` - Avtomatik git commit va push

### `maintenance/` - Tizim maintenance script'lari  
- `download_files_db_from_server.sh` - Serverdan database yuklash
- `fix_system.sh` - Tizimni avtomatik tuzatish
- `test_video_attributes.sh` - Video attributes testlari
- `log_cleanup.sh` - Eski log fayllarni tozalash

## 🚀 Qo'llanish:

```bash
# Git avtomatik commit/push
./scripts/git/git-auto.sh

# Tizimni tuzatish
./scripts/maintenance/fix_system.sh

# Database yuklash
./scripts/maintenance/download_files_db_from_server.sh

# Video testlari
./scripts/maintenance/test_video_attributes.sh

# Log tozalash
./scripts/maintenance/log_cleanup.sh
```

## ⚠️ Eslatma:
Barcha script'lar loyiha root papkasidan ishga tushirilishi kerak.