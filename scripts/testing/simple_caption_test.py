#!/usr/bin/env python3
"""
Simple Caption Test - Dependencies siz test
"""

import html
import re

def clean_text_for_caption(text: str) -> str:
    """Caption uchun matnni tozalash - butunlay HTML-siz"""
    if not text or not isinstance(text, str):
        return ""
    
    # HTML entities decode qilish
    text = html.unescape(text)
    
    # Barcha HTML teglarni olib tashlash
    text = re.sub(r'<[^>]+>', '', text)
    
    # Ortiqcha bo'shliqlarni tozalash
    text = re.sub(r'\s+', ' ', text).strip()
    
    # Maxsus belgilarni oddiy belgilarga aylantirish
    text = text.replace('&amp;', '&').replace('&lt;', '<').replace('&gt;', '>').replace('&quot;', '"')
    
    # Telegram uchun xavfli belgilarni tozalash
    text = text.replace('`', "'").replace('*', '').replace('_', '').replace('[', '(').replace(']', ')')
    
    return text

def format_file_size(size_bytes: int) -> str:
    """Fayl hajmini formatlash"""
    if not size_bytes or size_bytes == 0:
        return "0 B"
    
    if size_bytes >= 1024 ** 3:
        size_gb = size_bytes / (1024 ** 3)
        return f"{size_gb:.2f} GB"
    elif size_bytes >= 1024 ** 2:
        size_mb = size_bytes / (1024 ** 2)
        return f"{size_mb:.2f} MB"
    elif size_bytes >= 1024:
        size_kb = size_bytes / 1024
        return f"{size_kb:.2f} KB"
    else:
        return f"{size_bytes} B"

def create_html_free_caption(item: dict, size: int) -> str:
    """HTML-siz caption yaratish"""
    caption_parts = []
    
    # Title
    title = clean_text_for_caption(item.get("title", "No title"))
    caption_parts.append(f"📄 {title}")
    
    # Categories
    categories = item.get("categories", [])
    if isinstance(categories, str):
        categories = [cat.strip() for cat in categories.split(",") if cat.strip()]
    if categories:
        clean_categories = [clean_text_for_caption(cat) for cat in categories]
        caption_parts.append(f"🏷️ {', '.join(clean_categories)}")
    
    # Year and Country
    year = item.get("year", "")
    country = item.get("country", "")
    if year or country:
        year_country = []
        if year:
            year_country.append(str(year))
        if country:
            year_country.append(clean_text_for_caption(country))
        caption_parts.append(f"📅 {' | '.join(year_country)}")
    
    # Actors
    actors = item.get("actors", "")
    if actors:
        clean_actors = clean_text_for_caption(actors)
        caption_parts.append(f"🎭 {clean_actors}")
    
    # Language
    language = item.get("language", "")
    if language:
        clean_language = clean_text_for_caption(language)
        caption_parts.append(f"🌐 {clean_language}")
    
    # File size
    caption_parts.append(f"💾 {format_file_size(size)}")
    
    # Description (qisqartirilgan)
    description = item.get("description", "")
    if description:
        clean_desc = clean_text_for_caption(description)
        if len(clean_desc) > 200:
            clean_desc = clean_desc[:197] + "..."
        caption_parts.append(f"📝 {clean_desc}")
    
    # URL (agar kerak bo'lsa)
    url = item.get("file_url", "")
    if url and len(url) < 100:  # Faqat qisqa URL larni qo'shamiz
        caption_parts.append(f"🔗 {url}")
    
    caption = "\n".join(caption_parts)
    caption = caption[:4096]  # Telegram limit
    return caption

def test_caption():
    """Caption test qilish"""
    print("🧪 Simple Caption Test (HTML-siz)")
    print("=" * 50)
    
    # Test ma'lumotlari HTML belgila bilan
    test_item = {
        "title": "<b>Ajoyib Film</b> &amp; <i>Drama</i>",
        "categories": ["Drama", "Comedy", "Action"],
        "year": "2023",
        "country": "<span>O'zbekiston</span>",
        "actors": "Actor <strong>One</strong>, Actor Two &quot;Three&quot;",
        "language": "O'zbek",
        "description": "Bu <em>ajoyib</em> film haqida <u>batafsil</u> ma'lumot. HTML &lt;teglar&gt; bilan to'la matn...",
        "file_url": "https://example.com/file.mp4"
    }
    
    # Caption yaratish
    caption = create_html_free_caption(test_item, 1024*1024*500)  # 500MB
    
    print("📝 Yaratilgan caption:")
    print("-" * 30)
    print(caption)
    print("-" * 30)
    
    # HTML mavjudligini tekshirish
    html_patterns = ['<', '>', '&lt;', '&gt;', '&amp;', '&quot;', '*', '_', '`']
    html_found = []
    
    for pattern in html_patterns:
        if pattern in caption:
            html_found.append(pattern)
    
    if html_found:
        print(f"❌ Caption da HTML/Markdown belgilar topildi: {html_found}")
    else:
        print("✅ Caption da HTML/Markdown belgilar yo'q - to'liq tozalangan!")
    
    # Caption uzunligini tekshirish
    print(f"📏 Caption uzunligi: {len(caption)} belgi")
    
    if len(caption) <= 4096:
        print("✅ Caption uzunligi Telegram limitiga mos")
    else:
        print("⚠️ Caption juda uzun")
    
    # Clean text funksiyasini alohida test qilish
    print(f"\n🧪 clean_text_for_caption test:")
    test_texts = [
        "<b>Bold matn</b>",
        "Normal &amp; &quot;qo'shtirnoq&quot;",
        "<script>alert('xss')</script>Normal matn",
        "Emoji 🎬 va *markdown* `kod` _italic_"
    ]
    
    for test_text in test_texts:
        cleaned = clean_text_for_caption(test_text)
        print(f"   Original: {test_text}")
        print(f"   Cleaned:  {cleaned}")
        print()

if __name__ == "__main__":
    test_caption()