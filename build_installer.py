import os
import base64
import subprocess

APP_NAME = "QuishGuard"
EXE_NAME = "QuishGuard.exe"
DIST_PATH = os.path.join("dist", EXE_NAME)
INSTALLER_SCRIPT = "setup_script.py"

def create_installer():
    print(f"[*] Reading {EXE_NAME}...")
    if not os.path.exists(DIST_PATH):
        print(f"[!] Error: {DIST_PATH} not found. Build the app first!")
        return

    # 1. Read the actual App EXE as bytes
    with open(DIST_PATH, "rb") as f:
        exe_data = base64.b64encode(f.read()).decode('utf-8')

    # 2. Generate the Python Installer Logic
    # This script uses Tkinter (built-in) to show a GUI
    installer_code = f"""
import os
import sys
import base64
import tkinter as tk
from tkinter import messagebox
from pathlib import Path
import winshell # You need to install pywin32
from win32com.client import Dispatch

APP_NAME = "{APP_NAME}"
EXE_NAME = "{EXE_NAME}"
# We embed the binary data directly into the script
EXE_DATA = "{exe_data}"

def install():
    try:
        # 1. Define Install Path (AppData/Local/QuishGuard)
        home = str(Path.home())
        install_dir = os.path.join(home, "AppData", "Local", APP_NAME)
        
        if not os.path.exists(install_dir):
            os.makedirs(install_dir)
            
        exe_path = os.path.join(install_dir, EXE_NAME)
        
        # 2. Write the EXE file
        btn_install.config(text="Installing...", state="disabled")
        root.update()
        
        with open(exe_path, "wb") as f:
            f.write(base64.b64decode(EXE_DATA))
            
        # 3. Create Shortcut on Desktop
        desktop = winshell.desktop()
        path = os.path.join(desktop, f"{{APP_NAME}}.lnk")
        target = exe_path
        
        shell = Dispatch('WScript.Shell')
        shortcut = shell.CreateShortCut(path)
        shortcut.Targetpath = target
        shortcut.WorkingDirectory = install_dir
        shortcut.save()
        
        messagebox.showinfo("Success", f"{{APP_NAME}} has been installed successfully!")
        root.destroy()
        
    except Exception as e:
        messagebox.showerror("Error", f"Installation Failed:\\n{{str(e)}}")
        btn_install.config(text="Install", state="normal")

# --- GUI SETUP ---
root = tk.Tk()
root.title(f"Install {{APP_NAME}}")
root.geometry("400x250")
root.resizable(False, False)
root.configure(bg="#1E1E1E")

lbl_title = tk.Label(root, text=f"Install {{APP_NAME}}", font=("Segoe UI", 20, "bold"), bg="#1E1E1E", fg="white")
lbl_title.pack(pady=30)

lbl_desc = tk.Label(root, text="This wizard will install QuishGuard on your computer.", font=("Segoe UI", 10), bg="#1E1E1E", fg="#888")
lbl_desc.pack(pady=5)

btn_install = tk.Button(root, text="INSTALL NOW", font=("Segoe UI", 12, "bold"), bg="#00FF00", fg="black", command=install, width=20)
btn_install.pack(pady=30)

root.mainloop()
"""

    # 3. Write the temporary installer script
    with open(INSTALLER_SCRIPT, "w", encoding="utf-8") as f:
        f.write(installer_code)
    
    print(f"[*] Generated {INSTALLER_SCRIPT}")
    print("[*] Compiling Installer EXE...")

    # 4. Compile the Installer using PyInstaller
    # We need 'pywin32' for the shortcut creation
    subprocess.check_call([
        "pyinstaller", 
        "--onefile", 
        "--noconfirm", 
        "--windowed", 
        "--name", f"{APP_NAME}_Setup", 
        "--hidden-import", "winshell",
        "--hidden-import", "win32com.client",
        INSTALLER_SCRIPT
    ])

    print(f"\n[+] SUCCESS! Setup file created: dist/{APP_NAME}_Setup.exe")
    # Clean up temp file
    if os.path.exists(INSTALLER_SCRIPT):
        os.remove(INSTALLER_SCRIPT)

if __name__ == "__main__":
    create_installer()