import json
from pathlib import Path
from utils.helpers import normalize_category


def clean_and_remap_categories(json_path: str, out_path: str):
    """JSON itemlarini tozalab yangi faylga yozadi"""
    with open(json_path, "r", encoding="utf-8") as f:
        items = json.load(f)

    all_cats = set()
    for item in items:
        cats = item.get("categories")
        mapped = set()
        if cats:
            for raw in cats.split(","):
                mapped.add(normalize_category(raw))
        if not mapped:
            mapped.add("other")

        item["categories"] = ", ".join(sorted(mapped))
        all_cats.update(mapped)

    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(items, f, ensure_ascii=False, indent=2)

    print(f"✅ {len(items)} item qayta saqlandi → {out_path}")
    print(f"📊 Topilgan kategoriyalar soni: {len(all_cats)}")
    for c in sorted(all_cats):
        print("-", c)


if __name__ == "__main__":
    inp = Path("../finish/asilmedia.json")
    out = Path("../finish/asilmedia_clean.json")
    clean_and_remap_categories(inp, out)
