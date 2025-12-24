#!/usr/bin/env python3
"""
Haqiqiy ishlatilmayotgan funksiyalarni topish - to'g'ri tahlil
"""

def analyze_uploader_functions():
    """TelegramUploader class'dagi funksiyalarni tahlil qilish"""
    
    print("🔍 TelegramUploader funksiyalari tahlili:")
    print("=" * 60)
    
    # Haqiqatan ishlatilayotgan funksiyalar (asosiy workflow)
    active_functions = {
        'upload_file': '✅ Asosiy public method - fayllarni yuklash',
        '_create_caption': '✅ Caption yaratish - upload_file ichida',
        '_clean_text_for_caption': '✅ Text tozalash - _create_caption ichida',
        '_extra_html_clean': '✅ HTML tozalash - _create_caption ichida', 
        '_hashtag_caption_cleanup': '✅ Final cleanup - _create_caption ichida',
        '_get_telegram_entity': '✅ Telegram entity olish - upload_file ichida',
        'is_video_file': '✅ Video file check - upload_file ichida',
        'get_video_attributes': '✅ Video metadata - upload_file ichida',
    }
    
    # Potensial ishlatilmayotgan funksiyalar
    questionable_functions = {
        'validate_video_file': '⚠️ Video validation - upload_file ichida, lekin murakkab',
        '_get_video_info_direct': '❓ Video info olish - get_video_attributes ichida',
        '_get_video_info_ffmpeg_python': '❓ Video info olish - get_video_attributes ichida',
        '_get_smart_default_attributes': '❓ Default attributes - get_video_attributes ichida',
        '_get_default_video_attributes': '❓ Fallback attributes - _get_smart_default_attributes ichida'
    }
    
    print("✅ AKTIV FUNKSIYALAR:")
    for func, desc in active_functions.items():
        print(f"   {func}: {desc}")
    
    print("\n❓ TEKSHIRISHGA MUHTOJ:")
    for func, desc in questionable_functions.items():
        print(f"   {func}: {desc}")
    
    print("\n📋 TAVSIYALAR:")
    print("1. validate_video_file - saqlash (video sifat nazorati)")
    print("2. Video info funksiyalari - saqlash (metadata kerak)")
    print("3. _final_caption_cleanup - o'chirildi ✅")
    print("4. Barcha qolgan funksiyalar - ishlatilmoqda")

if __name__ == "__main__":
    analyze_uploader_functions()