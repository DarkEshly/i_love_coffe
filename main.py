import sqlite3
from PyQt5 import uic
from PyQt5.QtWidgets import QApplication
from PyQt5.QtWidgets import QMainWindow, QTableWidgetItem
import os
import sys

default_way = '\\'.join(str(os.path.abspath(__file__)).split('\\')[:-1]) + '\\'
sys.path.append(default_way + 'UI')
from addEditCoffeeForm import CoffeeMakeWindow
from main2 import Ui_MainWindow


def except_hook(cls, exception, traceback):
    sys.__excepthook__(cls, exception, traceback)


class MakeCoffeeWidget(QMainWindow, CoffeeMakeWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.con = sqlite3.connect("data/coffee.db")
        self.setVisible(False)
        self.finish_button.clicked.connect(self.apply_result)

    def apply_result(self):
        self.error_label.setText('')
        if self.name_field.text() != '' and self.taste_field.text() != '':
            cur = self.con.cursor()
            self.setVisible(False)
            name = self.name_field.text()
            roasting = self.roasting_field.currentText()
            kind = self.kind_field.currentText()
            taste = self.taste_field.text()
            cost = self.cost_field.value()
            v = self.v_field.value()
            if self.type_of_change == 'Add':
                roasting_id = cur.execute("""SELECT g.id FROM roasting AS g 
                WHERE g.name = ?""", (roasting,)).fetchone()[0]
                kind_id = cur.execute("""SELECT g.id FROM kind AS g 
                WHERE g.name = ?""", (kind,)).fetchone()[0]
                cur.execute("""INSERT INTO 
                                 coffee(name, roasting_id, kind_id, taste, cost, size) 
                                 VALUES(?, ?, ?, ?, ?, ?)""", (name, roasting_id, kind_id, taste, cost, v))
            elif self.type_of_change == 'Change':
                roasting_id = cur.execute("""SELECT g.id FROM roasting AS g 
                               WHERE g.name = ?""", (roasting,)).fetchone()[0]
                kind_id = cur.execute("""SELECT g.id FROM kind AS g 
                               WHERE g.name = ?""", (kind,)).fetchone()[0]
                cur.execute("""UPDATE coffee SET name = ? WHERE id = ?""", (name, self.change_id,))
                cur.execute("""UPDATE coffee SET roasting_id = ? WHERE id = ?""", (roasting_id, self.change_id,))
                cur.execute("""UPDATE coffee SET kind_id = ? WHERE id = ?""", (kind_id, self.change_id,))
                cur.execute("""UPDATE coffee SET taste = ? WHERE id = ?""", (taste, self.change_id,))
                cur.execute("""UPDATE coffee SET cost = ? WHERE id = ?""", (cost, self.change_id,))
                cur.execute("""UPDATE coffee SET size = ? WHERE id = ?""", (v, self.change_id,))
            self.con.commit()
            self.parent_form.request_field.setPlainText("SELECT * FROM coffee")
            self.parent_form.load_table()
        else:
            self.error_label.setText('Неверный формат')

    def show_form(self, type_of_change, parent_form, change_id=None):
        self.error_label.setText('')
        self.type_of_change = type_of_change
        if type_of_change == 'Add':
            self.finish_button.setText('Добавить')
        elif type_of_change == 'Change':
            self.finish_button.setText('Изменить')
        self.setVisible(True)
        self.parent_form = parent_form
        self.parent_form.error_label.setText('')
        self.change_id = change_id
        self.name_field.setText('')
        self.cost_field.setValue(1)
        self.v_field.setValue(1)
        self.taste_field.setText('')
        if self.type_of_change == 'Change':
            name = self.parent_form.tableWidget.item(self.change_id - 1, 1).text()
            roasting = self.parent_form.tableWidget.item(self.change_id - 1, 2).text()
            kind = self.parent_form.tableWidget.item(self.change_id - 1, 3).text()
            taste = self.parent_form.tableWidget.item(self.change_id - 1, 4).text()
            cost = self.parent_form.tableWidget.item(self.change_id - 1, 5).text()
            v = self.parent_form.tableWidget.item(self.change_id - 1, 5).text()
            self.name_field.setText(name)
            self.taste_field.setText(taste)
            self.cost_field.setValue(int(cost))
            self.v_field.setValue(int(v))
            self.roasting_field.setCurrentText(roasting)
            self.kind_field.setCurrentText(kind)


class CoffeeWidget(QMainWindow, Ui_MainWindow):
    def __init__(self, help_widget):
        super().__init__()
        self.setupUi(self)
        self.connection = sqlite3.connect("data/coffee.db")
        self.button.clicked.connect(self.load_table)
        self.add_button.clicked.connect(self.add_coffee)
        self.change_button.clicked.connect(self.change_coffee)
        self.request_field.setPlainText("SELECT * FROM coffee")
        self.help_widget = help_widget
        self.first_time = True
        self.used_roasting = []
        self.used_kind = []
        self.load_table()

    def add_coffee(self):
        self.help_widget.show_form('Add', self)

    def change_coffee(self):
        if len(self.tableWidget.selectedItems()) > 1 or len(self.tableWidget.selectedItems()) == 0:
            self.error_label.setText('Неверное число выделенных элементов')
        else:
            coffee_id = int(self.tableWidget.item(self.tableWidget.selectedItems()[0].row(), 0).text())
            self.help_widget.show_form('Change', self, change_id=coffee_id)

    def load_table(self):
        self.error_label.setText('')
        request = self.request_field.toPlainText()
        try:
            res = self.connection.cursor().execute(request).fetchall()
            if self.first_time:
                title = ['ИД', 'Название', 'Степень обжарки', 'Вид', 'Вкус', 'Цена', 'Объём']
                self.tableWidget.setColumnCount(len(title))
                self.tableWidget.setHorizontalHeaderLabels(title)
                self.first_time = False
            self.tableWidget.setRowCount(0)
            for i, row in enumerate(res):
                self.tableWidget.setRowCount(self.tableWidget.rowCount() + 1)
                for j, elem in enumerate(row):
                    if j == 2:
                        elem = self.connection.cursor().execute("SELECT f.name FROM roasting as f where f.id = ? ",
                                                                (elem,)).fetchone()[0]
                        if elem not in self.used_roasting:
                            self.used_roasting.append(elem)
                            self.help_widget.roasting_field.addItem(elem)

                    if j == 3:
                        elem = self.connection.cursor().execute("SELECT f.name FROM kind as f where f.id = ? ",
                                                                (elem,)).fetchone()[0]
                        if elem not in self.used_kind:
                            self.used_kind.append(elem)
                            self.help_widget.kind_field.addItem(elem)
                    self.tableWidget.setItem(i, j, QTableWidgetItem(str(elem)))
        except Exception:
            self.error_label.setText("Извините, но ваш запрос неверный")

    def closeEvent(self, event):
        self.connection.close()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    help_ex = MakeCoffeeWidget()
    ex = CoffeeWidget(help_ex)
    ex.show()
    sys.excepthook = except_hook
    sys.exit(app.exec())
