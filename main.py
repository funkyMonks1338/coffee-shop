# -*- coding: utf-8 -*-
import sys
import os
from PyQt5 import QtCore
from PyQt5.QtWidgets import QApplication, QMainWindow, \
    QTableWidgetItem, QMessageBox
from sqlalchemy import create_engine, Column, ForeignKey, \
    Integer, Text
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.ext.declarative import declarative_base
from UI.main_window import Ui_MainWindow
from UI.addEditCoffeeForm import Ui_addEditCoffeeForm


DATABASE_FILENAME = 'data/coffee.sqlite'
engine = create_engine(f'sqlite:///{DATABASE_FILENAME}')
Session = sessionmaker(bind=engine)
session = Session()
Base = declarative_base()
Base.metadata.bind = engine


class CoffeeCup(Base):
    """Непосредственно кофе"""
    __tablename__ = 'coffee_cup'

    id = Column(Integer, primary_key=True, autoincrement=True)
    kind_id = Column(Integer, ForeignKey('kind.id'))
    kind = relationship('Kind', back_populates='coffee_cups')
    roasting_id = Column(Integer, ForeignKey('roasting.id'))
    roasting = relationship('Roasting', back_populates='coffee_cups')
    condition_id = Column(Integer, ForeignKey('condition.id'))
    condition = relationship('Condition', back_populates='coffee_cups')
    taste_description = Column(Text)
    price = Column(Integer)  # в рублях
    size = Column(Integer)  # в кубических миллиметрах

    def __repr__(self):
        return (f'CoffeeCup(id={self.id!r}, '
                f'kind_id={self.kind_id!r}, '
                f'roasting_id={self.roasting_id!r}, '
                f'condition_id={self.condition_id!r}, '
                f'taste_description={self.taste_description!r}, '
                f'price={self.price!r}, '
                f'size={self.size!r})')


class Kind(Base):
    """Сорт кофе"""
    __tablename__ = 'kind'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(Text, unique=True)
    coffee_cups = relationship('CoffeeCup', back_populates='kind')

    def __repr__(self):
        return f'Kind(id={self.id!r}, name={self.name!r})'


class Roasting(Base):
    ("""Вид обжарки кофе."""
     """id - это степень обжарки кофе""")
    __tablename__ = 'roasting'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(Text, unique=True)
    coffee_cups = relationship('CoffeeCup', back_populates='roasting')

    def __repr__(self):
        return f'Roasting(id={self.id!r}, name={self.name!r})'


class Condition(Base):
    """Физическое состояние."""
    __tablename__ = 'condition'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(Text, unique=True)
    coffee_cups = relationship('CoffeeCup', back_populates='condition')

    def __repr__(self):
        return f'Сondition(id={self.id!r}, name={self.name!r})'


EVERY_FILTER = 'Любой'
INT_FIELDS = ('id', 'price', 'size')
STR_FIELDS = ('kind', 'roasting', 'condition')  # для поиска
RAW_STR_FIELDS = ('taste_description',)
TABLE_HEADERS = (
    'ID', 'Цена(руб.)', 'Объём(мм^3)', 'Сорт',
    'Обжарка', 'Состояние', 'Вкус')
ALL_FIELDS = INT_FIELDS + STR_FIELDS + RAW_STR_FIELDS
MODELS = (Kind, Roasting, Condition)
NAMES_AND_MODELS = list(zip(STR_FIELDS, MODELS))
NAMES_TO_MODELS = dict(NAMES_AND_MODELS)
# Когда кофе добавлен в таблицу, но заполнены ещё не все характеристики
NEW_COFFEE_NOT_READY = 'new_coffee_not_ready'


def refill_table_widget(table_widget, fields, coffee_data: list):
    while table_widget.rowCount() > 0:
        table_widget.removeRow(0)
    new_coffee_table = []
    table_widget.setColumnCount(len(TABLE_HEADERS))
    table_widget.setHorizontalHeaderLabels(TABLE_HEADERS)
    table_widget.setRowCount(0)
    for i, coffee_cup in enumerate(coffee_data):
        table_widget.setRowCount(table_widget.rowCount() + 1)
        row = [coffee_cup.id,
               coffee_cup.price,
               coffee_cup.size]
        for str_field in fields:
            row.append(getattr(coffee_cup, str_field).name)
        row.append(coffee_cup.taste_description)
        new_coffee_table.append(row)
        for j, elem in enumerate(row):
            item = QTableWidgetItem(str(elem))
            if not j:  # поле id
                item.setFlags(QtCore.Qt.ItemIsEnabled)  # отключение
            table_widget.setItem(i, j, item)
    table_widget.resizeColumnsToContents()
    return new_coffee_table


