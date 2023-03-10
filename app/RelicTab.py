"""
@file RelicTab.py
@author Ryan Missel

Handles the logic and state for the PyQT tab related to relic generation
"""
from PyQt5.QtGui import QFont, QPixmap

from classes.Relic import Relic
from classes.RelicImage import RelicImage

from app.tab_utils import add_stat_to_layout, clear_layout, split_effect_text
from classes.json_reader import get_file_data

from PyQt5.QtCore import Qt, QTimer
from PyQt5 import QtCore, QtWidgets
from PyQt5.QtWidgets import (QComboBox, QGridLayout, QGroupBox, QLabel, QWidget, QPushButton,
                             QCheckBox, QLineEdit, QFileDialog, QTextEdit)


class RelicTab(QWidget):
    def __init__(self, basedir, statusbar, foundry_translator):
        super(RelicTab, self).__init__()

        # Load classes
        self.basedir = basedir
        self.statusbar = statusbar

        # PDF and Image Classes
        self.relic_images = RelicImage(self.basedir)

        # API Classes
        self.foundry_translator = foundry_translator

        # Font to share for section headers
        font = QFont("Times", 9, QFont.Bold)
        font.setUnderline(True)

        ###################################
        ###  BEGIN: Relic Stats Grid    ###
        ###################################
        relic_stats_group = QGroupBox("Configuration")
        relic_stats_layout = QGridLayout()
        relic_stats_layout.setAlignment(Qt.AlignTop)

        # Index counter for gridlayout across all widgets
        idx = 0

        ##### Information Separator
        information_separator = QLabel("Relic Information")
        information_separator.setFont(font)
        information_separator.setAlignment(QtCore.Qt.AlignCenter)
        relic_stats_layout.addWidget(information_separator, idx, 0, 1, -1)
        idx += 1

        # Relic Name
        self.relic_line_edit = add_stat_to_layout(relic_stats_layout, "Relic Name:", idx, placeholder="Random")
        idx += 1

        # Relic % Selection
        relic_stats_layout.addWidget(QLabel("{:<15} ".format("Relic %:")), idx, 0)
        self.relic_id_box = QComboBox()
        self.relic_id_box.addItem("Random")
        for item in get_file_data(basedir + "resources/misc/relics/relic.json").keys():
            self.relic_id_box.addItem(item)
        relic_stats_layout.addWidget(self.relic_id_box, idx, 1)
        idx += 1

        # Relic Type
        self.relic_type_edit = add_stat_to_layout(relic_stats_layout, "Relic Type:", idx)
        self.relic_type_edit.setToolTip("Either manually enter a relic type or let it be rolled.")
        idx += 1

        # Relic Rarity
        rarities = ["Random", "Common", "Uncommon", "Rare", "Epic", "Legendary"]
        relic_stats_layout.addWidget(QLabel("Rarity: "), idx, 0)
        self.rarity_relic_type_box = QComboBox()
        for item in rarities:
            self.rarity_relic_type_box.addItem(item)
        relic_stats_layout.addWidget(self.rarity_relic_type_box, idx, 1)
        idx += 1

        # Relic Effect
        self.relic_effect_edit = add_stat_to_layout(relic_stats_layout, "Effect:", idx)
        self.relic_effect_edit.setToolTip("Either manually enter a relic effect or let it be rolled.")
        idx += 1

        # Relic Class
        rarities = ["Random", "Assassin", "Berserker", "Commando", "Gunzerker", "Hunter", "Mecromancer",
                    "Psycho", "Siren", "Soldier", "Any"]
        relic_stats_layout.addWidget(QLabel("Class: "), idx, 0)
        self.rarity_class_type_box = QComboBox()
        for item in rarities:
            self.rarity_class_type_box.addItem(item)
        relic_stats_layout.addWidget(self.rarity_class_type_box, idx, 1)
        idx += 1


        # Relic Class Effect
        self.relic_class_effect_edit = add_stat_to_layout(relic_stats_layout, "Class Effect:", idx)
        self.relic_class_effect_edit.setToolTip("Either manually enter a relic class effect or let it be rolled.")
        idx += 1

        # Add spacing between groups
        relic_stats_layout.addWidget(QLabel(""), idx, 0)
        idx += 1

        ##### Art Separator
        art_separator = QLabel("Custom Art Selection")
        art_separator.setFont(font)
        art_separator.setAlignment(QtCore.Qt.AlignCenter)
        relic_stats_layout.addWidget(art_separator, idx, 0, 1, -1)
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

        relic_stats_layout.addWidget(QLabel("Custom Art File/URL:"), idx, 0)
        relic_stats_layout.addLayout(art_gridlayout, idx, 1)
        idx += 1

        # Add spacing between groups
        relic_stats_layout.addWidget(QLabel(""), idx, 0)
        idx += 1

        ##### External Tools Separator
        api_separator = QLabel("External Tools")
        api_separator.setFont(font)
        api_separator.setAlignment(QtCore.Qt.AlignCenter)
        relic_stats_layout.addWidget(api_separator, idx, 0, 1, -1)
        idx += 1

        # FoundryVTT JSON flag
        foundry_export_label = QLabel("FoundryVTT JSON Export: ")
        foundry_export_label.setStatusTip(
            "Choose whether to output a JSON file that can be imported by the B&B FoundryVTT System.")
        relic_stats_layout.addWidget(foundry_export_label, idx, 0)
        self.foundry_export_check = QCheckBox()
        self.foundry_export_check.setStatusTip(
            "Choose whether to output a JSON file that can be imported by the B&B FoundryVTT System.")
        self.foundry_export_check.setChecked(False)
        relic_stats_layout.addWidget(self.foundry_export_check, idx, 1)
        idx += 1

        # Grid layout
        relic_stats_group.setLayout(relic_stats_layout)
        ###################################
        ###  END: Relic Stats Grid      ###
        ###################################

        ###################################
        ###  START: Relic Generation    ###
        ###################################
        relic_generation_group = QGroupBox("Single-Relic Generation")
        relic_generation_layout = QGridLayout()
        relic_generation_layout.setAlignment(Qt.AlignTop)

        # Generate button
        button = QPushButton("Generate Relic")
        button.setToolTip("Handles generating the relic card and locally saving the PDF in \"outputs/relics/\".")
        button.clicked.connect(lambda: self.generate_relic())
        relic_generation_layout.addWidget(button, 1, 0, 1, -1)

        # Label for save file output
        self.output_relic_pdf_label = QLabel()
        relic_generation_layout.addWidget(self.output_relic_pdf_label, 2, 0, 1, -1)

        # Grid layout
        relic_generation_group.setLayout(relic_generation_layout)
        ###################################
        ###  END: Relic Generation      ###
        ###################################

        ###################################
        ###  START: Relic Display       ###
        ###################################
        self.relic_card_group = QGroupBox("Relic Card")
        self.relic_card_layout = QGridLayout()
        self.relic_card_layout.setAlignment(Qt.AlignTop)

        self.relic_card_group.setLayout(self.relic_card_layout)
        ###################################
        ###  END: Potion Display        ###
        ###################################

        # Setting appropriate column widths
        relic_stats_group.setFixedWidth(300)
        relic_generation_group.setFixedWidth(300)
        self.relic_card_group.setFixedWidth(325)

        # Setting appropriate layout heights
        relic_stats_group.setFixedHeight(400)
        relic_generation_group.setFixedHeight(450)
        self.relic_card_group.setFixedHeight(850)

        # Potion Generation Layout
        self.relic_generation_layout = QGridLayout()
        self.relic_generation_layout.setAlignment(Qt.AlignLeft)
        self.relic_generation_layout.addWidget(relic_stats_group, 0, 0)
        self.relic_generation_layout.addWidget(relic_generation_group, 1, 0)
        self.relic_generation_layout.addWidget(self.relic_card_group, 0, 1, -1, 1)

        self.relic_tab = QWidget()
        self.relic_tab.setLayout(self.relic_generation_layout)

    def get_tab(self):
        return self.relic_tab

    def open_file(self):
        """ Handles opening a file for the art path images; if an invalid image then show a message to the statusbar """
        filename = self.art_filedialog.getOpenFileName(self, 'Load File', self.basedir + '/')[0]

        # Error handling for image paths
        if '.png' not in filename and '.jpg' not in filename:
            self.statusbar.showMessage("Filename invalid, select again!", 3000)
        else:
            self.art_filepath.setText(filename)

    def save_screenshot(self):
        """ Screenshots the Relic Card layout and saves to a local file """
        # Save as local image
        screen = QtWidgets.QApplication.primaryScreen()
        screenshot = screen.grabWindow(self.relic_card_group.winId(), height=550)
        screenshot.save(f"output/relics/{self.output_name}.png", "png")

        # Set label text for output
        self.output_relic_pdf_label.setText(f"Saved to output/relics/{self.output_name}.png")

    def generate_relic(self):
        """ Handles performing the call to generate a relic given the parameters and updating the Potion Card image """
        # Load in properties that are currently set in the program
        relic_id = self.relic_id_box.currentText()
        relic_name = self.relic_line_edit.text()
        relic_type = self.relic_type_edit.text()
        relic_rarity = self.rarity_relic_type_box.currentText()
        relic_effect = self.relic_effect_edit.text()
        relic_class_id = self.rarity_class_type_box.currentText()
        relic_class_effect = self.relic_class_effect_edit.text()
        relic_art_path = self.art_filepath.text()

        # Generate a relic
        relic = Relic(self.basedir, self.relic_images,
                      relic_name, relic_id, relic_type, relic_rarity,
                      relic_effect, relic_class_id, relic_class_effect,
                      relic_art_path)

        # Generate output name and check if it is already in use
        self.output_name = f"{relic.class_id}_{relic.type}_{relic.name.replace(' ', '')}"

        # Clear current relic card
        clear_layout(self.relic_card_layout)

        # Index counter for gridlayout across all widgets
        idx = 0

        # Pixmap for the Relic Image
        relic_display = QLabel()
        relic_pixmap = QPixmap(relic.relic_art_path).scaled(300, 300, Qt.KeepAspectRatio,
                                                            transformMode=QtCore.Qt.SmoothTransformation)
        relic_display.setAlignment(Qt.AlignCenter)
        relic_display.setPixmap(relic_pixmap)
        self.relic_card_layout.addWidget(relic_display, idx, 0, 1, -1)
        idx += 1

        # Add spacing between groups
        self.relic_card_layout.addWidget(QLabel(""), idx, 0)
        idx += 1

        # Relic Name
        relic_name = add_stat_to_layout(self.relic_card_layout, "Name: ", idx)
        relic_name.setText(relic.name)
        idx += 1

        # Relic Type
        relic_type = add_stat_to_layout(self.relic_card_layout, "Type: ", idx)
        relic_type.setText(relic.type)
        idx += 1

        # Relic Rarity
        relic_tier = add_stat_to_layout(self.relic_card_layout, "Rarity: ", idx)
        relic_tier.setText(relic.rarity.title())
        idx += 1

        # Relic Guild effect, dynamically expanded
        relic_effect = QTextEdit()
        prefix_info = split_effect_text(relic.effect)
        numOfLinesInText = prefix_info.count("\n") + 2
        relic_effect.setFixedHeight(numOfLinesInText * 15)
        relic_effect.setFixedWidth(235)
        relic_effect.setText(prefix_info)

        self.relic_card_layout.addWidget(QLabel("Effect: "), idx, 0, numOfLinesInText, 1)
        self.relic_card_layout.addWidget(relic_effect, idx, 1, numOfLinesInText, 1)
        idx += numOfLinesInText

        # Relic Guild effect, dynamically expanded
        relic_effect = QTextEdit()
        prefix_info = split_effect_text(f"({relic.class_id.title()}): {relic.class_effect}")
        numOfLinesInText = prefix_info.count("\n") + 2
        relic_effect.setFixedHeight(numOfLinesInText * 15)
        relic_effect.setFixedWidth(235)
        relic_effect.setText(prefix_info)

        self.relic_card_layout.addWidget(QLabel("Class Effect: "), idx, 0, numOfLinesInText, 1)
        self.relic_card_layout.addWidget(relic_effect, idx, 1, numOfLinesInText, 1)
        idx += numOfLinesInText

        # Add spacing between groups
        self.relic_card_layout.addWidget(QLabel(""), idx, 0)
        idx += 1

        # Save as output
        QTimer.singleShot(1000, self.save_screenshot)

        # FoundryVTT Check
        if self.foundry_export_check.isChecked() is True:
            self.foundry_translator.export_relic(relic, self.output_name)
