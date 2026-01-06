import sys
from pathlib import Path
PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from core.FileDB import FileDB


def run():
    db = FileDB()
    cfg = "perf_test"

    last_id = None
    total = 0
    while True:
        batch = db.get_undownloaded_files_paginated(cfg, last_id, limit=50)
        if not batch:
            break
        total += len(batch)
        last_id = batch[-1]["id"]
        print(f"Fetched {len(batch)} items, last_id={last_id}")
    print("Total fetched:", total)


if __name__ == "__main__":
    run()
