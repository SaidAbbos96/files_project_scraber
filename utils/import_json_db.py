import json
from pathlib import Path
from tqdm import tqdm

from core.FileDB import FileDB
from utils.helpers import normalize_item_categories
from utils.logger_core import logger
from utils.text import (
    normalize_description,
    normalize_item_fields,
    normalize_item_title,
)


def import_from_json(json_path: str, config_name: str):
    """JSON fayldan DB ga yozish"""
    db = FileDB()
    path = Path(json_path)

    if not path.exists():
        logger.error(f"❌ Fayl topilmadi: {json_path}")
        return

    with open(path, "r", encoding="utf-8") as f:
        items = json.load(f)

    if not isinstance(items, list):
        logger.error(f"❌ Noto‘g‘ri format: {json_path}")
        return

    logger.info(f"📥 {json_path} dan {len(items)} ta yozuv yuklanmoqda...")
    for item in tqdm(items, desc=f"📂 Import {config_name}", unit="file"):
        if not item.get("file_page"):
            logger.warning("⚠️ file_page yo‘q, tashlab ketildi")
            continue

        if db.file_exists(config_name, item["file_page"]):
            logger.info(f"♻️ Avval mavjud: {item['file_page']}")
            continue
        # Title ni tozalash
        item = normalize_item_title(item)

        # Country va actorsni translit qilish
        item = normalize_item_fields(
            item, keys_to_translate=["country", "actors", "categories"]
        )
        # Categories normalize
        item = normalize_item_categories(item)

        # Country va actorsni translit qilish
        item = normalize_description(item, lang=item.get("language", "uz"))
        db.insert_file(config_name, item)

    logger.info(
        f"✅ {json_path} dan {len(items)} ta yozuv DB ga qo‘shildi ({config_name})"
    )


if __name__ == "__main__":
    # Misol uchun bitta JSON faylni import qilish
    import_from_json("../finish/asilmedia.json", config_name="asilmedia")

    # Qo‘shimcha fayllar uchun ham ishlatishingiz mumkin
    import_from_json("../finish/asilmedia_multfilm.json",
                     config_name="asilmedia_multfilm")
