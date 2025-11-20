import os
import sys
from datetime import datetime
from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QPushButton, QLabel, QFrame, QTextEdit, QFileDialog, 
                             QApplication, QSplitter, QProgressBar, QStackedWidget,
                             QTableWidget, QTableWidgetItem, QHeaderView, QMessageBox)
from PyQt6.QtCore import Qt, QPropertyAnimation, QEasingCurve, pyqtSignal, QSize
from PyQt6.QtGui import QDragEnterEvent, QDropEvent

import qtawesome as qta 
from defang import defang 

from src.ui.styles import Theme
from src.core.scanner import ScannerEngine
from src.core.analyzer import URLAnalyzer
from src.utils.history import HistoryManager 

# --- CUSTOM DROPPABLE LABEL ---
class ClickableDropZone(QLabel):
    clicked = pyqtSignal() 
    def __init__(self, text, parent=None):
        super().__init__(text, parent)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setObjectName("drop_zone")
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setWordWrap(True)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit()

# --- MAIN WINDOW ---
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        
        self.scanner = ScannerEngine()
        self.analyzer = URLAnalyzer()
        self.history_manager = HistoryManager()
        
        # Track current file for reporting
        self.current_file_name = None
        self.current_scan_time = None
        
        self.setWindowTitle("QuishGuard | Phishing Detector")
        self.resize(1100, 750)
        self.setAcceptDrops(True) 
        
        self.is_dark_mode = True
        self.is_sidebar_expanded = True 
        
        # Icons
        self.icon_menu = qta.icon('fa5s.bars', color='white')
        self.icon_scan = qta.icon('fa5s.qrcode', color='#888888')
        self.icon_hist = qta.icon('fa5s.history', color='#888888')
        self.icon_info = qta.icon('fa5s.info-circle', color='#888888') 
        self.icon_save = qta.icon('fa5s.file-export', color='#888888') 
        self.icon_moon = qta.icon('fa5s.moon', color='#888888')
        self.icon_sun  = qta.icon('fa5s.sun', color='#555555')

        # --- LAYOUT ---
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QHBoxLayout(self.central_widget)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)
        
        self.init_sidebar()
        self.stack = QStackedWidget()
        
        self.page_scanner = QWidget()
        self.init_scanner_ui()
        self.stack.addWidget(self.page_scanner)
        
        self.page_history = QWidget()
        self.init_history_ui()
        self.stack.addWidget(self.page_history)
        
        self.page_about = QWidget()
        self.init_about_ui()
        self.stack.addWidget(self.page_about)
        
        self.main_layout.addWidget(self.sidebar)
        self.main_layout.addWidget(self.stack)
        
        self.setStyleSheet(Theme.DARK_STYLES)
        self.log_message("[*] QuishGuard Pro Loaded.")

    # --- UI SETUP ---
    def init_sidebar(self):
        self.sidebar = QFrame()
        self.sidebar.setObjectName("sidebar")
        self.sidebar.setFixedWidth(150) 
        self.sidebar_layout = QVBoxLayout(self.sidebar)
        self.sidebar_layout.setContentsMargins(0, 10, 0, 20)
        self.sidebar_layout.setSpacing(5)
        
        self.btn_menu = QPushButton(); self.btn_menu.setIcon(self.icon_menu); self.btn_menu.setIconSize(QSize(20, 20))
        self.btn_menu.clicked.connect(self.toggle_sidebar)
        
        self.btn_scan = QPushButton("  SCANNER"); self.btn_scan.setIcon(self.icon_scan); self.btn_scan.setIconSize(QSize(20, 20))
        self.btn_scan.clicked.connect(lambda: self.switch_page(0))
        
        self.btn_hist = QPushButton("  HISTORY"); self.btn_hist.setIcon(self.icon_hist); self.btn_hist.setIconSize(QSize(20, 20))
        self.btn_hist.clicked.connect(lambda: self.switch_page(1))
        
        self.btn_about = QPushButton("  ABOUT"); self.btn_about.setIcon(self.icon_info); self.btn_about.setIconSize(QSize(20, 20))
        self.btn_about.clicked.connect(lambda: self.switch_page(2))

        self.btn_theme = QPushButton("  DARK MODE"); self.btn_theme.setIcon(self.icon_moon); self.btn_theme.setIconSize(QSize(20, 20))
        self.btn_theme.clicked.connect(self.toggle_theme)
        
        self.sidebar_layout.addWidget(self.btn_menu); self.sidebar_layout.addSpacing(20)
        self.sidebar_layout.addWidget(self.btn_scan)
        self.sidebar_layout.addWidget(self.btn_hist)
        self.sidebar_layout.addWidget(self.btn_about)
        self.sidebar_layout.addStretch()
        self.sidebar_layout.addWidget(self.btn_theme)

    def init_scanner_ui(self):
        layout = QVBoxLayout(self.page_scanner)
        layout.setContentsMargins(20, 20, 20, 20)
        
        self.splitter = QSplitter(Qt.Orientation.Vertical)
        self.splitter.setHandleWidth(2)
        
        self.drop_zone = ClickableDropZone("CLICK TO UPLOAD\n\n[ OR DRAG FILE HERE ]\n[ OR PASTE (CTRL+V) ]")
        self.drop_zone.clicked.connect(self.open_file_dialog)
        self.splitter.addWidget(self.drop_zone)
        
        # Console Container
        console_widget = QWidget()
        console_layout = QVBoxLayout(console_widget)
        console_layout.setContentsMargins(0, 0, 0, 0)
        
        # Progress Bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setFixedHeight(4)
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setStyleSheet("QProgressBar { border: none; background: #222; } QProgressBar::chunk { background: #00FF00; }")
        self.progress_bar.setVisible(False)
        
        # Text Area
        self.console = QTextEdit()
        self.console.setObjectName("console")
        self.console.setReadOnly(True)
        
        # Save Report Button (Aligned Right, integrated look)
        self.btn_save_report = QPushButton(" Save Report to Disk")
        self.btn_save_report.setIcon(self.icon_save)
        self.btn_save_report.setFixedSize(160, 30)
        self.btn_save_report.clicked.connect(self.save_report)
        # Only show button when scan is done (optional, but good for focus)
        self.btn_save_report.setEnabled(False) 
        
        console_layout.addWidget(self.progress_bar)
        console_layout.addWidget(self.console)
        console_layout.addWidget(self.btn_save_report, alignment=Qt.AlignmentFlag.AlignRight)
        
        self.splitter.addWidget(console_widget)
        self.splitter.setSizes([500, 200])
        layout.addWidget(self.splitter)

    def init_history_ui(self):
        layout = QVBoxLayout(self.page_history)
        layout.setContentsMargins(20, 20, 20, 20)
        title = QLabel("SCAN HISTORY")
        title.setStyleSheet("font-size: 24px; font-weight: bold; color: #888;")
        layout.addWidget(title)
        self.table = QTableWidget()
        self.table.setColumnCount(4) 
        self.table.setHorizontalHeaderLabels(["Time", "File", "Type", "Content"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.setStyleSheet("background-color: #1E1E1E; color: #CCC; border: 1px solid #333; gridline-color: #333;")
        self.table.verticalHeader().setVisible(False)
        layout.addWidget(self.table)
        btn_refresh = QPushButton("Refresh Log")
        btn_refresh.setFixedSize(120, 30)
        btn_refresh.clicked.connect(self.load_history_data)
        layout.addWidget(btn_refresh, alignment=Qt.AlignmentFlag.AlignRight)

    def init_about_ui(self):
        layout = QVBoxLayout(self.page_about)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title = QLabel("QuishGuard"); title.setStyleSheet("font-size: 40px; font-weight: bold; color: #FFF;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        desc = QLabel("Advanced QR Phishing Detection System\n\nVersion 1.0.0\n\nDeveloped by Jampani Komal"); desc.setStyleSheet("font-size: 16px; color: #888;")
        desc.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title); layout.addWidget(desc)

    # --- LOGIC ---
    def switch_page(self, index):
        self.stack.setCurrentIndex(index)
        if index == 1: self.load_history_data()

    def load_history_data(self):
        data = self.history_manager.load_history()
        self.table.setRowCount(len(data))
        for row, entry in enumerate(data):
            self.table.setItem(row, 0, QTableWidgetItem(entry.get("timestamp", "")))
            self.table.setItem(row, 1, QTableWidgetItem(entry.get("file", "")))
            self.table.setItem(row, 2, QTableWidgetItem(entry.get("type", "")))
            self.table.setItem(row, 3, QTableWidgetItem(entry.get("content", "")))

    def log_message(self, message):
        self.console.append(message)
        sb = self.console.verticalScrollBar(); sb.setValue(sb.maximum())

    def update_progress(self, value):
        self.progress_bar.setValue(value); QApplication.processEvents()

    def save_report(self):
        """
        Generates a Professional Forensic Report.
        Auto-names the file with Date + Filename.
        """
        if not self.current_file_name:
            return

        # 1. Auto-Generate Filename
        # Clean filename to remove slashes/spaces
        safe_name = os.path.basename(self.current_file_name).replace(" ", "_")
        timestamp_str = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        default_name = f"QuishGuard_Report_{safe_name}_{timestamp_str}.txt"
        
        # 2. Get Save Path
        path, _ = QFileDialog.getSaveFileName(self, "Save Forensic Report", default_name, "Text Files (*.txt)")
        
        if path:
            # 3. Construct Professional Content
            report_content = []
            report_content.append("======================================================================")
            report_content.append("                     QUISHGUARD FORENSIC REPORT                       ")
            report_content.append("======================================================================")
            report_content.append(f"Date Generated : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            report_content.append(f"Target File    : {self.current_file_name}")
            report_content.append(f"Analyst Tool   : QuishGuard v1.0")
            report_content.append("======================================================================\n")
            
            report_content.append("[ ANALYSIS LOGS ]")
            report_content.append("-" * 60)
            # Grab everything from the console window
            report_content.append(self.console.toPlainText())
            
            report_content.append("\n" + "=" * 70)
            report_content.append("END OF REPORT | CONFIDENTIAL | DO NOT DISTRIBUTE IF MALICIOUS")
            report_content.append("=" * 70)

            # 4. Write to disk
            try:
                with open(path, "w", encoding="utf-8") as f:
                    f.write("\n".join(report_content))
                self.log_message(f"\n[+] Report successfully saved to:\n    {path}")
            except Exception as e:
                self.log_message(f"\n[!] Error saving report: {str(e)}")

    def process_file(self, file_path):
        self.stack.setCurrentIndex(0)
        if not file_path or not os.path.exists(file_path): return

        # --- CLEAR TERMINAL ON NEW SCAN (YES!) ---
        self.console.clear() 
        self.btn_save_report.setEnabled(False) # Disable save until done

        filename = os.path.basename(file_path)
        self.current_file_name = filename # Store for report naming
        self.current_scan_time = datetime.now()
        
        self.log_message(f"[>] Processing: {filename}")
        self.drop_zone.setText(f"ANALYZING:\n{filename}\n\n[ Please Wait... ]")
        self.drop_zone.setStyleSheet("color: #00FF00; border-color: #00FF00;") 
        self.progress_bar.setVisible(True); self.progress_bar.setValue(0)
        
        found_qrs = self.scanner.extract_qr(file_path, self.update_progress)
        self.progress_bar.setVisible(False)
        self.drop_zone.setText(f"ANALYSIS COMPLETE:\n{filename}\n\n[ Drop or Click or Paste to Scan Another ]")

        if not found_qrs:
            self.log_message("[-] No QR Code found.")
            self.drop_zone.setStyleSheet(""); self.drop_zone.setText("NO QR FOUND\n\n[ Drop or Click or Paste to Scan Another ]")
            self.btn_save_report.setEnabled(True) # Enable save even if empty (to log that it was clean)
            return
        
        self.log_message(f"[*] Found {len(found_qrs)} QR Code(s). Analyzing...")
        
        for i, raw_data in enumerate(found_qrs):
            if raw_data.startswith("[!]"):
                self.log_message(raw_data); continue

            self.log_message(f"\n--- RESULT #{i+1} ---")
            analysis = self.analyzer.analyze(raw_data)
            
            content_preview = analysis.get('final', analysis.get('original', 'N/A'))
            self.history_manager.add_entry(filename, analysis['type'], content_preview)

            if analysis["status"] == "error":
                self.log_message(f"[!] Analysis Failed: {analysis['message']}")
            elif analysis["type"] == "Text":
                self.log_message(f"[i] Type: Plain Text"); self.log_message(f"[>] Content: {analysis['original']}")
            else:
                self.log_message(f"[i] Type: URL"); self.log_message(f"[>] Destination: {analysis['final']}")
                if len(analysis["chain"]) > 1:
                    self.log_message("[~] Redirection Chain:")
                    for j, hop in enumerate(analysis["chain"]):
                        self.log_message(f"    {j+1}. {defang(hop)}")

        self.log_message("\n[*] Batch Analysis Complete.")
        self.btn_save_report.setEnabled(True) # Enable save button

    # --- INPUTS & ANIMATIONS ---
    def open_file_dialog(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Select Image", "", "Files (*.png *.jpg *.jpeg *.pdf)")
        if file_path: self.process_file(file_path)
    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls(): event.accept()
        else: event.ignore()
    def dropEvent(self, event):
        for url in event.mimeData().urls():
            path = url.toLocalFile()
            if path and os.path.exists(path): self.process_file(path)
    def keyPressEvent(self, event):
        if event.modifiers() == Qt.KeyboardModifier.ControlModifier and event.key() == Qt.Key.Key_V:
            cb = QApplication.clipboard(); md = cb.mimeData()
            if md.hasImage():
                img = cb.image(); path = os.path.abspath("temp_clipboard_scan.png"); img.save(path); self.process_file(path)
            elif md.hasUrls(): self.process_file(md.urls()[0].toLocalFile())

    def toggle_sidebar(self):
        width = self.sidebar.width(); target = 60 if width == 150 else 150 
        self.anim = QPropertyAnimation(self.sidebar, b"minimumWidth"); self.anim.setDuration(300); self.anim.setStartValue(width); self.anim.setEndValue(target); self.anim.setEasingCurve(QEasingCurve.Type.InOutQuart); self.anim.start()
        if target == 60:
            self.btn_menu.setStyleSheet("text-align: center; padding-left: 0;"); self.btn_scan.setStyleSheet("text-align: center; padding-left: 0;"); self.btn_hist.setStyleSheet("text-align: center; padding-left: 0;"); self.btn_about.setStyleSheet("text-align: center; padding-left: 0;"); self.btn_theme.setStyleSheet("text-align: center; padding-left: 0;")
            self.btn_scan.setText(""); self.btn_hist.setText(""); self.btn_about.setText(""); self.btn_theme.setText(""); self.is_sidebar_expanded = False
        else:
            self.btn_menu.setStyleSheet(""); self.btn_scan.setStyleSheet(""); self.btn_hist.setStyleSheet(""); self.btn_about.setStyleSheet(""); self.btn_theme.setStyleSheet("")
            self.btn_scan.setText("  SCANNER"); self.btn_hist.setText("  HISTORY"); self.btn_about.setText("  ABOUT"); self.btn_theme.setText("  DARK MODE" if self.is_dark_mode else "  LIGHT MODE"); self.is_sidebar_expanded = True

    def toggle_theme(self):
        if self.is_dark_mode:
            self.setStyleSheet(Theme.LIGHT_STYLES); self.is_dark_mode = False
            self.btn_theme.setText("" if not self.is_sidebar_expanded else "  LIGHT MODE"); self.btn_theme.setIcon(self.icon_sun)
            self.btn_scan.setIcon(qta.icon('fa5s.qrcode', color='#555')); self.btn_hist.setIcon(qta.icon('fa5s.history', color='#555')); self.btn_about.setIcon(qta.icon('fa5s.info-circle', color='#555')); self.btn_save_report.setIcon(qta.icon('fa5s.file-export', color='#555'))
        else:
            self.setStyleSheet(Theme.DARK_STYLES); self.is_dark_mode = True
            self.btn_theme.setText("" if not self.is_sidebar_expanded else "  DARK MODE"); self.btn_theme.setIcon(self.icon_moon)
            self.btn_scan.setIcon(qta.icon('fa5s.qrcode', color='#888')); self.btn_hist.setIcon(qta.icon('fa5s.history', color='#888')); self.btn_about.setIcon(qta.icon('fa5s.info-circle', color='#888')); self.btn_save_report.setIcon(qta.icon('fa5s.file-export', color='#888'))