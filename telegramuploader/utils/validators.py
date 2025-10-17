"""
File Validation Utilities
"""
import os
from typing import Tuple


class FileValidator:
    """Fayl validation uchun utility class"""
    
    @staticmethod
    def check_file_exists(file_path: str) -> bool:
        """Fayl mavjudligini tekshirish"""
        return os.path.exists(file_path) and os.path.isfile(file_path)
    
    @staticmethod  
    def get_file_size(file_path: str) -> int:
        """Fayl hajmini olish (bytes)"""
        if not FileValidator.check_file_exists(file_path):
            return 0
        return os.path.getsize(file_path)
    
    @staticmethod
    def validate_size_match(local_size: int, expected_size: int, tolerance_mb: int = 5) -> Tuple[bool, str, float]:
        """
        Fayl hajmini tekshirish
        
        Args:
            local_size: Local fayl hajmi (bytes)
            expected_size: Kutilayotgan hajm (bytes)  
            tolerance_mb: Tolerance (MB)
        
        Returns:
            (is_valid, reason, diff_mb) tuple
        """
        if expected_size <= 0:
            return True, "Server hajmi noma'lum, mavjud faylni ishlatamiz", 0.0
            
        size_diff = abs(local_size - expected_size)
        diff_mb = size_diff / (1024 ** 2)
        tolerance_bytes = tolerance_mb * 1024 * 1024
        
        if size_diff <= tolerance_bytes:
            return True, f"Hajm mos keladi (farq: {diff_mb:.1f}MB)", diff_mb
        else:
            return False, f"Hajm farqi katta: {diff_mb:.1f}MB", diff_mb


class SizeFormatter:
    """Hajm formatlovchi utility class"""
    
    @staticmethod
    def bytes_to_gb(size_bytes: int) -> float:
        """Bytes'ni GB ga aylantirish"""
        return size_bytes / (1024 ** 3) if size_bytes > 0 else 0.0
    
    @staticmethod
    def bytes_to_mb(size_bytes: int) -> float:
        """Bytes'ni MB ga aylantirish"""
        return size_bytes / (1024 ** 2) if size_bytes > 0 else 0.0
    
    @staticmethod
    def format_size(size_bytes: int, unit: str = "auto") -> str:
        """
        Hajmni human-readable formatga aylantirish
        
        Args:
            size_bytes: Hajm bytes da
            unit: "auto", "MB", "GB", "bytes"
        
        Returns:
            Formatted string
        """
        if unit == "bytes":
            return f"{size_bytes} bytes"
        elif unit == "MB":
            return f"{SizeFormatter.bytes_to_mb(size_bytes):.2f} MB"
        elif unit == "GB":
            return f"{SizeFormatter.bytes_to_gb(size_bytes):.2f} GB"
        else:  # auto
            if size_bytes >= 1024 ** 3:  # >= 1GB
                return f"{SizeFormatter.bytes_to_gb(size_bytes):.2f} GB"
            elif size_bytes >= 1024 ** 2:  # >= 1MB
                return f"{SizeFormatter.bytes_to_mb(size_bytes):.2f} MB"
            else:
                return f"{size_bytes} bytes"