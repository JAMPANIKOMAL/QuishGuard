import os
import sys
from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QPushButton, QLabel, QFrame, QTextEdit, QFileDialog, 
                             QApplication, QSplitter) # Added QSplitter
from PyQt6.QtCore import Qt, QPropertyAnimation, QEasingCurve, pyqtSignal, QSize
from PyQt6.QtGui import QDragEnterEvent, QDropEvent, QAction

# --- NEW IMPORT: Professional Icons ---
import qtawesome as qta 
from defang import defang 

from src.ui.styles import Theme
from src.core.scanner import ScannerEngine
from src.core.analyzer import URLAnalyzer 

# --- CUSTOM WIDGET ---
class ClickableDropZone(QLabel):
    clicked = pyqtSignal() 
    def __init__(self, text, parent=None):
        super().__init__(text, parent)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setObjectName("drop_zone")
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setWordWrap(True) # Allow text to wrap if filename is long

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit()

# --- MAIN WINDOW ---
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        
        self.scanner = ScannerEngine()
        self.analyzer = URLAnalyzer() 
        
        # Window Setup
        self.setWindowTitle("QuishGuard | Phishing Detector")
        self.resize(1100, 750)
        self.setAcceptDrops(True) 
        
        self.is_dark_mode = True
        self.is_sidebar_expanded = True
        
        # --- ICONS SETUP (FontAwesome) ---
        # We create icons with specific colors for Dark Mode
        self.icon_menu = qta.icon('fa5s.bars', color='white')
        self.icon_scan = qta.icon('fa5s.qrcode', color='#888888')
        self.icon_hist = qta.icon('fa5s.history', color='#888888')
        self.icon_moon = qta.icon('fa5s.moon', color='#888888')
        self.icon_sun  = qta.icon('fa5s.sun', color='#555555')
        self.icon_file = qta.icon('fa5s.file-alt', color='white') # For file drop

        # --- LAYOUT ---
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QHBoxLayout(self.central_widget)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)
        
        # 1. SIDEBAR
        self.sidebar = QFrame()
        self.sidebar.setObjectName("sidebar")
        self.sidebar.setFixedWidth(220)
        self.sidebar_layout = QVBoxLayout(self.sidebar)
        self.sidebar_layout.setContentsMargins(0, 10, 0, 20)
        self.sidebar_layout.setSpacing(5)
        
        # Menu Button
        self.btn_menu = QPushButton()
        self.btn_menu.setIcon(self.icon_menu)
        self.btn_menu.setIconSize(QSize(24, 24))
        self.btn_menu.setObjectName("btn_menu")
        self.btn_menu.clicked.connect(self.toggle_sidebar)
        
        # Nav Buttons
        self.btn_scan = QPushButton("  SCANNER")
        self.btn_scan.setIcon(self.icon_scan)
        self.btn_scan.setIconSize(QSize(20, 20))
        
        self.btn_history = QPushButton("  HISTORY")
        self.btn_history.setIcon(self.icon_hist)
        self.btn_history.setIconSize(QSize(20, 20))
        
        # Theme Button
        self.btn_theme = QPushButton("  DARK MODE")
        self.btn_theme.setIcon(self.icon_moon)
        self.btn_theme.setIconSize(QSize(20, 20))
        self.btn_theme.clicked.connect(self.toggle_theme)
        
        self.sidebar_layout.addWidget(self.btn_menu)
        self.sidebar_layout.addSpacing(20) # Space after menu
        self.sidebar_layout.addWidget(self.btn_scan)
        self.sidebar_layout.addWidget(self.btn_history)
        self.sidebar_layout.addStretch()
        self.sidebar_layout.addWidget(self.btn_theme)
        
        # 2. CONTENT AREA (Using QSplitter for Resizing)
        self.content_area = QWidget()
        self.content_layout = QVBoxLayout(self.content_area)
        self.content_layout.setContentsMargins(20, 20, 20, 20)
        
        # The Splitter holds the Drop Zone (Top) and Console (Bottom)
        self.splitter = QSplitter(Qt.Orientation.Vertical)
        self.splitter.setHandleWidth(2) # Thin divider
        
        # Top: Drop Zone
        self.drop_zone = ClickableDropZone("CLICK TO UPLOAD\n\n[ OR DRAG FILE HERE ]\n[ OR PASTE (CTRL+V) ]")
        self.drop_zone.clicked.connect(self.open_file_dialog)
        self.splitter.addWidget(self.drop_zone)
        
        # Bottom: Console
        self.console = QTextEdit()
        self.console.setObjectName("console")
        self.console.setReadOnly(True)
        self.console.setMinimumHeight(100) # Don't let it vanish
        self.splitter.addWidget(self.console)
        
        # Set initial ratio (2/3 Drop Zone, 1/3 Console)
        self.splitter.setSizes([500, 200])
        
        self.content_layout.addWidget(self.splitter)
        
        self.main_layout.addWidget(self.sidebar)
        self.main_layout.addWidget(self.content_area)
        self.setStyleSheet(Theme.DARK_STYLES)
        
        self.log_message("[*] QuishGuard Pro Loaded.")
        self.log_message("[*] Icons: qtawesome loaded.")

    def log_message(self, message):
        self.console.append(message)

    # --- LOGIC ---
    def process_file(self, file_path):
        if not file_path or not os.path.exists(file_path):
             return

        filename = os.path.basename(file_path)
        self.log_message(f"\n[>] Processing: {filename}")
        
        # DYNAMIC UI UPDATE: Change the Drop Zone text
        self.drop_zone.setText(f"ANALYZING:\n{filename}\n\n[ Drop new file to reset ]")
        self.drop_zone.setStyleSheet("color: #00FF00; border-color: #00FF00;") # Cyber Green border
        
        # 1. Extract
        raw_data = self.scanner.extract_qr(file_path)
        
        if not raw_data:
            self.log_message("[-] No QR Code found.")
            self.drop_zone.setStyleSheet("") # Reset style
            self.drop_zone.setText("NO QR FOUND\n\n[ Try Another File ]")
            return
        
        if raw_data.startswith("[!]"):
            self.log_message(raw_data)
            return

        # 2. Analyze
        analysis = self.analyzer.analyze(raw_data)
        
        if analysis["status"] == "error":
            self.log_message(f"[!] Analysis Failed: {analysis['message']}")
        elif analysis["type"] == "Text":
             self.log_message(f"[i] Type: Plain Text: {analysis['original']}")
        else:
            self.log_message(f"[i] Type: URL")
            self.log_message(f"[>] Destination: {analysis['final']}")
            if len(analysis["chain"]) > 1:
                self.log_message("[~] Redirection Chain:")
                for i, hop in enumerate(analysis["chain"]):
                    self.log_message(f"    {i+1}. {defang(hop)}")

    # --- INPUT HANDLERS (Unchanged) ---
    def open_file_dialog(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Select Image", "", "Files (*.png *.jpg *.jpeg *.pdf)")
        if file_path:
            self.process_file(file_path)

    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasUrls():
            event.accept()
        else:
            event.ignore()

    def dropEvent(self, event: QDropEvent):
        for url in event.mimeData().urls():
            file_path = url.toLocalFile()
            if file_path and os.path.exists(file_path):
                self.process_file(file_path)

    def keyPressEvent(self, event):
        if event.modifiers() == Qt.KeyboardModifier.ControlModifier and event.key() == Qt.Key.Key_V:
            clipboard = QApplication.clipboard()
            mime_data = clipboard.mimeData()
            if mime_data.hasImage():
                image = clipboard.image()
                temp_path = os.path.abspath("temp_clipboard_scan.png")
                image.save(temp_path)
                self.process_file(temp_path)
            elif mime_data.hasUrls():
                self.process_file(mime_data.urls()[0].toLocalFile())

    # --- UI ANIMATIONS (Revised for Icons) ---
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
            # Collapsed: Text Empty, Icons Centered
            self.btn_scan.setText("")
            self.btn_history.setText("")
            self.btn_theme.setText("")
            self.is_sidebar_expanded = False
        else:
            # Expanded: Text Visible
            self.btn_scan.setText("  SCANNER")
            self.btn_history.setText("  HISTORY")
            self.btn_theme.setText("  DARK MODE" if self.is_dark_mode else "  LIGHT MODE")
            self.is_sidebar_expanded = True

    def toggle_theme(self):
        if self.is_dark_mode:
            self.setStyleSheet(Theme.LIGHT_STYLES)
            # Update icons to dark color for light background
            self.icon_scan = qta.icon('fa5s.qrcode', color='#555555')
            self.icon_hist = qta.icon('fa5s.history', color='#555555')
            self.btn_scan.setIcon(self.icon_scan)
            self.btn_history.setIcon(self.icon_hist)
            self.btn_theme.setIcon(self.icon_sun)
            self.btn_theme.setText("" if not self.is_sidebar_expanded else "  LIGHT MODE")
            self.is_dark_mode = False
        else:
            self.setStyleSheet(Theme.DARK_STYLES)
            self.icon_scan = qta.icon('fa5s.qrcode', color='#888888')
            self.icon_hist = qta.icon('fa5s.history', color='#888888')
            self.btn_scan.setIcon(self.icon_scan)
            self.btn_history.setIcon(self.icon_hist)
            self.btn_theme.setIcon(self.icon_moon)
            self.btn_theme.setText("" if not self.is_sidebar_expanded else "  DARK MODE")
            self.is_dark_mode = True