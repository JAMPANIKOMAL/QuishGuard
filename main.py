import sys
from PyQt6.QtWidgets import QApplication
from src.ui.main_window import MainWindow

def main():
    # Create the Application
    app = QApplication(sys.argv)
    
    # Initialize the Main Window
    window = MainWindow()
    window.show()
    
    # Start the Event Loop
    sys.exit(app.exec())

if __name__ == "__main__":
    main()