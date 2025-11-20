import os
import subprocess

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(CURRENT_DIR)
DIST_DIR = os.path.join(PROJECT_ROOT, "dist")
UNINSTALL_SCRIPT = os.path.join(CURRENT_DIR, "temp_uninstall.py")

def create_uninstaller():
    print("[*] Generating uninstaller logic...")
    
    code = """
import os, shutil, winshell, sys
from tkinter import messagebox
from pathlib import Path

APP_NAME = "QuishGuard"

def uninstall():
    try:
        # 1. Delete AppData Folder
        home = str(Path.home())
        install_dir = os.path.join(home, "AppData", "Local", APP_NAME)
        
        # We can't delete the uninstaller while it is running inside the folder
        # So usually uninstallers mark files for deletion on reboot, 
        # but for this simple tool, we will just delete the artifacts.
        
        if os.path.exists(install_dir):
            for item in os.listdir(install_dir):
                if "Uninstall" not in item: # Delete everything else
                    try:
                        path = os.path.join(install_dir, item)
                        if os.path.isfile(path): os.remove(path)
                        else: shutil.rmtree(path)
                    except: pass
        
        # 2. Delete Desktop Shortcut
        desktop = winshell.desktop()
        shortcut = os.path.join(desktop, f"{APP_NAME}.lnk")
        if os.path.exists(shortcut):
            os.remove(shortcut)
            
        messagebox.showinfo("Success", f"{APP_NAME} has been removed.")
        
        # Self-destruction logic (optional/advanced) would go here
        
    except Exception as e:
        messagebox.showerror("Error", str(e))

if __name__ == "__main__":
    uninstall()
"""
    with open(UNINSTALL_SCRIPT, "w", encoding="utf-8") as f:
        f.write(code)

    print("[*] Compiling Uninstaller...")
    subprocess.check_call([
        "pyinstaller", "--onefile", "--noconfirm", "--windowed",
        "--name", "Uninstall_QuishGuard",
        "--distpath", DIST_DIR,
        "--workpath", os.path.join(PROJECT_ROOT, "build"),
        UNINSTALL_SCRIPT
    ])
    
    os.remove(UNINSTALL_SCRIPT)
    print(f"[+] Uninstaller Ready: dist/Uninstall_QuishGuard.exe")

if __name__ == "__main__":
    create_uninstaller()