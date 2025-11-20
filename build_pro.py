import os
import shutil
import base64
import subprocess
import sys

# --- CONFIGURATION ---
APP_NAME = "QuishGuard"
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
DIST_DIR = os.path.join(ROOT_DIR, "dist")
BUILD_DIR = os.path.join(ROOT_DIR, "build")

# Files
APP_EXE = os.path.join(DIST_DIR, "QuishGuard.exe")
UNINSTALL_EXE = os.path.join(DIST_DIR, "Uninstall.exe")
SETUP_SCRIPT = os.path.join(ROOT_DIR, "setup_source.py")
UNINSTALL_SCRIPT = os.path.join(ROOT_DIR, "uninstall_source.py")

def clean():
    print("[-] Cleaning artifacts...")
    if os.path.exists(DIST_DIR): shutil.rmtree(DIST_DIR)
    if os.path.exists(BUILD_DIR): shutil.rmtree(BUILD_DIR)
    if os.path.exists(SETUP_SCRIPT): os.remove(SETUP_SCRIPT)
    if os.path.exists(UNINSTALL_SCRIPT): os.remove(UNINSTALL_SCRIPT)
    # Clean spec files
    for f in os.listdir(ROOT_DIR):
        if f.endswith(".spec"): os.remove(os.path.join(ROOT_DIR, f))

def build_app():
    print("\n[1/3] Building Core Application...")
    subprocess.check_call([
        "pyinstaller", "main.py",
        "--name=QuishGuard",
        "--onefile", "--noconfirm", "--windowed",
        f"--distpath={DIST_DIR}", f"--workpath={BUILD_DIR}",
        "--collect-all=qtawesome",
        "--hidden-import=pyzbar",
        "--clean"
    ])

def build_uninstaller():
    print("\n[2/3] Building Uninstaller...")
    code = f"""
import os, sys, shutil, winshell
from PyQt6.QtWidgets import QApplication, QMessageBox
from pathlib import Path

def uninstall():
    app = QApplication(sys.argv)
    reply = QMessageBox.question(None, "Uninstall {APP_NAME}", 
                               "Are you sure you want to remove {APP_NAME} and all its data?",
                               QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
    
    if reply == QMessageBox.StandardButton.Yes:
        try:
            # 1. Remove Desktop Shortcut
            desktop = winshell.desktop()
            shortcut = os.path.join(desktop, "{APP_NAME}.lnk")
            if os.path.exists(shortcut): os.remove(shortcut)
            
            # 2. Schedule Self-Delete (The tricky part)
            # We can't delete the folder we are running in.
            # We rename the uninstaller and tell Windows to delete it on reboot, 
            # or just tell the user to delete the folder manually for safety.
            
            install_dir = os.path.dirname(sys.executable)
            
            # Try to delete content except self
            for item in os.listdir(install_dir):
                if item.lower() != "uninstall.exe":
                    try:
                        path = os.path.join(install_dir, item)
                        if os.path.isfile(path): os.remove(path)
                        else: shutil.rmtree(path)
                    except: pass
            
            QMessageBox.information(None, "Success", "{APP_NAME} removed.\\n\\nYou can now delete this folder.")
            
        except Exception as e:
            QMessageBox.critical(None, "Error", str(e))
            
if __name__ == "__main__":
    uninstall()
"""
    with open(UNINSTALL_SCRIPT, "w", encoding="utf-8") as f: f.write(code)
    
    subprocess.check_call([
        "pyinstaller", UNINSTALL_SCRIPT,
        "--name=Uninstall",
        "--onefile", "--noconfirm", "--windowed",
        f"--distpath={DIST_DIR}", f"--workpath={BUILD_DIR}",
        "--hidden-import=winshell",
        "--clean"
    ])
    os.remove(UNINSTALL_SCRIPT)

