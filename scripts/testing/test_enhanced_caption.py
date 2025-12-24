#!/usr/bin/env python3
"""
Enhanced Caption Test - HTML va Telegram xatoliklarini bartaraf etish
"""

import html
import re


def clean_text_for_caption(text: str) -> str:
    """Caption uchun matnni tozalash - Enhanced version"""
    if not text or not isinstance(text, str):
        return ""

    # HTML entities decode qilish
    text = html.unescape(text)

    # Barcha HTML teglarni olib tashlash - kuchaytirilan versiya
    # 1. Script va style teglar ichidagi kontentni butunlay olib tashlash
    text = re.sub(r'<script[^>]*>.*?</script>', '',
                  text, flags=re.DOTALL | re.IGNORECASE)
    text = re.sub(r'<style[^>]*>.*?</style>', '', text,
                  flags=re.DOTALL | re.IGNORECASE)

    # 2. Barcha HTML teglarni olib tashlash (attributes bilan)
    text = re.sub(r'<[^>]+>', '', text)

    # 3. HTML entities larni tozalash
    text = text.replace('&amp;', '&')
    text = text.replace('&lt;', '<')
    text = text.replace('&gt;', '>')
    text = text.replace('&quot;', '"')
    text = text.replace('&apos;', "'")
    text = text.replace('&nbsp;', ' ')
    text = text.replace('&#39;', "'")
    text = text.replace('&#34;', '"')

    # 4. Ortiqcha bo'shliqlarni tozalash
    text = re.sub(r'\s+', ' ', text).strip()

    # 5. Telegram uchun xavfli belgilarni tozalash
    text = text.replace('`', "'")  # Backtick → apostrophe
    text = text.replace('*', '')   # Asterisk olib tashlash
    text = text.replace('_', '')   # Underscore olib tashlash
    text = text.replace('[', '(')  # Square bracket → round bracket
    text = text.replace(']', ')')
    text = text.replace('{', '(')  # Curly bracket → round bracket
    text = text.replace('}', ')')

    # 6. Qolgan HTML-ga o'xshash belgilarni tozalash
    text = re.sub(r'<+', '', text)  # < belgilar
    text = re.sub(r'>+', '', text)  # > belgilar

    # 7. Control characters ni olib tashlash
    text = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', text)

    return text.strip()


def final_caption_cleanup(caption: str) -> str:
    """Caption ni final tozalash - har qanday HTML qoldiqlarini olib tashlash"""
    if not caption:
        return ""

    # 1. Barcha HTML teglarni yana bir bor tozalash
    caption = re.sub(r'<[^>]*>', '', caption)

    # 2. HTML entities lar
    html_entities = {
        '&amp;': '&', '&lt;': '<', '&gt;': '>', '&quot;': '"', '&apos;': "'",
        '&nbsp;': ' ', '&#39;': "'", '&#34;': '"', '&copy;': '©', '&reg;': '®'
    }
    for entity, replacement in html_entities.items():
        caption = caption.replace(entity, replacement)

    # 3. Numeric HTML entities (&#123; formatida)
    caption = re.sub(r'&#\d+;', '', caption)

    # 4. Hex HTML entities (&#x123; formatida)
    caption = re.sub(r'&#x[0-9a-fA-F]+;', '', caption)

    # 5. Telegram parse mode conflicts
    telegram_special = ['*', '_', '`', '[', ']',
                        '~', '|', '+', '-', '=', '.', '!']
    for char in telegram_special:
        caption = caption.replace(char, '')

    # 6. Multiple spaces va newlines tozalash
    caption = re.sub(r'\n{3,}', '\n\n', caption)  # 3+ newline → 2 newline
    caption = re.sub(r' {2,}', ' ', caption)       # 2+ space → 1 space

    # 7. Line boshida va oxirida ortiqcha belgilar
    lines = caption.split('\n')
    cleaned_lines = []
    for line in lines:
        line = line.strip()
        if line:  # Bo'sh qatorlarni tashlab ketmaslik
            cleaned_lines.append(line)

    return '\n'.join(cleaned_lines).strip()


