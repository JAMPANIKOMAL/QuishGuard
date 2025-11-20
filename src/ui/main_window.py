import os
import sys
from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QPushButton, QLabel, QFrame, QTextEdit, QFileDialog)
from PyQt6.QtCore import Qt, QPropertyAnimation, QEasingCurve, pyqtSignal
from PyQt6.QtGui import QDragEnterEvent, QDropEvent

from src.ui.styles import Theme
from src.core.scanner import ScannerEngine

# --- CUSTOM WIDGET: CLICKABLE LABEL ---
class ClickableDropZone(QLabel):
    clicked = pyqtSignal() # Signal to tell the window we were clicked

    def __init__(self, text, parent=None):
        super().__init__(text, parent)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setObjectName("drop_zone") # Keep style
        # Set policy to ensure it accepts clicks
        self.setCursor(Qt.CursorShape.PointingHandCursor)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit()

# --- MAIN WINDOW ---
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        
        self.scanner = ScannerEngine()
        
        # Window Setup
        self.setWindowTitle("QuishGuard | Phishing Detector")
        self.resize(1000, 700)
        self.setAcceptDrops(True) 
        
        # State
        self.is_dark_mode = True
        self.is_sidebar_expanded = True
        
        # Main Layout Setup
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QHBoxLayout(self.central_widget)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)
        
        # --- SIDEBAR ---
        self.sidebar = QFrame()
        self.sidebar.setObjectName("sidebar")
        self.sidebar.setFixedWidth(220)
        
        self.sidebar_layout = QVBoxLayout(self.sidebar)
        self.sidebar_layout.setContentsMargins(0, 10, 0, 20)
        self.sidebar_layout.setSpacing(10)
        
        self.btn_menu = QPushButton(" ≡")
        self.btn_menu.setObjectName("btn_menu")
        self.btn_menu.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_menu.clicked.connect(self.toggle_sidebar)
        
        self.btn_scan = QPushButton(" SCANNER")
        self.btn_history = QPushButton(" HISTORY")
        self.btn_theme = QPushButton(" ☾  DARK MODE")
        self.btn_theme.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_theme.clicked.connect(self.toggle_theme)
        
        self.sidebar_layout.addWidget(self.btn_menu)
        self.sidebar_layout.addWidget(self.btn_scan)
        self.sidebar_layout.addWidget(self.btn_history)
        self.sidebar_layout.addStretch()
        self.sidebar_layout.addWidget(self.btn_theme)
        
        # --- CONTENT AREA ---
        self.content_area = QWidget()
        self.content_layout = QVBoxLayout(self.content_area)
        self.content_layout.setContentsMargins(20, 20, 20, 20)
        
        # NEW: Clickable Drop Zone
        self.drop_zone = ClickableDropZone("CLICK TO UPLOAD\n\n[ OR DRAG & DROP FILE HERE ]")
        self.drop_zone.clicked.connect(self.open_file_dialog) # Connect click to function
        
        self.console = QTextEdit()
        self.console.setObjectName("console")
        self.console.setReadOnly(True)
        self.console.setFixedHeight(150)
        self.log_message("[*] QuishGuard System Initialized...")
        self.log_message("[*] Engine ready. Drop a file or click to upload.")
        
        self.content_layout.addWidget(self.drop_zone, stretch=2)
        self.content_layout.addWidget(self.console, stretch=1)
        
        self.main_layout.addWidget(self.sidebar)
        self.main_layout.addWidget(self.content_area)
        
        self.setStyleSheet(Theme.DARK_STYLES)

    # --- LOGGING ---
    def log_message(self, message):
        self.console.append(message)

    # --- FILE HANDLING LOGIC (The Fix) ---
    def process_file(self, file_path):
        """Common function to process a file path from any source"""
        if not file_path:
            return

        # Clean the path for Windows
        file_path = os.path.normpath(file_path)
        
        self.log_message(f"\n[>] Analyzing file: {os.path.basename(file_path)}")
        
        if not os.path.exists(file_path):
             self.log_message(f"[!] Error: System cannot find path: {file_path}")
             return

        # CALL THE BRAIN
        result = self.scanner.extract_qr(file_path)
        
        if result:
            if result.startswith("[!]"): 
                self.log_message(result)
            else:
                self.log_message(f"[+] QR DETECTED: {result}")
                self.log_message("[*] Analysis required for this URL.")
        else:
            self.log_message("[-] No QR Code found.")

    def open_file_dialog(self):
        """Opens the Windows File Explorer"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, 
            "Select Image", 
            "", 
            "Images (*.png *.jpg *.jpeg *.bmp *.pdf)"
        )
        if file_path:
            self.process_file(file_path)

    # --- DRAG AND DROP EVENTS ---
    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasUrls():
            event.accept()
        else:
            event.ignore()

    def dropEvent(self, event: QDropEvent):
        """Bulletproof Drop Handler"""
        for url in event.mimeData().urls():
            # Method 1: Standard Qt (Works 90% of time)
            file_path = url.toLocalFile()
            
            # Method 2: Fallback for raw paths (The Fix)
            if not file_path:
                file_path = url.path()
                # Windows Fix: remove leading slash if present (e.g. /C:/Users -> C:/Users)
                if os.name == 'nt' and file_path.startswith('/'):
                    file_path = file_path[1:]
            
            self.process_file(file_path)

    # --- ANIMATIONS (Unchanged) ---
    def toggle_sidebar(self):
        width = self.sidebar.width()
        target_width = 60 if width == 220 else 220
        self.animation = QPropertyAnimation(self.sidebar, b"minimumWidth")
        self.animation.setDuration(300)
        self.animation.setStartValue(width)
        self.animation.setEndValue(target_width)
        self.animation.setEasingCurve(QEasingCurve.Type.InOutQuart)
        self.animation.start()
        
        self.anim_max = QPropertyAnimation(self.sidebar, b"maximumWidth")
        self.anim_max.setDuration(300)
        self.anim_max.setStartValue(width)
        self.anim_max.setEndValue(target_width)
        self.anim_max.setEasingCurve(QEasingCurve.Type.InOutQuart)
        self.anim_max.start()
        
        if target_width == 60:
            self.btn_scan.setText("")
            self.btn_history.setText("")
            self.btn_theme.setText(" ☾")
            self.is_sidebar_expanded = False
        else:
            self.btn_scan.setText(" SCANNER")
            self.btn_history.setText(" HISTORY")
            icon = " ☾" if self.is_dark_mode else " ☀"
            text = "  DARK MODE" if self.is_dark_mode else "  LIGHT MODE"
            self.btn_theme.setText(icon + text)
            self.is_sidebar_expanded = True

    def toggle_theme(self):
        if self.is_dark_mode:
            self.setStyleSheet(Theme.LIGHT_STYLES)
            self.btn_theme.setText(" ☀" if not self.is_sidebar_expanded else " ☀  LIGHT MODE")
            self.is_dark_mode = False
        else:
            self.setStyleSheet(Theme.DARK_STYLES)
            self.btn_theme.setText(" ☾" if not self.is_sidebar_expanded else " ☾  DARK MODE")
            self.is_dark_mode = True