def build_installer():
    print("\n[3/3] Building Pro Installer (Dark Mode)...")
    
    if not os.path.exists(APP_EXE): return print("App build failed!")
    
    # Encode binaries
    with open(APP_EXE, "rb") as f: app_b64 = base64.b64encode(f.read()).decode('utf-8')
    with open(UNINSTALL_EXE, "rb") as f: uninst_b64 = base64.b64encode(f.read()).decode('utf-8')

    # Generate PyQt6 Installer Source
    setup_code = f"""
import sys, os, base64, winshell
from PyQt6.QtWidgets import (QApplication, QWidget, QVBoxLayout, QLabel, 
                             QPushButton, QLineEdit, QFileDialog, QProgressBar, QMessageBox)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QIcon
from pathlib import Path
from win32com.client import Dispatch

APP_DATA = "{app_b64}"
UNINST_DATA = "{uninst_b64}"
DEFAULT_PATH = os.path.join(str(Path.home()), "AppData", "Local", "{APP_NAME}")

class InstallThread(QThread):
    progress = pyqtSignal(int)
    finished = pyqtSignal(str)
    
    def __init__(self, path):
        super().__init__()
        self.path = path
        
    def run(self):
        try:
            self.progress.emit(10)
            if not os.path.exists(self.path): os.makedirs(self.path)
            
            # Write App
            self.progress.emit(30)
            with open(os.path.join(self.path, "QuishGuard.exe"), "wb") as f:
                f.write(base64.b64decode(APP_DATA))
                
            # Write Uninstaller
            self.progress.emit(60)
            with open(os.path.join(self.path, "Uninstall.exe"), "wb") as f:
                f.write(base64.b64decode(UNINST_DATA))
                
            # Shortcuts
            self.progress.emit(80)
            desktop = winshell.desktop()
            shell = Dispatch('WScript.Shell')
            lnk = shell.CreateShortCut(os.path.join(desktop, "{APP_NAME}.lnk"))
            lnk.Targetpath = os.path.join(self.path, "QuishGuard.exe")
            lnk.WorkingDirectory = self.path
            lnk.save()
            
            self.progress.emit(100)
            self.finished.emit("Success")
            
        except Exception as e:
            self.finished.emit(str(e))

class InstallerWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("{APP_NAME} Setup")
        self.setFixedSize(500, 350)
        self.setStyleSheet(\"\"\"
            QWidget {{ background-color: #121212; color: white; font-family: Segoe UI; }}
            QLineEdit {{ padding: 8px; background: #222; border: 1px solid #444; color: #CCC; }}
            QPushButton {{ background: #222; border: 1px solid #444; padding: 8px; font-weight: bold; }}
            QPushButton:hover {{ background: #333; border-color: #00FF00; color: white; }}
            QProgressBar {{ border: 1px solid #444; text-align: center; }}
            QProgressBar::chunk {{ background-color: #00FF00; }}
        \"\"\")
        
        layout = QVBoxLayout()
        layout.setSpacing(20)
        layout.setContentsMargins(40, 40, 40, 40)
        
        # Title
        title = QLabel("Install {APP_NAME}")
        title.setStyleSheet("font-size: 24px; font-weight: bold; color: #00FF00;")
        layout.addWidget(title)
        
        layout.addWidget(QLabel("Select Installation Location:"))
        
        # Path Selection
        path_layout = QVBoxLayout()
        self.path_input = QLineEdit(DEFAULT_PATH)
        btn_browse = QPushButton("Browse...")
        btn_browse.clicked.connect(self.browse)
        
        path_layout.addWidget(self.path_input)
        path_layout.addWidget(btn_browse)
        layout.addLayout(path_layout)
        
        # Progress
        self.bar = QProgressBar()
        self.bar.setValue(0)
        layout.addWidget(self.bar)
        
        # Install Button
        self.btn_install = QPushButton("INSTALL NOW")
        self.btn_install.setStyleSheet("background-color: #00FF00; color: black; font-size: 14px;")
        self.btn_install.clicked.connect(self.start_install)
        layout.addWidget(self.btn_install)
        
        layout.addStretch()
        self.setLayout(layout)
        
    def browse(self):
        d = QFileDialog.getExistingDirectory(self, "Select Folder")
        if d: self.path_input.setText(os.path.join(d, "{APP_NAME}"))
        
    def start_install(self):
        self.btn_install.setEnabled(False)
        self.btn_install.setText("Installing...")
        
        self.thread = InstallThread(self.path_input.text())
        self.thread.progress.connect(self.bar.setValue)
        self.thread.finished.connect(self.on_finished)
        self.thread.start()
        
    def on_finished(self, msg):
        if msg == "Success":
            QMessageBox.information(self, "Done", "{APP_NAME} Installed Successfully!")
            self.close()
        else:
            QMessageBox.critical(self, "Error", msg)
            self.btn_install.setEnabled(True)
            self.btn_install.setText("INSTALL NOW")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = InstallerWindow()
    win.show()
    sys.exit(app.exec())
"""
    with open(SETUP_SCRIPT, "w", encoding="utf-8") as f: f.write(setup_code)

    subprocess.check_call([
        "pyinstaller", SETUP_SCRIPT,
        "--name=QuishGuard_Setup",
        "--onefile", "--noconfirm", "--windowed",
        f"--distpath={DIST_DIR}", f"--workpath={BUILD_DIR}",
        "--collect-all=qtawesome", # Setup needs icons too maybe?
        "--hidden-import=winshell",
        "--hidden-import=win32com.client",
        "--clean"
    ])
    os.remove(SETUP_SCRIPT)

if __name__ == "__main__":
    clean()
    build_app()
    build_uninstaller()
    build_installer()
    
    # Cleanup binaries so only Setup remains?
    # os.remove(APP_EXE)
    # os.remove(UNINSTALL_EXE)
    
    print(f"\n[+] SUCCESS! Your Professional Installer is at:\n    {os.path.join(DIST_DIR, 'QuishGuard_Setup.exe')}")