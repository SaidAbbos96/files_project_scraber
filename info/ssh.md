# 🔑 SSH kalit o‘rnatish va parolsiz ulanish qo‘llanmasi

Quyida **Windows (PowerShell)** orqali serverga parolsiz SSH ulanishni sozlash bo‘yicha to‘liq qo‘llanma keltirilgan.  

---

## 1️⃣ SSH kalit yaratish

Kompyuteringizda PowerShell oching va buyruqni yozing:

```powershell
ssh-keygen -t ed25519 -C "your_email@example.com"
```

- Fayl nomi so‘ralsa – **Enter** bosing (`id_ed25519` default).  
- Passphrase so‘ralsa – **Enter** (bo‘sh qoldirsangiz parolsiz bo‘ladi).  

👉 Natijada kalit fayllari yaratiladi:  
- `C:\Users\<USERNAME>\.ssh\id_ed25519` – private key (sir, hech kimga bermaysiz)  
- `C:\Users\<USERNAME>\.ssh\id_ed25519.pub` – public key (serverga qo‘shamiz)  

---

## 2️⃣ Public key’ni serverga qo‘shish

Windows’da `ssh-copy-id` mavjud emas, shuning uchun **ikki xil usul** ishlatamiz.  

---

### 🅰️ Variant 1: Qo‘l bilan qo‘shish

1. Public key matnini o‘qib oling:
   ```powershell
   type $env:USERPROFILE\.ssh\id_ed25519.pub
   ```
   👉 Natijada `ssh-ed25519 AAAAC3... user@pc` ko‘rinishida chiqadi.  

2. Serverga parol bilan kiring:
   ```powershell
   ssh root@194.146.38.204
   ```

3. Serverda quyidagilarni yozing:
   ```bash
   mkdir -p ~/.ssh
   nano ~/.ssh/authorized_keys
   ```
   📌 Olingan public key matnini bu faylga **paste** qiling.  
   Saqlash uchun: **CTRL+O, ENTER, CTRL+X**.  

4. To‘g‘ri ruxsatlarni qo‘ying:
   ```bash
   chmod 700 ~/.ssh
   chmod 600 ~/.ssh/authorized_keys
   ```

---

### 🅱️ Variant 2: `scp` orqali yuborish

1. PowerShell’dan public key faylini yuboring:
   ```powershell
   scp $env:USERPROFILE\.ssh\id_ed25519.pub root@194.146.38.204:/root/id_ed25519.pub
   ```

2. Serverga kiring:
   ```powershell
   ssh root@194.146.38.204
   ```

3. Kalitni `authorized_keys` fayliga qo‘shing:
   ```bash
   mkdir -p ~/.ssh
   cat ~/id_ed25519.pub >> ~/.ssh/authorized_keys
   chmod 700 ~/.ssh
   chmod 600 ~/.ssh/authorized_keys
   rm ~/id_ed25519.pub
   ```

---

## 3️⃣ Sinov

Endi lokal kompyuteringizdan:  
```powershell
ssh root@194.146.38.204
```

👉 Endi parol so‘ralmasdan serverga kirishingiz kerak! 🚀  

---

## 4️⃣ Ixtiyoriy: Qulay ulanish uchun `~/.ssh/config`

Agar tez-tez ishlatsangiz, config fayl yarating:

PowerShell’da:
```powershell
notepad $env:USERPROFILE\.ssh\config
```

Quyidagini yozing:
```
Host myserver
    HostName 194.146.38.204
    User root
    IdentityFile ~/.ssh/id_ed25519
```

Endi faqat:  
```powershell
ssh myserver
```
deb kirasiz. 🎉  

---

⚡ Shu qo‘llanma orqali Windows’da SSH kalitni sozlab, serverga parolsiz ulanishni o‘rnatishingiz mumkin.  
