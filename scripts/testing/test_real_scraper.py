#!/usr/bin/env python3
"""
Real Scraper Test - Haqiqiy scraper parse_page_fields funksiyasini test qilish
"""

import sys
import os

# Project root'ni sys.path ga qo'shish
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)

from scraper.parsers.parse_file_page import parse_page_fields

def test_real_scraper_parsing():
    """Haqiqiy scraper parsing funksiyasini test qilish"""
    print("🧪 Real Scraper Parse Test")
    print("=" * 50)
    
    # Test HTML - asilmedia.org style
    test_html = """
    <html>
        <body>
            <article id="dle-content">
                <h1 class="title">Ajoyib <b>Film</b> Nomi - <span>2023</span></h1>
                <div class="fullcol">
                    <div class="fullcol-right flx-fx order-last">
                        <div class="full-bot mb-4">
                            <div>
                                <div>
                                    <span class="fullmeta-seclabel">2023</span>
                                </div>
                                <div>
                                    <span class="fullmeta-seclabel">O'zbekiston, <strong>AQSh</strong></span>
                                </div>
                            </div>
                        </div>
                        <div class="full-body mb-4">
                            <div>
                                <div>
                                    <span>Janr:</span>
                                    <span>Drama, <em>Comedy</em>, <b>Action</b></span>
                                </div>
                                <div>
                                    <span>Aktyorlar:</span>
                                    <span>John <strong>Smith</strong>, Jane <i>Doe</i></span>
                                </div>
                            </div>
                            <article>
                                Bu <strong>ajoyib</strong> film haqida ma'lumot.
                                <script>alert('xss attempt');</script>
                                HTML <b>bold</b> va <i>italic</i> bilan yozilgan <em>tavsif</em>.
                            </article>
                        </div>
                    </div>
                </div>
                <img class="img-fit" src="/image.jpg" alt="Film rasmi"/>
                <div id="download1">
                    <div>
                        <a href="/download1.mp4">Download 1</a>
                        <a href="/download2.mp4">Download 2</a>
                    </div>
                </div>
            </article>
        </body>
    </html>
    """
    
    # Asilmedia config simulation
    config = {
        "fields": {
            "title": "h1.title",
            "categories": "div.full-body > div > div:nth-child(1) > span:nth-child(2)",
            "description": "div.full-body article",
            "file_url": "#download1 div a:last-of-type::attr(href)",
            "image": "img.img-fit::attr(src)",
            "year": "#dle-content > article > div > div.fullcol > div.fullcol-right.flx-fx.order-last > div.full-bot.mb-4 > div > div:nth-child(1) > span.fullmeta-seclabel",
            "country": "#dle-content > article > div > div.fullcol.flx.mb-4 > div.fullcol-right.flx-fx.order-last > div.full-bot.mb-4 > div > div:nth-child(2) > span.fullmeta-seclabel",
            "actors": "#dle-content > article > div > div.fullcol.flx.mb-4 > div.fullcol-right.flx-fx.order-last > div.full-body.mb-4 > div > div:nth-child(2) > span:nth-child(2)"
        }
    }
    
    base_url = "http://asilmedia.org/film/test/"
    
    # Parse qilish
    result = parse_page_fields(config, test_html, base_url)
    
    print("📋 Parsing natijalari:")
    print("-" * 50)
    
    for key, value in result.items():
        if value:
            print(f"\n📄 {key.upper()}:")
            print(f"  Value: '{value}'")
            
            # HTML check
            if isinstance(value, str):
                html_found = any(char in value for char in ['<', '>'])
                script_found = '<script' in value.lower()
                
                if html_found:
                    print(f"  ⚠️  HTML tags topildi!")
                elif script_found:
                    print(f"  ⚠️  Script tag topildi!")
                else:
                    print(f"  ✅ Completely clean")
            else:
                print(f"  ℹ️  Non-string value")
        else:
            print(f"\n📄 {key.upper()}: None")
    
    # Global summary
    print(f"\n{'='*50}")
    print("🎯 XULOSA:")
    
    text_fields = ['title', 'categories', 'description', 'year', 'country', 'actors']
    clean_count = 0
    total_count = 0
    
    for field in text_fields:
        value = result.get(field)
        if value and isinstance(value, str):
            total_count += 1
            html_found = any(char in value for char in ['<', '>'])
            if not html_found:
                clean_count += 1
    
    if total_count > 0:
        clean_percentage = (clean_count / total_count) * 100
        print(f"✅ {clean_count}/{total_count} maydon HTML-free ({clean_percentage:.1f}%)")
        
        if clean_percentage == 100:
            print("🎉 Barcha matnli maydonlar to'liq tozalangan!")
        else:
            print("⚠️  Ba'zi maydonlarda HTML qoldiqlari mavjud")
    else:
        print("ℹ️  Test uchun matnli maydonlar topilmadi")

def test_meta_parsing():
    """Meta parsing test"""
    print(f"\n{'='*50}")
    print("📝 Meta Parsing Test")
    print("-" * 50)
    
    meta_html = """
    <html>
        <body>
            <div class="inner-page__desc">
                <div class="inner-page__text">
                    Janr: <strong>Drama</strong>, <em>Comedy</em>
                    Mamlakat: <span>O'zbekiston</span>, <b>AQSh</b>
                    Ishlab chiqarilgan yili: <span>2023</span>
                    Tarjima 1: <i>O'zbek</i>
                    Rollarda: <strong>John Smith</strong>, <em>Jane Doe</em>
                    Ta'rif: Bu <b>ajoyib</b> film haqida <i>ma'lumot</i>.
                </div>
            </div>
        </body>
    </html>
    """
    
    config = {
        "fields": {
            "meta": ".inner-page__desc .inner-page__text",
            "categories": "meta:Janr",
            "country": "meta:Mamlakat", 
            "year": "meta:Ishlab chiqarilgan yili",
            "language": "meta:Tarjima 1",
            "actors": "meta:Rollarda",
            "description": "meta:Ta'rif"
        }
    }
    
    base_url = "https://new.daxshat.net/test/"
    
    result = parse_page_fields(config, meta_html, base_url)
    
    print("Meta parsing results:")
    for key, value in result.items():
        if key != 'file_page' and value:
            print(f"  {key}: '{value}'")
            
            if isinstance(value, str):
                html_found = any(char in value for char in ['<', '>'])
                print(f"    Clean: {'✅' if not html_found else '❌'}")

if __name__ == "__main__":
    test_real_scraper_parsing()
    test_meta_parsing()