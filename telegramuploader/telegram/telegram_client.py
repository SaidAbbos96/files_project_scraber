from utils.logger_core import logger
from telethon import TelegramClient
import sys
from pathlib import Path
from datetime import datetime
from core import config


phone = config.TELEGRAM_PHONE
api_id = config.TELEGRAM_API_ID
api_hash = config.TELEGRAM_API_HASH
files_group_link = config.FILES_GROUP_LINK


# Root papkani sys.path ga qo'shish
root_dir = Path(__file__).parent.parent.parent
sys.path.append(str(root_dir))


# Session fayl yo'li - telegramuploader papkasida
current_dir = Path(__file__).parent.parent  # telegramuploader/
session_path = current_dir / f"session_{phone}.session"

Telegram_client = TelegramClient(str(session_path), api_id, api_hash)


async def send_startup_messages(client=Telegram_client):
    """Dastur ishga tushganda test xabarlari - rate limiting bilan"""
    try:
        await client.start()
        me = await client.get_me()
        logger.info("✅ Auth qilindi: %s", me.username or me.first_name)

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
                    entity, f"✅ Downloader bot ishga tushdi va tayyor!\n🕒 {now}"
                )
                logger.info("📨 Guruhga xabar yuborildi")
        except Exception as e:
            logger.error("❌ Guruhga yuborilmadi: %s", e)

    except Exception as e:
        logger.error("❌ Telegram ulanish xatosi: %s", e)
        raise


# 🔑 Guruh yoki kanal entity aniqlash
async def resolve_group(group_ref: str):
    """
    group_ref -> int ID (-100...), yoki username (@channel), yoki invite link (https://t.me/...)
    """
    try:
        await Telegram_client.start()

        # Agar ID bo'lsa (int yoki str shaklda)
        if isinstance(group_ref, int) or (
            isinstance(group_ref, str) and group_ref.startswith("-")
        ):
            entity = await Telegram_client.get_entity(int(group_ref))
        else:
            # Username yoki invite link
            entity = await Telegram_client.get_entity(group_ref)

        logger.info(
            f"✅ Guruh aniqlangan: {entity.id} ({getattr(entity, 'title', 'N/A')})")
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
