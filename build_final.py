import os
import shutil
import subprocess

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
DIST_DIR = os.path.join(ROOT_DIR, "dist")
BUILD_DIR = os.path.join(ROOT_DIR, "build")
INSTALLER_DIR = os.path.join(ROOT_DIR, "installer")

def clean():
    print("[-] Cleaning...")
    if os.path.exists(DIST_DIR): shutil.rmtree(DIST_DIR)
    if os.path.exists(BUILD_DIR): shutil.rmtree(BUILD_DIR)

def build_component(script, name, console=False, extra_args=[]):
    print(f"\n[*] Building {name}...")
    cmd = [
        "pyinstaller",
        "--noconfirm",
        "--onefile",
        "--clean",
        "--name", name,
        "--distpath", DIST_DIR,
        "--workpath", BUILD_DIR,
    ]
    if not console:
        cmd.append("--windowed")
    
    cmd.extend(extra_args)
    cmd.append(script)
    
    subprocess.check_call(cmd)

def main():
    clean()
    
    # 1. Build Main App
    # Include pyzbar and qtawesome
    build_component("main.py", "QuishGuard", extra_args=[
        "--collect-all=qtawesome",
        "--collect-all=pyzbar",
        "--hidden-import=winshell"
    ])
    
    # 2. Build Uninstaller
    build_component(os.path.join(INSTALLER_DIR, "uninstaller.py"), "Uninstall", extra_args=[
        "--hidden-import=winshell"
    ])
    
    # 3. Build Installer
    # Crucial: We bundle the previous 2 EXEs inside this one
    # Format for --add-data is "source;dest" on Windows
    app_exe = os.path.join(DIST_DIR, "QuishGuard.exe")
    uninst_exe = os.path.join(DIST_DIR, "Uninstall.exe")
    
    build_component(os.path.join(INSTALLER_DIR, "setup.py"), "QuishGuard_Setup", extra_args=[
        f"--add-data={app_exe};.",
        f"--add-data={uninst_exe};.",
        "--hidden-import=winshell",
        "--hidden-import=win32com.client"
    ])
    
    print("\n[+] SUCCESS! Final installer: dist/QuishGuard_Setup.exe")

if __name__ == "__main__":
    main()