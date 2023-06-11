from PyQt6 import uic
from PyQt6.QtWidgets import QMessageBox,  QGraphicsLineItem, QGraphicsEllipseItem, QGraphicsPolygonItem, QGraphicsView
from PyQt6.QtGui import QPen, QBrush, QColor,  QPolygonF, QTransform
from PyQt6.QtCore import Qt, QPointF, QPoint

YELLOW = QColor(255, 255, 0)
RED = QColor(255, 0, 0)


# Класс для работы с картой
class myMap():
    def __init__(self, map_canvas, scene) :
        self.selected_item= None
        self.map_canvas = map_canvas
        self.scene = scene
        self.draggable = False
        self.previous_pos = None
        
    # Функция приближения по колесику мыши к точке где находиться курсор
    def wheelEvent(self, event):
        try:
            scaling_value = 1.1
            numDegrees = -event.angleDelta().y() / 8
            numSteps = numDegrees / 15
            scale = self.map_canvas.transform().m11()

            if numSteps > 0:
                scale *= pow(scaling_value, numSteps)
            elif numSteps < 0:
                scale /= pow(scaling_value, -numSteps)
                
            self.map_canvas.setTransform(QTransform.fromScale(scale, scale))
            cursor_pos = event.position()
            
            scene_pos = self.map_canvas.mapToScene(QPoint(cursor_pos.x(), cursor_pos.y()))
            self.map_canvas.centerOn(scene_pos)
        except Exception as e:
            print("Ошибка выполнения приближения: ", str(e))

    # Функция отвечает за обработку события клика мыши
    def mousePressEvent(self, event):
        try:
            if event.button() == Qt.MouseButton.LeftButton:
                self.draggable = True
                self.previous_pos = event.pos()
        except Exception as e:
            print("Error occurred:", e)

    #  Функция отвечает за обработку события перемещения мыши при зажатой левой кнопке
    def mouseMoveEvent(self, event):
        try:
            if self.draggable and event.buttons() == Qt.MouseButton.LeftButton:
                cursor_pos = event.pos() 
                dx = cursor_pos.x() - self.previous_pos.x()
                dy = cursor_pos.y() - self.previous_pos.y()

                self.map_canvas.horizontalScrollBar().setValue(self.map_canvas.horizontalScrollBar().value() - dx)
                self.map_canvas.verticalScrollBar().setValue(self.map_canvas.verticalScrollBar().value() - dy)

                self.previous_pos = cursor_pos
        except Exception as e:
            print(f"An error occurred in mouseMoveEvent: {e}")

    # Функция вызывается, когда пользователь отпускает кнопку мыши (красим элементы)
    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            pos = event.pos()
            item = self.map_canvas.itemAt(pos)
            if type(item) == None:
                if self.selected_item is not None:
                    self.selected_item.setPen(RED)
                    if isinstance(self.selected_item, QGraphicsPolygonItem):
                        self.selected_item.setBrush(RED)

            if item:
                if self.selected_item:
                    self.selected_item.setPen(RED)
                    if isinstance(self.selected_item, QGraphicsPolygonItem):
                        self.selected_item.setBrush(RED)

                self.selected_item = item
                self.selected_item.setPen(YELLOW)
                if isinstance(self.selected_item, QGraphicsPolygonItem):
                    self.selected_item.setBrush(YELLOW)

            else:
                if self.selected_item:
                    self.selected_item.setPen(YELLOW)
                    if isinstance(self.selected_item, QGraphicsPolygonItem):
                        self.selected_item.setBrush(YELLOW)

            self.draggable = False
            self.previous_pos = None

    # Функция удаления выбранного объекта
    def deleteObject(self):
        if self.selected_item:
            self.scene.removeItem(self.selected_item)
            self.selected_item= None
        else:
            QMessageBox.warning(None, 'Предупреждение', 'Требуется выбрать объект')

    # Функция отрисовки объектов на карте
    def drawDataOnMap(self, data):
        try:
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
        except:
            print("Файл не выбран")

    # Функция получения коорднат с карты для последующей записи в файл
    def getCoordinates(self):
        coordinates = []
        items = self.map_canvas.items()
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