def test_problematic_html():
    """Muammoli HTML matnlarni test qilish"""
    print("🧪 Enhanced Caption Test - Telegram Xatoliklarini Bartaraf Etish")
    print("=" * 70)

    # Telegram xatolik beruvchi matnlar
    problematic_texts = [
        '<class="film-title">Ajoyib Film</class>',
        '<div class="movie-info">Film haqida</div>',
        '<span class="actor">Aktyor nomi</span>',
        'Bu <script>alert("xss")</script> film',
        'Matn &quot;qo&#39;shtirnoq&quot; bilan',
        'HTML entities: &amp; &lt; &gt; &nbsp; &#34;',
        'Telegram *bold* _italic_ `code` format',
        'Square [brackets] va {curly} brackets',
        'Multiple    spaces\n\n\n\nva    newlines',
        '<b>Bold</b> <i>italic</i> <u>underline</u>',
        '< > belgilar <> va <<>> ko\'p belgilar'
    ]

    print("📋 Test natijalari:")
    print("-" * 70)

    for i, text in enumerate(problematic_texts, 1):
        print(f"\n{i}. Original:")
        print(f"   {text}")

        # Birinchi tozalash
        cleaned = clean_text_for_caption(text)
        print(f"   Cleaned: {cleaned}")

        # Final tozalash
        final = final_caption_cleanup(cleaned)
        print(f"   Final:   {final}")

        # Telegram entities tekshirish
        telegram_issues = []
        if '<' in final:
            telegram_issues.append('< tag start')
        if '>' in final:
            telegram_issues.append('> tag end')
        if '&' in final and any(ent in final for ent in ['&amp;', '&lt;', '&gt;']):
            telegram_issues.append('HTML entities')
        if any(char in final for char in ['*', '_', '`', '[', ']']):
            telegram_issues.append('Telegram markup')

        if telegram_issues:
            print(f"   ⚠️  Potential issues: {', '.join(telegram_issues)}")
        else:
            print(f"   ✅ Telegram-safe")

    # Full caption test
    print(f"\n{'='*70}")
    print("📝 To'liq Caption Test:")

    test_item = {
        "title": '<div class="title">Ajoyib <b>Film</b></div>',
        "categories": ["Drama", "Comedy"],
        "year": "2023",
        "country": '<span class="country">O\'zbekiston</span>',
        "actors": 'Actor <strong class="main">One</strong>, Actor Two',
        "language": "O'zbek",
        "description": 'Bu <em class="desc">ajoyib</em> film haqida ma\'lumot. HTML <script>kod</script> bilan.',
        "file_url": "https://example.com/file.mp4"
    }

    # Caption qismlari
    caption_parts = []

    # Title
    title = clean_text_for_caption(test_item.get("title", "No title"))
    caption_parts.append(f"📄 {title}")

    # Categories
    categories = test_item.get("categories", [])
    if categories:
        clean_categories = [clean_text_for_caption(cat) for cat in categories]
        caption_parts.append(f"🏷️ {', '.join(clean_categories)}")

    # Year and Country
    year = test_item.get("year", "")
    country = test_item.get("country", "")
    if year or country:
        year_country = []
        if year:
            year_country.append(str(year))
        if country:
            year_country.append(clean_text_for_caption(country))
        caption_parts.append(f"📅 {' | '.join(year_country)}")

    # Actors
    actors = test_item.get("actors", "")
    if actors:
        clean_actors = clean_text_for_caption(actors)
        caption_parts.append(f"🎭 {clean_actors}")

    # Language
    language = test_item.get("language", "")
    if language:
        clean_language = clean_text_for_caption(language)
        caption_parts.append(f"🌐 {clean_language}")

    # File size
    caption_parts.append(f"💾 500.00 MB")

    # Description
    description = test_item.get("description", "")
    if description:
        clean_desc = clean_text_for_caption(description)
        if len(clean_desc) > 200:
            clean_desc = clean_desc[:197] + "..."
        caption_parts.append(f"📝 {clean_desc}")

    caption = "\n".join(caption_parts)
    final_caption = final_caption_cleanup(caption)

    print("-" * 70)
    print("Final Caption:")
    print(final_caption)
    print("-" * 70)

    # Telegram safety check
    unsafe_patterns = [
        (r'<[^>]*>', 'HTML tags'),
        (r'&[a-zA-Z]+;', 'HTML entities'),
        (r'&#\d+;', 'Numeric entities'),
        (r'[*_`\[\]]', 'Telegram markup'),
        (r'<|>', 'Angle brackets')
    ]

    issues = []
    for pattern, desc in unsafe_patterns:
        if re.search(pattern, final_caption):
            issues.append(desc)

    if issues:
        print(f"❌ Telegram safety issues: {', '.join(issues)}")
    else:
        print("✅ Caption is completely Telegram-safe!")

    print(f"📏 Caption length: {len(final_caption)} characters")


if __name__ == "__main__":
    test_problematic_html()
