from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QPushButton, QLabel, QFrame, QTextEdit)
from PyQt6.QtCore import Qt, QPropertyAnimation, QEasingCurve
from src.ui.styles import Theme

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        
        # Window Setup
        self.setWindowTitle("QuishGuard | Phishing Detector")
        self.resize(1000, 700)
        
        # State
        self.is_dark_mode = True
        self.is_sidebar_expanded = True
        
        # Main Container
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        
        self.main_layout = QHBoxLayout(self.central_widget)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)
        
        # --- 1. SIDEBAR ---
        self.sidebar = QFrame()
        self.sidebar.setObjectName("sidebar")
        self.sidebar.setFixedWidth(220) # Start Expanded
        
        self.sidebar_layout = QVBoxLayout(self.sidebar)
        self.sidebar_layout.setContentsMargins(0, 10, 0, 20)
        self.sidebar_layout.setSpacing(10)
        
        # Toggle Menu Button (Hamburger)
        self.btn_menu = QPushButton(" ≡")
        self.btn_menu.setObjectName("btn_menu")
        self.btn_menu.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_menu.clicked.connect(self.toggle_sidebar)
        
        # Navigation Buttons
        self.btn_scan = QPushButton(" SCANNER")
        self.btn_history = QPushButton(" HISTORY")
        
        # Theme Toggle (With Icon)
        self.btn_theme = QPushButton(" ☾  DARK MODE")
        self.btn_theme.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_theme.clicked.connect(self.toggle_theme)
        
        self.sidebar_layout.addWidget(self.btn_menu)
        self.sidebar_layout.addWidget(self.btn_scan)
        self.sidebar_layout.addWidget(self.btn_history)
        self.sidebar_layout.addStretch()
        self.sidebar_layout.addWidget(self.btn_theme)
        
        # --- 2. CONTENT AREA ---
        self.content_area = QWidget()
        self.content_layout = QVBoxLayout(self.content_area)
        self.content_layout.setContentsMargins(20, 20, 20, 20)
        
        self.drop_zone = QLabel("DRAG & DROP IMAGE / PDF HERE\n\n[ OR PASTE FROM CLIPBOARD ]")
        self.drop_zone.setObjectName("drop_zone")
        self.drop_zone.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        self.console = QTextEdit()
        self.console.setObjectName("console")
        self.console.setReadOnly(True)
        self.console.setFixedHeight(150)
        self.console.setText("[*] QuishGuard System Initialized...\n[*] Waiting for input...")
        
        self.content_layout.addWidget(self.drop_zone, stretch=2)
        self.content_layout.addWidget(self.console, stretch=1)
        
        self.main_layout.addWidget(self.sidebar)
        self.main_layout.addWidget(self.content_area)
        
        self.setStyleSheet(Theme.DARK_STYLES)

    def toggle_sidebar(self):
        """Animates the sidebar width"""
        width = self.sidebar.width()
        
        # If expanded (220), shrink to 60. If collapsed (60), grow to 220.
        target_width = 60 if width == 220 else 220
        
        # Animation Logic
        self.animation = QPropertyAnimation(self.sidebar, b"minimumWidth")
        self.animation.setDuration(300) # 300ms duration
        self.animation.setStartValue(width)
        self.animation.setEndValue(target_width)
        self.animation.setEasingCurve(QEasingCurve.Type.InOutQuart) # Smooth curve
        self.animation.start()
        
        # Also animate maximumWidth to prevent layout glitches
        self.anim_max = QPropertyAnimation(self.sidebar, b"maximumWidth")
        self.anim_max.setDuration(300)
        self.anim_max.setStartValue(width)
        self.anim_max.setEndValue(target_width)
        self.anim_max.setEasingCurve(QEasingCurve.Type.InOutQuart)
        self.anim_max.start()
        
        # Hide/Show Text depending on state
        if target_width == 60:
            self.btn_scan.setText("")
            self.btn_history.setText("")
            self.btn_theme.setText(" ☾")
            self.is_sidebar_expanded = False
        else:
            # Delay text restoration slightly so it doesn't overlap during animation
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