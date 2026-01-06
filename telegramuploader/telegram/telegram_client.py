import asyncio
from utils.logger_core import logger
from telethon import TelegramClient
import sys
from pathlib import Path
from datetime import datetime
from core import config
from core.config import WORKER_NAME


phone = config.TELEGRAM_PHONE_NUMBER
api_id = config.TELEGRAM_API_ID
api_hash = config.TELEGRAM_API_HASH
files_group_link = config.FILES_GROUP_LINK


# Root papkani sys.path ga qo'shish
root_dir = Path(__file__).parent.parent.parent
sys.path.append(str(root_dir))


# Session fayl yo'li - telegramuploader papkasida
current_dir = Path(__file__).parent.parent  # telegramuploader/
session_path = current_dir / f"session_{phone}.session"

# Session lock conflict ni oldini olish uchun connection parametrlari
_session_lock = asyncio.Lock()

# SQLite timeout bilan Telegram client
Telegram_client = TelegramClient(
    str(session_path),
    api_id,
    api_hash,
    connection_retries=config.TELEGRAM_CONNECTION_RETRIES,
    retry_delay=config.TELEGRAM_RETRY_DELAY,
    timeout=config.TELEGRAM_TIMEOUT,
    request_retries=config.TELEGRAM_REQUEST_RETRIES,
    flood_sleep_threshold=config.TELEGRAM_FLOOD_SLEEP_THRESHOLD,
)


async def send_startup_messages(client=Telegram_client):
    """Dastur ishga tushganda test xabarlari - rate limiting bilan"""
    try:
        await client.start()
        me = await client.get_me()
        logger.info(
            f"✅ Auth qilindi: {me.username or me.first_name}, premium: {getattr(me, 'premium', 'UNKNOWN')}")

        # Sana va vaqtni olish
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # O'zingizga
        await client.send_message(me.id, f"✅ Downloader Auto User Bot ({me.username or me.first_name}) ishga tushdi!\n🕒 {now}")
        logger.info("📨 O'zingizga xabar yuborildi")

        # Guruhga
        try:
            # Invite link orqali
            entity = await resolve_group(files_group_link)
            if entity:
                await client.send_message(
                    entity, f"✅ Downloader bot ishga tushdi va tayyor!\n🤖 Bot: {WORKER_NAME}\n🕒 {now}"
                )
                logger.info("📨 Guruhga xabar yuborildi")
        except Exception as e:
            logger.error("❌ Guruhga yuborilmadi: %s", e)

        # PREMIUM STATUS CHECK
        is_premium = getattr(me, 'premium', None)
        if is_premium is not None:
            logger.info(f"💎 Telegram account premium: {is_premium}")
        else:
            logger.info(
                "💎 Telegram account premium: UNKNOWN (old Telethon version?)")
        # Save to global for use in upload logic
        config.TELEGRAM_USER_IS_PREMIUM = is_premium

    except Exception as e:
        logger.error("❌ Telegram ulanish xatosi: %s", e)
        raise


# 🔑 Guruh yoki kanal entity aniqlash
async def safe_telegram_start():
    """Session lock bilan xavfsiz Telegram start"""
    async with _session_lock:
        try:
            if not Telegram_client.is_connected():
                logger.info("🔌 Telegram client ulanmoqda...")
                await Telegram_client.start()
                logger.info("✅ Telegram client ulandi")
            return True
        except Exception as e:
            logger.error(f"❌ Telegram start xato: {e}")
            return False


async def resolve_group(group_ref: str):
    """
    group_ref -> int ID (-100...), yoki username (@channel), yoki invite link (https://t.me/...)
    """
    try:
        if not await safe_telegram_start():
            return None

        # Agar ID bo'lsa (int yoki str shaklda)
        if isinstance(group_ref, int) or (
            isinstance(group_ref, str) and group_ref.startswith("-")
        ):
            entity = await Telegram_client.get_entity(int(group_ref))
        else:
            # Username yoki invite link
            entity = await Telegram_client.get_entity(group_ref)

        # logger.info(
        #     f"✅ Guruh aniqlangan: {entity.id} ({getattr(entity, 'title', 'N/A')})")
        return entity
    except Exception as e:
        logger.error(f"❌ Guruhni aniqlab bo'lmadi: {e}")
        return None


async def main():
    """Test function for telegram client"""
    try:
        logger.info("🚀 Telegram client test boshlandi")
        await send_startup_messages(client=Telegram_client)
        logger.info("🎉 Test muvaffaqiyatli tugadi")
    except Exception as e:
        logger.error(f"❌ Test xatosi: {e}")
    finally:
        if Telegram_client.is_connected():
            await Telegram_client.disconnect()
            logger.info("🔌 Client uzildi")


def test_session():
    """Session faylni tekshirish"""
    logger.info(f"📁 Session fayl yo'li: {session_path}")
    logger.info(f"📁 Session fayl mavjud: {session_path.exists()}")
    if session_path.exists():
        logger.info(f"📊 Fayl hajmi: {session_path.stat().st_size} bytes")
        logger.info(
            f"📅 Oxirgi o'zgarish: {datetime.fromtimestamp(session_path.stat().st_mtime)}")
    return session_path.exists()


if __name__ == "__main__":
    # Test uchun import
    import asyncio
    import logging
    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s | %(levelname)s | %(message)s')
    logger = logging.getLogger(__name__)

    async def simple_test():
        print(f"📁 Session fayl yo'li: {session_path}")
        print(f"📁 Session fayl mavjud: {session_path.exists()}")
        if session_path.exists():
            print(f"📊 Fayl hajmi: {session_path.stat().st_size} bytes")

        try:
            print("🚀 Telegram client test boshlandi")
            await Telegram_client.start()
            me = await Telegram_client.get_me()
            print(f"✅ Ulanish muvaffaqiyatli: {me.username or me.first_name}")
            print(f"📱 Telefon: {me.phone}")
            print(f"🆔 ID: {me.id}")

            # Test xabar
            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            await Telegram_client.send_message(me.id, f"🧪 Test xabar: {now}")
            print("📨 Test xabar yuborildi")

        except Exception as e:
            print(f"❌ Test xatosi: {e}")
        finally:
            if Telegram_client.is_connected():
                await Telegram_client.disconnect()
                print("🔌 Client uzildi")

    asyncio.run(simple_test())
