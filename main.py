import sys
import re
import os
from PyQt6.QtWidgets import QApplication, QMainWindow, QLabel, QLineEdit, QPushButton, QStatusBar, QFileDialog, \
    QGraphicsScene, QGraphicsView, QMessageBox,  QGraphicsLineItem, QGraphicsEllipseItem, QGraphicsPolygonItem
from PyQt6.QtGui import QPen, QBrush, QColor,  QKeySequence, QShortcut, QPolygonF
from PyQt6.QtCore import Qt, QPointF


YELLOW = QColor(255, 255, 0)
RED = QColor(255, 0, 0)

class MapApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Настольная ГИС")

        # Надпись для адреса файла
        self.label_file = QLabel(self)
        self.label_file.setText("Адрес файла:")
        self.label_file.move(10, 10)

        # Поле для ввода адреса файла
        self.entry_file = QLineEdit(self)
        self.entry_file.move(100, 10)
        self.entry_file.resize(350, 30)
        self.entry_file.setPlaceholderText("Введите путь до файла")

        # Кнопка "Обзор"
        self.browse_button = QPushButton(self)
        self.browse_button.setText("Обзор")
        self.browse_button.move(470, 10)
        self.browse_button.clicked.connect(self.browseFile)

        # Кнопка "Удалить объект"
        self.delete_button = QPushButton(self)
        self.delete_button.setText("Удалить объект")
        self.delete_button.move(650, 10)
        self.delete_button.resize(150, 30)
        self.delete_button.clicked.connect(self.deleteObject)

        # Отображениу карты
        self.map_canvas = QGraphicsView(self)
        self.map_canvas.move(10, 40)
        self.map_canvas.resize(820, 820)
        self.scene = QGraphicsScene(self)
        self.map_canvas.setScene(self.scene)

        # Строка состояния приложения
        self.status_bar = QStatusBar(self)
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Готово")

        # Флаг для перетаскивания объекта на карте
        self.draggable = False
        self.previous_pos = None

        # Назначение событий мыши для отслеживания нажатий на канве
        self.map_canvas.setFocusPolicy(Qt.FocusPolicy.ClickFocus)
        self.map_canvas.mousePressEvent = self.mousePressEvent
        self.map_canvas.mouseMoveEvent = self.mouseMoveEvent
        self.map_canvas.mouseReleaseEvent = self.mouseReleaseEvent
        self.map_canvas.setMouseTracking(True) # enable mouse tracking for wheel events

        # Выбранный объект
        self.selected_item = None

        # Горячие клавиши для сохранения и загрузки файла
        self.save_shortcut = QShortcut(QKeySequence("Ctrl+S"), self)
        self.save_shortcut.activated.connect(self.saveFile)

        self.load_shortcut = QShortcut(QKeySequence(Qt.Key.Key_Return), self)
        self.load_shortcut.activated.connect(self.loadEnterShortcut)

    # Функция сохранения координат в файл 
    def saveFile(self):
        coords = self.getCcoordinates()
        file_dialog = QFileDialog()
        file_dialog.setFileMode(QFileDialog.FileMode.Directory)
        file_dialog.setOption(QFileDialog.Option.ShowDirsOnly)
        file_path = file_dialog.getExistingDirectory(self, "Выбрать директорию")

        if file_path:
            file_path += "/coordinates.txt"

            try:
                with open(file_path, "w") as f:
                    for obj in coords:
                        exit_str = ""
                        if type(obj) == list:
                            for item in obj:
                                if type(item) == tuple:
                                    exit_str += f"{int(item[0])} {int(item[1])} "
                                else:
                                    exit_str = exit_str + str(int(item)) + " "
                            f.write(str(exit_str) + "\n")
                        else:
                            f.write(str(obj) + "\n")
            except IOError:
                self.status_bar.showMessage("Ошибка записи в файл")
        else:
            self.status_bar.showMessage("Директория не выбрана")


    # Функция получения координат с карты
    def getCcoordinates(self):
        coordinates = []
        items = self.scene.items()
        for item in items:
            if isinstance(item, QGraphicsLineItem):
                x1 = item.line().x1()
                y1 = item.line().y1()
                x2 = item.line().x2()
                y2 = item.line().y2()
                coordinates.append([x1, y1, x2, y2])
            elif isinstance(item, QGraphicsEllipseItem):
                x = item.rect().x()
                y = item.rect().y()
                coordinates.append([x, y])
            elif isinstance(item, QGraphicsPolygonItem):
                polygon = item.polygon()
                points = [(int(point.x()), int(point.y())) for point in polygon]
                coordinates.append(points)
        return coordinates
            

    # Функция приближения/отдаление от карты по полесику мыши
    def wheelEvent(self, event):
        if event.angleDelta().y() > 0:
            # Zoom in
            self.map_canvas.scale(1.1, 1.1)
        elif event.angleDelta().y() < 0:
            # Zoom out
            self.map_canvas.scale(1 / 1.1, 1 / 1.1)


    # Функция отвечает за обработку события клика мыши
    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.draggable = True
            self.previous_pos = event.pos() 

    #  Функция отвечает за обработку события перемещения мыши при зажатой левой кнопке
    def mouseMoveEvent(self, event):
        if self.draggable and event.buttons() == Qt.MouseButton.LeftButton:
            cursor_pos = event.pos() 
            dx = cursor_pos.x() - self.previous_pos.x()
            dy = cursor_pos.y() - self.previous_pos.y()

            self.map_canvas.horizontalScrollBar().setValue(self.map_canvas.horizontalScrollBar().value() - dx)
            self.map_canvas.verticalScrollBar().setValue(self.map_canvas.verticalScrollBar().value() - dy)

            self.previous_pos = cursor_pos

    # Функция вызывается, когда пользователь отпускает кнопку мыши (красим элементы)
    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            pos = event.pos()
            item = self.map_canvas.itemAt(pos)
            if item:
                if self.selected_item:
                    if type(self.selected_item) == QGraphicsPolygonItem:
                        self.selected_item.setPen(RED)
                        self.selected_item.setBrush(RED)
                    else:
                        self.selected_item.setPen(RED)

                self.selected_item = item
                if type(self.selected_item) == QGraphicsPolygonItem:
                    self.selected_item.setPen(YELLOW)
                    self.selected_item.setBrush(YELLOW)
                else:
                    self.selected_item.setPen(YELLOW)

            else:
                if self.selected_item:
                    if type(self.selected_item) == QGraphicsPolygonItem:
                        if self.selected_item:
                            self.selected_item.setPen(YELLOW)
                            self.selected_item.setBrush(YELLOW)
                    else:
                        if self.selected_item:
                            self.selected_item.setPen(YELLOW)
                    self.selected_item = None
                else:
                    if self.selected_item:
                        self.selected_item.setPen(YELLOW)
                    self.selected_item = None

        self.draggable = False
        self.previous_pos = None


    # Функция удаления выбранного объекта
    def deleteObject(self):
        if self.selected_item:
            self.scene.removeItem(self.selected_item)
            self.selected_item = None
        else:
            QMessageBox.warning(self, 'Предупреждение', 'Требуется выбрать объект')

    # Функция вызывает окно выбора файла
    def browseFile(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Выберите файл", "", "Файлы формата txt (*.txt)")
        if file_path:
            self.entry_file.setText(file_path)
            self.readFile(file_path)
        else:
            self.status_bar.showMessage("Файл не выбран")

    # Функция чтения файла и обработки ошибок 
    def readFile(self, file_path):
        try:
            data = self.loadFile(file_path)
            self.drawDataOnMap(data)

        except Exception as e:
            self.status_bar.showMessage("Ошибка чтения файла: " + str(e))

    # Фкнуция для загрузки файла по шорткату 
    def loadEnterShortcut(self):
        file = self.entry_file.text()
        try:
            data = self.loadFile(file)
            self.drawDataOnMap(data)
        except Exception as e:
            self.status_bar.showMessage("Ошибка чтения файла: " + str(e))

    # Функция загрузки файла и считывание координат
    def loadFile(self, file_path):
        if file_path == "" or not os.path.isfile(file_path):
            self.status_bar.showMessage("Не найден файл или директория")
            return {}
        
        else:
            data_dict = {}
            try:
                with open(file_path, "r") as file:
                    lines = file.readlines()
                    for i in range(len(lines)):
                        if any(c.isalpha() for c in lines[i]): # проверяем, содержит ли строка буквы
                            continue
                        data_dict[i+1] = [int(x) for x in re.findall(r'\d+', lines[i])]

                if len(lines) > len(data_dict):
                    self.status_bar.showMessage('Обратите внимание на правильность введеных данных, не все объекты удалось загрузить')
                else:
                    self.status_bar.showMessage("Документ прочитан без ошибок")

                return data_dict
            except:
                self.status_bar.showMessage("Не найден файл или директория")
                return {}

    # Функция добавления объектов на карту
    def drawDataOnMap(self, data):
        for value in data.values():
            
            if len(value) == 2:
                pen = QPen(RED)
                self.scene.addEllipse(value[0], value[1], 1, 1, pen)
            if len(value) == 4:
                pen = QPen(RED)
                self.scene.addLine(value[0], value[1], value[2], value[3], pen)
            if len(value) >= 6:
                pen = QPen(RED)
                brush = QBrush(RED)
                points = []

                for i in range(len(value)):
                    if i % 2 == 0:
                        if i+1 <= len(value):
                            points.append(QPointF(value[i], value[i+1]))

                polygon = QPolygonF(points)
                self.scene.addPolygon(polygon, pen, brush)

           
# Точка входа 
if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MapApp()
    window.resize(840, 840)
    window.show()
    sys.exit(QApplication.exec()) 
