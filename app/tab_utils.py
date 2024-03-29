"""
@file tab_utils.py
@author Ryan Missel

Holds shared functions across the PyQT tabs
"""
import json

from PyQt5 import QtWidgets
from PyQt5.QtGui import QIntValidator, QGuiApplication, QClipboard
from PyQt5.QtWidgets import QLabel, QLineEdit, QAction, QMenu, QFileDialog


def add_stat_to_layout(layout, label, row, force_int=False, placeholder=None, read_only=False):
    """
    Adds all the necessary widgets to a grid layout for a single stat
    :param label: The label to display
    :param row: The row number to add on
    :param force_int: Force input to be an integer value
    :param placeholder: light gray text to put in, usually to guide a user for input
    :returns: The QLineEdit object
    """
    new_label = QLabel(label)
    new_line_edit = QLineEdit()

    if force_int:
        new_line_edit.setValidator(QIntValidator(new_line_edit))
    if placeholder is not None:
        new_line_edit.setPlaceholderText(placeholder)
    if read_only is True:
        new_line_edit.setReadOnly(read_only)

    layout.addWidget(new_label, row, 0)
    layout.addWidget(new_line_edit, row, 1)
    return new_line_edit


def clear_layout(layout):
    """
    Wipe the current melee card. Technically has a memory leak on the 'wiped' components, but
    really a non-issue with how much memory it would accumulate.
    :param layout: QtLayout of the Melee Card
    """
    if layout is not None:
        while layout.count():
            child = layout.takeAt(0)
            if child.widget() is not None:
                child.widget().deleteLater()
            elif child.layout() is not None:
                clear_layout(child.layout())


def split_effect_text(initial_string, line_length=32):
    """
    Handles splitting an effect string into multiple lines depending on the length of words.
    Cleaner for visualizing in the cards
    :param initial_string: effect string to split
    :param line_length: length of line to split
    :return: line with newlines put in
    """
    cur_chars = 0
    info = ""
    for idx, word in enumerate(initial_string.split(" ")):
        cur_chars += len(word)
        if cur_chars > line_length:
            info += "\n"
            cur_chars = len(word)

        info += f"{word} "
    return info


def copy_image_action(self, winID, height=750, y=0):
    """ Build a QAction for copying a generated card to a clipped Image"""
    # Enable copy-pasting image cards
    copy_action = QAction("Copy Image", self)
    copy_action.setShortcut("Ctrl+C")
    copy_action.triggered.connect(lambda: copy_card(winID, height, y))
    return copy_action


def copy_card(winID, height, y=0):
    """ Converts the Card layout into an Image in the Clipboard """
    # Save as local image
    screen = QtWidgets.QApplication.primaryScreen()
    screenshot = screen.grabWindow(winID, y=y, height=height)
    QGuiApplication.clipboard().setImage(screenshot.toImage(), QClipboard.Clipboard)


def save_image_action(self, winID, image_type, height=750, y=0):
    """ Build a QAction for saving a generated card to a local Image"""
    # Enable copy-pasting image cards
    save_action = QAction("Save Image", self)
    save_action.setShortcut("Ctrl+S")
    save_action.triggered.connect(lambda: save_card(self, winID, image_type, height, y))
    return save_action


def save_card(self, winID, image_type, height, y=0):
    """ Converts the Card layout into a local image """
    # Get the filename to be saved
    dlg = QFileDialog()
    filename = dlg.getSaveFileName(
        self, 'Save File', f'output/{image_type}/{self.output_name}', f'{image_type.title()} Card (*.png)')[0]

    # Save as local image
    screen = QtWidgets.QApplication.primaryScreen()
    screenshot = screen.grabWindow(winID, y=y, height=height)
    screenshot.save(filename, "png")


def update_config(basedir, widget, config, config_tab, config_variable):
    """ For a given widget that has a configuration associated with it, update the config when checked """
    # Set config variable to current widget
    config[config_tab][config_variable] = widget.isChecked()

    # Update configuration file
    with open(f"{basedir}resources/CONFIG.json", 'w') as f:
        json.dump(config, f)
