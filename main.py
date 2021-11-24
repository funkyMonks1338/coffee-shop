# -*- coding: utf-8 -*-
import sys
import os
from PyQt5 import uic
from PyQt5.QtWidgets import QApplication, QMainWindow, \
    QTableWidgetItem
from sqlalchemy import create_engine, Column, ForeignKey, \
    Integer, Text
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.ext.declarative import declarative_base


DATABASE_FILENAME = 'coffee.sqlite'
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
    size = Column(Integer)  # в кубических сантиметрах

    def __repr__(self):
        return (f'CoffeeCup(id={self.id!r}, '
                f'kind_id={self.kind_id!r}, '
                f'roasting_id={self.roasting_id!r}, '
                f'condition={self.condition!r}, '
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


class CoffeeSearcher(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi('main.ui', self)
        self.search_btn.clicked.connect(self.search_coffee)
        self.EVERY_FILTER = 'Любой'
        self.int_fields = ('id', 'price', 'size')
        self.str_fields = ('kind', 'roasting', 'condition')
        self.models = (Kind, Roasting, Condition)
        names_and_models = list(zip(self.str_fields, self.models))
        self.names_to_models = dict(names_and_models)
        for field, model in names_and_models:
            try:
                cmb_box = getattr(self, f'{field}_combobox')
            except AttributeError:
                continue
            cmb_box.addItem(self.EVERY_FILTER)
            for item in session.query(model).all():
                cmb_box.addItem(item.name)

    def search_coffee(self):
        ("""Находит кофе по фильтрам"""
         """Все неправильно заполненные фильтры удаляются""")
        filters = self.get_filters()
        for name, value in tuple(filters.items()):
            if isinstance(value, str):
                model = self.names_to_models.get(name)
                if model is None:
                    del filters[name]
                    continue
                model_obj = session.query(model).filter_by(name=value).first()
                if model_obj is None:
                    del filters[name]
                    continue
                filters[name] = model_obj
        result = session.query(CoffeeCup).filter_by(**filters).all()
        self.refill_table_widget(result)

    def refill_table_widget(self, coffee_data: list):
        headers = ('ID', 'Цена(руб.)', 'Объём(мм^3)', 'Сорт',
            'Обжарка', 'Состояние', 'Описание вкуса')
        self.table_widget.setColumnCount(len(headers))
        self.table_widget.setHorizontalHeaderLabels(headers)
        self.table_widget.setRowCount(0)
        for i, coffee_cup in enumerate(coffee_data):
            self.table_widget.setRowCount(
                self.table_widget.rowCount() + 1)
            row = [coffee_cup.id,
                   coffee_cup.price,
                   coffee_cup.size]
            for str_field in self.str_fields:
                row.append(getattr(coffee_cup, str_field).name)
            row.append(coffee_cup.taste_description)
            for j, elem in enumerate(row):
                self.table_widget.setItem(
                    i, j, QTableWidgetItem(str(elem)))
        self.table_widget.resizeColumnsToContents()

    def get_filters(self) -> dict:
        filters_info = {}
        for int_field in self.int_fields:
            try:
                spinbox = getattr(self, f'{int_field}_spinbox')
            except AttributeError:
                continue
            spinbox_value = spinbox.value()
            if spinbox_value:
                filters_info[int_field] = spinbox_value
        for str_field in self.str_fields:
            try:
                cmb_box = getattr(self, f'{str_field}_combobox')
            except AttributeError:
                continue
            cmb_box_value = cmb_box.currentText()
            if cmb_box_value and cmb_box_value != self.EVERY_FILTER:
                filters_info[str_field] = cmb_box_value
        return filters_info


if __name__ == '__main__':
    if not os.path.isfile(DATABASE_FILENAME):
        Base.metadata.create_all()
    app = QApplication(sys.argv)
    coffee_searcher = CoffeeSearcher()
    coffee_searcher.show()
    sys.exit(app.exec())
