# Async Movie Web Scraper & Downloader

## Overview

This project is an **asynchronous web scraper and downloader** designed for efficiently collecting and downloading movie metadata and files from various websites. It leverages **Playwright** for browser automation, **aiohttp** for high-performance async HTTP requests, and **tqdm** for progress visualization. Key features include:

- **Parallel scraping** with configurable concurrency for speed and efficiency
- **Flexible configuration system** supporting multiple sites via `config.py`
- **Human-like scraping** with random delays to avoid detection
- **Structured JSON database** for storing scraped metadata
- **Asynchronous file downloads** for fast, reliable bulk downloading

---

## Installation

### Windows

1. **Install Python 3.10+**

   - Download from [python.org](https://www.python.org/downloads/)
   - Ensure you check "Add Python to PATH" during installation

2. **Create and activate a virtual environment:**

   ```powershell
   python -m venv venv
   .\venv\Scripts\Activate.ps1
   ```

3. **Install dependencies:**

   ```powershell
   pip install -r requirements.txt
   playwright install
   ```

4. **Run the scraper:**
   ```powershell
   python main.py
   ```

### Ubuntu Server

1. **Install Python va kerakli paketlar:**

   ```bash
   sudo apt update
   sudo apt install python3 python3-venv python3-pip screen -y
   ```

2. **Virtual environment yaratish va faollashtirish:**

   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Kerakli kutubxonalarni o'rnatish:**

   ```bash
   pip install -r requirements.txt
   playwright install
   ```

4. **Screen sessiyasini yaratish va scraper'ni ishga tushurish:**

   ```bash
   screen -S scraper
   source venv/bin/activate
   python3 main.py
   ```

5. **Screen sessiyasidan chiqib, fonda qoldirish:**

   - Klaviaturada `Ctrl+A` keyin `D` ni bosing (avval Ctrl va A, so'ng D)

6. **Screen sessiyasiga qaytish:**

   ```bash
   screen -r scraper
   ```

---

## Usage

1. **Start the program:**

   ```bash
   python main.py
   ```

2. **Select a configuration:**

   - The program will prompt you to choose a site config (from those defined in `config.py`).

3. **Choose a mode:**

   - **Scrape**: Crawls the site, collects movie metadata (title, categories, description, file links, images), and saves results to a JSON file (e.g., `asilmedia/asilmedia.json`).
   - **Download**: Reads the JSON file and downloads all associated files (videos, images) asynchronously into the `downloads/` directory.

4. **Example Console Flow:**

   ```
   $ python main.py
   Select site config: [asilmedia, ...]
   Select mode: [scrape, download]
   ...
   ```

5. **Results:**
   - **Scraped data** is saved as JSON in a subfolder named after the config.
   - **Downloaded files** are saved in the `downloads/` directory, organized by config and movie.

---

## Configuration

All site-specific settings are managed in `config.py` via the `CONFIGS` dictionary. Each config defines how to scrape a particular site.

**Important keys:**

- `base_url`: The starting URL for scraping
- `pagination_selector`: CSS selector for pagination links
- `card_selector`: CSS selector for movie cards on listing pages
- `fields`: Dict mapping metadata fields to their selectors or extraction logic
- `scrape_concurrency`: Number of browser pages to use in parallel
- `concurrency`: Number of concurrent downloads
- `sleep_min`, `sleep_max`: Min/max random delay (in seconds) between requests for human-like behavior

**Example config snippet:**

```python
CONFIGS = {
    "asilmedia": {
        "base_url": "https://example.com/movies",
        "pagination_selector": ".pagination a",
        "card_selector": ".movie-card",
        "fields": {
            "title": ".title",
            "categories": ".categories",
            "description": ".desc",
            "file_links": ".download-link",
            "images": ".poster img",
        },
        "scrape_concurrency": 4,
        "concurrency": 6,
        "sleep_min": 2,
        "sleep_max": 5,
    },
    # ... more configs ...
}
```

---

## Logging

The project uses Python’s built-in logging system. Logs are written both to the console and to `scraper.log` in the project root. Log levels include:

- **INFO**: General progress and status updates
- **WARNING**: Recoverable issues (e.g., missing fields)
- **ERROR**: Critical failures (e.g., network errors, crashes)

---

## Notes

---

## Projectni ZIP qilib serverga yuborish va ochish

### 1. Loyiha papkasini ZIP arxivga o'rash (masalan, Windows yoki Ubuntu'da):

#### Windows PowerShell:

```powershell
Compress-Archive -Path * -DestinationPath project.zip
```

#### Ubuntu/Linux:

```bash
zip -r project.zip .
```

### 2. ZIP faylni serverga yuborish (masalan, scp yordamida):

```bash
scp project.zip user@server_ip:/home/user/
```

### 3. Serverda ZIP arxivni ochish:

```bash
unzip project.zip
```

### 4. Fayllarni bevosita (ZIPsiz) ko'chirish uchun:

```bash
scp -r * user@server_ip:/home/user/project_folder/
```

scp scraper.zip root@194.146.38.204:/root/
scp root@194.146.38.204:/root/scraper.zip /local/path/
scp root@194.146.38.204:/root/scraper/asilmedia/asilmedia.json "C:\Users\GEEK SHOP\Downloads\asilmedia.json"

**Eslatma:**

- `scp` ishlatishda serverda kerakli papka mavjud bo'lishi yoki uni oldindan yaratib qo'yish kerak.
- ZIP arxivlashda `venv` yoki `__pycache__` kabi keraksiz papkalarni arxivga qo'shmaslik tavsiya etiladi.

- **Resource requirements:**
  - For smooth operation, a VPS with **2–4 GB RAM** is recommended. Disk space depends on the number and size of files downloaded.
- **Long-running scrapes:**
  - On Ubuntu, use `screen` or `tmux` to keep the scraper running after disconnecting from SSH:
    ```bash
    sudo apt install screen
    screen
    # or
    sudo apt install tmux
    tmux
    ```
- **Playwright browsers:**
  - The first run of `playwright install` will download browser binaries (Chromium, Firefox, WebKit).

---

## License

This project is provided as-is for educational and personal use. Please respect the terms of service of target websites.

sudo apt autoremove
sudo apt clean

1️⃣ ZIP qilib yuborish
🔧 Lokal kompyuterda

Loyihani zip qilasiz:

zip -r scraper_project.zip scraper_project/

(agar Windows bo‘lsa: papkani o‘ng tugma → Send to → Compressed (zip))

ZIP faylni serverga yuborasiz:

scp scraper_project.zip root@194.146.38.204:/root/

scp ishlashi uchun sizda OpenSSH o‘rnatilgan bo‘lishi kerak (Windows 10/11’da default bor).

root — bu foydalanuvchi, 194.146.38.204 esa server IP.

🔧 Serverda
unzip scraper_project.zip -d scraper_project
cd scraper_project

2️⃣ Fayllarni to‘g‘ridan-to‘g‘ri yuborish (SCP orqali)

Agar zip qilishni xohlamasangiz, butun papkani yuborishingiz mumkin:

scp -r scraper_project/ root@194.146.38.204:/root/scraper_project
### 3️⃣ Remote serverdan fayllarni lokal kompyuterga yuklab olish (SCP orqali)

Agar sizga serverdan fayl yoki papkani o‘z kompyuteringizga ko‘chirib olish kerak bo‘lsa, quyidagi buyruqlardan foydalaning:

#### Faylni yuklab olish:
```bash
scp user@server_ip:/path/to/remote/file /path/to/local/destination/
```
**Misol:**
```bash
scp root@194.146.38.204:/root/scraper_project/asilmedia/asilmedia.json ~/Downloads/
```

#### Papkani butunlay yuklab olish:
```bash
scp -r user@server_ip:/path/to/remote/folder /path/to/local/destination/
```
**Misol:**
```bash
scp -r root@194.146.38.204:/root/scraper_project ~/Downloads/
```

**Eslatma:**  
- `user` — serverdagi foydalanuvchi nomi (ko‘pincha `root`).
- `server_ip` — server IP manzili.
- SCP ishlashi uchun lokal kompyuteringizda OpenSSH o‘rnatilgan bo‘lishi kerak.
- Windows’da PowerShell yoki Git Bash orqali ham ushbu buyruqlarni ishlatishingiz mumkin.
