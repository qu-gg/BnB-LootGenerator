"""
@file GrenadeTab.py
@author Ryan Missel

Handles the logic and state for the PyQT tab related to grenade generation
"""
from PyQt5.QtGui import QFont, QPixmap

from classes.Grenade import Grenade
from classes.GrenadeImage import GrenadeImage

from app.tab_utils import add_stat_to_layout, split_effect_text, clear_layout
from classes.json_reader import get_file_data

from PyQt5.QtCore import Qt, QTimer
from PyQt5 import QAxContainer, QtCore, QtWidgets
from PyQt5.QtWidgets import (QComboBox, QGridLayout, QGroupBox, QLabel, QWidget, QPushButton, QLineEdit, QFileDialog,
                             QCheckBox, QTextEdit)


class GrenadeTab(QWidget):
    def __init__(self, basedir, statusbar, foundry_translator):
        super(GrenadeTab, self).__init__()

        # Load classes
        self.basedir = basedir
        self.statusbar = statusbar

        # PDF and Image Classes
        self.grenade_images = GrenadeImage(self.basedir)

        # API Classes
        self.foundry_translator = foundry_translator

        # Font to share for section headers
        font = QFont("Times", 9, QFont.Bold)
        font.setUnderline(True)

        ###################################
        ###  BEGIN: Grenade Stats Grid    ###
        ###################################
        grenade_stats_group = QGroupBox("Configuration")
        grenade_stats_layout = QGridLayout()
        grenade_stats_layout.setAlignment(Qt.AlignTop)

        # Index counter for gridlayout across all widgets
        idx = 0

        ##### Information Separator
        information_separator = QLabel("Grenade Information")
        information_separator.setFont(font)
        information_separator.setAlignment(QtCore.Qt.AlignCenter)
        grenade_stats_layout.addWidget(information_separator, idx, 0, 1, -1)
        idx += 1

        # grenade Name
        self.grenade_line_edit = add_stat_to_layout(grenade_stats_layout, "Grenade Name:", idx, placeholder="Random")
        idx += 1

        # grenade Guild
        grenade_stats_layout.addWidget(QLabel("Guild: "), idx, 0)
        self.guild_grenade_type_box = QComboBox()
        self.guild_grenade_type_box.addItem("Random")
        for item in get_file_data(basedir + "resources/misc/grenades/grenade.json").keys():
            self.guild_grenade_type_box.addItem(item)
        grenade_stats_layout.addWidget(self.guild_grenade_type_box, idx, 1)
        idx += 1

        # grenade Tier
        grenade_stats_layout.addWidget(QLabel("Tier: "), idx, 0)
        self.tier_grenade_type_box = QComboBox()
        self.tier_grenade_type_box.addItem("Random")
        for item in get_file_data(basedir + "resources/misc/grenades/grenade.json")["Ashen"].keys():
            self.tier_grenade_type_box.addItem(item)
        grenade_stats_layout.addWidget(self.tier_grenade_type_box, idx, 1)
        idx += 1

        # Grenade Type
        self.grenade_type_edit = add_stat_to_layout(grenade_stats_layout, "Type:", idx)
        self.grenade_type_edit.setToolTip("Either manually enter a grenade type or let it be rolled.")
        idx += 1

        # Grenade Damage
        self.grenade_damage_edit = add_stat_to_layout(grenade_stats_layout, "Damage:", idx, placeholder="NdX")
        self.grenade_damage_edit.setToolTip("Either manually enter a grenade damage stat or let it be rolled.")
        idx += 1

        # Grenade Effect
        self.grenade_effect_edit = add_stat_to_layout(grenade_stats_layout, "Effect:", idx)
        self.grenade_effect_edit.setToolTip("Either manually enter a grenade effect or let it be rolled.")
        idx += 1

        # Add spacing between groups
        grenade_stats_layout.addWidget(QLabel(""), idx, 0)
        idx += 1

        ##### Art Separator
        art_separator = QLabel("Custom Art Selection")
        art_separator.setFont(font)
        art_separator.setAlignment(QtCore.Qt.AlignCenter)
        grenade_stats_layout.addWidget(art_separator, idx, 0, 1, -1)
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

        grenade_stats_layout.addWidget(QLabel("Custom Art File/URL:"), idx, 0)
        grenade_stats_layout.addLayout(art_gridlayout, idx, 1)
        idx += 1

        # Add spacing between groups
        grenade_stats_layout.addWidget(QLabel(""), idx, 0)
        idx += 1

        ##### External Tools Separator
        api_separator = QLabel("External Tools")
        api_separator.setFont(font)
        api_separator.setAlignment(QtCore.Qt.AlignCenter)
        grenade_stats_layout.addWidget(api_separator, idx, 0, 1, -1)
        idx += 1

        # FoundryVTT JSON flag
        foundry_export_label = QLabel("FoundryVTT JSON Export: ")
        foundry_export_label.setStatusTip(
            "Choose whether to output a JSON file that can be imported by the B&B FoundryVTT System.")
        grenade_stats_layout.addWidget(foundry_export_label, idx, 0)
        self.foundry_export_check = QCheckBox()
        self.foundry_export_check.setStatusTip(
            "Choose whether to output a JSON file that can be imported by the B&B FoundryVTT System.")
        self.foundry_export_check.setChecked(False)
        grenade_stats_layout.addWidget(self.foundry_export_check, idx, 1)
        idx += 1

        # Grid layout
        grenade_stats_group.setLayout(grenade_stats_layout)
        ###################################
        ###  END: Grenade Stats Grid      ###
        ###################################

        ###################################
        ###  START: Grenade Generation    ###
        ###################################
        grenade_generation_group = QGroupBox("Single-Grenade Generation")
        grenade_generation_layout = QGridLayout()
        grenade_generation_layout.setAlignment(Qt.AlignTop)

        # Generate button
        button = QPushButton("Generate Grenade")
        button.setToolTip("Handles generating the grenade card and locally saving the PDF in \"outputs/grenades/\".")
        button.clicked.connect(lambda: self.generate_grenade())
        grenade_generation_layout.addWidget(button, 1, 0, 1, -1)

        # Label for save file output
        self.output_grenade_pdf_label = QLabel()
        grenade_generation_layout.addWidget(self.output_grenade_pdf_label, 2, 0, 1, -1)

        # Grid layout
        grenade_generation_group.setLayout(grenade_generation_layout)
        ###################################
        ###  END: Grenade Generation      ###
        ###################################

        ###################################
        ###  START: Grenade Display       ###
        ###################################
        self.grenade_card_group = QGroupBox("Grenade Card")
        self.grenade_card_layout = QGridLayout()
        self.grenade_card_layout.setAlignment(Qt.AlignTop)

        self.grenade_card_group.setLayout(self.grenade_card_layout)
        ###################################
        ###  END: Grenade Display       ###
        ###################################

        # Setting appropriate column widths
        grenade_stats_group.setFixedWidth(300)
        grenade_generation_group.setFixedWidth(300)
        self.grenade_card_group.setFixedWidth(325)

        # Setting appropriate layout heights
        grenade_stats_group.setFixedHeight(375)
        grenade_generation_group.setFixedHeight(475)
        self.grenade_card_group.setFixedHeight(850)

        # Potion Generation Layout
        self.grenade_generation_layout = QGridLayout()
        self.grenade_generation_layout.setAlignment(Qt.AlignLeft)
        self.grenade_generation_layout.addWidget(grenade_stats_group, 0, 0)
        self.grenade_generation_layout.addWidget(grenade_generation_group, 1, 0)
        self.grenade_generation_layout.addWidget(self.grenade_card_group, 0, 1, -1, 1)

        self.grenade_tab = QWidget()
        self.grenade_tab.setLayout(self.grenade_generation_layout)

    def get_tab(self):
        return self.grenade_tab

    def open_file(self):
        """ Handles opening a file for the art path images; if an invalid image then show a message to the statusbar """
        filename = self.art_filedialog.getOpenFileName(self, 'Load File', self.basedir + '/')[0]

        # Error handling for image paths
        if '.png' not in filename and '.jpg' not in filename:
            self.statusbar.showMessage("Filename invalid, select again!", 3000)
        else:
            self.art_filepath.setText(filename)

    def save_screenshot(self):
        """ Screenshots the Grenade Card layout and saves to a local file """
        # Save as local image
        screen = QtWidgets.QApplication.primaryScreen()
        screenshot = screen.grabWindow(self.grenade_card_group.winId(), height=600)
        screenshot.save(f"output/grenades/{self.output_name}.png", "png")

        # Set label text for output
        self.output_grenade_pdf_label.setText(f"Saved to output/grenades/{self.output_name}.png")

    def generate_grenade(self):
        """ Handles performing the call to generate a grenade given the parameters and updating the Grenade Card image """
        # Load in properties that are currently set in the program
        grenade_name = self.grenade_line_edit.text()
        grenade_guild = self.guild_grenade_type_box.currentText()
        grenade_tier = self.tier_grenade_type_box.currentText()
        grenade_type = self.grenade_type_edit.text()
        grenade_damage = self.grenade_damage_edit.text()
        grenade_effect = self.grenade_effect_edit.text()
        grenade_art_path = self.art_filepath.text()

        # Generate a grenade
        grenade = Grenade(self.basedir, self.grenade_images,
                          name=grenade_name, guild=grenade_guild, grenade_type=grenade_type,
                          tier=grenade_tier, damage=grenade_damage, effect=grenade_effect, grenade_art=grenade_art_path)

        # Generate output name and check if it is already in use
        self.output_name = "{}_Tier{}_{}".format(grenade.guild, grenade.tier, grenade.name.replace(" ", ""))

        # Clear current grenade card
        clear_layout(self.grenade_card_layout)

        # Index counter for gridlayout across all widgets
        idx = 0

        # Pixmap for the Grenade Image
        grenade_display = QLabel()
        grenade_pixmap = QPixmap(grenade.grenade_art_path).scaled(300, 300, Qt.KeepAspectRatio,
                                                               transformMode=QtCore.Qt.SmoothTransformation)
        grenade_display.setAlignment(Qt.AlignCenter)
        grenade_display.setPixmap(grenade_pixmap)
        self.grenade_card_layout.addWidget(grenade_display, idx, 0, 1, -1)
        idx += 1

        # Add spacing between groups
        self.grenade_card_layout.addWidget(QLabel(""), idx, 0)
        idx += 1

        # Grenade Name
        grenade_name = add_stat_to_layout(self.grenade_card_layout, "Name: ", idx)
        grenade_name.setText(grenade.name)
        idx += 1

        # Grenade Guild
        grenade_guild = add_stat_to_layout(self.grenade_card_layout, "Guild: ", idx)
        grenade_guild.setText(grenade.guild.title())
        idx += 1

        # Grenade Tier
        grenade_tier = add_stat_to_layout(self.grenade_card_layout, "Item Tier: ", idx)
        grenade_tier.setText(str(grenade.tier))
        idx += 1

        # Grenade Capacity
        grenade_capacity = add_stat_to_layout(self.grenade_card_layout, "Type: ", idx)
        grenade_capacity.setText(str(grenade.type))
        idx += 1

        # Grenade Recharge
        grenade_recharge = add_stat_to_layout(self.grenade_card_layout, "Damage: ", idx)
        grenade_recharge.setText(str(grenade.damage))
        idx += 1

        # Grenade Guild effect, dynamically expanded
        grenade_effect = QTextEdit()
        prefix_info = split_effect_text(grenade.effect)
        numOfLinesInText = prefix_info.count("\n") + 2
        grenade_effect.setFixedHeight(numOfLinesInText * 15)
        grenade_effect.setFixedWidth(249)
        grenade_effect.setText(prefix_info)

        self.grenade_card_layout.addWidget(QLabel("Effect: "), idx, 0, numOfLinesInText, 1)
        self.grenade_card_layout.addWidget(grenade_effect, idx, 1, numOfLinesInText, 1)
        idx += numOfLinesInText

        # Add spacing between groups
        self.grenade_card_layout.addWidget(QLabel(""), idx, 0)
        idx += 1

        # Save as output
        QTimer.singleShot(1000, self.save_screenshot)

        # FoundryVTT Check
        if self.foundry_export_check.isChecked() is True:
            self.foundry_translator.export_grenade(grenade, self.output_name)
