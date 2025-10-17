import re

from utils.translator import cyrillic_to_latin


def clean_title(text: str) -> str:
    """
    Kino nomidan keraksiz qismlarni olib tashlaydi:
    - Uzbek tilida / O'zbekcha tarjima kino / Full HD / tas-ix / skachat
    - Premyera
    - Jangari kino
    - Qo'shimcha qavslar va qavs ichidagi "O'zbek tilida", "Tarjima kino"
    - Yillar (2000–2099)
    """
    if not text:
        return ""

    remove_patterns = [
        # (O'zbek tilida), O`zbek tilida
        r"\(?\s*O[`']?zbek(cha)?\s*tilida\s*\)?",
        r"\(?\s*Tarjima\s*kino\s*\)?",  # (Tarjima kino)
        # "Uzbek tilida ..." va oxirigacha
        r"Uzbek\s*tilida.*?(skachat|HD|tas-ix)?",
        r"O[`']?zbek(cha)?\s*tarjima\s*kino.*?(skachat|HD|tas-ix)?",
        r"Premyera",  # Premyera
        r"Jangari\s*kino",  # Jangari kino
        r"Смотреть\s*Tas-ix",  # Ruscha bo‘lak
        r"Full\s*HD",  # Full HD
        r"tas-ix",  # tas-ix
        r"skachat",  # skachat
        r"\(\s*\)",  # bo‘sh qavslar ()
        r"\[\s*\]",  # bo‘sh qavslar []
        r"\b(19|20)\d{2}\b",  # Yillar (1900–2099)
        r"\bHD\b",  # HD so'zi
        r"O['`]?zbekchaHD",  # O'zbekchaHD
        r"O['`]?zbek\s*tarjima",  # O'zbek tarjima
        r"Turk\s*kinosi",  # Turk kinosi
        r"Hind\s*kino",  # Hind kino
        r"-\s*qismlar!?+",  # -qismlar!!!
        r"[!]{2,}",  # !!! belgilar
        r"\b\d+-\d+-\d+\b",  # masalan: 1-2-3
        r"\b\d+(?:-\d+)+\b",  # masalan: 1-2 yoki 1-2-3
        r"\b\d+(?:,\d+)+\b",  # masalan: 1,2 yoki 1,2,3
        r"\b\d+\s*qism(lar)?\b",  # "1 qism", "2-qism", "3 qismlar"
    ]

    clean = text
    for pattern in remove_patterns:
        clean = re.sub(pattern, "", clean, flags=re.IGNORECASE)

    # Ortiqcha bo‘sh joy va qavslarni tozalash
    clean = re.sub(r"[\[\]\(\)]", "", clean)  # qolgan qavslarni olib tashlash
    clean = re.sub(r"\s{2,}", " ", clean)  # ortiqcha bo‘sh joylar
    clean = clean.strip(" ,.-")

    return clean


def normalize_item_title(item: dict) -> dict:
    """
    Item ichidagi title ni clean_title orqali tozalaydi
    """
    if "title" in item and item["title"]:
        item["title"] = clean_title(item["title"])
    return item


def normalize_item_fields(item: dict, keys_to_translate: list[str]) -> dict:
    """
    Item ichidagi ma'lumotlarni normalizatsiya qiladi.
    - Agar language None bo‘lsa → 'uz'
    - Agar language == 'uz' bo‘lsa → `keys_to_translate` dagi ustunlarni
      `cyrillic_to_latin` orqali o‘tkazadi.
    """
    if not item:
        return item

    lang = item.get("language")
    if not lang:
        item["language"] = "uz"
        lang = "uz"

    if lang == "uz":
        for key in keys_to_translate:
            if key in item and isinstance(item[key], str) and item[key]:
                if key == "country":
                    # Country uchun vergul bilan ajratilgan bo‘lishi mumkin
                    countries = [c.strip()
                                 for c in item[key].split(",") if c.strip()]
                    item[key] = ", ".join(
                        cyrillic_to_latin(c) for c in countries
                    ).upper()
                else:
                    item[key] = cyrillic_to_latin(item[key])

    return item


def normalize_description(item: dict, lang: str = "uz") -> dict:
    """
    Itemdagi description maydonini lang flagga qarab tozalaydi.
    - Agar lang="uz" bo‘lsa → faqat uzbekcha qismi qoldiriladi
    - Agar lang="ru" bo‘lsa → faqat ruscha qismi qoldiriladi
    """

    desc = item.get("description")
    if not desc or not isinstance(desc, str):
        return item

    # Matnni \n orqali bo‘lamiz
    parts = [p.strip() for p in desc.split("\n") if p.strip()]

    if len(parts) == 1:
        # Bitta til bo‘lsa hech nima qilmaymiz
        item["description"] = parts[0]
        return item

    # Tilni aniqlash: rus tilida asosan кириллица mavjud
    def is_russian(text: str) -> bool:
        return bool(re.search(r"[А-Яа-яЁё]", text))

    uz_parts = [p for p in parts if not is_russian(p)]
    ru_parts = [p for p in parts if is_russian(p)]

    if lang == "uz" and uz_parts:
        item["description"] = " ".join(uz_parts).strip()
    elif lang == "ru" and ru_parts:
        item["description"] = " ".join(ru_parts).strip()
    else:
        # Agar kerakli til topilmasa → butun matnni qaytaramiz
        item["description"] = " ".join(parts).strip()

    return item
