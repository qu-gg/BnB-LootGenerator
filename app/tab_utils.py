"""
@file tab_utils.py
@author Ryan Missel

Holds shared functions across the PyQT tabs
"""
from PyQt5.QtGui import QIntValidator
from PyQt5.QtWidgets import QLabel, QLineEdit


def add_stat_to_layout(layout, label, row, force_int=False, placeholder=None):
    """
    Adds all the necessary widgets to a grid layout for a single stat
    :param label: The label to display
    :param row: The row number to add on
    :param force_int: Force input to be an integer value
    :returns: The QLineEdit object
    """
    new_label = QLabel(label)
    new_line_edit = QLineEdit()

    if force_int:
        new_line_edit.setValidator(QIntValidator(new_line_edit))
    if placeholder is not None:
        new_line_edit.setPlaceholderText(placeholder)

    layout.addWidget(new_label, row, 0)
    layout.addWidget(new_line_edit, row, 1)
    return new_line_edit
