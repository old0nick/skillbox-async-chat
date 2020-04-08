"""
Пример программы для работы с интерфейсами Qt
"""
from PySide2.QtWidgets import QMainWindow, QApplication

from app.interface import Ui_MainWindow

class MainWindow(QMainWindow, Ui_MainWindow)
    def __init__(self):
        super().__init__()
        self.setupUi(self)

app = QApplication()
window = MainWindow()

window.show()
app.exec_()