class AddEditCoffeeForm(QMainWindow, Ui_addEditCoffeeForm):
    def __init__(self, parent):
        super().__init__(parent)
        self.setupUi(self)
        self.coffee_list = session.query(CoffeeCup).all()
        self.coffee_str_table = (
            refill_table_widget(self.table_widget, STR_FIELDS, self.coffee_list))
        self.show_hint_btn.clicked.connect(self.show_hint)
        self.show_signatures_btn.clicked.connect(self.show_signatures)
        self.create_coffee_btn.clicked.connect(self.create_coffee)
        self.change_coffee_btn.clicked.connect(self.submit_coffee_changes)
        self.is_capturing_item_changes = True
        self.table_widget.itemChanged.connect(self.coffee_properties_changed)

    def show_signatures(self):
        """Показывает образцы заполнения полей, связанных с моделями"""
        n = len(STR_FIELDS)
        signatures = [''] * n
        for i in range(n):
            signatures[i] = ', '.join(
                f'{obj.name!r}' for obj in session.query(MODELS[i]).all())
        QMessageBox.information(
            self, 'Образцы заполнения полей',
            ('\n' * 3).join(
                (f'Поле {TABLE_HEADERS[i + len(INT_FIELDS)]!r} '
                 f'должно быть заполнено как \n{signatures[i]}') for i in range(n)))

    def show_hint(self):
        QMessageBox.information(
            self, 'Подсказка',
            ('Чтобы изменить характеристику кофе, отредактируйте её в нужной ячейке, '
             'следуя образцам заполнения и всплывающим сообщениям. '
             'После чего нажмите \'Изменить характеристики кофе\'.\n'
             'Чтобы добавить новую запись о кофе, нажмите \'Создать кофе\', '
             'после этого появится новая строка в таблице, заполните её по образцам. '
             'После заполнения всех полей нажмите \'Изменить характеристики кофе\', '
             'это не только добавит новый кофе, но и изменит отредактированные Вами.\n'
             'Если вы закроете это окно перед тем, как нажмёте \'Изменить кофе\', '
             'то записи в базе данных останутся без изменений.'))

    def create_coffee(self):
        """Добавляет новый кофе для заполнения в таблицу без изменений в БД"""
        if self.is_capturing_item_changes == NEW_COFFEE_NOT_READY:
            QMessageBox.critical(
                self, 'Ошибка!',
                f'Вы ещё не закончили добавление последнего нового кофе')
            return
        self.is_capturing_item_changes = False
        row_count = self.table_widget.rowCount()
        self.table_widget.setRowCount(row_count + 1)
        for i in range(len(TABLE_HEADERS)):
            item = QTableWidgetItem('' if i else str(row_count + 1))
            if not i:  # поле id
                item.setFlags(QtCore.Qt.ItemIsEnabled)  # отключение
            self.table_widget.setItem(row_count, i, item)
        self.coffee_list.append(CoffeeCup())
        session.add(self.coffee_list[-1])
        self.is_capturing_item_changes = NEW_COFFEE_NOT_READY

    def validate_coffee_field(self, row: int, col: int, new_text: str):
        ("""Возвращает объект нужного типа для последующей обработки """
         """Если поле введено неправильно, то возвращает None.""")
        coffee = self.coffee_list[-1]
        field_name = ALL_FIELDS[col]
        if field_name == 'id':
            return None
        field_value = getattr(coffee, field_name)
        if isinstance(field_value, int) or (
                field_value is None and field_name in INT_FIELDS):
            try:
                new_value = int(new_text)
            except ValueError:
                return None
        elif isinstance(field_value, str) or (
                field_value is None and field_name in RAW_STR_FIELDS):
            new_value = new_text
        else:
            model = NAMES_TO_MODELS.get(field_name)
            if model is None:
                return None
            new_text = ' '.join(new_text.split()).capitalize()
            new_property_obj = session.query(
                model).filter_by(name=new_text).first()
            if new_property_obj is None:
                return None
            new_value = new_property_obj
        return new_value

    def coffee_properties_changed(self, item):
        """"Этот метод вызывается при редактировании элементов таблицы"""
        row, col = item.row(), item.column()
        new_text = item.text()
        if not self.is_capturing_item_changes:
            return
        coffee = self.coffee_list[row]
        field_name = ALL_FIELDS[col]
        new_value = self.validate_coffee_field(row, col, new_text)
        if new_value is None:
            return self.rollback_table_item(row, col)
        setattr(coffee, field_name, new_value)

    def rollback_table_item(self, row: int, col: int) -> None:
        prev_capturing_const = self.is_capturing_item_changes
        self.is_capturing_item_changes = False
        try:
            str_item = self.coffee_str_table[row][col]
        except IndexError:
            str_item = ''
        self.table_widget.setItem(
            row, col,
            QTableWidgetItem(str(str_item)))
        self.is_capturing_item_changes = prev_capturing_const
        QMessageBox.critical(
            self, 'Ошибка!',
            f'Неправильно введено поле {TABLE_HEADERS[col]}')
        self.table_widget.resizeColumnsToContents()

    def submit_coffee_changes(self):
        if self.is_capturing_item_changes == NEW_COFFEE_NOT_READY:
            # проверка всех полей нового кофе
            last_row_ind = self.table_widget.rowCount() - 1
            coffee = self.coffee_list[-1]
            for col in range(1, self.table_widget.columnCount()):
                item = self.table_widget.item(last_row_ind, col)
                if self.validate_coffee_field(
                        last_row_ind, col, item.text()) is None:
                    QMessageBox.critical(
                        self, 'Ошибка!',
                        f'Вы ещё не закончили добавление последнего нового кофе')
                    return
        session.commit()
        self.is_capturing_item_changes = False
        QMessageBox.information(
            self, 'Успех!', 'Все действия успешно применены')
        self.coffee_str_table = (
            refill_table_widget(self.table_widget, STR_FIELDS, self.coffee_list))
        self.is_capturing_item_changes = True

    def closeEvent(self, event):
        self.parent().show()
        session.rollback()  # отмена неподтверждённых изменений
        event.accept()


