#!/usr/bin/env python3
"""
Test HTML cleaning for Telegram captions
"""

from utils.helpers import clean_html_for_telegram, sanitize_caption_data, make_caption
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


def test_html_cleaning():
    """HTML tozalash testlari"""

    print("🧪 HTML CLEANING TEST")
    print("=" * 50)

    # Test cases
    test_cases = [
        # Muammoli HTML
        '<class="text">Bu oddiy matn</class>',
        '<div class="title">Film nomi</div>',
        '<span style="color:red">Qizil matn</span>',

        # HTML entities
        'Tom &amp; Jerry',
        'A &lt; B &gt; C',
        '&quot;Quotes&quot;',

        # Mixed content
        'Film haqida <p>Bu juda yaxshi film</p> deb aytishadi',

        # Normal text
        'Oddiy matn hech qanday HTML yo\'q',

        # Empty/None
        '',
        None
    ]

    for i, test_text in enumerate(test_cases, 1):
        print(f"\n{i}. Test: {repr(test_text)}")
        result = clean_html_for_telegram(test_text)
        print(f"   Natija: {repr(result)}")

    # Caption data test
    print("\n" + "=" * 50)
    print("📝 CAPTION DATA TEST")

    test_data = {
        "title": "Zo'r <class=\"film\">Film</class> nomi",
        "desc": "Bu film haqida <div>ma'lumot</div> va &amp; belgisi",
        "actors": ["Tom <b>Holland</b>", "Emma <i>Stone</i>"],
        "year": 2023,
        "categories": ["Action", "Drama <tag>"]
    }

    print(f"\nOriginal data:")
    for k, v in test_data.items():
        print(f"  {k}: {repr(v)}")

    clean_data = sanitize_caption_data(test_data)
    print(f"\nTozalangan data:")
    for k, v in clean_data.items():
        print(f"  {k}: {repr(v)}")

    # Final caption test
    print(f"\n📄 FINAL CAPTION:")
    caption = make_caption(clean_data)
    print(caption)

    print("\n" + "=" * 50)
    print("✅ Test tugadi!")


if __name__ == "__main__":
    test_html_cleaning()
