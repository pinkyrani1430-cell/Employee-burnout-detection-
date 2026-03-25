import sys
from PySide6.QtWidgets import QApplication
from gui import BurnoutApp

def main():
    """
    Main entry point for the Employee Burnout Detection application.
    """
    # Create the Qt Application
    app = QApplication(sys.argv)
    
    # Create and show the main window
    window = BurnoutApp()
    window.show()
    
    # Run the application loop
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
