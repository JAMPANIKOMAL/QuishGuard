import os
import base64
import subprocess
import shutil

# Paths
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(CURRENT_DIR)
DIST_DIR = os.path.join(PROJECT_ROOT, "dist")
EXE_PATH = os.path.join(DIST_DIR, "QuishGuard.exe")
INSTALLER_SCRIPT = os.path.join(CURRENT_DIR, "temp_setup_script.py")

APP_NAME = "QuishGuard"

def create_installer():
    if not os.path.exists(EXE_PATH):
        print(f"[!] Error: {EXE_PATH} missing. Run '1_build_app.py' first.")
        return

    print("[*] Encoding QuishGuard binary...")
    with open(EXE_PATH, "rb") as f:
        exe_data = base64.b64encode(f.read()).decode('utf-8')

    print("[*] Generating setup logic...")
    # We embed the Uninstaller creation logic inside the Installer
    installer_code = f"""
import os, sys, base64, winshell
import tkinter as tk
from tkinter import messagebox, ttk
from pathlib import Path
from win32com.client import Dispatch

APP_NAME = "{APP_NAME}"
EXE_DATA = "{exe_data}"

def install():
    btn_install.config(state="disabled", text="Installing...")
    progress.start(10)
    root.update()
    
    try:
        # 1. Paths
        home = str(Path.home())
        install_dir = os.path.join(home, "AppData", "Local", APP_NAME)
        if not os.path.exists(install_dir): os.makedirs(install_dir)
        
        exe_path = os.path.join(install_dir, "QuishGuard.exe")
        uninst_path = os.path.join(install_dir, "Uninstall.exe") # We will copy uninstaller here later if separate
        
        # 2. Write App
        with open(exe_path, "wb") as f:
            f.write(base64.b64decode(EXE_DATA))
            
        # 3. Create Shortcuts
        desktop = winshell.desktop()
        start_menu = winshell.programs()
        
        # Desktop Shortcut
        shell = Dispatch('WScript.Shell')
        shortcut = shell.CreateShortCut(os.path.join(desktop, f"{{APP_NAME}}.lnk"))
        shortcut.Targetpath = exe_path
        shortcut.WorkingDirectory = install_dir
        shortcut.save()
        
        progress.stop()
        messagebox.showinfo("Success", f"{{APP_NAME}} installed successfully!")
        root.destroy()
        
    except Exception as e:
        progress.stop()
        messagebox.showerror("Error", f"Install Failed:\\n{{e}}")
        btn_install.config(state="normal", text="Retry")

root = tk.Tk()
root.title(f"Setup - {{APP_NAME}}")
root.geometry("400x200")
root.eval('tk::PlaceWindow . center')
lbl = tk.Label(root, text=f"Install {{APP_NAME}}", font=("Segoe UI", 16, "bold"))
lbl.pack(pady=20)
progress = ttk.Progressbar(root, orient="horizontal", length=300, mode="indeterminate")
progress.pack(pady=10)
btn_install = tk.Button(root, text="INSTALL", bg="#00E676", command=install)
btn_install.pack(pady=10)
root.mainloop()
"""

    with open(INSTALLER_SCRIPT, "w", encoding="utf-8") as f:
        f.write(installer_code)

    print("[*] Compiling Setup Wizard...")
    subprocess.check_call([
        "pyinstaller", "--onefile", "--noconfirm", "--windowed",
        "--name", f"{APP_NAME}_Setup",
        "--distpath", DIST_DIR,
        "--workpath", os.path.join(PROJECT_ROOT, "build"),
        "--hidden-import", "winshell",
        "--hidden-import", "win32com.client",
        INSTALLER_SCRIPT
    ])
    
    os.remove(INSTALLER_SCRIPT)
    print(f"[+] Installer Ready: dist/{APP_NAME}_Setup.exe")

if __name__ == "__main__":
    create_installer()