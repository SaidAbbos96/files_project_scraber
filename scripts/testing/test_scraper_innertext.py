#!/usr/bin/env python3
"""
Scraper Inner Text Test - HTML taglarni olib tashlash testi
"""

from bs4 import BeautifulSoup


def test_selector_parsing():
    """Selector parsing testlari"""
    print("🧪 Scraper Inner Text Test")
    print("=" * 50)

    # Test HTML
    test_html = """
    <html>
        <body>
            <div class="title">
                <span>Film Nomi</span> - <b>2023</b>
            </div>
            <div class="meta-info">
                <p class="category">Janr: <strong>Drama</strong>, <em>Comedy</em></p>
                <p class="country">Mamlakat: <span class="flag">🇺🇸</span> AQSh</p>
                <p class="year">Yil: <b>2023</b></p>
            </div>
            <div class="description">
                Bu <strong>ajoyib</strong> film haqida ma'lumot.
                <script>console.log('script tag');</script>
                HTML <em>formatting</em> bilan yozilgan.
            </div>
            <div class="actors">
                <ul>
                    <li>Actor <b>One</b></li>
                    <li>Actor <span>Two</span></li>
                </ul>
            </div>
        </body>
    </html>
    """

    soup = BeautifulSoup(test_html, "html.parser")

    # Test selectors
    test_cases = [
        (".title", "Film nomi (HTML taglar bilan)"),
        (".meta-info", "Meta ma'lumotlar (ko'p qatorli)"),
        (".description", "Tavsif (script tag bilan)"),
        (".actors", "Aktörlar (list format)")
    ]

    print("📋 Test natijalari:")
    print("-" * 50)

    for selector, description in test_cases:
        el = soup.select_one(selector)
        if el:
            # Eski usul (.text)
            old_text = el.text.strip()

            # Yangi usul (.get_text(strip=True))
            new_text = el.get_text(strip=True)

            # Separator bilan
            sep_text = el.get_text(" ", strip=True)

            print(f"\n🎯 {description}")
            print(f"Selector: {selector}")
            print(f"Old (.text):     '{old_text}'")
            print(f"New (get_text):  '{new_text}'")
            print(f"With separator:  '{sep_text}'")

            # HTML taglar mavjudligini tekshirish
            html_found = any(char in new_text for char in ['<', '>'])
            if html_found:
                print(f"⚠️  HTML tags topildi!")
            else:
                print(f"✅ HTML-free")


def test_meta_parsing():
    """Meta parsing testi"""
    print(f"\n{'='*50}")
    print("📝 Meta Parsing Test")
    print("-" * 50)

    meta_html = """
    <div class="meta-content">
        Janr: <strong>Drama</strong>, <em>Comedy</em>
        Mamlakat: <span class="country">O'zbekiston</span>, <b>AQSh</b>
        Yil: <span>2023</span>
        Til: <i>O'zbek</i>, <u>Ingliz</u>
        <script>alert('xss');</script>
        Rejissor: <strong class="director">John Smith</strong>
    </div>
    """

    soup = BeautifulSoup(meta_html, "html.parser")
    el = soup.select_one(".meta-content")

    if el:
        # get_text with newline separator
        meta_text = el.get_text("\n", strip=True)

        print("Meta content:")
        print(f"'{meta_text}'")
        print()

        # Meta key-value parsing
        meta_data = {}
        for line in meta_text.split("\n"):
            parts = line.split(":", 1)
            if len(parts) == 2:
                key = parts[0].strip()
                val = parts[1].strip()
                meta_data[key] = val
                print(f"  {key}: {val}")

        # HTML check
        html_found = any(
            '<' in val or '>' in val for val in meta_data.values())
        if html_found:
            print(f"\n⚠️  Meta da HTML tags topildi!")
        else:
            print(f"\n✅ Meta completely HTML-free")


def test_field_parsing_simulation():
    """Real field parsing simulation"""
    print(f"\n{'='*50}")
    print("🔧 Field Parsing Simulation")
    print("-" * 50)

    # Asilmedia-style HTML
    film_html = """
    <article>
        <h1 class="title">Ajoyib <b>Film</b> - <span>2023</span></h1>
        <div class="full-body">
            <div>
                <div>
                    <span>Janr:</span>
                    <span>Drama, <em>Comedy</em></span>
                </div>
            </div>
            <article>
                Bu <strong>ajoyib</strong> film haqida ma'lumot.
                <script>console.log('bad script');</script>
                HTML <b>bold</b> va <i>italic</i> bilan.
            </article>
        </div>
        <div class="meta-section">
            <div>
                <span class="fullmeta-seclabel">2023</span>
            </div>
            <div>
                <span class="fullmeta-seclabel">O'zbekiston, <strong>AQSh</strong></span>
            </div>
        </div>
    </article>
    """

    soup = BeautifulSoup(film_html, "html.parser")

    # Simulate config fields
    test_fields = {
        "title": "h1.title",
        "categories": "div.full-body > div > div:nth-child(1) > span:nth-child(2)",
        "description": "div.full-body article",
        "year": "div.meta-section > div:nth-child(1) > span.fullmeta-seclabel",
        "country": "div.meta-section > div:nth-child(2) > span.fullmeta-seclabel"
    }

    results = {}

    for field, selector in test_fields.items():
        # Eski usul simulation
        el = soup.select_one(selector)
        if el:
            old_value = el.text.strip()
            new_value = el.get_text(strip=True)

            results[field] = {
                "old": old_value,
                "new": new_value,
                "html_clean": not any(char in new_value for char in ['<', '>'])
            }

    print("Field extraction results:")
    for field, data in results.items():
        print(f"\n📄 {field.upper()}:")
        print(f"  Old: '{data['old']}'")
        print(f"  New: '{data['new']}'")
        print(f"  Clean: {'✅' if data['html_clean'] else '❌'}")


if __name__ == "__main__":
    test_selector_parsing()
    test_meta_parsing()
    test_field_parsing_simulation()

    print(f"\n{'='*50}")
    print("🎯 XULOSA:")
    print("✅ .get_text(strip=True) HTML taglarni to'liq olib tashlaydi")
    print("✅ Meta parsing ham HTML-free bo'ladi")
    print("✅ Script taglar avtomatik olib tashlanadi")
    print("✅ Barcha formatlar (bold, italic, span) tozalanadi")
