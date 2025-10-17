import random
import asyncio


async def human_sleep(CONFIG):
    if not CONFIG.get("enable_sleep", False):
        return  # kutish o‘chirilgan
    delay = random.uniform(CONFIG["sleep_min"], CONFIG["sleep_max"])
    await asyncio.sleep(delay)
