import re
import os
from PyQt6.QtWidgets import  QFileDialog


# Класс для работы с файлами 
class myFileManager():
    def __init__(self, map) :
        self.map_canvas = map

    # Функция сохранения файла
    def saveFile(self, coords):
        file_dialog = QFileDialog()
        file_dialog.setFileMode(QFileDialog.FileMode.Directory)
        file_dialog.setOption(QFileDialog.Option.ShowDirsOnly)
        file_path = file_dialog.getExistingDirectory(self.map_canvas, "Выбрать директорию")

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
                self.map_canvas.statusBar.showMessage("Файл успешно созранен в " + file_path)
            except IOError:
                self.map_canvas.statusBar.showMessage("Ошибка записи в файл")
        else:
            self.map_canvas.statusBar.showMessage("Директория не выбрана")

    # Функция выбора файла в файловом окне
    def browseFile(self):
        file_path, _ = QFileDialog.getOpenFileName(self.map_canvas, "Выберите файл", "", "Файлы формата txt (*.txt)")
        if file_path:
            self.map_canvas.entry_file.setText(file_path)
            data = self.readFile(file_path)
            return data
        else:
            self.map_canvas.statusBar.showMessage("Файл не выбран")

    # Функция чтения файла и обработки ошибок 
    def readFile(self, file_path):
        try:
            data = self.loadFile(file_path)
            return data

        except Exception as e:
            self.map_canvas.statusBar.showMessage("Ошибка чтения файла: " + str(e))

    # Фкнуция для загрузки файла по шорткату 
    def loadEnterShortcut(self):
        file = self.map_canvas.entry_file.text()
        try:
            data = self.loadFile(file)
            return data
        
        except Exception as e:
            self.map_canvas.statusBar.showMessage("Ошибка чтения файла: " + str(e))

    # Функция загрузки файла и считывание координат
    def loadFile(self, file_path):
        if file_path == "" or not os.path.isfile(file_path):
            self.map_canvas.statusBar.showMessage("Не найден файл или директория")
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
                    self.map_canvas.statusBar.showMessage('Обратите внимание на правильность введеных данных, не все объекты удалось загрузить')
                else:
                    self.map_canvas.statusBar.showMessage("Документ прочитан без ошибок")

                return data_dict
            except:
                self.map_canvas.statusBar.showMessage("Не найден файл или директория")
                return {}