#!/usr/bin/env python3
"""
Test script for Upload Only mode
"""
from utils.logger_core import logger
from core.config import SITE_CONFIGS
from telegramuploader.legacy_adapter import upload_only_mode
import asyncio
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))


async def test_upload_only():
    """Upload Only mode test"""
    logger.info("🧪 Upload Only mode test")

    # Use first available config for testing
    site_name = list(SITE_CONFIGS.keys())[0]
    CONFIG = SITE_CONFIGS[site_name]

    logger.info(f"📋 Test site: {site_name}")
    logger.info(f"📁 Downloads dir: {CONFIG['download_dir']}")

    try:
        await upload_only_mode(CONFIG)
        logger.info("✅ Upload Only mode test completed")
    except Exception as e:
        logger.error(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_upload_only())
