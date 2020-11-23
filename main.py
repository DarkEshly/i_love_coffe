import sqlite3
import sys
from PyQt5 import uic
from PyQt5.QtWidgets import QApplication
from PyQt5.QtWidgets import QMainWindow, QTableWidgetItem


class CoffeeWidget(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi('main.ui', self)
        self.connection = sqlite3.connect("coffee.db")
        self.button.clicked.connect(self.load_table)
        self.request_field.setPlainText("SELECT * FROM coffee")
        self.load_table()

    def load_table(self):
        request = self.request_field.toPlainText()
        try:
            res = self.connection.cursor().execute(request).fetchall()
            self.tableWidget.setColumnCount(len(res[0]))
            self.tableWidget.setRowCount(0)
            for i, row in enumerate(res):
                self.tableWidget.setRowCount(self.tableWidget.rowCount() + 1)
                for j, elem in enumerate(row):
                    self.tableWidget.setItem(i, j, QTableWidgetItem(str(elem)))
        except Exception:
            self.error_label.setText("Извините, но ваш запрос неверный")

    def closeEvent(self, event):
        self.connection.close()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = CoffeeWidget()
    ex.show()
    sys.exit(app.exec())
