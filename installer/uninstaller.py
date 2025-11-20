import sys
import os
import shutil
import winshell
import winreg # <--- NEW
from PyQt6.QtWidgets import QApplication, QMessageBox

APP_NAME = "QuishGuard"

def uninstall():
    app = QApplication(sys.argv)
    
    reply = QMessageBox.question(None, f"Uninstall {APP_NAME}", 
                               f"Are you sure you want to completely remove {APP_NAME}?",
                               QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
    
    if reply == QMessageBox.StandardButton.Yes:
        try:
            # 1. Remove Registry Entry (So it vanishes from Settings)
            try:
                key_path = f"Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\{APP_NAME}"
                winreg.DeleteKey(winreg.HKEY_CURRENT_USER, key_path)
            except Exception:
                pass # Key might not exist, ignore

            # 2. Remove Files
            install_dir = os.path.dirname(os.path.abspath(sys.argv[0]))
            desktop = winshell.desktop()
            shortcut_path = os.path.join(desktop, f"{APP_NAME}.lnk")
            
            if os.path.exists(shortcut_path):
                os.remove(shortcut_path)
            
            # 3. Self-Destruct Batch Script
            batch_file = os.path.join(os.environ["TEMP"], "cleanup_quishguard.bat")
            with open(batch_file, "w") as f:
                f.write("@echo off\n")
                f.write("timeout /t 2 /nobreak > NUL\n") 
                f.write(f'rmdir /s /q "{install_dir}"\n') 
                f.write('(goto) 2>nul & del "%~f0"\n')
            
            os.startfile(batch_file)
            QMessageBox.information(None, "Uninstall", f"{APP_NAME} has been removed.")
            sys.exit(0)
            
        except Exception as e:
            QMessageBox.critical(None, "Error", f"Uninstall failed: {str(e)}")
            sys.exit(1)

    sys.exit(0)

if __name__ == "__main__":
    uninstall()