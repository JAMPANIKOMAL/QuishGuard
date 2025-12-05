import os
import sys
from datetime import datetime
from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QPushButton, QLabel, QFrame, QTextEdit, QFileDialog, 
                             QApplication, QSplitter, QProgressBar, QStackedWidget,
                             QTableWidget, QTableWidgetItem, QHeaderView, QMessageBox)
from PyQt6.QtCore import Qt, QPropertyAnimation, QEasingCurve, pyqtSignal, QSize, QThread, pyqtSlot
from PyQt6.QtGui import QDragEnterEvent, QDropEvent

import qtawesome as qta 
from src.ui.styles import Theme
from src.core.scanner import ScannerEngine
from src.core.analyzer import URLAnalyzer
from src.utils.history import HistoryManager 

class AnalysisWorker(QThread):
    """
    Background thread to handle file scanning and URL analysis.
    Prevents the Main UI thread from freezing during network requests.
    """
    log_signal = pyqtSignal(str)
    progress_signal = pyqtSignal(int)
    result_signal = pyqtSignal(object)
    finished_signal = pyqtSignal()

    def __init__(self, file_path):
        super().__init__()
        self.file_path = file_path
        self.scanner = ScannerEngine()
        self.analyzer = URLAnalyzer()

    def run(self):
        self.log_signal.emit(f"[INFO] Initializing Engine...")
        self.progress_signal.emit(10)
        
        found_qrs = self.scanner.extract_qr(self.file_path, self._forward_progress)
        
        if not found_qrs:
            self.log_signal.emit("[INFO] No QR Code found in file.")
            self.finished_signal.emit()
            return

        self.log_signal.emit(f"[INFO] Found {len(found_qrs)} QR Code(s). Starting deep analysis...")
        self.progress_signal.emit(50)

        for i, raw_data in enumerate(found_qrs):
            if raw_data.startswith("[ERROR]"):
                self.log_signal.emit(raw_data)
                continue

            self.log_signal.emit(f"\n--- OBJECT {i+1} ---")
            analysis_result = self.analyzer.analyze(raw_data)
            self.result_signal.emit(analysis_result)
            
        self.progress_signal.emit(100)
        self.finished_signal.emit()

    def _forward_progress(self, val):
        # Scale scanner progress to fit within the first half of the progress bar
        scaled = 10 + int(val * 0.4)
        self.progress_signal.emit(scaled)

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

