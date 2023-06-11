import os
from PyQt6 import uic
from PyQt6.QtWidgets import QMainWindow, QGraphicsScene
from PyQt6.QtGui import QKeySequence, QShortcut
from PyQt6.QtCore import Qt

from Map.Map import myMap
from FileManager.FileManager import myFileManager

# Получение UI из файла 
_DIR_PATH = os.path.dirname(__file__)
FORM_CLASS, _ = uic.loadUiType(os.path.join(_DIR_PATH, 'MainWindow.ui'))


# Класс главной формы
class MapApp(QMainWindow, FORM_CLASS):
    def __init__(self):
        super(MapApp, self).__init__()
        self.setupUi(self)
        self.setWindowTitle("Настольная ГИС")

        # Создание объекта карты
        self.map_canvas = self.graphicsView
        self.scene = QGraphicsScene(self)
        self.map_canvas.setScene(self.scene)
        self.scale_factor = 1.0

        # Экземпляры классов для  работы с картой и файлами
        self.Map = myMap(self.map_canvas, self.scene)
        self.FileManager = myFileManager(self)

        # Кнопка "Обзор"
        self.browse_button.clicked.connect(self.drawObject)

        # Кнопка "Удалить объект"
        self.delete_button.clicked.connect(self.Map.deleteObject)

        # Строка состояния приложения
        self.statusBar.showMessage("Готово")

        # Назначение событий мыши для отслеживания нажатий на канве
        self.map_canvas.setFocusPolicy(Qt.FocusPolicy.ClickFocus)
        self.map_canvas.mousePressEvent = self.Map.mousePressEvent
        self.map_canvas.mouseMoveEvent = self.Map.mouseMoveEvent
        self.map_canvas.mouseReleaseEvent = self.Map.mouseReleaseEvent
        self.map_canvas.setMouseTracking(True)
        self.map_canvas.wheelEvent = self.Map.wheelEvent # enable mouse tracking for wheel events

        # Горячие клавиши для сохранения и загрузки файла
        self.save_shortcut = QShortcut(QKeySequence("Ctrl+S"), self)
        self.save_shortcut.activated.connect(self.saveFile)

        self.load_shortcut = QShortcut(QKeySequence(Qt.Key.Key_Return), self)
        self.load_shortcut.activated.connect(self.loadFileEnterShortcut)

    # Функция отрисовка объектов из файла на карте 
    def drawObject(self):
        data = self.FileManager.browseFile()
        self.Map.drawDataOnMap(data)

    # Функция загруки объектов из файла по шотркату
    def loadFileEnterShortcut(self):
        data = self.FileManager.loadEnterShortcut()
        self.Map.drawDataOnMap(data)

    # Функция сохранения объектов с карты в файл
    def saveFile(self):
        data = self.Map.getCoordinates()
        self.FileManager.saveFile(data)

