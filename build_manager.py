import os
import shutil
import base64
import subprocess
import PyInstaller.__main__

# --- CONFIGURATION ---
APP_NAME = "QuishGuard"
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
DIST_DIR = os.path.join(ROOT_DIR, "dist")
BUILD_DIR = os.path.join(ROOT_DIR, "build")
ASSETS_DIR = os.path.join(ROOT_DIR, "assets") # Ensure this exists or remove icon config

# Files to be generated
APP_EXE = os.path.join(DIST_DIR, "QuishGuard.exe")
UNINSTALL_EXE = os.path.join(DIST_DIR, "Uninstall_QuishGuard.exe")
SETUP_EXE = os.path.join(DIST_DIR, "QuishGuard_Setup.exe")

def clean_environment():
    print("[-] Cleaning old build artifacts...")
    if os.path.exists(DIST_DIR): shutil.rmtree(DIST_DIR)
    if os.path.exists(BUILD_DIR): shutil.rmtree(BUILD_DIR)
    # Cleanup spec files
    for f in os.listdir(ROOT_DIR):
        if f.endswith(".spec"):
            os.remove(os.path.join(ROOT_DIR, f))

def build_uninstaller():
    print("\n[1/3] Building Uninstaller...")
    script_path = os.path.join(ROOT_DIR, "temp_uninstaller.py")
    
    code = f"""
import os, shutil, winshell, sys, time
from tkinter import messagebox
from pathlib import Path

APP_NAME = "{APP_NAME}"

def uninstall():
    try:
        # 1. Delete AppData
        home = str(Path.home())
        install_dir = os.path.join(home, "AppData", "Local", APP_NAME)
        
        # 2. Delete Desktop Shortcut
        desktop = winshell.desktop()
        shortcut = os.path.join(desktop, f"{{APP_NAME}}.lnk")
        if os.path.exists(shortcut): os.remove(shortcut)

        # 3. Attempt to remove files
        if os.path.exists(install_dir):
            for item in os.listdir(install_dir):
                # Don't delete self while running
                if "Uninstall" not in item:
                    try:
                        path = os.path.join(install_dir, item)
                        if os.path.isfile(path): os.remove(path)
                        else: shutil.rmtree(path)
                    except: pass
            
        messagebox.showinfo("Success", f"{{APP_NAME}} has been removed.\\n(You may delete this Uninstaller file now)")
        
    except Exception as e:
        messagebox.showerror("Error", str(e))

if __name__ == "__main__":
    uninstall()
"""
    with open(script_path, "w", encoding="utf-8") as f: f.write(code)

    PyInstaller.__main__.run([
        script_path,
        '--name=Uninstall_QuishGuard',
        '--onefile', '--noconfirm', '--windowed',
        f'--distpath={DIST_DIR}',
        f'--workpath={BUILD_DIR}',
        '--hidden-import=winshell',
        '--clean'
    ])
    os.remove(script_path)

def build_main_app():
    print("\n[2/3] Building Main QuishGuard Application...")
    
    PyInstaller.__main__.run([
        'main.py',
        '--name=QuishGuard',
        '--onefile', '--noconfirm', '--windowed',
        f'--distpath={DIST_DIR}',
        f'--workpath={BUILD_DIR}',
        # CRITICAL FIXES FOR LIBRARIES
        '--collect-all=qtawesome', 
        '--hidden-import=pyzbar',
        '--hidden-import=winshell',
        '--clean'
    ])

def build_installer():
    print("\n[3/3] Building Final Setup Wizard...")
    
    if not os.path.exists(APP_EXE) or not os.path.exists(UNINSTALL_EXE):
        print("[!] Error: Binaries missing. Build failed.")
        return

    # Read Binaries
    with open(APP_EXE, "rb") as f: app_b64 = base64.b64encode(f.read()).decode('utf-8')
    with open(UNINSTALL_EXE, "rb") as f: uninst_b64 = base64.b64encode(f.read()).decode('utf-8')

    script_path = os.path.join(ROOT_DIR, "temp_setup.py")
    
    code = f"""
import os, base64, winshell, sys
import tkinter as tk
from tkinter import messagebox, ttk
from pathlib import Path
from win32com.client import Dispatch

APP_NAME = "{APP_NAME}"
APP_DATA = "{app_b64}"
UNINST_DATA = "{uninst_b64}"

def install():
    btn.config(state="disabled", text="Installing...")
    bar.start(10); root.update()
    
    try:
        # Install Paths
        home = str(Path.home())
        install_dir = os.path.join(home, "AppData", "Local", APP_NAME)
        if not os.path.exists(install_dir): os.makedirs(install_dir)
        
        app_path = os.path.join(install_dir, "QuishGuard.exe")
        uninst_path = os.path.join(install_dir, "Uninstall.exe")
        
        # Write Files
        with open(app_path, "wb") as f: f.write(base64.b64decode(APP_DATA))
        with open(uninst_path, "wb") as f: f.write(base64.b64decode(UNINST_DATA))
        
        # Create Shortcut
        desktop = winshell.desktop()
        shell = Dispatch('WScript.Shell')
        lnk = shell.CreateShortCut(os.path.join(desktop, f"{{APP_NAME}}.lnk"))
        lnk.Targetpath = app_path
        lnk.WorkingDirectory = install_dir
        lnk.save()
        
        bar.stop()
        messagebox.showinfo("Success", "Installed successfully! Check your Desktop.")
        root.destroy()
    except Exception as e:
        bar.stop()
        messagebox.showerror("Error", str(e))
        btn.config(state="normal", text="Retry")

root = tk.Tk(); root.title("Setup"); root.geometry("400x200")
tk.Label(root, text=f"Install {{APP_NAME}}", font=("Segoe UI", 16, "bold")).pack(pady=20)
bar = ttk.Progressbar(root, length=300, mode='indeterminate'); bar.pack(pady=10)
btn = tk.Button(root, text="INSTALL NOW", bg="#00E676", command=install); btn.pack(pady=10)
root.mainloop()
"""
    with open(script_path, "w", encoding="utf-8") as f: f.write(code)

    PyInstaller.__main__.run([
        script_path,
        f'--name={APP_NAME}_Setup',
        '--onefile', '--noconfirm', '--windowed',
        f'--distpath={DIST_DIR}',
        f'--workpath={BUILD_DIR}',
        '--hidden-import=winshell',
        '--hidden-import=win32com.client',
        '--clean'
    ])
    os.remove(script_path)

def main():
    clean_environment()
    build_uninstaller()
    build_main_app()
    build_installer()
    
    # Cleanup Artifacts to leave only the Setup file?
    # Uncomment these lines if you ONLY want the Setup file and nothing else
    # if os.path.exists(APP_EXE): os.remove(APP_EXE)
    # if os.path.exists(UNINSTALL_EXE): os.remove(UNINSTALL_EXE)

    print(f"\n[+] SUCCESS! Distribution package ready at:\n    {SETUP_EXE}")

if __name__ == "__main__":
    main()