import sys
import os
import shutil
import winshell
from PyQt6.QtWidgets import QApplication, QMessageBox

APP_NAME = "QuishGuard"

def uninstall():
    app = QApplication(sys.argv)
    
    # 1. Confirm
    reply = QMessageBox.question(None, f"Uninstall {APP_NAME}", 
                               f"Are you sure you want to completely remove {APP_NAME}?",
                               QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
    
    if reply == QMessageBox.StandardButton.Yes:
        try:
            # 2. Define Paths
            install_dir = os.path.dirname(os.path.abspath(sys.argv[0]))
            desktop = winshell.desktop()
            shortcut_path = os.path.join(desktop, f"{APP_NAME}.lnk")
            
            # 3. Remove Shortcut
            if os.path.exists(shortcut_path):
                os.remove(shortcut_path)
            
            # 4. Schedule Folder Deletion
            # We cannot delete the folder we are currently running inside.
            # Professional Trick: Create a temporary batch file to delete us after we close.
            batch_file = os.path.join(os.environ["TEMP"], "cleanup_quishguard.bat")
            with open(batch_file, "w") as f:
                f.write("@echo off\n")
                f.write("timeout /t 2 /nobreak > NUL\n") # Wait for us to close
                f.write(f'rmdir /s /q "{install_dir}"\n') # Nuke the folder
                f.write('(goto) 2>nul & del "%~f0"\n')   # Delete this script
            
            # 5. Launch the cleaner and exit
            os.startfile(batch_file)
            QMessageBox.information(None, "Uninstall", f"{APP_NAME} has been removed.")
            sys.exit(0)
            
        except Exception as e:
            QMessageBox.critical(None, "Error", f"Uninstall failed: {str(e)}")
            sys.exit(1)

    sys.exit(0)

if __name__ == "__main__":
    uninstall()