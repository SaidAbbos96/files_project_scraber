#!/usr/bin/env python3
"""
Test Runner - Barcha testlarni ishga tushirish uchun
"""
import os
import sys
import subprocess

# Project root ni sys.path ga qo'shish
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

def run_all_tests():
    """Barcha testlarni ishga tushirish"""
    test_files = [
        'test_enhanced_downloader.py',
        'test_real_download.py', 
        'test_diagnostics.py',
        'test_video_attributes.py'
    ]
    
    print("🧪 Running all tests...")
    print("=" * 50)
    
    passed = 0
    failed = 0
    
    for test_file in test_files:
        test_path = os.path.join(os.path.dirname(__file__), test_file)
        if os.path.exists(test_path):
            print(f"\n🔍 Running: {test_file}")
            try:
                result = subprocess.run([sys.executable, test_path], 
                                      capture_output=True, text=True, timeout=60)
                if result.returncode == 0:
                    print(f"✅ {test_file} - PASSED")
                    passed += 1
                else:
                    print(f"❌ {test_file} - FAILED")
                    print(f"Error: {result.stderr}")
                    failed += 1
            except subprocess.TimeoutExpired:
                print(f"⏰ {test_file} - TIMEOUT")
                failed += 1
            except Exception as e:
                print(f"💥 {test_file} - ERROR: {e}")
                failed += 1
        else:
            print(f"⚠️ {test_file} - NOT FOUND")
    
    print("\n" + "=" * 50)
    print(f"📊 Test Results: {passed} passed, {failed} failed")
    
    return failed == 0

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)