class CoffeeSearcher(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.search_btn.clicked.connect(self.search_coffee)
        self.control_btn.clicked.connect(self.open_control_win)
        for field, model in NAMES_AND_MODELS:
            try:
                cmb_box = getattr(self, f'{field}_combobox')
            except AttributeError:
                continue
            cmb_box.addItem(EVERY_FILTER)
            for item in session.query(model).all():
                cmb_box.addItem(item.name)

    def open_control_win(self):
        self.control_window = AddEditCoffeeForm(self)
        while self.table_widget.rowCount() > 0:
            self.table_widget.removeRow(0)
        self.hide()
        self.control_window.show()

    def search_coffee(self):
        ("""Находит кофе по фильтрам"""
         """Все неправильно заполненные фильтры удаляются""")
        filters = self.get_filters()
        for name, value in tuple(filters.items()):
            if isinstance(value, str):
                model = NAMES_TO_MODELS.get(name)
                if model is None:
                    del filters[name]
                    continue
                model_obj = session.query(model).filter_by(name=value).first()
                if model_obj is None:
                    del filters[name]
                    continue
                filters[name] = model_obj
        result = session.query(CoffeeCup).filter_by(**filters).all()
        refill_table_widget(self.table_widget, STR_FIELDS, result)

    def get_filters(self) -> dict:
        filters_info = {}
        for int_field in INT_FIELDS:
            try:
                spinbox = getattr(self, f'{int_field}_spinbox')
            except AttributeError:
                continue
            spinbox_value = spinbox.value()
            if spinbox_value:
                filters_info[int_field] = spinbox_value
        for str_field in STR_FIELDS:
            try:
                cmb_box = getattr(self, f'{str_field}_combobox')
            except AttributeError:
                continue
            cmb_box_value = cmb_box.currentText()
            if cmb_box_value and cmb_box_value != EVERY_FILTER:
                filters_info[str_field] = cmb_box_value
        return filters_info


if __name__ == '__main__':
    if not os.path.isfile(DATABASE_FILENAME):
        Base.metadata.create_all()
    app = QApplication(sys.argv)
    coffee_searcher = CoffeeSearcher()
    coffee_searcher.show()
    sys.exit(app.exec())
