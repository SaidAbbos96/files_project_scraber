import subprocess
import os
from typing import Optional


class VideoCompressor:
    """
    Video siqish va optimallashtirish uchun class.
    FFmpeg talab etiladi (https://ffmpeg.org/download.html).
    """

    RESOLUTIONS = {
        "480p": "640x480",
        "720p": "1280x720",
        "1080p": "1920x1080",
        "1440p": "2560x1440",
        "2160p": "3840x2160",  # 4K
    }

    QUALITY_PRESETS = {"low": 28, "medium": 23, "high": 18, "lossless": 0}

    def __init__(self, codec: str = "libx265", audio_codec: str = "aac"):
        """
        codec: Video kodek ('libx264', 'libx265', 'libaom-av1')
        audio_codec: Audio kodek ('aac', 'libopus', ...)
        """
        self.codec = codec
        self.audio_codec = audio_codec

    def compress(
        self,
        input_file: str,
        output_file: Optional[str] = None,
        resolution: Optional[str] = None,
        quality: str = "medium",
        crf: Optional[int] = None,
        preset: str = "fast",
    ) -> str:
        """
        Videoni siqadi va optimallashtiradi.

        input_file: kiruvchi video fayl
        output_file: chiqish fayli (default: inputname_compressed.mp4)
        resolution: '480p', '720p', '1080p', '1440p', '2160p'
        quality: 'low', 'medium', 'high', 'lossless'
        crf: aniq CRF qiymati (agar berilsa, quality ustidan yozadi)
        preset: ffmpeg tezlik/sifat balans parametri ('ultrafast' ... 'veryslow')
        """

        if not os.path.exists(input_file):
            raise FileNotFoundError(f"❌ Fayl topilmadi: {input_file}")

        # Chiqish fayl nomi
        if output_file is None:
            name, ext = os.path.splitext(input_file)
            output_file = f"{name}_compressed.mp4"

        # CRF qiymatini aniqlash
        if crf is None:
            crf = self.QUALITY_PRESETS.get(quality, 23)

        # Resolution parametri
        scale_cmd = []
        if resolution and resolution in self.RESOLUTIONS:
            scale_cmd = ["-vf", f"scale={self.RESOLUTIONS[resolution]}"]

        # FFmpeg komandasi
        cmd = (
            [
                "ffmpeg",
                "-y",  # -y mavjud faylni ustidan yozadi
                "-i",
                input_file,
                "-c:v",
                self.codec,
                "-preset",
                preset,
                "-crf",
                str(crf),
                "-c:a",
                self.audio_codec,
                "-b:a",
                "128k",  # audio sifatini baland ushlab qoladi
            ]
            + scale_cmd
            + [output_file]
        )

        # Komandani ishga tushirish
        subprocess.run(cmd, check=True)

        return output_file


# === Foydalanish misoli ===
if __name__ == "__main__":
    compressor = VideoCompressor(codec="libx265")

    out = compressor.compress(
        input_file="video.mp4",
        resolution="720p",  # 480p / 720p / 1080p / 1440p / 2160p
        quality="high",  # low / medium / high / lossless
        preset="fast",  # ultrafast / superfast / veryfast / fast / medium / slow / veryslow
    )
    compressor = VideoCompressor(codec="libx265")
    print(f"✅ Siqilgan video: {out}")

    # out = compressor.compress(
    #     input_file="video.mp4",
    #     resolution="1080p",    # yoki umuman bermasangiz, asl resolution saqlanadi
    #     quality="medium",      # low / medium / high / lossless
    #     preset="fast"          # tezlik va siqish samaradorligi balansi
    # )

    # print(f"✅ Yengilroq video: {out}")
