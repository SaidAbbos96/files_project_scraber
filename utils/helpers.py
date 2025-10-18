import json
import re
import html

from core.catigories import CATEGORY_MAP, CATEGORY_NAME_TO_ID, STANDARD_CATEGORIES


def clean_html_for_telegram(text: str) -> str:
    """
    HTML ni Telegram uchun xavfsiz formatga aylantirish
    
    Args:
        text: HTML yoki oddiy matn
        
    Returns:
        Telegram uchun xavfsiz matn
    """
    if not text:
        return ""
    
    # HTML entities decode qilish
    text = html.unescape(text)
    
    # Qo'llab-quvvatlanmaydigan HTML teglarni olib tashlash
    # Telegram faqat <b>, <i>, <u>, <s>, <a>, <code>, <pre> teglarini qo'llab-quvvatlaydi
    
    # Barcha HTML teglarni olib tashlash (xavfsiz variant)
    text = re.sub(r'<[^>]+>', '', text)
    
    # Ortiqcha bo'shliqlarni tozalash
    text = re.sub(r'\s+', ' ', text).strip()
    
    # ✅ HTML entities dan keyin tozalash - faqat oddiy matn qoldirish
    # Maxsus belgilarni oddiy belgilarga aylantirish (escape qilmaslik)
    text = text.replace('&amp;', '&').replace('&lt;', '<').replace('&gt;', '>').replace('&quot;', '"')
    
    return text


def sanitize_caption_data(data: dict) -> dict:
    """
    Caption data ni Telegram uchun xavfsiz qilish
    
    Args:
        data: Caption ma'lumotlari
        
    Returns:
        Tozalangan data
    """
    sanitized = {}
    
    for key, value in data.items():
        if isinstance(value, str):
            # String qiymatlarni tozalash
            sanitized[key] = clean_html_for_telegram(value)
        elif isinstance(value, list):
            # List ichidagi stringlarni tozalash
            sanitized[key] = [clean_html_for_telegram(str(item)) if isinstance(item, str) else item for item in value]
        else:
            # Boshqa turlarni o'zgartimasdan qoldirish
            sanitized[key] = value
    
    return sanitized


def format_file_size(size_bytes: int) -> str:
    """
    Fayl hajmini odam o'qiy oladigan formatga o'tkazish
    
    Args:
        size_bytes: Hajm bytes da
        
    Returns:
        Formatlangan string (masalan: "1.5 GB", "500 MB", "100 KB")
    """
    if not size_bytes or size_bytes == 0:
        return "0 B"
    
    # GB
    if size_bytes >= 1024 ** 3:
        size_gb = size_bytes / (1024 ** 3)
        return f"{size_gb:.2f} GB"
    
    # MB
    elif size_bytes >= 1024 ** 2:
        size_mb = size_bytes / (1024 ** 2)
        return f"{size_mb:.2f} MB"
    
    # KB
    elif size_bytes >= 1024:
        size_kb = size_bytes / 1024
        return f"{size_kb:.2f} KB"
    
    # Bytes
    else:
        return f"{size_bytes} B"


# --- Normalizatsiya funksiyasi ---
def normalize_category(raw: str) -> str:
    if not raw:
        return "other"

    # tozalash
    raw = raw.strip().lower()
    raw = re.sub(r"[^\w\s\-+]", "", raw)

    # mapping orqali tekshirish
    for key, keywords in STANDARD_CATEGORIES.items():
        for kw in keywords:
            if kw in raw:
                return key

    return "other"


def normalize_item_categories(item):
    """
    Item ichidagi kategoriyalarni normalize qiladi va list sifatida qaytaradi.
    """
    raw_cats = item.get("categories")
    if not raw_cats:
        return item

    # Kategoriyalar vergul orqali bo‘linadi
    cats = [c.strip() for c in str(raw_cats).split(",") if c.strip()]

    # Normalize qilish va takrorlarni olib tashlash
    mapped = list({normalize_category(c) for c in cats if normalize_category(c)})

    item["categories"] = ", ".join(mapped) if mapped else "other"
    return item


# --- JSON dan unikal kategoriyalarni yig‘ish ---
def extract_and_map_categories(json_path: str):
    with open(json_path, "r", encoding="utf-8") as f:
        items = json.load(f)

    mapped = set()

    for item in items:
        cats = item.get("categories")
        if not cats:
            continue
        for raw in cats.split(","):
            mapped.add(normalize_category(raw))

    return sorted(mapped)


def get_category_names(ids: list[int]) -> str:
    """
    Berilgan category_id larni nomlarga aylantiradi
    """
    names = [CATEGORY_MAP.get(cid, f"unknown({cid})") for cid in ids]
    return ", ".join(names)


def categories_to_ids(categories: list[str]) -> list[int]:
    """
    Category nomlarini ID ro‘yxatiga aylantiradi.
    Bir xil ID faqat bir marta chiqadi.
    Agar nom topilmasa, 1 (other) qo‘shiladi.
    """
    ids = set()
    for name in categories:
        cid = CATEGORY_NAME_TO_ID.get(name.strip().lower())
        if cid:
            ids.add(cid)
        else:
            ids.add(1)  # default -> other
    return list(ids)


def make_caption(data: dict) -> str:
    """
    Dict → caption string (Telegram uchun xavfsiz)
    Masalan:
    {
        "lang": "uz",
        "category_id": [29, 31],
        "title": "🧭 Romanti rasm (2023)",
        "desc": "Vaqt mashinasi orqali..."
    }
    """
    # Data ni tozalash
    clean_data = sanitize_caption_data(data)
    
    caption = []
    for key, value in clean_data.items():
        if isinstance(value, list):
            value = ", ".join(map(str, value))
        elif isinstance(value, (int, float)):
            value = str(value)
        elif not isinstance(value, str):
            value = str(value)
        
        # Bo'sh qiymatlarni o'tkazib yuborish
        if value and str(value).strip():
            caption.append(f"#{key}={value}")
    
    return "\n".join(caption)


def parse_page_selection(selection: str, total_pages: int):
    """
    selection: foydalanuvchi inputi, masalan "1,2,5,10,250" yoki "1-10,50,51" yoki "*"
    total_pages: umumiy sahifalar soni
    """
    if selection.strip() == "*":
        return list(range(1, total_pages + 1))

    pages = set()
    for part in selection.split(","):
        part = part.strip()
        if "-" in part:
            start, end = part.split("-")
            try:
                start, end = int(start), int(end)
                pages.update(range(start, end + 1))
            except ValueError:
                continue
        else:
            try:
                pages.add(int(part))
            except ValueError:
                continue

    # faqat mavjud sahifalarni qoldiramiz
    return sorted([p for p in pages if 1 <= p <= total_pages])
