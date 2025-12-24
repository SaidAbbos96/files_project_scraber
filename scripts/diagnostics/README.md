# 🔍 Diagnostics Scripts

Bu papka tizim diagnostikasi va monitoring uchun scriptlarni o'z ichiga oladi.

## 📋 Fayllar ro'yxati

### `server_test.sh`
- **Maqsad**: Server connectivity va holatini tekshirish
- **Imkoniyatlar**: Network, services, va system health testlari
- **Foydalanish**: `./scripts/diagnostics/server_test.sh`

## 🚀 Foydalanish

```bash
# Server holatini tekshirish
./scripts/diagnostics/server_test.sh
```

## 📊 Diagnostika turlari

### Network Connectivity
- Internet aloqasini tekshirish
- DNS resolution testlari
- Telegram API connectivity

### System Health
- Disk maydoni tekshiruvi
- Memory va CPU foydalanish
- Process monitoring

### Service Status
- Database holatini tekshirish
- Session fayllar mavjudligi
- Log fayllar tahlili

## 🔧 Qo'shimcha diagnostika

Batafsil tizim diagnostikasi uchun:

```bash
# System diagnostics (main.py orqali)
python main.py
# Keyin [info] ni tanlang

# Session diagnostics
./scripts/session_management/check_session_status.sh

# Minimal test
python scripts/testing/minimal_session_test.py
```

## 📋 Eslatma

- Diagnostika scriptlari system health monitoring uchun
- Regular intervals da ishlatilishi tavsiya etiladi
- Production serverda monitoring setup qiling
- Log fayllarni muntazam tekshiring