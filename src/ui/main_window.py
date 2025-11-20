from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QPushButton, QLabel, QFrame, QTextEdit)
from PyQt6.QtCore import Qt
from src.ui.styles import Theme

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        
        # Window Setup
        self.setWindowTitle("QuishGuard | Phishing Detector")
        self.resize(1000, 700)
        
        # State
        self.is_dark_mode = True
        
        # Main Container
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        
        # Main Layout (Horizontal: Sidebar | Main Content)
        self.main_layout = QHBoxLayout(self.central_widget)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)
        
        # --- 1. SIDEBAR ---
        self.sidebar = QFrame()
        self.sidebar.setObjectName("sidebar") # ID for Stylesheet
        self.sidebar.setFixedWidth(220)
        self.sidebar_layout = QVBoxLayout(self.sidebar)
        self.sidebar_layout.setContentsMargins(0, 20, 0, 20)
        
        # Sidebar Buttons
        self.btn_scan = QPushButton("  SCANNER")
        self.btn_history = QPushButton("  HISTORY")
        self.btn_theme = QPushButton("  TOGGLE THEME")
        
        self.btn_theme.clicked.connect(self.toggle_theme)
        
        self.sidebar_layout.addWidget(self.btn_scan)
        self.sidebar_layout.addWidget(self.btn_history)
        self.sidebar_layout.addStretch() # Pushes buttons to top
        self.sidebar_layout.addWidget(self.btn_theme)
        
        # --- 2. CONTENT AREA (Right Side) ---
        self.content_area = QWidget()
        self.content_layout = QVBoxLayout(self.content_area)
        self.content_layout.setContentsMargins(20, 20, 20, 20)
        
        # Drop Zone (Top)
        self.drop_zone = QLabel("DRAG & DROP IMAGE / PDF HERE\n\n[ OR PASTE FROM CLIPBOARD ]")
        self.drop_zone.setObjectName("drop_zone")
        self.drop_zone.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Console / Forensic Log (Bottom)
        self.console = QTextEdit()
        self.console.setObjectName("console")
        self.console.setReadOnly(True)
        self.console.setFixedHeight(150)
        self.console.setText("[*] QuishGuard System Initialized...\n[*] Waiting for input...")
        
        # Add to Content Layout
        self.content_layout.addWidget(self.drop_zone, stretch=2) # Takes 2/3 space
        self.content_layout.addWidget(self.console, stretch=1)   # Takes 1/3 space
        
        # Add frames to Main Layout
        self.main_layout.addWidget(self.sidebar)
        self.main_layout.addWidget(self.content_area)
        
        # Apply Initial Style
        self.setStyleSheet(Theme.DARK_STYLES)

    def toggle_theme(self):
        """Swaps between Dark and Light QSS"""
        if self.is_dark_mode:
            self.setStyleSheet(Theme.LIGHT_STYLES)
            self.is_dark_mode = False
        else:
            self.setStyleSheet(Theme.DARK_STYLES)
            self.is_dark_mode = True