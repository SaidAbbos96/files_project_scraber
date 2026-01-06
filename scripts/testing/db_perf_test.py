import time
import sys
from pathlib import Path

# Ensure project root is on sys.path for imports
PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from core.FileDB import FileDB


def run():
    db = FileDB()
    config = "perf_test"
    item = {
        "file_page": "https://example.com/file/123",
        "title": "Perf Test Title",
        "categories": "test",
        "language": "uz",
        "description": "desc",
        "file_url": "https://cdn.example.com/file.mp4",
        "image": "https://cdn.example.com/img.jpg",
        "year": "2024",
        "country": "UZ",
        "actors": "",
        "local_path": None,
        "file_size": 12345678,
        "mime": "video/mp4",
        "telegram_type": "document",
        "uploaded": False,
    }

    # Single upsert perf
    start = time.time()
    last_id = None
    for i in range(50):
        last_id = db.insert_file(config, item)
    end = time.time()
    print("single_upsert_elapsed_ms:", round((end - start) * 1000, 2))

    exists_start = time.time()
    exists = db.file_exists(config, item["file_page"])
    exists_end = time.time()
    print("exists:", exists, "check_ms:", round((exists_end - exists_start) * 1000, 2))

    # Bulk upsert perf
    bulk_items = []
    for i in range(300):
        bulk_items.append({
            **item,
            "file_page": f"https://example.com/file/{i}",
            "title": f"Perf {i}",
        })

    bstart = time.time()
    total = db.bulk_upsert_files(config, bulk_items, batch_size=150)
    bend = time.time()
    print("bulk_upsert_total:", total, "bulk_elapsed_ms:", round((bend - bstart) * 1000, 2))


if __name__ == "__main__":
    run()
