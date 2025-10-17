from UzTransliterator import UzTransliterator
# pip install UzTransliterator
# Transliterator obyektini yaratamiz
_trans = UzTransliterator.UzTransliterator()

def cyrillic_to_latin(text: str) -> str:
    """
    Krildan Lotinga o'girish funksiyasi
    """
    return _trans.transliterate(text, from_="cyr", to="lat")

def latin_to_cyrillic(text: str) -> str:
    """
    Lotindan Krilga o'girish funksiyasi
    """
    return _trans.transliterate(text, from_="lat", to="cyr")


# Namuna
if __name__ == "__main__":
    cyr_text = "Ўзбекистон Республикаси"
    lat_text = "O'zbekiston Respublikasi"

    print("Cyr -> Lat:", cyrillic_to_latin(cyr_text))
    print("Lat -> Cyr:", latin_to_cyrillic(lat_text))
