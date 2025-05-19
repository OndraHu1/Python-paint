import sys
from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QGuiApplication
from PyQt6.QtCore import Qt
from paint_app import PaintApp

if __name__ == "__main__":
    # Nastavení režimu vysokého DPI před vytvořením QApplication
    QGuiApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
    )
    
    app = QApplication(sys.argv)
    window = PaintApp()
    window.show()
    sys.exit(app.exec())