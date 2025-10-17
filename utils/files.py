from pathlib import Path
from tqdm.asyncio import tqdm
import re
from utils.logger_core import logger


async def fetch_file(session, url, output_path, sem):
    async with sem:  # 🔑 parallel yuklashni cheklash
        async with session.get(url) as resp:
            resp.raise_for_status()
            total = int(resp.headers.get("Content-Length", 0))
            downloaded = 0

            with open(output_path, "wb") as f, tqdm(
                total=total,
                unit="B",
                unit_scale=True,
                desc=Path(output_path).name,
                leave=False,
            ) as pbar:
                async for chunk in resp.content.iter_chunked(1024 * 1024):
                    f.write(chunk)
                    downloaded += len(chunk)
                    pbar.update(len(chunk))

            return {
                "size": downloaded,
                "mime": resp.headers.get("Content-Type"),
                "ext": Path(output_path).suffix,
            }


def safe_filename(name: str, ext: str = "") -> str:
    """
    Fayl nomidan OS taqiqlangan belgilarni olib tashlaydi.
    """
    # ruxsat etilmagan belgilarni _ ga almashtiramiz
    name = re.sub(r'[\\/*?:"<>|]', "_", name)
    return f"{name}{ext}"


async def get_file_size(session, url: str) -> int:
    """HEAD yoki Range GET orqali fayl hajmini aniqlash."""
    try:
        # 1️⃣ Avval HEAD bilan sinab ko‘ramiz
        async with session.head(url, timeout=15, allow_redirects=True) as resp:
            if resp.status == 200 and "Content-Length" in resp.headers:
                return int(resp.headers["Content-Length"])

        # 2️⃣ Agar HEAD ishlamasa, GET bilan Range yuboramiz
        headers = {"Range": "bytes=0-1"}
        async with session.get(url, headers=headers, timeout=15, allow_redirects=True) as resp:
            if resp.status in (200, 206):
                # Content-Range: bytes 0-1/12345678
                crange = resp.headers.get("Content-Range")
                if crange and "/" in crange:
                    total_size = crange.split("/")[-1]
                    if total_size.isdigit():
                        return int(total_size)
                # fallback – Content-Length
                if "Content-Length" in resp.headers:
                    return int(resp.headers["Content-Length"])
    except Exception as e:
        logger.warning(f"⚠️ Fayl hajmini aniqlab bo‘lmadi: {url} | {e}")

    return 0


async def get_small_url(filepage: str, attempt: int = 1) -> str | None:
    """
    Fayl nomidagi sifatni kamaytirish orqali kichikroq URL qaytaradi.
    Masalan: https://cdn.site/video_1080.mp4 -> video_720.mp4 -> video_480.mp4
    """
    if not filepage:
        return None

    if "1080" in filepage:
        return filepage.replace("1080", "720") if attempt == 1 else filepage.replace("1080", "480")
    elif "720" in filepage and attempt > 1:
        return filepage.replace("720", "480")
    return None
