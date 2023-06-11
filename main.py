import sys
from PyQt6.QtWidgets import QApplication

from MainWindow.mainWindow import MapApp

# Точка входа в приложение ( Запуск MainWindow )
if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MapApp()
    window.show()
    sys.exit(app.exec())