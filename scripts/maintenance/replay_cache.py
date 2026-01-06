import sys
from pathlib import Path
import json

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from core.FileDB import FileDB
from core.config import APP_CONFIG


def replay(cache_path: Path, config_name: str, batch_size: int = 300):
    db = FileDB()
    if not cache_path.exists():
        print("No cache file found:", cache_path)
        return
    lines = cache_path.read_text(encoding="utf-8").splitlines()
    items = []
    for line in lines:
        try:
            items.append(json.loads(line))
        except Exception:
            continue
    if not items:
        print("Cache file empty:", cache_path)
        return
    total = db.bulk_upsert_files(config_name, items, batch_size=batch_size)
    # truncate cache after success
    cache_path.write_text("", encoding="utf-8")
    print(f"Replayed {total} items from cache and truncated {cache_path}")


if __name__ == "__main__":
    cfg_name = sys.argv[1] if len(sys.argv) > 1 else "unknown"
    cache = Path(APP_CONFIG.get("db_cache_path", "logs/db_cache.jsonl"))
    replay(cache, cfg_name)
