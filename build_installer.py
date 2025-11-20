import os
import base64
import subprocess

# CONFIGURATION
APP_NAME = "QuishGuard"
EXE_NAME = "QuishGuard.exe"
DIST_PATH = os.path.join("dist", EXE_NAME)
SETUP_FILENAME = f"{APP_NAME}_Setup.exe"
INSTALLER_SCRIPT = "setup_logic.py"

def create_installer():
    print(f"[*] Checking for {DIST_PATH}...")
    if not os.path.exists(DIST_PATH):
        print(f"[!] Error: {DIST_PATH} missing. Run 'pyinstaller build_config.spec' first.")
        return

    # 1. Read your App into memory (base64)
    print("[*] Encoding application binary...")
    with open(DIST_PATH, "rb") as f:
        exe_data = base64.b64encode(f.read()).decode('utf-8')

    # 2. Create the Installer Logic (Tkinter GUI)
    print("[*] Generating setup script...")
    installer_code = f"""
import os
import sys
import base64
import tkinter as tk
from tkinter import messagebox, ttk
from pathlib import Path
import winshell
from win32com.client import Dispatch

APP_NAME = "{APP_NAME}"
EXE_NAME = "{EXE_NAME}"
EXE_DATA = "{exe_data}"

def create_shortcut(target_path, install_dir):
    try:
        desktop = winshell.desktop()
        path = os.path.join(desktop, f"{{APP_NAME}}.lnk")
        shell = Dispatch('WScript.Shell')
        shortcut = shell.CreateShortCut(path)
        shortcut.Targetpath = target_path
        shortcut.WorkingDirectory = install_dir
        shortcut.save()
    except Exception as e:
        print(f"Shortcut Error: {{e}}")

def run_install():
    btn_install.config(state="disabled", text="Installing...")
    progress.start(10)
    root.update()
    
    try:
        # 1. Create Folder in AppData
        home = str(Path.home())
        install_dir = os.path.join(home, "AppData", "Local", APP_NAME)
        if not os.path.exists(install_dir):
            os.makedirs(install_dir)
            
        exe_path = os.path.join(install_dir, EXE_NAME)
        
        # 2. Extract EXE
        with open(exe_path, "wb") as f:
            f.write(base64.b64decode(EXE_DATA))
            
        # 3. Create Shortcut
        create_shortcut(exe_path, install_dir)
        
        progress.stop()
        messagebox.showinfo("Success", f"{{APP_NAME}} installed successfully!\\n\\nCheck your Desktop.")
        root.destroy()
        
    except Exception as e:
        progress.stop()
        messagebox.showerror("Error", f"Installation Failed:\\n{{str(e)}}")
        btn_install.config(state="normal", text="Retry")

# --- INSTALLER UI ---
root = tk.Tk()
root.title(f"Setup - {{APP_NAME}}")
root.geometry("400x220")
root.resizable(False, False)
root.configure(bg="#222")

style = ttk.Style()
style.theme_use('clam')
style.configure("TProgressbar", thickness=5)

lbl_title = tk.Label(root, text=f"Install {{APP_NAME}}", font=("Segoe UI", 18, "bold"), bg="#222", fg="white")
lbl_title.pack(pady=(30, 5))

lbl_sub = tk.Label(root, text="Secure Phishing Detector v1.0", font=("Segoe UI", 9), bg="#222", fg="#888")
lbl_sub.pack(pady=(0, 20))

progress = ttk.Progressbar(root, orient="horizontal", length=300, mode="indeterminate")
progress.pack(pady=10)

btn_install = tk.Button(root, text="INSTALL", font=("Segoe UI", 10, "bold"), bg="#00E676", fg="#000", width=15, command=run_install)
btn_install.pack(pady=10)

root.mainloop()
"""

    with open(INSTALLER_SCRIPT, "w", encoding="utf-8") as f:
        f.write(installer_code)

    # 3. Compile the Installer
    print("[*] Building Setup.exe (this may take a minute)...")
    subprocess.check_call([
        "pyinstaller", "--onefile", "--noconfirm", "--windowed", 
        "--name", f"{APP_NAME}_Setup", 
        "--hidden-import", "winshell", 
        "--hidden-import", "win32com.client",
        INSTALLER_SCRIPT
    ])
    
    # Cleanup
    if os.path.exists(INSTALLER_SCRIPT): os.remove(INSTALLER_SCRIPT)
    print(f"\n[+] DONE! Your installer is ready: dist/{SETUP_FILENAME}")

if __name__ == "__main__":
    create_installer()