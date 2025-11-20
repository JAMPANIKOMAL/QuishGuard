import PyInstaller.__main__
import os
import shutil

# 1. Setup Paths (Handle running from subfolder)
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(CURRENT_DIR) # Go up one level
MAIN_SCRIPT = os.path.join(PROJECT_ROOT, "main.py")
DIST_DIR = os.path.join(PROJECT_ROOT, "dist")
BUILD_DIR = os.path.join(PROJECT_ROOT, "build")
ICON_PATH = os.path.join(PROJECT_ROOT, "assets", "icon.ico") # If you have one

print(f"[*] Building QuishGuard from: {MAIN_SCRIPT}")

# 2. Clean previous builds
if os.path.exists(DIST_DIR): shutil.rmtree(DIST_DIR)
if os.path.exists(BUILD_DIR): shutil.rmtree(BUILD_DIR)

# 3. Run PyInstaller
# We use --collect-all qtawesome to FIX the "ModuleNotFound" error
# We use --hidden-import to ensure DLLs are found
PyInstaller.__main__.run([
    MAIN_SCRIPT,
    '--name=QuishGuard',
    '--onefile',
    '--noconfirm',
    '--windowed',
    f'--distpath={DIST_DIR}',
    f'--workpath={BUILD_DIR}',
    '--collect-all=qtawesome',  # <--- THE FIX
    '--hidden-import=pyzbar',
    '--hidden-import=winshell',
    '--clean',
])

print("\n[+] Build Complete! Check 'dist/QuishGuard.exe'")