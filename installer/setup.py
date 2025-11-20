import sys
import os
import shutil
import winshell
from pathlib import Path
from PyQt6.QtWidgets import (QApplication, QWidget, QVBoxLayout, QLabel, 
                             QPushButton, QLineEdit, QFileDialog, QProgressBar, 
                             QStackedWidget, QHBoxLayout, QMessageBox, QFrame)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QIcon, QPixmap
from win32com.client import Dispatch

# Configuration
APP_NAME = "QuishGuard"
DEFAULT_PATH = os.path.join(os.environ['LOCALAPPDATA'], APP_NAME)

# Resource Helper (Finds bundled files inside PyInstaller)
def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

class InstallWorker(QThread):
    progress = pyqtSignal(int)
    status = pyqtSignal(str)
    finished = pyqtSignal(bool, str)
    
    def __init__(self, target_dir):
        super().__init__()
        self.target_dir = target_dir
        
    def run(self):
        try:
            # 1. Prepare
            self.status.emit("Creating directories...")
            self.progress.emit(10)
            if not os.path.exists(self.target_dir):
                os.makedirs(self.target_dir)
            
            # 2. Extract Files
            # In the 'Professional' build, we bundle the EXE as a data file named 'CORE_APP'
            self.status.emit("Copying application files...")
            self.progress.emit(30)
            
            src_app = resource_path("QuishGuard.exe")
            src_uninst = resource_path("Uninstall.exe")
            
            dst_app = os.path.join(self.target_dir, "QuishGuard.exe")
            dst_uninst = os.path.join(self.target_dir, "Uninstall.exe")
            
            shutil.copy2(src_app, dst_app)
            self.progress.emit(60)
            shutil.copy2(src_uninst, dst_uninst)
            self.progress.emit(70)
            
            # 3. Create Shortcuts
            self.status.emit("Creating shortcuts...")
            desktop = winshell.desktop()
            shell = Dispatch('WScript.Shell')
            
            lnk = shell.CreateShortCut(os.path.join(desktop, f"{APP_NAME}.lnk"))
            lnk.Targetpath = dst_app
            lnk.WorkingDirectory = self.target_dir
            lnk.save()
            
            self.progress.emit(100)
            self.status.emit("Installation Complete.")
            self.finished.emit(True, "Success")
            
        except Exception as e:
            self.finished.emit(False, str(e))

