"""
@file PotionTab.py
@author Ryan Missel

Handles the logic and state for the PyQT tab related to potion generation
"""
from PyQt5.QtGui import QFont, QPixmap

from classes.Potion import Potion
from classes.PotionImage import PotionImage

from app.tab_utils import add_stat_to_layout, split_effect_text, clear_layout, copy_image_action
from classes.json_reader import get_file_data

from PyQt5.QtCore import Qt, QTimer
from PyQt5 import QtCore, QtWidgets
from PyQt5.QtWidgets import (QComboBox, QGridLayout, QGroupBox, QLabel, QWidget, QPushButton,
                             QCheckBox, QLineEdit, QFileDialog, QTextEdit, QAction)


class PotionTab(QWidget):
    def __init__(self, basedir, statusbar, foundry_translator):
        super(PotionTab, self).__init__()

        # Load classes
        self.basedir = basedir
        self.statusbar = statusbar

        # PDF and Image Classes
        self.potion_images = PotionImage(self.basedir)

        # API Classes
        self.foundry_translator = foundry_translator

        # Font to share for section headers
        font = QFont("Times", 9, QFont.Bold)
        font.setUnderline(True)

        ###################################
        ###  BEGIN: Potion Stats Grid   ###
        ###################################
        potion_stats_group = QGroupBox("Configuration")
        potion_stats_layout = QGridLayout()
        potion_stats_layout.setAlignment(Qt.AlignTop)

        # Index counter for gridlayout across all widgets
        idx = 0

        ##### Information Separator
        information_separator = QLabel("Potion Information")
        information_separator.setFont(font)
        information_separator.setAlignment(QtCore.Qt.AlignCenter)
        potion_stats_layout.addWidget(information_separator, idx, 0, 1, -1)
        idx += 1

        # Potion ID Selection
        potion_stats_layout.addWidget(QLabel("Potion %: "), idx, 0)
        self.potion_id_box = QComboBox()
        self.potion_id_box.addItem("Random")
        for item in get_file_data(basedir + "resources/misc/potions/potion.json").keys():
            self.potion_id_box.addItem(item)
        potion_stats_layout.addWidget(self.potion_id_box, idx, 1)
        idx += 1

        # Add spacing between groups
        potion_stats_layout.addWidget(QLabel(""), idx, 0)
        idx += 1

        ##### Art Separator
        art_separator = QLabel("Custom Art Selection")
        art_separator.setFont(font)
        art_separator.setAlignment(QtCore.Qt.AlignCenter)
        potion_stats_layout.addWidget(art_separator, idx, 0, 1, -1)
        idx += 1

        # Filepath display for custom art
        self.art_filepath = QLineEdit("")

        # Buttons and file dialog associated with selecting local files
        art_gridlayout = QGridLayout()
        self.art_filedialog = QFileDialog()
        self.art_filedialog.setStatusTip(
            "Uses custom art on the relic art side when given either a local image path or a URL.")

        self.art_select = QPushButton("Open")
        self.art_select.clicked.connect(self.open_file)
        self.art_select.setStatusTip("Used to select an image to use in place of the Borderlands relic art.")

        art_gridlayout.addWidget(self.art_filepath, 0, 1)
        art_gridlayout.addWidget(self.art_select, 0, 2)

        potion_stats_layout.addWidget(QLabel("Custom Art File/URL:"), idx, 0)
        potion_stats_layout.addLayout(art_gridlayout, idx, 1)
        idx += 1

        # Add spacing between groups
        potion_stats_layout.addWidget(QLabel(""), idx, 0)
        idx += 1

        ##### External Tools Separator
        api_separator = QLabel("External Tools")
        api_separator.setFont(font)
        api_separator.setAlignment(QtCore.Qt.AlignCenter)
        potion_stats_layout.addWidget(api_separator, idx, 0, 1, -1)
        idx += 1

        # FoundryVTT JSON flag
        foundry_export_label = QLabel("FoundryVTT JSON Export: ")
        foundry_export_label.setStatusTip(
            "Choose whether to output a JSON file that can be imported by the B&B FoundryVTT System.")
        potion_stats_layout.addWidget(foundry_export_label, idx, 0)
        self.foundry_export_check = QCheckBox()
        self.foundry_export_check.setStatusTip(
            "Choose whether to output a JSON file that can be imported by the B&B FoundryVTT System.")
        self.foundry_export_check.setChecked(False)
        potion_stats_layout.addWidget(self.foundry_export_check, idx, 1)
        idx += 1

        # Grid layout
        potion_stats_group.setLayout(potion_stats_layout)
        ###################################
        ###  END: Potion Stats Grid     ###
        ###################################

        ###################################
        ###  START: Potion Generation   ###
        ###################################
        potion_generation_group = QGroupBox("Single-Potion Generation")
        potion_generation_layout = QGridLayout()
        potion_generation_layout.setAlignment(Qt.AlignTop)

        # Generate button
        button = QPushButton("Generate Potion")
        button.setToolTip("Handles generating the potion card and locally saving the PDF in \"outputs/\".")
        button.clicked.connect(lambda: self.generate_potion())
        potion_generation_layout.addWidget(button, 1, 0, 1, -1)

        # Label for savefile output
        self.output_potion_pdf_label = QLabel()
        potion_generation_layout.addWidget(self.output_potion_pdf_label, 2, 0, 1, -1)

        # Grid layout
        potion_generation_group.setLayout(potion_generation_layout)
        ###################################
        ###  END: Potion Generation     ###
        ###################################

        ###################################
        ###  START: Potion Display      ###
        ###################################
        self.potion_card_group = QGroupBox("Potion Card")
        self.potion_card_layout = QGridLayout()
        self.potion_card_layout.setAlignment(Qt.AlignTop)

        # Enable copy-pasting image cards
        self.potion_card_group.addAction(copy_image_action(self, self.potion_card_group.winId(), height=500))

        self.potion_card_group.setLayout(self.potion_card_layout)
        ###################################
        ###  END: Potion Display        ###
        ###################################

        # Setting appropriate column widths
        potion_stats_group.setFixedWidth(300)
        potion_generation_group.setFixedWidth(300)
        self.potion_card_group.setFixedWidth(325)

        # Setting appropriate layout heights
        potion_stats_group.setFixedHeight(300)
        potion_generation_group.setFixedHeight(550)
        self.potion_card_group.setFixedHeight(850)

        # Potion Generation Layout
        self.potion_generation_layout = QGridLayout()
        self.potion_generation_layout.setAlignment(Qt.AlignLeft)
        self.potion_generation_layout.addWidget(potion_stats_group, 0, 0)
        self.potion_generation_layout.addWidget(potion_generation_group, 1, 0)
        self.potion_generation_layout.addWidget(self.potion_card_group, 0, 1, -1, 1)

        self.potion_tab = QWidget()
        self.potion_tab.setLayout(self.potion_generation_layout)

    def get_tab(self):
        return self.potion_tab

    def open_file(self):
        """ Handles opening a file for the art path images; if an invalid image then show a message to the statusbar """
        filename = self.art_filedialog.getOpenFileName(self, 'Load File', self.basedir + '/')[0]

        # Error handling for image paths
        if '.png' not in filename and '.jpg' not in filename:
            self.statusbar.showMessage("Filename invalid, select again!", 3000)
        else:
            self.art_filepath.setText(filename)

    def save_screenshot(self):
        """ Screenshots the Potion Card layout and saves to a local file """
        # Save as local image
        screen = QtWidgets.QApplication.primaryScreen()
        screenshot = screen.grabWindow(self.potion_card_group.winId(), height=500)
        screenshot.save(f"output/potions/{self.output_name}.png", "png")

        # Set label text for output
        self.output_potion_pdf_label.setText(f"Saved to output/potions/{self.output_name}.png")

    def generate_potion(self):
        """ Handles performing the call to generate a potion given the parameters and updating the Potion Card image """
        # Load in properties that are currently set in the program
        potion_id = self.potion_id_box.currentText()
        potion_art_path = self.art_filepath.text()

        # Generate a potion
        potion = Potion(self.basedir, self.potion_images, potion_id, potion_art_path)

        # Generate output name and check if it is already in use
        self.output_name = potion.name.replace(" ", "")

        # Clear current potion card
        clear_layout(self.potion_card_layout)

        # Index counter for gridlayout across all widgets
        idx = 0

        # Pixmap for the Potion Image
        potion_display = QLabel()
        potion_pixmap = QPixmap(potion.potion_art_path).scaled(300, 300, Qt.KeepAspectRatio,
                                                               transformMode=QtCore.Qt.SmoothTransformation)
        potion_display.setAlignment(Qt.AlignCenter)
        potion_display.setPixmap(potion_pixmap)
        self.potion_card_layout.addWidget(potion_display, idx, 0, 1, -1)
        idx += 1

        # Add spacing between groups
        self.potion_card_layout.addWidget(QLabel(""), idx, 0)
        idx += 1

        # Potion Name
        potion_name = add_stat_to_layout(self.potion_card_layout, "Name: ", idx)
        if potion.tina_potion is True:
            potion_name.setText(f"{potion.name} (Tina Potion)")
        else:
            potion_name.setText(potion.name)
        idx += 1

        # Potion Effect, dynamically expanded
        potion_effect = QTextEdit()
        prefix_info = split_effect_text(potion.effect)
        numOfLinesInText = prefix_info.count("\n") + 2
        potion_effect.setFixedHeight(numOfLinesInText * 15)
        potion_effect.setFixedWidth(263)
        potion_effect.setText(prefix_info)

        self.potion_card_layout.addWidget(QLabel("Effect: "), idx, 0, numOfLinesInText, 1)
        self.potion_card_layout.addWidget(potion_effect, idx, 1, numOfLinesInText, 1)
        idx += numOfLinesInText

        # Add spacing between groups
        self.potion_card_layout.addWidget(QLabel(""), idx, 0)
        idx += 1

        # Save as output
        QTimer.singleShot(1000, self.save_screenshot)

        # FoundryVTT Check
        if self.foundry_export_check.isChecked() is True:
            self.foundry_translator.export_potion(potion, self.output_name)
