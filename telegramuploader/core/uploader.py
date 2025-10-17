"""
Telegram Uploader - Telegramga fayl yuborish uchun
"""
import time
from core.config import FILES_GROUP_LINK
from utils.logger_core import logger
from utils.helpers import categories_to_ids, make_caption
from telegramuploader.utils.diagnostics import diagnostics
from telegramuploader.telegram.telegram_client import Telegram_client, resolve_group
import os
import asyncio
from pathlib import Path
from tqdm.asyncio import tqdm
from typing import Dict, Any, Optional
from telethon.tl.types import DocumentAttributeVideo

import sys
import os
# Add the parent directory to sys.path to import telegram module
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(os.path.dirname(current_dir))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)


class TelegramUploader:
    """Telegramga fayl yuborish uchun class"""

    def __init__(self, default_group: str = FILES_GROUP_LINK, timeout: int = 7200):
        """
        Args:
            default_group: Default Telegram group
            timeout: Upload timeout in seconds (default: 2 hours)
        """
        self.default_group = default_group
        self.timeout = timeout

    def get_video_attributes(self, file_path: str) -> Optional[DocumentAttributeVideo]:
        """Video fayl uchun attributes olish"""
        try:
            import ffmpeg
            import subprocess

            # ffprobe path'ini topish - avval system, keyin imageio-ffmpeg
            ffprobe_path = None

            # 1. Avval system ffprobe'ni tekshiramiz (ko'pincha mavjud va tez)
            for path in ['/usr/bin/ffprobe', '/usr/local/bin/ffprobe', 'ffprobe']:
                try:
                    subprocess.run([path, '-version'], capture_output=True, check=True, timeout=5)
                    ffprobe_path = path
                    logger.info(f"🔍 System ffprobe: {ffprobe_path}")
                    break
                except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired):
                    continue

            # 2. Agar system ffprobe yo'q bo'lsa, imageio-ffmpeg'dan foydalanish
            if not ffprobe_path:
                try:
                    import imageio_ffmpeg
                    ffmpeg_path = imageio_ffmpeg.get_ffmpeg_exe()
                    if ffmpeg_path and os.path.exists(ffmpeg_path):
                        # ffmpeg binary'dan ffprobe path yasash
                        potential_ffprobe = ffmpeg_path.replace('ffmpeg', 'ffprobe')
                        
                        # Agar ffprobe fayl mavjud bo'lsa
                        if os.path.exists(potential_ffprobe):
                            ffprobe_path = potential_ffprobe
                            logger.info(f"🔍 imageio-ffmpeg ffprobe: {ffprobe_path}")
                        else:
                            # ffmpeg'ni ffprobe sifatida ishlatish (ffmpeg -i ... bilan ham ma'lumot olish mumkin)
                            logger.warning(f"⚠️ ffprobe topilmadi: {potential_ffprobe}")
                            logger.info("🔄 ffmpeg'ni probe uchun ishlatamiz")
                            ffprobe_path = ffmpeg_path
                except ImportError:
                    logger.warning("⚠️ imageio-ffmpeg topilmadi")
                except Exception as e:
                    logger.warning(f"⚠️ imageio-ffmpeg xato: {e}")

            if not ffprobe_path:
                logger.warning(
                    "⚠️ ffprobe topilmadi, default attributes ishlatiladi")
                return self._get_default_video_attributes()

            # Video info olish
            probe = ffmpeg.probe(file_path, cmd=ffprobe_path)
            video_stream = next(
                (stream for stream in probe['streams'] if stream['codec_type'] == 'video'), None)

            if video_stream:
                width = int(video_stream.get('width', 1280))
                height = int(video_stream.get('height', 720))
                duration = float(probe.get('format', {}).get('duration', 0))

                logger.info(f"📹 Video info: {width}x{height}, {duration:.1f}s")

                # Video attributes yaratish
                return DocumentAttributeVideo(
                    duration=int(duration),
                    w=width,
                    h=height,
                    supports_streaming=True,
                    round_message=False
                )
            else:
                logger.warning("⚠️ Video stream topilmadi")
                return self._get_default_video_attributes()

        except Exception as e:
            logger.warning(f"⚠️ Video attributes olishda xato: {e}")
            return self._get_default_video_attributes()

    def _get_default_video_attributes(self) -> DocumentAttributeVideo:
        """Default video attributes qaytarish"""
        return DocumentAttributeVideo(
            duration=0,
            w=1280,
            h=720,
            supports_streaming=True,
            round_message=False
        )

    def is_video_file(self, filename: str) -> bool:
        """Fayl video ekanligini tekshirish"""
        video_extensions = {'.mp4', '.avi', '.mkv',
                            '.mov', '.wmv', '.flv', '.webm', '.m4v'}
        return Path(filename).suffix.lower() in video_extensions

    async def upload_file(self, item: Dict[str, Any], config: Dict[str, Any],
                          group_ref: Optional[str] = None) -> bool:
        """
        Faylni Telegramga yuborish

        Args:
            item: Fayl ma'lumotlari dict
            config: Konfiguratsiya
            group_ref: Telegram group reference

        Returns:
            True if successful, False otherwise
        """
        filename = "unknown"  # default qiymat
        start_time = time.time()  # Upload boshlanish vaqti
        try:
            logger.info(
                f"🔍 Upload funksiyasiga kirildi: {item.get('title', 'No title')}")

            # Debug: item structure
            # logger.info(f"🔍 Item keys: {list(item.keys())}")
            # logger.info(f"🔍 local_path: {item.get('local_path', 'NOT_FOUND')}")

            # ✅ Absolut path olish
            try:
                output_path = os.path.abspath(item["local_path"])
                filename = Path(output_path).name
                size = item.get("file_size", 0)
                logger.info(f"📁 Fayl path: {output_path}")
                logger.info(f"💾 Fayl hajmi: {size} bytes")
            except Exception as path_error:
                duration = time.time() - start_time
                logger.error(f"❌ Path olishda xato: {path_error}")
                diagnostics.log_error(
                    filename, 0, f"Path error: {path_error}", str(path_error), duration)
                return False

            if not os.path.exists(output_path):
                duration = time.time() - start_time
                logger.error(f"❌ Fayl topilmadi: {output_path}")
                diagnostics.log_error(
                    filename, size, "File not found", f"File does not exist: {output_path}", duration)
                return False

            # 📌 Caption yaratish
            caption = await self._create_caption(item, size)

            # 📌 Telegram connection va entity olish
            entity = await self._get_telegram_entity(group_ref)
            if not entity:
                duration = time.time() - start_time
                logger.error("❌ Guruh aniqlanmadi, upload qilib bo'lmadi")
                diagnostics.log_error(
                    filename, size, "Entity resolution failed", "Failed to get Telegram entity", duration)
                return False

            logger.info(
                f"✅ Guruh aniqlandi: {getattr(entity, 'title', str(entity))} !")
            logger.info(f"📤 Telegram send_file ishga tushmoqda...")

            # ⏰ Timeout bilan upload
            async with asyncio.timeout(self.timeout):
                with tqdm(total=size, unit="B", unit_scale=True, desc=f"📤 {filename}") as bar:

                    def progress(sent, total_size):
                        bar.n = sent
                        bar.total = total_size
                        bar.refresh()

                    # Video fayl uchun attributes tayyorlash
                    attributes = None
                    if self.is_video_file(filename):
                        video_attr = self.get_video_attributes(output_path)
                        if video_attr:
                            attributes = [video_attr]
                            logger.info(
                                f"🎬 Video attributes: {video_attr.w}x{video_attr.h}, {video_attr.duration}s")

                    await Telegram_client.send_file(
                        entity,
                        output_path,
                        caption=caption,
                        parse_mode="html",
                        supports_streaming=True,  # 🔑 video sifatida yuboriladi
                        progress_callback=progress,
                        attributes=attributes,  # 🎬 Video attributes qo'shish
                        force_document=False,   # Video'ni video sifatida yuborish
                    )

            duration = time.time() - start_time
            logger.info(
                f"✅ Telegramga yuborildi: {filename} ({duration:.1f}s)")

            # Muvaffaqiyatli uploadni diagnostics ga qayd qilish
            diagnostics.log_success(filename, duration)
            return True

        except asyncio.TimeoutError:
            duration = time.time() - start_time
            error_msg = f"Timeout: {filename} telegramga yuklash {self.timeout//60} daqiqadan oshdi"
            logger.error(f"⏰ {error_msg}")

            # Timeout error ni diagnostics ga qayd qilish
            diagnostics.log_error(filename, size, error_msg,
                                  "TimeoutError", duration)
            return False
        except Exception as e:
            import traceback
            duration = time.time() - start_time
            error_msg = str(e)
            full_traceback = traceback.format_exc()

            # Telegram API xatoliklarini aniqlash
            if "wait of" in error_msg and "seconds" in error_msg:
                logger.error(
                    f"⏰ Telegram rate limit: {filename} - {error_msg}")
            elif "PEER_FLOOD" in error_msg:
                logger.error(
                    f"🚫 Telegram flood limit: {filename} - {error_msg}")
            elif "FILE_PARTS_INVALID" in error_msg:
                logger.error(f"💔 Fayl corruption: {filename} - {error_msg}")
            elif "AUTH_KEY_INVALID" in error_msg:
                logger.error(
                    f"🔑 Auth invalid: {filename} - Telegram client qayta ulaning")
            elif "CONNECTION_NOT_INITED" in error_msg:
                logger.error(
                    f"🔌 Connection xato: {filename} - Telegram client ishga tushmagan")
            else:
                logger.error(f"❌ Noma'lum xato: {filename} - {error_msg}")

            logger.error(f"🔍 Full traceback:\n{full_traceback}")

            # Barcha xatolarni diagnostics ga qayd qilish
            diagnostics.log_error(filename, size if 'size' in locals(
            ) else 0, error_msg, full_traceback, duration)
            return False

    async def _create_caption(self, item: Dict[str, Any], size: int) -> str:
        """Caption yaratish"""
        logger.info("🔍 Caption yaratish boshlandi")
        logo = item.get("image", None)
        # logo ni faqat to'g'ri URL bo'lsa yoki data:image emas va None emas bo'lsa qo'shamiz
        if (
            not logo
            or not isinstance(logo, str)
            or logo.strip() == ""
            or logo.startswith("data:image")
        ):
            logo = None
        try:
            # Categories ni to'g'ri formatda olish
            categories = item.get("categories", [])
            # Agar string bo'lsa, uni split qilamiz yoki list sifatida qoldiramiz
            if isinstance(categories, str):
                # Agar vergul bilan ajratilgan bo'lsa
                categories = [cat.strip()
                              for cat in categories.split(",") if cat.strip()]
            elif not isinstance(categories, list):
                categories = []

            caption_data = {
                "title": item.get("title", "No title"),
                "lang": item.get("language", "uz"),
                "category_id": ", ".join(
                    map(str, categories_to_ids(categories))
                ),
                "actors": item.get("actors") or "",
                "year": item.get("year") or "",
                "country": item.get("country") or "",
                "categories": ", ".join(categories),
                "file_size": size,  # ✅ Bytes formatda
                "url": item.get("file_url") or "",
                "desc": (item.get("description") or "")[:500],
            }
            if logo:
                # faqat logo mavjud va to'g'ri bo'lsa qo'shamiz
                caption_data["logo"] = logo

            caption = make_caption(caption_data)
            caption = caption[:4096]  # Telegram limit
            logger.info("✅ Caption yaratildi")
            logger.info(f"📝 Caption uzunligi: {len(caption)} belgi")
            return caption
        except Exception as caption_error:
            logger.error(f"❌ Caption yaratishda xato: {caption_error}")
            return f"📄 {item.get('title', 'No title')}\n💾 Hajmi: {size} bytes"

    async def _get_telegram_entity(self, group_ref: Optional[str] = None):
        """Telegram entity olish"""
        # 📌 Telegram client ulanganligini tekshiramiz
        if not Telegram_client.is_connected():
            logger.warning(
                "⚠️ Telegram client ulanmagan, qayta ulanishga harakat qilamiz")
            await Telegram_client.connect()

        # 📌 Guruhni aniqlaymiz
        target_group = group_ref or self.default_group

        # Guruh bo'sh bo'lsa xato
        if not target_group or target_group.strip() == "":
            logger.error(
                "❌ Telegram guruh ID si berilmagan! Config da 'telegram_group' parametrini to'ldiring.")
            logger.error(
                f"💡 Yoki default_group ishlatiladi: {self.default_group}")
            target_group = self.default_group

        logger.info(f"🔍 Guruhni aniqlash: {target_group}")

        entity = await resolve_group(target_group)
        return entity