class SetupWizard(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(f"{APP_NAME} Setup")
        self.setFixedSize(600, 400)
        self.setStyleSheet("""
            QWidget { background-color: #121212; color: white; font-family: 'Segoe UI', sans-serif; }
            QPushButton { background-color: #333; border: 1px solid #555; color: white; padding: 8px 16px; border-radius: 4px; }
            QPushButton:hover { background-color: #444; border-color: #00FF00; }
            QPushButton:disabled { background-color: #222; color: #555; border-color: #333; }
            QLineEdit { background-color: #222; border: 1px solid #444; color: white; padding: 5px; }
            QProgressBar { border: 1px solid #444; text-align: center; background-color: #222; }
            QProgressBar::chunk { background-color: #00FF00; }
            QLabel#Title { font-size: 22px; font-weight: bold; color: #00FF00; }
            QLabel#Desc { font-size: 14px; color: #AAA; }
        """)
        
        self.layout = QVBoxLayout(self)
        self.stack = QStackedWidget()
        
        # Pages
        self.page1_welcome = self.create_welcome_page()
        self.page2_location = self.create_location_page()
        self.page3_install = self.create_install_page()
        self.page4_finish = self.create_finish_page()
        
        self.stack.addWidget(self.page1_welcome)
        self.stack.addWidget(self.page2_location)
        self.stack.addWidget(self.page3_install)
        self.stack.addWidget(self.page4_finish)
        
        self.layout.addWidget(self.stack)
        
        # Bottom Bar
        self.btn_layout = QHBoxLayout()
        self.btn_cancel = QPushButton("Cancel")
        self.btn_cancel.clicked.connect(self.close)
        self.btn_next = QPushButton("Next >")
        self.btn_next.clicked.connect(self.next_page)
        
        self.btn_layout.addWidget(self.btn_cancel)
        self.btn_layout.addStretch()
        self.btn_layout.addWidget(self.btn_next)
        
        self.layout.addLayout(self.btn_layout)
        
    def create_welcome_page(self):
        p = QWidget()
        l = QVBoxLayout(p)
        title = QLabel(f"Welcome to the {APP_NAME} Setup Wizard"); title.setObjectName("Title")
        desc = QLabel(f"\nThis will install {APP_NAME} on your computer.\n\nIt is recommended that you close all other applications before continuing.\n\nClick Next to continue, or Cancel to exit Setup."); desc.setObjectName("Desc")
        desc.setWordWrap(True)
        l.addStretch()
        l.addWidget(title)
        l.addWidget(desc)
        l.addStretch()
        return p

    def create_location_page(self):
        p = QWidget()
        l = QVBoxLayout(p)
        title = QLabel("Select Destination Location"); title.setObjectName("Title")
        desc = QLabel(f"Where should {APP_NAME} be installed?"); desc.setObjectName("Desc")
        
        self.path_edit = QLineEdit(DEFAULT_PATH)
        browse_btn = QPushButton("Browse...")
        browse_btn.clicked.connect(self.browse_folder)
        
        h = QHBoxLayout()
        h.addWidget(self.path_edit)
        h.addWidget(browse_btn)
        
        l.addStretch()
        l.addWidget(title)
        l.addWidget(desc)
        l.addLayout(h)
        l.addStretch()
        return p

    def create_install_page(self):
        p = QWidget()
        l = QVBoxLayout(p)
        title = QLabel("Installing..."); title.setObjectName("Title")
        self.status_label = QLabel("Preparing..."); self.status_label.setObjectName("Desc")
        self.progress = QProgressBar()
        self.progress.setValue(0)
        
        l.addStretch()
        l.addWidget(title)
        l.addWidget(self.status_label)
        l.addWidget(self.progress)
        l.addStretch()
        return p

    def create_finish_page(self):
        p = QWidget()
        l = QVBoxLayout(p)
        title = QLabel("Installation Complete"); title.setObjectName("Title")
        desc = QLabel(f"{APP_NAME} has been installed on your computer.\n\nClick Finish to close this wizard."); desc.setObjectName("Desc")
        l.addStretch()
        l.addWidget(title)
        l.addWidget(desc)
        l.addStretch()
        return p

    def browse_folder(self):
        d = QFileDialog.getExistingDirectory(self, "Select Install Folder")
        if d: self.path_input.setText(os.path.join(d, APP_NAME))

    def next_page(self):
        idx = self.stack.currentIndex()
        if idx == 0:
            self.stack.setCurrentIndex(1)
        elif idx == 1:
            self.stack.setCurrentIndex(2)
            self.run_installation()
        elif idx == 2:
            pass # Wait for install
        elif idx == 3:
            self.close()

    def run_installation(self):
        self.btn_next.setEnabled(False)
        self.btn_cancel.setEnabled(False)
        self.worker = InstallWorker(self.path_edit.text())
        self.worker.progress.connect(self.progress.setValue)
        self.worker.status.connect(self.status_label.setText)
        self.worker.finished.connect(self.install_finished)
        self.worker.start()

    def install_finished(self, success, msg):
        if success:
            self.stack.setCurrentIndex(3)
            self.btn_next.setText("Finish")
            self.btn_next.setEnabled(True)
            self.btn_cancel.setVisible(False)
        else:
            QMessageBox.critical(self, "Error", msg)
            self.btn_next.setEnabled(True)
            self.btn_cancel.setEnabled(True)
            self.stack.setCurrentIndex(1)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    wiz = SetupWizard()
    wiz.show()
    sys.exit(app.exec())