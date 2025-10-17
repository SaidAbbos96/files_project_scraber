#!/usr/bin/env python3
"""
System Diagnostics - Dastur uchun kerakli narsalarni tekshirish
"""
import os
import sys
import subprocess
import platform
import shutil
from pathlib import Path
from typing import Dict, List, Tuple, Optional
import importlib.util
from utils.logger_core import logger


class SystemDiagnostics:
    """Tizim diagnostikasi class"""
    
    def __init__(self):
        self.results = []
        self.requirements = []
        self.python_packages = []
        self.system_packages = []
        self.config_issues = []
        
    def log_result(self, category: str, name: str, status: str, message: str, fix_command: str = None):
        """Tekshiruv natijasini yozish"""
        result = {
            'category': category,
            'name': name,
            'status': status,
            'message': message,
            'fix_command': fix_command
        }
        self.results.append(result)
        
        status_emoji = {
            'OK': '✅',
            'WARN': '⚠️',
            'ERROR': '❌',
            'INFO': '📋'
        }
        
        emoji = status_emoji.get(status, '❓')
        print(f"{emoji} {category} - {name}: {message}")
        
        if fix_command and status in ['ERROR', 'WARN']:
            print(f"   💡 Fix: {fix_command}")
            
    def check_python_environment(self):
        """Python muhitini tekshirish"""
        print("\n🐍 PYTHON ENVIRONMENT CHECK")
        print("=" * 50)
        
        # Python version
        python_version = platform.python_version()
        major, minor = map(int, python_version.split('.')[:2])
        if major > 3 or (major == 3 and minor >= 8):
            self.log_result("Python", "Version", "OK", f"Python {python_version}")
        else:
            self.log_result("Python", "Version", "ERROR", 
                          f"Python {python_version} - 3.8+ kerak",
                          "Python 3.8+ o'rnating")
        
        # Virtual environment
        if hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
            venv_path = sys.prefix
            self.log_result("Python", "Virtual Environment", "OK", f"Active: {venv_path}")
        else:
            self.log_result("Python", "Virtual Environment", "WARN", 
                          "Virtual environment ishlatilmayapti",
                          "python -m venv venv && source venv/bin/activate")
        
        # Pip version
        try:
            result = subprocess.run([sys.executable, '-m', 'pip', '--version'], 
                                  capture_output=True, text=True, check=True)
            pip_version = result.stdout.split()[1]
            self.log_result("Python", "Pip", "OK", f"Pip {pip_version}")
        except Exception as e:
            self.log_result("Python", "Pip", "ERROR", f"Pip xato: {e}", 
                          "python -m ensurepip --upgrade")
    
    def check_required_python_packages(self):
        """Kerakli Python paketlarni tekshirish"""
        print("\n📦 PYTHON PACKAGES CHECK")
        print("=" * 50)
        
        required_packages = {
            'aiohttp': '3.12.15',
            'playwright': '1.55.0',
            'beautifulsoup4': '4.14.2',
            'telethon': '1.41.2',
            'tqdm': '4.67.1',
            'ffmpeg-python': '0.2.0',
            'imageio-ffmpeg': '0.4.9',
            'UzTransliterator': '0.0.36',
            'python-dotenv': '1.1.1'
        }
        
        for package, min_version in required_packages.items():
            try:
                # Package import test
                if package == 'beautifulsoup4':
                    import bs4
                    version = bs4.__version__ if hasattr(bs4, '__version__') else 'unknown'
                elif package == 'python-dotenv':
                    import dotenv
                    version = dotenv.__version__ if hasattr(dotenv, '__version__') else 'unknown'
                elif package == 'ffmpeg-python':
                    import ffmpeg
                    version = 'installed'
                elif package == 'imageio-ffmpeg':
                    import imageio_ffmpeg
                    version = imageio_ffmpeg.__version__ if hasattr(imageio_ffmpeg, '__version__') else 'unknown'
                else:
                    module = importlib.import_module(package.replace('-', '_'))
                    version = getattr(module, '__version__', 'unknown')
                
                self.log_result("Package", package, "OK", f"Installed: {version}")
                
            except ImportError:
                self.log_result("Package", package, "ERROR", 
                              f"Package topilmadi", 
                              f"pip install {package}>={min_version}")
                self.python_packages.append(f"{package}>={min_version}")
    
    def check_system_dependencies(self):
        """Tizim dependencylarini tekshirish"""
        print("\n🔧 SYSTEM DEPENDENCIES CHECK")
        print("=" * 50)
        
        # FFmpeg binaries
        ffmpeg_binaries = ['ffmpeg', 'ffprobe']
        for binary in ffmpeg_binaries:
            path = shutil.which(binary)
            if path:
                try:
                    result = subprocess.run([binary, '-version'], 
                                          capture_output=True, text=True, check=True, timeout=5)
                    version_line = result.stdout.split('\n')[0]
                    version = version_line.split('version')[1].split()[0] if 'version' in version_line else 'unknown'
                    self.log_result("System", binary, "OK", f"Found: {path} (v{version})")
                except Exception as e:
                    self.log_result("System", binary, "WARN", f"Path found but error: {e}")
            else:
                self.log_result("System", binary, "ERROR", 
                              f"{binary} topilmadi",
                              f"sudo apt install ffmpeg  # Ubuntu/Debian\nbrew install ffmpeg  # macOS")
                self.system_packages.append('ffmpeg')
        
        # Git
        git_path = shutil.which('git')
        if git_path:
            try:
                result = subprocess.run(['git', '--version'], 
                                      capture_output=True, text=True, check=True)
                version = result.stdout.strip().split()[-1]
                self.log_result("System", "git", "OK", f"Found: {git_path} (v{version})")
            except Exception as e:
                self.log_result("System", "git", "WARN", f"Git error: {e}")
        else:
            self.log_result("System", "git", "WARN", 
                          "Git topilmadi",
                          "sudo apt install git")
        
        # Curl
        curl_path = shutil.which('curl')
        if curl_path:
            self.log_result("System", "curl", "OK", f"Found: {curl_path}")
        else:
            self.log_result("System", "curl", "WARN", 
                          "Curl topilmadi", 
                          "sudo apt install curl")
    
    def check_playwright_browsers(self):
        """Playwright browserlarini tekshirish"""
        print("\n🌐 PLAYWRIGHT BROWSERS CHECK")
        print("=" * 50)
        
        try:
            import playwright
            self.log_result("Playwright", "Installation", "OK", "Playwright o'rnatilgan")
            
            # Browser binaries check - faqat path mavjudligini tekshiramiz
            import os
            from pathlib import Path
            
            # Playwright browser cache directory
            playwright_cache = Path.home() / ".cache" / "ms-playwright"
            
            browsers_found = 0
            browsers = ['chromium']
            
            for browser in browsers:
                browser_dirs = list(playwright_cache.glob(f"{browser}-*"))
                if browser_dirs:
                    # Eng yangi versiyani topish
                    latest_browser = max(browser_dirs, key=lambda x: x.stat().st_mtime)
                    
                    # Executable file mavjudligini tekshirish
                    if browser == 'chromium':
                        executable = latest_browser / "chrome-linux" / "chrome"
                    elif browser == 'firefox':
                        executable = latest_browser / "firefox" / "firefox"
                    else:  # webkit
                        executable = latest_browser / "minibrowser-gtk" / "MiniBrowser"
                    
                    if executable.exists():
                        self.log_result("Playwright", f"{browser.title()}", "OK", 
                                      f"Browser mavjud: {latest_browser}")
                        browsers_found += 1
                    else:
                        self.log_result("Playwright", f"{browser.title()}", "WARN", 
                                      f"Browser papka mavjud lekin executable yo'q")
                else:
                    self.log_result("Playwright", f"{browser.title()}", "ERROR", 
                                  f"Browser topilmadi")
            
            if browsers_found == 0:
                self.log_result("Playwright", "Browser Status", "ERROR", 
                              "Chromium topilmadi - loyiha ishlamaydi",
                              "playwright install chromium")
            else:
                self.log_result("Playwright", "Browser Status", "OK", 
                              "Chromium tayyor - loyiha ishlashi mumkin")
                
        except ImportError:
            self.log_result("Playwright", "Installation", "ERROR", 
                          "Playwright o'rnatilmagan",
                          "pip install playwright && playwright install")
    
    def check_project_structure(self):
        """Loyiha tuzilmasini tekshirish"""
        print("\n📁 PROJECT STRUCTURE CHECK")
        print("=" * 50)
        
        required_dirs = [
            'core', 'scraper', 'filedownloader', 'telegramuploader', 
            'utils', 'logs', 'downloads', 'local_db', 'results'
        ]
        
        required_files = [
            'main.py', 'requirements.txt', 'README.md',
            'core/config.py', 'core/FileDB.py',
            'utils/logger_core.py'
        ]
        
        project_root = Path.cwd()
        
        # Directories
        for dir_name in required_dirs:
            dir_path = project_root / dir_name
            if dir_path.exists() and dir_path.is_dir():
                self.log_result("Structure", f"Dir: {dir_name}", "OK", f"Mavjud: {dir_path}")
            else:
                self.log_result("Structure", f"Dir: {dir_name}", "ERROR", 
                              f"Papka topilmadi: {dir_path}",
                              f"mkdir -p {dir_path}")
        
        # Files
        for file_name in required_files:
            file_path = project_root / file_name
            if file_path.exists() and file_path.is_file():
                size = file_path.stat().st_size
                self.log_result("Structure", f"File: {file_name}", "OK", 
                              f"Mavjud ({size} bytes)")
            else:
                self.log_result("Structure", f"File: {file_name}", "ERROR", 
                              f"Fayl topilmadi: {file_path}")
    
    def check_configuration(self):
        """Konfiguratsiya fayllarini tekshirish"""
        print("\n⚙️ CONFIGURATION CHECK")
        print("=" * 50)
        
        # .env file
        env_path = Path('.env')
        if env_path.exists():
            self.log_result("Config", ".env", "OK", "Environment file mavjud")
            
            # .env content check
            try:
                with open(env_path, 'r') as f:
                    env_content = f.read()
                
                required_env_vars = [
                    'TELEGRAM_API_ID', 'TELEGRAM_API_HASH', 
                    'TELEGRAM_PHONE_NUMBER', 'FILES_GROUP_LINK'
                ]
                
                for var in required_env_vars:
                    if var in env_content and f'{var}=' in env_content:
                        # Check if not empty
                        lines = [line for line in env_content.split('\n') if line.startswith(f'{var}=')]
                        if lines and '=' in lines[0]:
                            value = lines[0].split('=', 1)[1].strip()
                            if value and value != 'your_value' and value != '':
                                self.log_result("Config", f"Env: {var}", "OK", "O'rnatilgan")
                            else:
                                self.log_result("Config", f"Env: {var}", "WARN", "Bo'sh qiymat yoki default")
                        else:
                            self.log_result("Config", f"Env: {var}", "WARN", "Bo'sh qiymat")
                    else:
                        self.log_result("Config", f"Env: {var}", "ERROR", 
                                      f"Environment variable topilmadi",
                                      f"echo '{var}=your_value' >> .env")
                        
            except Exception as e:
                self.log_result("Config", ".env content", "ERROR", f"O'qishda xato: {e}")
        else:
            self.log_result("Config", ".env", "ERROR", 
                          "Environment file topilmadi",
                          "cp .env.example .env  # va kerakli qiymatlarni to'ldiring")
        
        # .env.example
        env_example_path = Path('.env.example')
        if env_example_path.exists():
            self.log_result("Config", ".env.example", "OK", "Example file mavjud")
        else:
            self.log_result("Config", ".env.example", "WARN", 
                          "Example file topilmadi")
    
    def check_permissions_and_space(self):
        """Ruxsatlar va disk bo'sh joyini tekshirish"""
        print("\n🔐 PERMISSIONS & DISK SPACE CHECK")
        print("=" * 50)
        
        # Current directory write permission
        current_dir = Path.cwd()
        if os.access(current_dir, os.W_OK):
            self.log_result("Permission", "Current Dir", "OK", 
                          f"Yozish ruxsati bor: {current_dir}")
        else:
            self.log_result("Permission", "Current Dir", "ERROR", 
                          f"Yozish ruxsati yo'q: {current_dir}",
                          f"chmod u+w {current_dir}")
        
        # Important directories
        important_dirs = ['logs', 'downloads', 'local_db', 'results']
        for dir_name in important_dirs:
            dir_path = current_dir / dir_name
            if dir_path.exists():
                if os.access(dir_path, os.W_OK):
                    self.log_result("Permission", f"Dir: {dir_name}", "OK", "Yozish ruxsati bor")
                else:
                    self.log_result("Permission", f"Dir: {dir_name}", "ERROR", 
                                  "Yozish ruxsati yo'q",
                                  f"chmod u+w {dir_path}")
        
        # Disk space
        try:
            statvfs = os.statvfs(current_dir)
            free_space = statvfs.f_frsize * statvfs.f_bavail
            free_space_gb = free_space / (1024**3)
            
            if free_space_gb > 10:
                self.log_result("Disk", "Free Space", "OK", 
                              f"{free_space_gb:.1f} GB bo'sh joy")
            elif free_space_gb > 2:
                self.log_result("Disk", "Free Space", "WARN", 
                              f"{free_space_gb:.1f} GB bo'sh joy - yetarli lekin kam")
            else:
                self.log_result("Disk", "Free Space", "ERROR", 
                              f"{free_space_gb:.1f} GB bo'sh joy - juda kam")
        except Exception as e:
            self.log_result("Disk", "Free Space", "ERROR", f"Tekshirib bo'lmadi: {e}")
    
    def generate_fix_script(self):
        """Muammolarni hal qilish uchun script yaratish"""
        print("\n🔧 GENERATING FIX SCRIPT")
        print("=" * 50)
        
        fix_commands = []
        
        # Python packages
        if self.python_packages:
            fix_commands.append("# Python packages o'rnatish")
            fix_commands.append(f"pip install {' '.join(self.python_packages)}")
            fix_commands.append("")
        
        # System packages
        if self.system_packages:
            fix_commands.append("# System packages o'rnatish")
            fix_commands.append("# Ubuntu/Debian:")
            fix_commands.append(f"sudo apt update && sudo apt install -y {' '.join(self.system_packages)}")
            fix_commands.append("# macOS:")
            fix_commands.append(f"brew install {' '.join(self.system_packages)}")
            fix_commands.append("")
        
        # Playwright browsers
        playwright_needed = any(r['name'] == 'Browser Status' and r['status'] == 'ERROR' 
                               for r in self.results if r['category'] == 'Playwright')
        if playwright_needed:
            fix_commands.append("# Playwright Chromium o'rnatish")
            fix_commands.append("playwright install chromium")
            fix_commands.append("")
        
        # Create directories
        missing_dirs = [r['name'].replace('Dir: ', '') for r in self.results 
                       if r['category'] == 'Structure' and r['status'] == 'ERROR' and 'Dir:' in r['name']]
        if missing_dirs:
            fix_commands.append("# Kerakli papkalar yaratish")
            for dir_name in missing_dirs:
                fix_commands.append(f"mkdir -p {dir_name}")
            fix_commands.append("")
        
        # Environment file
        env_needed = any(r['name'] == '.env' and r['status'] == 'ERROR' 
                        for r in self.results if r['category'] == 'Config')
        if env_needed:
            fix_commands.append("# Environment file yaratish")
            fix_commands.append("cp .env.example .env")
            fix_commands.append("# .env faylni tahrir qiling va kerakli qiymatlarni to'ldiring")
            fix_commands.append("")
        
        if fix_commands:
            fix_script_path = Path('fix_system.sh')
            try:
                with open(fix_script_path, 'w') as f:
                    f.write("#!/bin/bash\n")
                    f.write("# Auto-generated system fix script\n")
                    f.write("# " + "="*50 + "\n\n")
                    f.write("\n".join(fix_commands))
                
                # Make executable
                os.chmod(fix_script_path, 0o755)
                
                self.log_result("Fix", "Script", "OK", 
                              f"Fix script yaratildi: {fix_script_path}")
                print(f"   💡 Ishga tushirish: ./fix_system.sh")
            except Exception as e:
                self.log_result("Fix", "Script", "ERROR", f"Script yaratishda xato: {e}")
        else:
            self.log_result("Fix", "Script", "INFO", "Hech qanday fix kerak emas!")
    
    def print_summary(self):
        """Umumiy natijalar"""
        print("\n📊 DIAGNOSTICS SUMMARY")
        print("=" * 60)
        
        total = len(self.results)
        ok_count = len([r for r in self.results if r['status'] == 'OK'])
        warn_count = len([r for r in self.results if r['status'] == 'WARN'])
        error_count = len([r for r in self.results if r['status'] == 'ERROR'])
        info_count = len([r for r in self.results if r['status'] == 'INFO'])
        
        print(f"Jami tekshiruvlar: {total}")
        print(f"✅ Muvaffaqiyatli: {ok_count}")
        print(f"⚠️ Ogohlantirishlar: {warn_count}")
        print(f"❌ Xatolar: {error_count}")
        print(f"📋 Ma'lumotlar: {info_count}")
        
        if error_count == 0 and warn_count <= 2:
            print("\n🎉 Tizim tayyor! Dasturni ishga tushirishingiz mumkin.")
            return True
        elif error_count == 0:
            print(f"\n⚠️ Ba'zi ogohlantirishlar bor, lekin dastur ishlashi mumkin.")
            return True
        else:
            print(f"\n❌ {error_count} ta muhim muammo topildi. Avval ularni hal qiling.")
            return False
    
    def run_full_diagnostics(self):
        """Barcha diagnostikalarni ishga tushirish"""
        print("🔍 SYSTEM DIAGNOSTICS - Files Project Scraper")
        print("=" * 60)
        print(f"Platform: {platform.system()} {platform.release()}")
        print(f"Python: {platform.python_version()}")
        print(f"Working Directory: {Path.cwd()}")
        print()
        
        self.check_python_environment()
        self.check_required_python_packages()
        self.check_system_dependencies()
        self.check_playwright_browsers()
        self.check_project_structure()
        self.check_configuration()
        self.check_permissions_and_space()
        self.generate_fix_script()
        
        return self.print_summary()


def main():
    """Main diagnostics runner"""
    try:
        diagnostics = SystemDiagnostics()
        success = diagnostics.run_full_diagnostics()
        
        if success:
            print("\n🚀 Tayyor! Dasturni ishga tushiring:")
            print("   python main.py")
            return 0
        else:
            print("\n🔧 Avval muammolarni hal qiling, keyin qayta tekshiring:")
            print("   python utils/system_diagnostics.py")
            return 1
            
    except KeyboardInterrupt:
        print("\n⚠️ Diagnostics to'xtatildi")
        return 130
    except Exception as e:
        print(f"\n💥 Kutilmagan xato: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit(main())