import os
import sys
import shutil # specific for temporary file handling
from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QPushButton, QLabel, QFrame, QTextEdit, QFileDialog, QApplication)
from PyQt6.QtCore import Qt, QPropertyAnimation, QEasingCurve, pyqtSignal, QUrl
from PyQt6.QtGui import QDragEnterEvent, QDropEvent, QPixmap, QKeySequence, QShortcut

from src.ui.styles import Theme
from src.core.scanner import ScannerEngine

# --- CUSTOM WIDGET (Unchanged) ---
class ClickableDropZone(QLabel):
    clicked = pyqtSignal() 
    def __init__(self, text, parent=None):
        super().__init__(text, parent)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setObjectName("drop_zone")
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
        
        # Main Layout
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
        self.btn_menu.clicked.connect(self.toggle_sidebar)
        
        self.btn_scan = QPushButton(" SCANNER")
        self.btn_history = QPushButton(" HISTORY")
        self.btn_theme = QPushButton(" ☾  DARK MODE")
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
        
        self.drop_zone = ClickableDropZone("CLICK TO UPLOAD\n\n[ OR DRAG FILE HERE ]\n[ OR PASTE (CTRL+V) ]")
        self.drop_zone.clicked.connect(self.open_file_dialog)
        
        self.console = QTextEdit()
        self.console.setObjectName("console")
        self.console.setReadOnly(True)
        self.console.setFixedHeight(150)
        self.log_message("[*] QuishGuard System Initialized...")
        self.log_message("[*] Ready. Paste image (Ctrl+V), Drag & Drop, or Click.")
        
        self.content_layout.addWidget(self.drop_zone, stretch=2)
        self.content_layout.addWidget(self.console, stretch=1)
        
        self.main_layout.addWidget(self.sidebar)
        self.main_layout.addWidget(self.content_area)
        
        self.setStyleSheet(Theme.DARK_STYLES)

    # --- LOGGING ---
    def log_message(self, message):
        self.console.append(message)

    # --- CLIPBOARD SUPPORT (New) ---
    def keyPressEvent(self, event):
        """Detects Ctrl+V to paste images"""
        if event.modifiers() == Qt.KeyboardModifier.ControlModifier and event.key() == Qt.Key.Key_V:
            self.handle_paste()
        else:
            super().keyPressEvent(event)

    def handle_paste(self):
        clipboard = QApplication.clipboard()
        mime_data = clipboard.mimeData()

        if mime_data.hasImage():
            self.log_message("\n[>] Clipboard image detected...")
            # Save clipboard image to a temporary file so the scanner can read it
            image = clipboard.image()
            temp_path = os.path.abspath("temp_clipboard_scan.png")
            image.save(temp_path)
            self.process_file(temp_path)
        elif mime_data.hasUrls():
            # If they copied a file file from Explorer
            url = mime_data.urls()[0]
            self.process_file(url.toLocalFile())
        else:
            self.log_message("[-] Clipboard is empty or does not contain an image.")

    # --- LOGIC ---
    def process_file(self, file_path):
        if not file_path:
            return

        file_path = os.path.normpath(file_path) # Fix slashes
        
        # Filter out bad paths (like the "url" error you saw)
        if not os.path.exists(file_path):
             self.log_message(f"[!] Error: System cannot find path: {file_path}")
             return

        self.log_message(f"\n[>] Analyzing: {os.path.basename(file_path)}")
        
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
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select Image", "", "Images (*.png *.jpg *.jpeg *.bmp *.pdf)"
        )
        if file_path:
            self.process_file(file_path)

    # --- DRAG AND DROP (Refined) ---
    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasUrls():
            event.accept()
        else:
            event.ignore()

    def dropEvent(self, event: QDropEvent):
        for url in event.mimeData().urls():
            file_path = url.toLocalFile()
            
            # Check if valid path
            if file_path and os.path.exists(file_path):
                self.process_file(file_path)
            else:
                self.log_message(f"[!] drop ignored: Invalid file source. Try clicking to upload.")

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