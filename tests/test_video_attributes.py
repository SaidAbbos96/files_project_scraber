#!/usr/bin/env python3
"""
Video attributes va ffmpeg binary'larni tekshirish uchun test
"""
import os
import sys
import subprocess
import tempfile
from pathlib import Path

# Project root'ni sys.path ga qo'shish
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from telegramuploader.core.uploader import TelegramUploader
from utils.logger_core import logger


class VideoAttributesTest:
    """Video attributes test class"""
    
    def __init__(self):
        self.uploader = TelegramUploader()
        self.results = []
    
    def log_result(self, test_name: str, status: str, message: str):
        """Test natijasini yozish"""
        result = {
            'test': test_name,
            'status': status,
            'message': message
        }
        self.results.append(result)
        
        if status == "✅ PASS":
            print(f"✅ {test_name}: {message}")
        elif status == "❌ FAIL":
            print(f"❌ {test_name}: {message}")
        else:
            print(f"⚠️ {test_name}: {message}")
    
    def test_ffmpeg_availability(self):
        """FFmpeg binary'larning mavjudligini tekshirish"""
        print("\n🔍 FFmpeg Binary Availability Test")
        print("=" * 50)
        
        # 1. imageio-ffmpeg test
        try:
            import imageio_ffmpeg
            ffmpeg_path = imageio_ffmpeg.get_ffmpeg_exe()
            
            if ffmpeg_path and os.path.exists(ffmpeg_path):
                self.log_result("imageio-ffmpeg", "✅ PASS", f"FFmpeg found: {ffmpeg_path}")
                
                # Version check
                try:
                    result = subprocess.run([ffmpeg_path, '-version'], 
                                          capture_output=True, text=True, check=True, timeout=10)
                    version = result.stdout.split('\n')[0].split('version')[1].split()[0] if 'version' in result.stdout else 'unknown'
                    self.log_result("ffmpeg-version", "✅ PASS", f"Version: {version}")
                except Exception as e:
                    self.log_result("ffmpeg-version", "❌ FAIL", f"Version check failed: {e}")
            else:
                self.log_result("imageio-ffmpeg", "❌ FAIL", "FFmpeg binary not found")
                
        except ImportError:
            self.log_result("imageio-ffmpeg", "❌ FAIL", "imageio-ffmpeg not installed")
        except Exception as e:
            self.log_result("imageio-ffmpeg", "❌ FAIL", f"Error: {e}")
        
        # 2. System ffmpeg test
        system_paths = ['/usr/bin/ffmpeg', '/usr/local/bin/ffmpeg', 'ffmpeg']
        for path in system_paths:
            try:
                result = subprocess.run([path, '-version'], 
                                      capture_output=True, check=True, timeout=10)
                self.log_result(f"system-ffmpeg-{path}", "✅ PASS", f"System FFmpeg found: {path}")
                break
            except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired):
                self.log_result(f"system-ffmpeg-{path}", "❌ FAIL", f"Not found: {path}")
        
        # 3. ffprobe test
        ffprobe_paths = ['/usr/bin/ffprobe', '/usr/local/bin/ffprobe', 'ffprobe']
        for path in ffprobe_paths:
            try:
                result = subprocess.run([path, '-version'], 
                                      capture_output=True, check=True, timeout=10)
                self.log_result(f"system-ffprobe-{path}", "✅ PASS", f"System FFprobe found: {path}")
                break
            except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired):
                self.log_result(f"system-ffprobe-{path}", "❌ FAIL", f"Not found: {path}")
    
    def test_ffmpeg_python_wrapper(self):
        """ffmpeg-python wrapper'ni tekshirish"""
        print("\n🐍 FFmpeg-Python Wrapper Test")
        print("=" * 50)
        
        try:
            import ffmpeg
            self.log_result("ffmpeg-python-import", "✅ PASS", "ffmpeg-python imported successfully")
            
            # Simple probe test with non-existent file
            try:
                ffmpeg.probe('/non/existent/file.mp4')
                self.log_result("ffmpeg-probe-test", "❌ FAIL", "Should have failed with non-existent file")
            except ffmpeg.Error as e:
                self.log_result("ffmpeg-probe-test", "✅ PASS", "Correctly failed with non-existent file")
            except Exception as e:
                self.log_result("ffmpeg-probe-test", "⚠️ WARN", f"Unexpected error: {e}")
                
        except ImportError:
            self.log_result("ffmpeg-python-import", "❌ FAIL", "ffmpeg-python not installed")
        except Exception as e:
            self.log_result("ffmpeg-python-import", "❌ FAIL", f"Import error: {e}")
    
    def test_video_attributes_function(self):
        """TelegramUploader.get_video_attributes funksiyasini tekshirish"""
        print("\n🎬 Video Attributes Function Test")
        print("=" * 50)
        
        # Test with non-existent file
        try:
            result = self.uploader.get_video_attributes('/non/existent/video.mp4')
            if result and result.w == 1280 and result.h == 720:
                self.log_result("video-attrs-fallback", "✅ PASS", 
                              f"Fallback attributes work: {result.w}x{result.h}")
            else:
                self.log_result("video-attrs-fallback", "❌ FAIL", 
                              f"Unexpected result: {result}")
        except Exception as e:
            self.log_result("video-attrs-fallback", "❌ FAIL", f"Function error: {e}")
    
    def test_video_file_detection(self):
        """Video fayl detection test"""
        print("\n📁 Video File Detection Test")
        print("=" * 50)
        
        test_cases = [
            ('video.mp4', True),
            ('video.avi', True),
            ('video.mkv', True),
            ('video.mov', True),
            ('video.MP4', True),  # Case insensitive
            ('document.pdf', False),
            ('image.jpg', False),
            ('audio.mp3', False),
            ('video', False),  # No extension
        ]
        
        for filename, expected in test_cases:
            result = self.uploader.is_video_file(filename)
            if result == expected:
                self.log_result(f"video-detection-{filename}", "✅ PASS", 
                              f"Correctly detected: {result}")
            else:
                self.log_result(f"video-detection-{filename}", "❌ FAIL", 
                              f"Expected {expected}, got {result}")
    
    def create_test_video(self) -> str:
        """Test uchun minimal video fayl yaratish (ffmpeg orqali)"""
        try:
            # Temp fayl yaratish
            temp_file = tempfile.NamedTemporaryFile(suffix='.mp4', delete=False)
            temp_path = temp_file.name
            temp_file.close()
            
            # FFmpeg binary topish
            ffmpeg_path = None
            
            # imageio-ffmpeg dan olishga harakat
            try:
                import imageio_ffmpeg
                ffmpeg_path = imageio_ffmpeg.get_ffmpeg_exe()
            except ImportError:
                pass
            
            # System ffmpeg
            if not ffmpeg_path:
                for path in ['/usr/bin/ffmpeg', '/usr/local/bin/ffmpeg', 'ffmpeg']:
                    try:
                        subprocess.run([path, '-version'], capture_output=True, check=True, timeout=5)
                        ffmpeg_path = path
                        break
                    except:
                        continue
            
            if not ffmpeg_path:
                return None
            
            # 1 sekund test video yaratish (qizil kvadrat)
            cmd = [
                ffmpeg_path,
                '-f', 'lavfi',
                '-i', 'color=red:size=320x240:duration=1',
                '-y',  # Overwrite
                temp_path
            ]
            
            result = subprocess.run(cmd, capture_output=True, timeout=30)
            
            if result.returncode == 0 and os.path.exists(temp_path) and os.path.getsize(temp_path) > 0:
                self.log_result("test-video-creation", "✅ PASS", f"Test video created: {temp_path}")
                return temp_path
            else:
                self.log_result("test-video-creation", "❌ FAIL", 
                              f"Failed to create video. Return code: {result.returncode}")
                return None
                
        except Exception as e:
            self.log_result("test-video-creation", "❌ FAIL", f"Error creating test video: {e}")
            return None
    
    def test_real_video_attributes(self):
        """Haqiqiy video fayl bilan attributes test"""
        print("\n🎥 Real Video Attributes Test")
        print("=" * 50)
        
        # Test video yaratish
        test_video = self.create_test_video()
        
        if not test_video:
            self.log_result("real-video-test", "⚠️ SKIP", "Could not create test video")
            return
        
        try:
            # Video attributes olish
            attrs = self.uploader.get_video_attributes(test_video)
            
            if attrs:
                self.log_result("real-video-attrs", "✅ PASS", 
                              f"Attributes extracted: {attrs.w}x{attrs.h}, {attrs.duration}s")
                
                # Expected values check
                if attrs.w == 320 and attrs.h == 240:
                    self.log_result("video-dimensions", "✅ PASS", "Correct dimensions extracted")
                else:
                    self.log_result("video-dimensions", "⚠️ WARN", 
                                  f"Unexpected dimensions: {attrs.w}x{attrs.h}")
                
                if attrs.duration >= 0 and attrs.duration <= 2:  # ~1 second video
                    self.log_result("video-duration", "✅ PASS", f"Duration seems correct: {attrs.duration}s")
                else:
                    self.log_result("video-duration", "⚠️ WARN", 
                                  f"Unexpected duration: {attrs.duration}s")
            else:
                self.log_result("real-video-attrs", "❌ FAIL", "No attributes returned")
                
        except Exception as e:
            self.log_result("real-video-attrs", "❌ FAIL", f"Error: {e}")
        finally:
            # Cleanup
            try:
                if os.path.exists(test_video):
                    os.unlink(test_video)
                    self.log_result("test-cleanup", "✅ PASS", "Test video cleaned up")
            except Exception as e:
                self.log_result("test-cleanup", "⚠️ WARN", f"Cleanup error: {e}")
    
    def print_summary(self):
        """Test natijalarini umumlashtirish"""
        print("\n📊 TEST SUMMARY")
        print("=" * 50)
        
        total = len(self.results)
        passed = len([r for r in self.results if r['status'] == '✅ PASS'])
        failed = len([r for r in self.results if r['status'] == '❌ FAIL'])
        warned = len([r for r in self.results if r['status'] == '⚠️ WARN' or r['status'] == '⚠️ SKIP'])
        
        print(f"Total tests: {total}")
        print(f"✅ Passed: {passed}")
        print(f"❌ Failed: {failed}")
        print(f"⚠️ Warnings/Skipped: {warned}")
        
        if failed == 0:
            print("\n🎉 All critical tests passed!")
        else:
            print(f"\n⚠️ {failed} tests failed - check the details above")
        
        return failed == 0
    
    def run_all_tests(self):
        """Barcha testlarni ishga tushirish"""
        print("🧪 VIDEO ATTRIBUTES COMPREHENSIVE TEST")
        print("=" * 60)
        
        self.test_ffmpeg_availability()
        self.test_ffmpeg_python_wrapper()
        self.test_video_attributes_function()
        self.test_video_file_detection()
        self.test_real_video_attributes()
        
        return self.print_summary()


def main():
    """Main test runner"""
    try:
        tester = VideoAttributesTest()
        success = tester.run_all_tests()
        
        if success:
            print("\n✅ All tests completed successfully!")
            return 0
        else:
            print("\n❌ Some tests failed!")
            return 1
            
    except KeyboardInterrupt:
        print("\n⚠️ Tests interrupted by user")
        return 130
    except Exception as e:
        print(f"\n💥 Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit(main())