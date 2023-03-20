"""
@file ShieldTab.py
@author Ryan Missel

Handles the logic and state for the PyQT tab related to shield generation
"""
from PyQt5.QtGui import QFont, QPixmap

from classes.Shield import Shield
from classes.ShieldImage import ShieldImage
from classes.json_reader import get_file_data
from app.tab_utils import add_stat_to_layout, clear_layout, split_effect_text, copy_image_action

from PyQt5.QtCore import Qt, QTimer
from PyQt5 import QtCore, QtWidgets
from PyQt5.QtWidgets import (QComboBox, QGridLayout, QGroupBox, QLabel, QWidget, QPushButton,
                             QCheckBox, QLineEdit, QFileDialog, QTextEdit, QAction, QMenu)


class ShieldTab(QWidget):
    def __init__(self, basedir, statusbar, foundry_translator):
        super(ShieldTab, self).__init__()

        # Load classes
        self.basedir = basedir
        self.statusbar = statusbar

        # PDF and Image Classes
        self.shield_images = ShieldImage(self.basedir)

        # API Classes
        self.foundry_translator = foundry_translator

        # Font to share for section headers
        font = QFont("Times", 9, QFont.Bold)
        font.setUnderline(True)

        ###################################
        ###  BEGIN: Shield Stats Grid    ###
        ###################################
        shield_stats_group = QGroupBox("Configuration")
        shield_stats_layout = QGridLayout()
        shield_stats_layout.setAlignment(Qt.AlignTop)

        # Index counter for gridlayout across all widgets
        idx = 0

        ##### Information Separator
        information_separator = QLabel("Shield Information")
        information_separator.setFont(font)
        information_separator.setAlignment(QtCore.Qt.AlignCenter)
        shield_stats_layout.addWidget(information_separator, idx, 0, 1, -1)
        idx += 1

        # Shield Name
        self.shield_line_edit = add_stat_to_layout(shield_stats_layout, "Shield Name:", idx, placeholder="Random")
        idx += 1

        # Shield Guild
        shield_stats_layout.addWidget(QLabel("Guild: "), idx, 0)
        self.guild_shield_type_box = QComboBox()
        self.guild_shield_type_box.addItem("Random")
        for item in get_file_data(basedir + "resources/misc/shields/shield.json").keys():
            self.guild_shield_type_box.addItem(item)
        shield_stats_layout.addWidget(self.guild_shield_type_box, idx, 1)
        idx += 1

        # Shield Tier
        shield_stats_layout.addWidget(QLabel("Tier: "), idx, 0)
        self.tier_shield_type_box = QComboBox()
        self.tier_shield_type_box.addItem("Random")
        for item in get_file_data(basedir + "resources/misc/shields/shield.json")["Ashen"].keys():
            self.tier_shield_type_box.addItem(item)
        shield_stats_layout.addWidget(self.tier_shield_type_box, idx, 1)
        idx += 1

        # Shield Capacity
        self.shield_capacity_edit = add_stat_to_layout(shield_stats_layout, "Capacity:", idx, force_int=True)
        self.shield_capacity_edit.setToolTip("Either manually enter a shield capacity or let it be rolled.")
        idx += 1

        # Shield Recharge
        self.shield_recharge_edit = add_stat_to_layout(shield_stats_layout, "Recharge Rate:", idx, force_int=True)
        self.shield_recharge_edit.setToolTip("Either manually enter a shield recharge rate or let it be rolled.")
        idx += 1

        # Shield Effect
        self.shield_effect_edit = add_stat_to_layout(shield_stats_layout, "Effect:", idx, placeholder="Random")
        self.shield_effect_edit.setToolTip("Either manually enter a shield effect or let it be rolled.")
        idx += 1

        # Add spacing between groups
        shield_stats_layout.addWidget(QLabel(""), idx, 0)
        idx += 1

        ##### Art Separator
        art_separator = QLabel("Custom Art Selection")
        art_separator.setFont(font)
        art_separator.setAlignment(QtCore.Qt.AlignCenter)
        shield_stats_layout.addWidget(art_separator, idx, 0, 1, -1)
        idx += 1

        # Filepath display for custom art
        self.art_filepath = QLineEdit("")

        # Buttons and file dialog associated with selecting local files
        art_gridlayout = QGridLayout()
        self.art_filedialog = QFileDialog()
        self.art_filedialog.setStatusTip(
            "Uses custom art on the gun art side when given either a local image path or a URL.")

        self.art_select = QPushButton("Open")
        self.art_select.clicked.connect(self.open_file)
        self.art_select.setStatusTip("Used to select an image to use in place of the Borderlands gun art.")

        art_gridlayout.addWidget(self.art_filepath, 0, 1)
        art_gridlayout.addWidget(self.art_select, 0, 2)

        shield_stats_layout.addWidget(QLabel("Custom Art File/URL:"), idx, 0)
        shield_stats_layout.addLayout(art_gridlayout, idx, 1)
        idx += 1

        # Add spacing between groups
        shield_stats_layout.addWidget(QLabel(""), idx, 0)
        idx += 1

        ##### External Tools Separator
        api_separator = QLabel("External Tools")
        api_separator.setFont(font)
        api_separator.setAlignment(QtCore.Qt.AlignCenter)
        shield_stats_layout.addWidget(api_separator, idx, 0, 1, -1)
        idx += 1

        # FoundryVTT JSON flag
        foundry_export_label = QLabel("FoundryVTT JSON Export: ")
        foundry_export_label.setStatusTip(
            "Choose whether to output a JSON file that can be imported by the B&B FoundryVTT System.")
        shield_stats_layout.addWidget(foundry_export_label, idx, 0)
        self.foundry_export_check = QCheckBox()
        self.foundry_export_check.setStatusTip(
            "Choose whether to output a JSON file that can be imported by the B&B FoundryVTT System.")
        self.foundry_export_check.setChecked(False)
        shield_stats_layout.addWidget(self.foundry_export_check, idx, 1)
        idx += 1

        # Grid layout
        shield_stats_group.setLayout(shield_stats_layout)
        ###################################
        ###  END: Shield Stats Grid      ###
        ###################################

        ###################################
        ###  START: Shield Generation    ###
        ###################################
        shield_generation_group = QGroupBox("Single-Shield Generation")
        shield_generation_layout = QGridLayout()
        shield_generation_layout.setAlignment(Qt.AlignTop)

        # Generate button
        button = QPushButton("Generate Shield")
        button.setToolTip("Handles generating the shield card and locally saving the PDF in \"outputs/shields/\".")
        button.clicked.connect(lambda: self.generate_shield())
        shield_generation_layout.addWidget(button, 1, 0, 1, -1)

        # Label for save file output
        self.output_shield_pdf_label = QLabel()
        shield_generation_layout.addWidget(self.output_shield_pdf_label, 2, 0, 1, -1)

        # Grid layout
        shield_generation_group.setLayout(shield_generation_layout)
        ###################################
        ###  END: Shield Generation      ###
        ###################################

        ###################################
        ###  START: Shield Display       ###
        ###################################
        self.shield_card_group = QGroupBox("Shield Card")
        self.shield_card_layout = QGridLayout()
        self.shield_card_layout.setAlignment(Qt.AlignTop)

        # Give a right-click menu for copying image cards
        self.display_height = 600
        self.shield_card_group.setContextMenuPolicy(Qt.ActionsContextMenu)

        # Enable copy-pasting image cards
        self.shield_card_group.addAction(
            copy_image_action(self, self.shield_card_group.winId(), height=self.display_height))

        self.shield_card_group.setLayout(self.shield_card_layout)
        ###################################
        ###  END: Potion Display        ###
        ###################################

        # Setting appropriate column widths
        shield_stats_group.setFixedWidth(300)
        shield_generation_group.setFixedWidth(300)
        self.shield_card_group.setFixedWidth(325)

        # Setting appropriate layout heights
        shield_stats_group.setFixedHeight(375)
        shield_generation_group.setFixedHeight(150 + 325)
        self.shield_card_group.setFixedHeight(850)

        # Potion Generation Layout
        self.shield_generation_layout = QGridLayout()
        self.shield_generation_layout.setAlignment(Qt.AlignLeft)
        self.shield_generation_layout.addWidget(shield_stats_group, 0, 0)
        self.shield_generation_layout.addWidget(shield_generation_group, 1, 0)
        self.shield_generation_layout.addWidget(self.shield_card_group, 0, 1, -1, 1)

        self.shield_tab = QWidget()
        self.shield_tab.setLayout(self.shield_generation_layout)

    def get_tab(self):
        return self.shield_tab

    def open_file(self):
        """ Handles opening a file for the art path images; if an invalid image then show a message to the statusbar """
        filename = self.art_filedialog.getOpenFileName(self, 'Load File', self.basedir + '/')[0]

        # Error handling for image paths
        if '.png' not in filename and '.jpg' not in filename:
            self.statusbar.showMessage("Filename invalid, select again!", 3000)
        else:
            self.art_filepath.setText(filename)

    def save_screenshot(self):
        """ Screenshots the Shield Card layout and saves to a local file """
        # Save as local image
        screen = QtWidgets.QApplication.primaryScreen()
        screenshot = screen.grabWindow(self.shield_card_group.winId(), height=self.display_height)
        screenshot.save(f"output/shields/{self.output_name}.png", "png")

        # Set label text for output
        self.output_shield_pdf_label.setText(f"Saved to output/shields/{self.output_name}.png")

    def generate_shield(self):
        """ Handles performing the call to generate a shield given the parameters and updating the Shield Card image """
        # Load in properties that are currently set in the program
        shield_name = self.shield_line_edit.text()
        shield_guild = self.guild_shield_type_box.currentText()
        shield_tier = self.tier_shield_type_box.currentText()
        shield_capacity = str(self.shield_capacity_edit.text())
        shield_recharge = str(self.shield_recharge_edit.text())
        shield_effect = self.shield_effect_edit.text()
        shield_art_path = self.art_filepath.text()

        # Generate a shield
        shield = Shield(self.basedir, self.shield_images,
                        name=shield_name, guild=shield_guild, tier=shield_tier,
                        capacity=shield_capacity, recharge=shield_recharge, effect=shield_effect,
                        shield_art=shield_art_path)

        # Generate output name and check if it is already in use
        self.output_name = "{}_Tier{}_{}".format(shield.guild, shield.tier, shield.name.replace(" ", ""))

        # Clear current shield card
        clear_layout(self.shield_card_layout)

        # Index counter for gridlayout across all widgets
        idx = 0

        # Pixmap for the Shield Image
        shield_display = QLabel()
        shield_pixmap = QPixmap(shield.shield_art_path).scaled(300, 300, Qt.KeepAspectRatio,
                                                               transformMode=QtCore.Qt.SmoothTransformation)
        shield_display.setAlignment(Qt.AlignCenter)
        shield_display.setPixmap(shield_pixmap)
        self.shield_card_layout.addWidget(shield_display, idx, 0, 1, -1)
        idx += 1

        # Add spacing between groups
        self.shield_card_layout.addWidget(QLabel(""), idx, 0)
        idx += 1

        # Shield Name
        shield_name = add_stat_to_layout(self.shield_card_layout, "Name: ", idx)
        shield_name.setText(shield.name)
        idx += 1

        # Shield Guild
        shield_guild = add_stat_to_layout(self.shield_card_layout, "Guild: ", idx)
        shield_guild.setText(shield.guild)
        idx += 1

        # Shield Tier
        shield_tier = add_stat_to_layout(self.shield_card_layout, "Item Tier: ", idx)
        shield_tier.setText(shield.tier)
        idx += 1

        # Shield Capacity
        shield_capacity = add_stat_to_layout(self.shield_card_layout, "Capacity: ", idx)
        shield_capacity.setText(str(shield.capacity))
        idx += 1

        # Shield Recharge
        shield_recharge = add_stat_to_layout(self.shield_card_layout, "Recharge: ", idx)
        shield_recharge.setText(str(shield.recharge))
        idx += 1

        # Shield Guild effect, dynamically expanded
        shield_effect = QTextEdit()
        prefix_info = split_effect_text(shield.effect)
        numOfLinesInText = prefix_info.count("\n") + 2
        shield_effect.setFixedHeight(numOfLinesInText * 15)
        shield_effect.setFixedWidth(245)
        shield_effect.setText(prefix_info)

        self.shield_card_layout.addWidget(QLabel("Effect: "), idx, 0, numOfLinesInText, 1)
        self.shield_card_layout.addWidget(shield_effect, idx, 1, numOfLinesInText, 1)
        idx += numOfLinesInText

        # Add spacing between groups
        self.shield_card_layout.addWidget(QLabel(""), idx, 0)
        idx += 1

        # Save as output
        QTimer.singleShot(1000, self.save_screenshot)

        # FoundryVTT Check
        if self.foundry_export_check.isChecked() is True:
            self.foundry_translator.export_shield(shield, self.output_name)
