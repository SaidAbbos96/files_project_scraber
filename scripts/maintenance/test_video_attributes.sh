#!/bin/bash

# Server video test script
# Video attributes va upload testini amalga oshirish

echo "🔍 Video Attributes Test Script"
echo "================================"

# Virtual environment activate qilish
cd /home/aicoder/coding/files_project/files_project_scraber
source venv/bin/activate

echo "📦 Python environment:"
python --version
echo

echo "🔍 FFmpeg toollar:"
ffmpeg -version | head -1
ffprobe -version | head -1
echo

echo "🔍 Python packages:"
python -c "import ffmpeg; print('✅ ffmpeg-python installed')"
python -c "import imageio_ffmpeg; print('✅ imageio-ffmpeg installed')"
echo

echo "🎬 Video attributes test:"
python -c "
from telegramuploader.core.uploader import TelegramUploader
import tempfile
import subprocess
import os

# Test video yaratish
uploader = TelegramUploader()
with tempfile.NamedTemporaryFile(suffix='.mp4', delete=False) as tmp:
    test_file = tmp.name

try:
    # 3 sekund test video
    subprocess.run([
        'ffmpeg', '-f', 'lavfi', '-i', 'testsrc=duration=3:size=854x480:rate=25', 
        '-c:v', 'libx264', '-preset', 'ultrafast', '-t', '3', '-y', test_file
    ], capture_output=True, check=True, timeout=15)
    
    print(f'✅ Test video: {test_file}')
    
    # Attributes test
    attrs = uploader.get_video_attributes(test_file)
    print(f'📹 Attributes: {attrs.w}x{attrs.h}, {attrs.duration}s')
    
    file_size = os.path.getsize(test_file)
    print(f'📦 Size: {file_size/1024:.1f} KB')
    
    if attrs.w > 0 and attrs.h > 0 and attrs.duration > 0:
        print('✅ Video attributes WORKING!')
    else:
        print('❌ Video attributes FAILED!')
        
finally:
    if os.path.exists(test_file):
        os.remove(test_file)
"

echo
echo "🎉 Test completed!"