class OverlayConsole(QTextEdit):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("console")
        self.setReadOnly(True)
        self.btn_save = QPushButton("Save Report", self)
        self.btn_save.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_save.setVisible(False) 
        self.btn_save.setStyleSheet("""
            QPushButton { background-color: #222; color: #AAA; border: 1px solid #444; border-radius: 4px; padding: 4px 12px; font-size: 11px; font-weight: bold; }
            QPushButton:hover { background-color: #333; color: #FFF; border-color: #00FF00; }
        """)
        
    def resizeEvent(self, event):
        super().resizeEvent(event)
        padding = 20
        btn_w = self.btn_save.sizeHint().width() + 10
        btn_h = self.btn_save.sizeHint().height()
        self.btn_save.move(
            self.viewport().width() - btn_w - padding,
            self.viewport().height() - btn_h - 10
        )

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.history_manager = HistoryManager()
        self.worker = None 
        
        self.setWindowTitle("QuishGuard | Forensic Phishing Detector")
        self.resize(1100, 750)
        self.setAcceptDrops(True) 
        
        self.is_dark_mode = True
        self.is_sidebar_expanded = True 
        
        self._load_icons()

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QHBoxLayout(self.central_widget)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)
        
        self.init_sidebar()
        self.stack = QStackedWidget()
        
        self.page_scanner = QWidget(); self.init_scanner_ui(); self.stack.addWidget(self.page_scanner)
        self.page_history = QWidget(); self.init_history_ui(); self.stack.addWidget(self.page_history)
        self.page_about = QWidget(); self.init_about_ui(); self.stack.addWidget(self.page_about)
        
        self.main_layout.addWidget(self.sidebar)
        self.main_layout.addWidget(self.stack)
        
        self.setStyleSheet(Theme.DARK_STYLES)
        self.log_message("[INFO] System Ready. Waiting for input.")

    def _load_icons(self):
        self.icon_menu = qta.icon('fa5s.bars', color='white')
        self.icon_scan = qta.icon('fa5s.qrcode', color='#888')
        self.icon_hist = qta.icon('fa5s.history', color='#888')
        self.icon_info = qta.icon('fa5s.info-circle', color='#888') 
        self.icon_save = qta.icon('fa5s.file-download', color='#888') 
        self.icon_moon = qta.icon('fa5s.moon', color='#888')
        self.icon_sun  = qta.icon('fa5s.sun', color='#555')

    def init_sidebar(self):
        self.sidebar = QFrame()
        self.sidebar.setObjectName("sidebar")
        self.sidebar.setFixedWidth(150) 
        l = QVBoxLayout(self.sidebar); l.setContentsMargins(0, 10, 0, 20); l.setSpacing(5)
        
        self.btn_menu = QPushButton(); self.btn_menu.setIcon(self.icon_menu); self.btn_menu.clicked.connect(self.toggle_sidebar)
        self.btn_scan = QPushButton("  SCANNER"); self.btn_scan.setIcon(self.icon_scan); self.btn_scan.clicked.connect(lambda: self.switch_page(0))
        self.btn_hist = QPushButton("  HISTORY"); self.btn_hist.setIcon(self.icon_hist); self.btn_hist.clicked.connect(lambda: self.switch_page(1))
        self.btn_about = QPushButton("  ABOUT"); self.btn_about.setIcon(self.icon_info); self.btn_about.clicked.connect(lambda: self.switch_page(2))
        self.btn_theme = QPushButton("  DARK MODE"); self.btn_theme.setIcon(self.icon_moon); self.btn_theme.clicked.connect(self.toggle_theme)
        
        l.addWidget(self.btn_menu); l.addSpacing(20)
        l.addWidget(self.btn_scan); l.addWidget(self.btn_hist); l.addWidget(self.btn_about)
        l.addStretch(); l.addWidget(self.btn_theme)

    def init_scanner_ui(self):
        l = QVBoxLayout(self.page_scanner); l.setContentsMargins(20, 20, 20, 20)
        splitter = QSplitter(Qt.Orientation.Vertical); splitter.setHandleWidth(2)
        
        self.drop_zone = ClickableDropZone("CLICK TO UPLOAD\n\nOR DRAG FILE HERE")
        self.drop_zone.clicked.connect(self.open_file_dialog)
        splitter.addWidget(self.drop_zone)
        
        console_cont = QWidget(); cl = QVBoxLayout(console_cont); cl.setContentsMargins(0, 0, 0, 0)
        self.progress_bar = QProgressBar(); self.progress_bar.setFixedHeight(4); self.progress_bar.setTextVisible(False); self.progress_bar.setVisible(False)
        self.progress_bar.setStyleSheet("QProgressBar { border: none; background: #222; } QProgressBar::chunk { background: #00FF00; }")
        
        self.console = OverlayConsole()
        self.console.btn_save.clicked.connect(self.save_report); self.console.btn_save.setIcon(self.icon_save)
        
        cl.addWidget(self.progress_bar); cl.addWidget(self.console)
        splitter.addWidget(console_cont); splitter.setSizes([400, 300])
        l.addWidget(splitter)

    def init_history_ui(self):
        l = QVBoxLayout(self.page_history); l.setContentsMargins(20, 20, 20, 20)
        l.addWidget(QLabel("SCAN HISTORY", styleSheet="font-size: 24px; font-weight: bold; color: #888;"))
        self.table = QTableWidget(); self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["Time", "File", "Verdict", "Content"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.setStyleSheet("background-color: #1E1E1E; color: #CCC; border: 1px solid #333; gridline-color: #333;")
        self.table.verticalHeader().setVisible(False)
        l.addWidget(self.table)
        btn = QPushButton("Refresh Log"); btn.setFixedSize(120, 30); btn.clicked.connect(self.load_history_data)
        l.addWidget(btn, alignment=Qt.AlignmentFlag.AlignRight)

    def init_about_ui(self):
        l = QVBoxLayout(self.page_about); l.setAlignment(Qt.AlignmentFlag.AlignCenter)
        l.addWidget(QLabel("QuishGuard", styleSheet="font-size: 40px; font-weight: bold; color: #FFF;", alignment=Qt.AlignmentFlag.AlignCenter))
        l.addWidget(QLabel("Advanced QR Phishing Detection System\nVersion 1.0.0\nDeveloped by Jampani Komal", styleSheet="font-size: 16px; color: #888;", alignment=Qt.AlignmentFlag.AlignCenter))

    def process_file(self, file_path):
        self.stack.setCurrentIndex(0)
        if not file_path or not os.path.exists(file_path): return

        self.console.clear()
        self.console.btn_save.setVisible(False)
        self.current_file_name = os.path.basename(file_path)
        
        self.drop_zone.setText(f"ANALYZING:\n{self.current_file_name}\n\n[ Please Wait ]")
        self.drop_zone.setStyleSheet("color: #00FF00; border-color: #00FF00;")
        self.progress_bar.setVisible(True); self.progress_bar.setValue(0)

        self.worker = AnalysisWorker(file_path)
        self.worker.log_signal.connect(self.log_message)
        self.worker.progress_signal.connect(self.update_progress)
        self.worker.result_signal.connect(self.handle_analysis_result)
        self.worker.finished_signal.connect(self.on_scan_finished)
        self.worker.start()

    @pyqtSlot(str)
    def log_message(self, message):
        self.console.append(message)
        sb = self.console.verticalScrollBar(); sb.setValue(sb.maximum())

    @pyqtSlot(int)
    def update_progress(self, value):
        self.progress_bar.setValue(value)

    @pyqtSlot(object)
    def handle_analysis_result(self, analysis):
        verdict = analysis.get("verdict", "UNKNOWN")
        color = "#00FF00" 
        if verdict == "HIGH RISK": color = "#FF0000"
        elif verdict == "SUSPICIOUS": color = "#FFFF00"
        
        self.console.append(f"<span style='color:{color}; font-weight:bold'>[{verdict}] Score: {analysis.get('score', 0)}</span>")
        
        if "flags" in analysis and analysis["flags"]:
            for flag in analysis["flags"]:
                self.console.append(f"<span style='color:#AAA'>    [x] FLAG: {flag}</span>")

        if analysis["type"] == "URL":
            self.console.append(f"<span style='color:#FFF'>[>] Destination: {analysis['final']}</span>")
            if len(analysis["chain"]) > 1:
                self.console.append("<span style='color:#888'>[>] Redirection Chain:</span>")
                for j, hop in enumerate(analysis["chain"]):
                    self.console.append(f"<span style='color:#888'>    {j+1}. {hop}</span>")
        else:
             self.console.append(f"[>] Content: {analysis['original']}")
        
        content_preview = analysis.get('final', analysis.get('original', 'N/A'))
        self.history_manager.add_entry(self.current_file_name, verdict, content_preview)

    @pyqtSlot()
    def on_scan_finished(self):
        self.drop_zone.setStyleSheet("")
        self.drop_zone.setText("SCAN COMPLETE\n\n[ Drop File to Scan Another ]")
        self.progress_bar.setVisible(False)
        self.console.btn_save.setVisible(True)

    def switch_page(self, index):
        self.stack.setCurrentIndex(index)
        if index == 1: self.load_history_data()

    def load_history_data(self):
        data = self.history_manager.load_history()
        self.table.setRowCount(len(data))
        for row, entry in enumerate(data):
            self.table.setItem(row, 0, QTableWidgetItem(entry.get("timestamp", "")))
            self.table.setItem(row, 1, QTableWidgetItem(entry.get("file", "")))
            verdict = entry.get("type", "")
            item = QTableWidgetItem(verdict)
            if "HIGH RISK" in verdict: item.setForeground(Qt.GlobalColor.red)
            elif "SAFE" in verdict: item.setForeground(Qt.GlobalColor.green)
            self.table.setItem(row, 2, item)
            self.table.setItem(row, 3, QTableWidgetItem(entry.get("content", "")))

    def save_report(self):
        if not hasattr(self, 'current_file_name'): return
        timestamp_str = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        default_name = f"QuishGuard_Report_{timestamp_str}.txt"
        path, _ = QFileDialog.getSaveFileName(self, "Save Forensic Report", default_name, "Text Files (*.txt)")
        if path:
            try:
                with open(path, "w", encoding="utf-8") as f:
                    f.write(f"QUISHGUARD FORENSIC REPORT\nDate: {datetime.now()}\nFile: {self.current_file_name}\n\n")
                    f.write(self.console.toPlainText())
                self.log_message(f"\n[INFO] Report saved.")
            except Exception as e:
                self.log_message(f"\n[ERROR] Error saving: {e}")

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
    def toggle_sidebar(self):
        width = self.sidebar.width(); target = 60 if width == 150 else 150 
        self.anim = QPropertyAnimation(self.sidebar, b"minimumWidth"); self.anim.setDuration(300); self.anim.setStartValue(width); self.anim.setEndValue(target); self.anim.setEasingCurve(QEasingCurve.Type.InOutQuart); self.anim.start()
        if target == 60:
            for btn in [self.btn_menu, self.btn_scan, self.btn_hist, self.btn_about, self.btn_theme]: btn.setStyleSheet("text-align: center; padding-left: 0;")
            self.btn_scan.setText(""); self.btn_hist.setText(""); self.btn_about.setText(""); self.btn_theme.setText(""); self.is_sidebar_expanded = False
        else:
            for btn in [self.btn_menu, self.btn_scan, self.btn_hist, self.btn_about, self.btn_theme]: btn.setStyleSheet("")
            self.btn_scan.setText("  SCANNER"); self.btn_hist.setText("  HISTORY"); self.btn_about.setText("  ABOUT"); self.btn_theme.setText("  DARK MODE" if self.is_dark_mode else "  LIGHT MODE"); self.is_sidebar_expanded = True
    def toggle_theme(self):
        if self.is_dark_mode:
            self.setStyleSheet(Theme.LIGHT_STYLES); self.is_dark_mode = False
            self.btn_theme.setText("" if not self.is_sidebar_expanded else "  LIGHT MODE"); self.btn_theme.setIcon(self.icon_sun)
        else:
            self.setStyleSheet(Theme.DARK_STYLES); self.is_dark_mode = True
            self.btn_theme.setText("" if not self.is_sidebar_expanded else "  DARK MODE"); self.btn_theme.setIcon(self.icon_moon)