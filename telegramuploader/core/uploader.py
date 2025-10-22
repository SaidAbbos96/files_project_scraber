"""
Telegram Uploader - Telegramga fayl yuborish uchun
"""
import html
import os
import re
import sys
import time
from pathlib import Path
from typing import Any, Dict, Optional

from telethon.tl.types import DocumentAttributeVideo
from tqdm.asyncio import tqdm
from core.config import FILES_GROUP_ID, FILES_GROUP_LINK, WORKER_NAME, TELEGRAM_USER_IS_PREMIUM
from telegramuploader.telegram.telegram_client import Telegram_client, resolve_group
from telegramuploader.utils.diagnostics import diagnostics
from utils.helpers import format_file_size
from utils.logger_core import logger
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
                # logger.info(
                #     f"📹 Direct method: {video_info['width']}x{video_info['height']}, {video_info['duration']:.1f}s")
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
                        # logger.info(f"✅ Direct ffprobe success: {cmd}")
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

                    # logger.info(
                    #     f"✅ Video validation OK: {width}x{height}, {codec}, {duration:.1f}s")
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
            # logger.info(
            #     f"🔍 Upload funksiyasiga kirildi: {item.get('title', 'No title')}")

            # Debug: item structure
            # logger.info(f"🔍 Item keys: {list(item.keys())}")
            # logger.info(f"🔍 local_path: {item.get('local_path', 'NOT_FOUND')}")

            # ✅ Absolut path olish
            try:
                output_path = os.path.abspath(item["local_path"])
                filename = Path(output_path).name
                size = item.get("file_size", 0)
                # logger.info(f"📁 Fayl path: {output_path}")
                # logger.info(f"💾 Fayl hajmi: {size} bytes")
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
                # logger.info(f"🎬 Video fayl validation: {filename}")
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

            # --- PREMIUM LIMIT CHECK ---

            if TELEGRAM_USER_IS_PREMIUM is False and size > 2 * 1024 * 1024 * 1024:
                logger.warning(f"⏭️ Premium emas: {filename} ({size} bytes) 2GB dan katta, o'tkazib yuborildi!")
                diagnostics.log_error(filename, size, "Not premium, skipped", "File >2GB, not premium", 0)
                return False

            # 📌 Caption yaratish
            caption = await self._create_caption(item, size)

            # --- BOT API URL UPLOAD LOGIC ---
            # If enabled, try to send via bot API (URL) if file size <= 2GB and file_url exists
            use_bot_api = config.get("use_bot_api_upload", False)
            bot_token = config.get("bot_api_token")
            bot_chat_id = config.get("bot_api_chat_id") or FILES_GROUP_ID
            file_url = item.get("file_url")
            size2GB = 2 * 1024 * 1024 * 1024
            if use_bot_api and bot_token and bot_chat_id and file_url and size <= size2GB:
                try:
                    from telegramuploader.utils.bot_api import send_file_by_url_via_bot
                    is_video = self.is_video_file(filename)
                    bot_result = send_file_by_url_via_bot(
                        token=bot_token,
                        chat_id=bot_chat_id,
                        file_url=file_url,
                        caption=caption,
                        as_video=is_video
                    )
                    if bot_result.get("ok"):
                        logger.info(f"✅ BOT API orqali yuborildi: {filename}")
                        diagnostics.log_success(
                            filename, time.time() - start_time)
                        return True
                    else:
                        logger.warning(
                            f"⚠️ BOT API orqali yuborib bo'lmadi: {bot_result}")
                except Exception as bot_api_error:
                    logger.warning(
                        f"⚠️ BOT API upload xatolik: {bot_api_error}")

            # logger.info(f"📜 Caption: {caption}")
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
            # logger.info(f"📤 Telegram send_file ishga tushmoqda...")

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
                        # logger.info(
                        #     f"🎬 Video attributes: {video_attr.w}x{video_attr.h}, {video_attr.duration}s")

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
        """Caption yaratish - hashtag parameter formatida"""
        try:
            # Categories ni to'g'ri formatda olish
            from core.catigories import CATEGORY_MAP, CATEGORY_NAME_TO_ID

            categories = item.get("categories", [])
            category_names = []
            category_ids = []

            # Agar string bo'lsa, uni split qilamiz
            if isinstance(categories, str):
                # Agar vergul bilan ajratilgan raqamlar yoki nomlar bo'lsa: "1,5,20" yoki "other, drama, crime"
                raw_categories = [cat.strip()
                                  for cat in categories.split(",") if cat.strip()]
                for cat_item in raw_categories:
                    try:
                        # Avval raqam emasligini tekshiramiz
                        cat_num = int(cat_item)
                        category_ids.append(str(cat_num))
                        # CATEGORY_MAP dan nom topish
                        if cat_num in CATEGORY_MAP:
                            category_names.append(CATEGORY_MAP[cat_num])
                        else:
                            # Agar raqam yo'q bo'lsa, raqamni o'zini qo'shamiz
                            category_names.append(f"category_{cat_num}")
                    except ValueError:
                        # Agar raqam emas bo'lsa, nom deb hisoblaymiz va ID topamiz
                        category_name = cat_item
                        category_names.append(category_name)
                        # Nom orqali ID topish
                        if category_name in CATEGORY_NAME_TO_ID:
                            category_ids.append(
                                str(CATEGORY_NAME_TO_ID[category_name]))
                        else:
                            # Agar nom topilmasa ham, default ID berish
                            logger.warning(
                                f"🔍 CATEGORY WARNING: '{category_name}' ID topilmadi")
                            # Default 'other' category ID (1) berish
                            if 'other' in CATEGORY_NAME_TO_ID:
                                category_ids.append(
                                    str(CATEGORY_NAME_TO_ID['other']))
            elif isinstance(categories, list):
                # Agar list bo'lsa, har bir elementni tekshiramiz
                for cat in categories:
                    if isinstance(cat, (int, str)):
                        try:
                            cat_num = int(cat)
                            # ✅ ID ham qo'shiladi
                            category_ids.append(str(cat_num))
                            if cat_num in CATEGORY_MAP:
                                category_names.append(CATEGORY_MAP[cat_num])
                            else:
                                category_names.append(f"category_{cat_num}")
                        except ValueError:
                            # Agar raqam bo'lmasa, nom deb hisoblaymiz
                            category_name = str(cat)
                            category_names.append(category_name)
                            # Nom orqali ID topish
                            if category_name in CATEGORY_NAME_TO_ID:
                                category_ids.append(
                                    str(CATEGORY_NAME_TO_ID[category_name]))
                            else:
                                logger.warning(
                                    f"🔍 CATEGORY WARNING: '{category_name}' ID topilmadi")
                                # Default 'other' category ID berish
                                if 'other' in CATEGORY_NAME_TO_ID:
                                    category_ids.append(
                                        str(CATEGORY_NAME_TO_ID['other']))
            else:
                # Agar categories boshqa tur bo'lsa (int, None, etc.)
                if categories:
                    try:
                        cat_num = int(categories)
                        category_ids.append(str(cat_num))
                        if cat_num in CATEGORY_MAP:
                            category_names.append(CATEGORY_MAP[cat_num])
                        else:
                            category_names.append(f"category_{cat_num}")
                    except (ValueError, TypeError):
                        # Agar raqam bo'lmasa, nom deb hisoblaymiz
                        category_name = str(categories)
                        category_names.append(category_name)
                        # Nom orqali ID topish
                        if category_name in CATEGORY_NAME_TO_ID:
                            category_ids.append(
                                str(CATEGORY_NAME_TO_ID[category_name]))
                        else:
                            logger.warning(
                                f"🔍 CATEGORY WARNING: '{category_name}' ID topilmadi")
                            # Default 'other' category ID berish
                            if 'other' in CATEGORY_NAME_TO_ID:
                                category_ids.append(
                                    str(CATEGORY_NAME_TO_ID['other']))

            # Caption yaratish - hashtag parameter formatida
            caption_parts = []

            # Bot nomi
            caption_parts.append(f"#bot={WORKER_NAME}")

            # Title
            title = self._clean_text_for_caption(item.get("title", "No title"))
            caption_parts.append(f"#title={title}")

            # Language
            language = item.get("language", "")
            if language:
                clean_language = self._clean_text_for_caption(language)
                caption_parts.append(f"#lang={clean_language}")

            # Category IDs (vergul bilan ajratilgan raqamlar)
            if category_ids:
                caption_parts.append(f"#category_id={','.join(category_ids)}")

            # Actors
            actors = item.get("actors", "")
            if actors:
                clean_actors = self._clean_text_for_caption(actors)
                caption_parts.append(f"#actors={clean_actors}")

            # Year
            year = item.get("year", "")
            if year:
                caption_parts.append(f"#year={year}")

            # Country
            country = item.get("country", "")
            if country:
                clean_country = self._clean_text_for_caption(country)
                caption_parts.append(f"#country={clean_country}")

            # Categories (vergul bilan ajratilgan nomlar)
            if category_names:
                caption_parts.append(f"#categories={','.join(category_names)}")

            # File size (bytes)
            caption_parts.append(f"#file_size={size}")

            # URL (qo'shtirnoqsiz, toza)
            url = item.get("file_url", "")
            if url:
                # URL ni tozalash - faqat asosiy belgilarni olib tashlash
                clean_url = url.strip().replace('"', '').replace("'", '')
                caption_parts.append(f"#url={clean_url}")

            # Description (kuchli HTML tozalash va qisqartirish)
            description = item.get("description", "")
            if description:
                clean_desc = self._clean_text_for_caption(description)
                # Qo'shimcha HTML tozalash description uchun
                clean_desc = self._extra_html_clean(clean_desc)

                # Description'ni qisqartirish - 150 belgigacha
                if len(clean_desc) > 150:
                    clean_desc = clean_desc[:500] + "..."

                caption_parts.append(f"#desc={clean_desc}")

            caption = "\n".join(caption_parts)

            # Final hashtag caption tozalash - oddiy va samarali
            caption = self._hashtag_caption_cleanup(caption)
            caption = caption[:4096]  # Telegram limit

            return caption

        except Exception as caption_error:
            logger.error(f"❌ Caption yaratishda xato: {caption_error}")
            clean_title = self._clean_text_for_caption(
                item.get('title', 'No title'))
            return f"#title={clean_title}\n#file_size={size}"

    def _clean_text_for_caption(self, text: str) -> str:
        """Caption uchun matnni tozalash - butunlay HTML-siz (Enhanced)"""
        if not text or not isinstance(text, str):
            return ""

        # HTML entities decode qilish
        text = html.unescape(text)

        # Barcha HTML teglarni olib tashlash - kuchaytirilan versiya
        # 1. Script va style teglar ichidagi kontentni butunlay olib tashlash
        text = re.sub(r'<script[^>]*>.*?</script>', '',
                      text, flags=re.DOTALL | re.IGNORECASE)
        text = re.sub(r'<style[^>]*>.*?</style>', '',
                      text, flags=re.DOTALL | re.IGNORECASE)

        # 2. Barcha HTML teglarni olib tashlash (attributes bilan)
        text = re.sub(r'<[^>]+>', '', text)

        # 3. HTML entities larni tozalash
        text = text.replace('&amp;', '&')
        text = text.replace('&lt;', '<')
        text = text.replace('&gt;', '>')
        text = text.replace('&quot;', '"')
        text = text.replace('&apos;', "'")
        text = text.replace('&nbsp;', ' ')
        text = text.replace('&#39;', "'")
        text = text.replace('&#34;', '"')

        # 4. Ortiqcha bo'shliqlarni tozalash
        text = re.sub(r'\s+', ' ', text).strip()

        # 5. Telegram uchun xavfli belgilarni tozalash
        text = text.replace('`', "'")  # Backtick → apostrophe
        text = text.replace('*', '')   # Asterisk olib tashlash
        text = text.replace('_', '')   # Underscore olib tashlash
        text = text.replace('[', '(')  # Square bracket → round bracket
        text = text.replace(']', ')')
        text = text.replace('{', '(')  # Curly bracket → round bracket
        text = text.replace('}', ')')

        # 6. Qolgan HTML-ga o'xshash belgilarni tozalash
        text = re.sub(r'<+', '', text)  # < belgilar
        text = re.sub(r'>+', '', text)  # > belgilar

        # 7. Control characters ni olib tashlash
        text = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', text)

        return text.strip()

    def _extra_html_clean(self, text: str) -> str:
        """Qo'shimcha HTML tozalash - description uchun"""
        if not text or not isinstance(text, str):
            return ""

        # HTML class, id, style attributes bilan teglarni olib tashlash
        text = re.sub(r'<[^>]*class[^>]*>', '', text, flags=re.IGNORECASE)
        text = re.sub(r'<[^>]*id[^>]*>', '', text, flags=re.IGNORECASE)
        text = re.sub(r'<[^>]*style[^>]*>', '', text, flags=re.IGNORECASE)

        # Qolgan barcha HTML teglarni olib tashlash
        text = re.sub(r'<[^>]+>', '', text)

        # HTML entities
        text = text.replace('&nbsp;', ' ')
        text = text.replace('&hellip;', '...')
        text = text.replace('&mdash;', '-')
        text = text.replace('&ndash;', '-')
        text = text.replace('&laquo;', '"')
        text = text.replace('&raquo;', '"')

        # Ortiqcha bo'shliqlar
        text = re.sub(r'\s+', ' ', text).strip()

        return text

    def _hashtag_caption_cleanup(self, caption: str) -> str:
        """Hashtag format uchun maxsus tozalash"""
        if not caption:
            return ""

        # Faqat kerakli tozalash - hashtag formatni saqlab qolish
        # 1. HTML entities tozalash
        html_entities = {
            '&amp;': '&', '&lt;': '<', '&gt;': '>', '&quot;': '"', '&apos;': "'",
            '&nbsp;': ' ', '&#39;': "'", '&#34;': '"'
        }
        for entity, replacement in html_entities.items():
            caption = caption.replace(entity, replacement)

        # 2. Numeric va hex HTML entities
        caption = re.sub(r'&#\d+;', '', caption)
        caption = re.sub(r'&#x[0-9a-fA-F]+;', '', caption)

        # 3. Ortiqcha bo'shliqlar va newline'lar
        caption = re.sub(r'\n{3,}', '\n\n', caption)  # 3+ newline → 2 newline
        caption = re.sub(r' {2,}', ' ', caption)       # 2+ space → 1 space

        # 4. Faqat Telegram uchun xavfli belgilarni olib tashlash
        # Hashtag format uchun `=`, `.`, `-` larni saqlab qolish
        dangerous_chars = ['`', '~', '|']  # Faqat eng xavfli belgilar
        for char in dangerous_chars:
            caption = caption.replace(char, '')

        return caption.strip()

    async def _get_telegram_entity(self, group_ref: Optional[str] = None):
        """Telegram entity olish"""
        # 📌 Telegram client ulanganligini tekshiramiz (session safe)
        from telegramuploader.telegram.telegram_client import safe_telegram_start
        if not await safe_telegram_start():
            return None

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
