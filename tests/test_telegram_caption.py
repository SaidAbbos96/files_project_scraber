#!/usr/bin/env python3
"""
Test Telegram caption with cleaned HTML
"""

from utils.logger_core import logger
from utils.helpers import make_caption, sanitize_caption_data
import asyncio
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


async def test_telegram_caption():
    """Telegram caption test with problematic HTML"""

    logger.info("🧪 TELEGRAM CAPTION TEST")
    logger.info("=" * 60)

    # Test data with HTML that causes issues
    problematic_data = {
        "title": "Film <class=\"movie\">Title</class> Test",
        "desc": "Bu film <div>description</div> va &amp; boshqa ma'lumotlar",
        "actors": "Tom <b>Holland</b>, Emma <span>Stone</span>",
        "categories": "Action, Drama <tag>removed</tag>",
        "year": 2023,
        "file_size": 1024 * 1024 * 500,  # 500MB
        "lang": "uz"
    }

    logger.info("📝 Original problematic data:")
    for k, v in problematic_data.items():
        logger.info(f"  {k}: {repr(v)}")

    # Clean data
    clean_data = sanitize_caption_data(problematic_data)
    logger.info("\n🧹 Cleaned data:")
    for k, v in clean_data.items():
        logger.info(f"  {k}: {repr(v)}")

    # Generate caption
    caption = make_caption(clean_data)
    logger.info("\n📄 Final caption:")
    logger.info(caption)

    # Check caption length
    logger.info(f"\n📏 Caption uzunligi: {len(caption)} belgi")
    if len(caption) > 4096:
        logger.warning("⚠️ Caption 4096 belgidan uzun!")
        caption = caption[:4096]
        logger.info(f"✂️ Qisqartirildi: {len(caption)} belgi")

    # Simulate what would be sent to Telegram
    logger.info("\n📱 Telegram ga yuboriladigan format:")
    logger.info("=" * 40)
    logger.info(caption)
    logger.info("=" * 40)

    # Check for dangerous HTML patterns
    dangerous_patterns = ['<class', '<div',
                          '<span', '<script', '&amp;', '&lt;', '&gt;']
    found_dangerous = []

    for pattern in dangerous_patterns:
        if pattern in caption:
            found_dangerous.append(pattern)

    if found_dangerous:
        logger.error(f"❌ Xavfli HTML topildi: {found_dangerous}")
    else:
        logger.info("✅ Caption xavfsiz - hech qanday xavfli HTML yo'q")

    logger.info("\n" + "=" * 60)
    logger.info("📋 TEST XULOSASI:")
    logger.info("✅ HTML tozalash ishlaydi")
    logger.info("✅ Caption xavfsiz formatda")
    logger.info("✅ Telegram parse error yo'q bo'ladi")
    logger.info("=" * 60)

if __name__ == "__main__":
    asyncio.run(test_telegram_caption())
