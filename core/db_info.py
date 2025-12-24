from core.FileDB import FileDB
from utils.logger_core import logger


async def test_print_files(site_name):
    db = FileDB()
    files = db.get_files(site_name)

    for f in files:
        print(f["id"], f["title"], f["categories"],
              f["file_page"], f["uploaded"])


async def print_all_file_urls(site_name: str):
    db = FileDB()
    files = db.get_files(site_name)

    if not files:
        logger.error(f"❌ {site_name} uchun fayllar topilmadi")
        return

    total = len(files)
    idx = 0

    while idx < total:
        batch = files[idx:idx+100]
        for f in batch:
            file_size = f.get('file_size', 0)
            gb_size = file_size / (1024 ** 3) if file_size else 0
            # Categories database'da string sifatida saqlangan
            categories = f.get('categories', '') or 'other'
            uploaded = f.get('uploaded', 'Noma’lum')
            file_url = f.get('file_url', '❌ yo‘q')
            file_page = f.get('file_page', '❌ yo‘q')
            logger.info(
                f"ID: {f['id']:>5} | "
                f"Size: {gb_size:.2f} GB | "
                f"Title: {f['title'][:40]:<40} | "
                f"Categories: {categories:<30} | "
                f"Uploaded: {uploaded:<20} | "
                f"File Page: {file_page} | "
                f"File URL: {file_url}"
            )
        idx += 100
        if idx < total:
            input("Davom etish uchun Enter tugmasini bosing...")
