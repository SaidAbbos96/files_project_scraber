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

    def __init__(self, default_group: str = FILES_GROUP_LINK):
        """
        Args:
            default_group: Default Telegram group
        """
        self.default_group = default_group

    def get_video_attributes(self, file_path: str) -> Optional[DocumentAttributeVideo]:
        """Video fayl uchun attributes olish - Enhanced version"""
        try:
            import subprocess
            import json
            import ffmpeg

            # Multiple methods to get video info

            # Method 1: Direct subprocess with system tools
            video_info = self._get_video_info_direct(file_path)
            if video_info:
                logger.info(
                    f"📹 Direct method: {video_info['width']}x{video_info['height']}, {video_info['duration']:.1f}s")
                return DocumentAttributeVideo(
                    duration=int(video_info['duration']),
                    w=video_info['width'],
                    h=video_info['height'],
                    supports_streaming=True,
                    round_message=False
                )

            # Method 2: ffmpeg-python library
            video_info = self._get_video_info_ffmpeg_python(file_path)
            if video_info:
                logger.info(
                    f"� ffmpeg-python: {video_info['width']}x{video_info['height']}, {video_info['duration']:.1f}s")
                return DocumentAttributeVideo(
                    duration=int(video_info['duration']),
                    w=video_info['width'],
                    h=video_info['height'],
                    supports_streaming=True,
                    round_message=False
                )

            # Method 3: Fallback to default with some intelligence
            logger.warning("⚠️ Video info olib bo'lmadi, default attributes")
            return self._get_smart_default_attributes(file_path)

        except Exception as e:
            logger.error(f"❌ Video attributes critical error: {e}")
            return self._get_smart_default_attributes(file_path)

    def _get_video_info_direct(self, file_path: str) -> Optional[dict]:
        """Direct subprocess bilan video info olish"""
        try:
            import subprocess
            import json

            # 1. System ffprobe
            for cmd in ['ffprobe', '/usr/bin/ffprobe', '/usr/local/bin/ffprobe']:
                try:
                    result = subprocess.run([
                        cmd, '-v', 'quiet', '-print_format', 'json',
                        '-show_format', '-show_streams', file_path
                    ], capture_output=True, text=True, timeout=10, check=True)

                    data = json.loads(result.stdout)
                    video_stream = next((s for s in data.get(
                        'streams', []) if s.get('codec_type') == 'video'), None)

                    if video_stream:
                        width = int(video_stream.get('width', 1280))
                        height = int(video_stream.get('height', 720))
                        duration = float(
                            data.get('format', {}).get('duration', 0))
                        logger.info(f"✅ Direct ffprobe success: {cmd}")
                        return {'width': width, 'height': height, 'duration': duration}

                except (subprocess.CalledProcessError, FileNotFoundError, json.JSONDecodeError, subprocess.TimeoutExpired) as e:
                    logger.debug(f"🔄 {cmd} failed: {e}")
                    continue

            return None
        except Exception as e:
            logger.debug(f"Direct method error: {e}")
            return None

    def _get_video_info_ffmpeg_python(self, file_path: str) -> Optional[dict]:
        """ffmpeg-python library bilan video info olish"""
        try:
            import ffmpeg

            # Try with different ffmpeg/ffprobe paths
            for ffmpeg_cmd in ['ffprobe', '/usr/bin/ffprobe', 'ffmpeg']:
                try:
                    probe = ffmpeg.probe(file_path, cmd=ffmpeg_cmd)
                    video_stream = next(
                        (s for s in probe['streams'] if s['codec_type'] == 'video'), None)

                    if video_stream:
                        width = int(video_stream.get('width', 1280))
                        height = int(video_stream.get('height', 720))
                        duration = float(
                            probe.get('format', {}).get('duration', 0))
                        logger.info(f"✅ ffmpeg-python success: {ffmpeg_cmd}")
                        return {'width': width, 'height': height, 'duration': duration}

                except Exception as e:
                    logger.debug(f"🔄 ffmpeg-python {ffmpeg_cmd} failed: {e}")
                    continue

            return None
        except Exception as e:
            logger.debug(f"ffmpeg-python method error: {e}")
            return None

    def _get_smart_default_attributes(self, file_path: str) -> DocumentAttributeVideo:
        """Smart default attributes - file size asosida duration taxmin qilish"""
        try:
            file_size = os.path.getsize(file_path)
            # Taxminiy duration = file_size / (1MB/minute) - very rough estimate
            estimated_duration = max(
                60, min(7200, file_size // (1024 * 1024)))  # 1min - 2hours

            logger.info(
                f"🎬 Smart default: 1280x720, ~{estimated_duration}s (estimated from {file_size/1024/1024:.1f}MB)")

            return DocumentAttributeVideo(
                duration=int(estimated_duration),
                w=1280,
                h=720,
                supports_streaming=True,
                round_message=False
            )
        except Exception as e:
            logger.warning(f"⚠️ Smart default error: {e}")
            return self._get_default_video_attributes()

    def validate_video_file(self, file_path: str) -> tuple[bool, str]:
        """
        Video faylni telegramga yuborishdan avval tekshirish

        Args:
            file_path: Video fayl path'i

        Returns:
            (is_valid, reason) tuple
        """
        if not os.path.exists(file_path):
            return False, "Fayl topilmadi"

        file_size = os.path.getsize(file_path)
        if file_size == 0:
            return False, "Fayl bo'sh"

        if file_size < 1024:  # 1KB
            return False, "Fayl juda kichik (1KB dan kam)"

        # Video format tekshirish
        file_ext = Path(file_path).suffix.lower()
        if file_ext not in ['.mp4', '.avi', '.mkv', '.mov', '.wmv', '.flv', '.webm', '.m4v']:
            logger.warning(f"⚠️ Noma'lum video format: {file_ext}")

        # FFprobe bilan video stream tekshirish
        try:
            import subprocess
            import json

            for cmd in ['ffprobe', '/usr/bin/ffprobe', '/usr/local/bin/ffprobe']:
                try:
                    result = subprocess.run([
                        cmd, '-v', 'quiet', '-print_format', 'json',
                        '-show_streams', file_path
                    ], capture_output=True, text=True, timeout=15, check=True)

                    data = json.loads(result.stdout)
                    streams = data.get('streams', [])

                    # Video stream mavjudligini tekshirish
                    video_streams = [s for s in streams if s.get(
                        'codec_type') == 'video']
                    if not video_streams:
                        return False, "Video stream topilmadi"

                    video_stream = video_streams[0]

                    # Asosiy parametrlarni tekshirish
                    width = video_stream.get('width')
                    height = video_stream.get('height')

                    if not width or not height:
                        return False, "Video o'lchamlari aniqlanmadi"

                    if width < 64 or height < 64:
                        return False, f"Video juda kichik: {width}x{height}"

                    if width > 4096 or height > 4096:
                        return False, f"Video juda katta: {width}x{height}"

                    # Codec tekshirish
                    codec = video_stream.get('codec_name', 'unknown')
                    if codec in ['prores', 'rawvideo']:
                        logger.warning(
                            f"⚠️ Telegram uchun optimal emas codec: {codec}")

                    # Duration tekshirish
                    duration = float(video_stream.get('duration', 0))
                    if duration > 0:
                        if duration < 1:
                            return False, f"Video juda qisqa: {duration:.1f}s"
                        if duration > 14400:  # 4 hours
                            logger.warning(
                                f"⚠️ Juda uzun video: {duration/3600:.1f}h")

                    logger.info(
                        f"✅ Video validation OK: {width}x{height}, {codec}, {duration:.1f}s")
                    return True, f"Video valid: {width}x{height}, {codec}"

                except subprocess.CalledProcessError as e:
                    logger.debug(f"🔄 ffprobe {cmd} failed: {e}")
                    continue
                except json.JSONDecodeError as e:
                    logger.debug(f"🔄 JSON parse error: {e}")
                    continue
                except Exception as e:
                    logger.debug(f"🔄 ffprobe {cmd} error: {e}")
                    continue

            # FFprobe ishlamasa, basic file validation
            logger.warning("⚠️ FFprobe ishlamadi, basic validation")
            if file_size > 100 * 1024:  # 100KB dan katta bo'lsa OK deb hisoblaymiz
                return True, "Basic validation: fayl hajmi normal"
            else:
                return False, "Fayl juda kichik va FFprobe ishlamadi"

        except Exception as e:
            logger.error(f"❌ Video validation critical error: {e}")
            # Critical error bo'lsa ham, katta fayllarni o'tkazamiz
            if file_size > 1024 * 1024:  # 1MB+
                return True, "Validation error, lekin fayl katta - o'tkazildi"
            return False, f"Validation error: {e}"

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

            # 🎬 Video validation - telegramga yuborishdan avval tekshirish
            file_ext = Path(output_path).suffix.lower()
            if file_ext in ['.mp4', '.avi', '.mkv', '.mov', '.wmv', '.flv', '.webm', '.m4v']:
                logger.info(f"🎬 Video fayl validation: {filename}")
                is_valid, reason = self.validate_video_file(output_path)

                if not is_valid:
                    duration = time.time() - start_time
                    logger.error(f"❌ Video validation failed: {reason}")
                    diagnostics.log_error(
                        filename, size, "Invalid video", f"Video validation failed: {reason}", duration)
                    return False
                else:
                    pass
                    # logger.info(f"✅ Video validation passed: {reason}")

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

            # logger.info(
            #     f"✅ Guruh aniqlandi: {getattr(entity, 'title', str(entity))} !")
            logger.info(f"📤 Telegram send_file ishga tushmoqda...")

            # 📤 Timeout siz upload - muvaffaqiyatli yuklashni to'xtatmaymiz
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
                    parse_mode=None,  # ✅ HTML parsing ni o'chiramiz - oddiy matn
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
        # logger.info("🔍 Caption yaratish boshlandi")
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
            # logger.info("✅ Caption yaratildi")
            # logger.info(f"📝 Caption uzunligi: {len(caption)} belgi")
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

        # logger.info(f"🔍 Guruhni aniqlash: {target_group}")

        entity = await resolve_group(target_group)
        return entity
