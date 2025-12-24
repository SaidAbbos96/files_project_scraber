from telethon import TelegramClient
import asyncio
from pathlib import Path

# TELEGRAM_API_ID = 21164919
# TELEGRAM_API_HASH = '24dca1a54ec240b398c6d157ff550add'
# TELEGRAM_PHONE_NUMBER = '+998994460450'

TELEGRAM_API_ID = 28837519
TELEGRAM_API_HASH = "e22cefa35ca74ad27a92bceebd1291b3"
TELEGRAM_PHONE_NUMBER="+998200089990"

# Use the same session path as your project
session_path = Path(__file__).parent / 'telegramuploader' / f'session_{TELEGRAM_PHONE_NUMBER}.session'

async def test_premium():
    client = TelegramClient(str(session_path), TELEGRAM_API_ID, TELEGRAM_API_HASH)
    await client.start(phone=TELEGRAM_PHONE_NUMBER)
    me = await client.get_me()
    print(me)
    print('premium:', getattr(me, 'premium', 'NOT_FOUND'))
    await client.disconnect()

asyncio.run(test_premium())