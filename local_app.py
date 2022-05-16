"""
@file local_app.py
@author Ryan Missel
Entrypoint for the Bunkers & Badasses loot generator program (https://github.com/qu-gg/BnB-LootGenerator)
Handles all of the UI interaction and display for the PyQT frontend
"""
import os
import sys
from pathlib import Path

from classes.Gun import Gun
from classes.GunPDF import GunPDF
from classes.GunImage import GunImage

from classes.Potion import Potion
from classes.PotionPDF import PotionPDF
from classes.PotionImage import PotionImage

from classes.Relic import Relic
from classes.RelicPDF import RelicPDF
from classes.RelicImage import RelicImage

from classes.json_reader import get_file_data

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon, QIntValidator
from PyQt5 import QAxContainer
from PyQt5.QtWidgets import (QApplication, QComboBox, QGridLayout, QGroupBox, QLabel,
                             QLineEdit, QWidget, QPushButton, QCheckBox, QMainWindow, QTabWidget)


class Window(QMainWindow):
    def __init__(self, basedir):
        super(Window, self).__init__()

        # Load classes
        self.basedir = basedir

        # PDF and Image Classes
        self.gun_pdf = GunPDF(self.basedir)
        self.gun_images = GunImage(self.basedir)

        self.potion_pdf = PotionPDF(self.basedir)
        self.potion_images = PotionImage(self.basedir)

        self.relic_pdf = RelicPDF(self.basedir)
        self.relic_images = RelicImage(self.basedir)

        # Window Title
        self.setWindowTitle("Bunkers and Badasses - LootGenerator")

        # Add stat function
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

        ######################################### START GUNS ##############################################

        ###################################
        ###  BEGIN: Base Stats Grid     ###
        ###################################
        base_stats_group = QGroupBox("Configuration")
        base_stats_layout = QGridLayout()
        base_stats_layout.setAlignment(Qt.AlignTop)

        # Gun Name
        self.name_line_edit = add_stat_to_layout(base_stats_layout, "Gun Name:", 0)

        # Item Level
        base_stats_layout.addWidget(QLabel("Item Level: "), 1, 0)
        self.item_level_box = QComboBox()
        self.item_level_box.addItem("Random")
        for item in get_file_data(basedir + "resources/guns/gun_types.json").get("pistol").keys():
            self.item_level_box.addItem(item)
        base_stats_layout.addWidget(self.item_level_box, 1, 1)

        # Gun Type
        self.gun_type_choices = ['pistol', 'submachine_gun', 'shotgun', 'combat_rifle', 'sniper_rifle', 'rocket_launcher']

        base_stats_layout.addWidget(QLabel("Gun Type: "), 2, 0)
        self.gun_type_box = QComboBox()
        self.gun_type_box.addItem("Random")
        for item in self.gun_type_choices:
            self.gun_type_box.addItem(item.capitalize().replace('_', ' '))
        base_stats_layout.addWidget(self.gun_type_box, 2, 1)

        # Guild
        base_stats_layout.addWidget(QLabel("Guild: "), 3, 0)
        self.guild_type_box = QComboBox()
        self.guild_type_box.addItem("Random")
        for item in get_file_data(basedir + "resources/guns/guild_table.json").keys():
            self.guild_type_box.addItem(item.capitalize())
        base_stats_layout.addWidget(self.guild_type_box, 3, 1)

        # Rarity
        rarities = ["Random", "Common", "Uncommon", "Rare", "Epic", "Legendary"]

        base_stats_layout.addWidget(QLabel("Rarity: "), 4, 0)
        self.rarity_type_box = QComboBox()
        for item in rarities:
            self.rarity_type_box.addItem(item)
        base_stats_layout.addWidget(self.rarity_type_box, 4, 1)

        # Roll for Rarity
        element_roll_text_label = QLabel("Force an Element Roll: ")
        element_roll_text_label.setToolTip("Choose whether to always add an element roll regardless of the rarity rolled. "
                                           "This does NOT guarantee an element, just rolling on the table.")
        base_stats_layout.addWidget(element_roll_text_label, 5, 0)
        self.element_roll = QCheckBox()
        self.element_roll.setToolTip("Choose whether to always add an element roll regardless of the rarity rolled. "
                                           "This does NOT guarantee an element, just rolling on the table.")
        base_stats_layout.addWidget(self.element_roll, 5, 1)

        # Whether to use a gun prefix
        prefix_text_label = QLabel("Include a Prefix: ")
        prefix_text_label.setToolTip("Choose whether to roll a Prefix modifier to the gun, as per Page 99.")
        base_stats_layout.addWidget(prefix_text_label, 6, 0)
        self.gun_prefix = QCheckBox()
        self.gun_prefix.setToolTip("Choose whether to roll a Prefix modifier to the gun, as per Page 99.")
        base_stats_layout.addWidget(self.gun_prefix, 6, 1)

        # Whether to roll for Red Text on epic or legendary
        red_text_label = QLabel("Include Red Text: ")
        red_text_label.setToolTip("Choose whether to roll for a Red Text modifier on guns of rarity Epic or Legendary, as per Page 100.")
        base_stats_layout.addWidget(red_text_label, 7, 0)
        self.red_text = QCheckBox()
        self.red_text.setToolTip("Choose whether to roll for a Red Text modifier on guns of rarity Epic or Legendary, as per Page 100.")
        base_stats_layout.addWidget(self.red_text, 7, 1)

        base_stats_layout.addWidget(QLabel(""), 8, 0)

        # Whether to roll for Red Text on epic or legendary
        damage_balance_label = QLabel("Use RobMWJ's Damage Balance: ")
        damage_balance_label.setToolTip("Choose whether to use alternative damage tables, written by user/robmwj on Reddit.")
        base_stats_layout.addWidget(damage_balance_label, 9, 0)
        self.damage_balance_check = QCheckBox()
        self.damage_balance_check.setToolTip("Choose whether to use alternative damage tables, written by user/robmwj on Reddit.")
        base_stats_layout.addWidget(self.damage_balance_check, 9, 1)

        # Whether to roll for Red Text on epic or legendary
        rarity_border_label = QLabel("Use Gun Rarity Borders: ")
        rarity_border_label.setToolTip("EXPERIMENTAL: Choose whether to outline the gun art in a colored-outline based on rarity. Doesn't work for all guns currently.")
        base_stats_layout.addWidget(rarity_border_label, 10, 0)
        self.rarity_border_check = QCheckBox()
        self.rarity_border_check.setToolTip("EXPERIMENTAL: Choose whether to outline the gun art in a colored-outline based on rarity. Doesn't work for all guns currently.")
        base_stats_layout.addWidget(self.rarity_border_check, 10, 1)

        # Grid layout
        base_stats_group.setLayout(base_stats_layout)
        ###################################
        ###  END: Base Stats Grid       ###
        ###################################

        ###################################
        ###  START: Generation          ###
        ###################################
        generation_group = QGroupBox("Single-Gun Generation")
        generation_layout = QGridLayout()
        generation_layout.setAlignment(Qt.AlignTop)

        # PDF Output Name
        self.pdf_line_edit = add_stat_to_layout(generation_layout, "PDF Filename:", 0)
        self.pdf_line_edit.setToolTip("Specify the filename that Generate Gun saves the next gun under.")

        # Generate button
        button = QPushButton("Generate Gun")
        button.setToolTip("Handles generating the gun and locally saving the PDF in \"outputs/\".")
        button.clicked.connect(lambda: self.generate_gun())
        generation_layout.addWidget(button, 1, 0, 1, -1)

        # Label for savefile output
        self.output_pdf_label = QLabel()
        generation_layout.addWidget(self.output_pdf_label, 2, 0, 1, -1)

        # Grid layout
        generation_group.setLayout(generation_layout)
        ###################################
        ###  END: Generation            ###
        ###################################

        ###################################
        ###  START: Multi Generation    ###
        ###################################
        multi_group = QGroupBox("Multi-Gun Generation")
        multi_layout = QGridLayout()
        multi_layout.setAlignment(Qt.AlignTop)

        # PDF Output Name
        self.numgun_line_edit = add_stat_to_layout(multi_layout, "# Guns to Generate:", 0, force_int=True)
        self.numgun_line_edit.setToolTip("Choose how many guns to automatically generate and save.")

        # Generate button
        button = QPushButton("Generate Multiple Guns")
        button.setToolTip("Handles generating the guns and locally saving their PDFs in \"outputs/\".")
        button.clicked.connect(lambda: self.generate_multiple_guns())
        multi_layout.addWidget(button, 1, 0, 1, -1)

        # Label for savefile output
        self.multi_output_label = QLabel()
        multi_layout.addWidget(self.multi_output_label, 2, 0, 1, -1)

        # Grid layout
        multi_group.setLayout(multi_layout)
        ###################################
        ###  END: Multi Generation      ###
        ###################################

        ###################################
        ###  START: Gun Display         ###
        ###################################
        gun_card_group = QGroupBox("Gun Card")
        gun_card_layout = QGridLayout()
        gun_card_layout.setAlignment(Qt.AlignVCenter)

        self.WebBrowser = QAxContainer.QAxWidget(self)
        self.WebBrowser.setFixedHeight(800)
        self.WebBrowser.setControl("{8856F961-340A-11D0-A96B-00C04FD705A2}")
        self.WebBrowser.setToolTip("If nothing is displaying or the text is not displaying, then either "
                                   "1.) you do not have a local PDF Viewer or 2.) the OS you are on doesn't support annotation rendering.")
        gun_card_layout.addWidget(self.WebBrowser, 0, 1, -1, 1)

        # Need to check if attempting to re-save when the PDF name is already taken
        self.current_pdf = "EXAMPLE_GUN.pdf"

        # Load in Gun Card Template
        f = Path(os.path.abspath(self.basedir + "output/guns/EXAMPLE_GUN.pdf")).as_uri()
        self.WebBrowser.dynamicCall('Navigate(const QString&)', f)

        # Grid layout
        gun_card_group.setLayout(gun_card_layout)
        ###################################
        ###  END: Gun Display           ###
        ###################################

        # Setting appropriate column widths
        base_stats_group.setFixedWidth(300)
        generation_group.setFixedWidth(300)
        multi_group.setFixedWidth(300)
        gun_card_group.setFixedWidth(1000)

        # Setting appropriate layout heights
        base_stats_group.setFixedHeight(300)
        generation_group.setFixedHeight(150)
        multi_group.setFixedHeight(350)
        gun_card_group.setFixedHeight(800)

        # Gun Generation Layout
        self.gun_generation_layout = QGridLayout()
        self.gun_generation_layout.addWidget(base_stats_group, 0, 0)
        self.gun_generation_layout.addWidget(generation_group, 1, 0)
        self.gun_generation_layout.addWidget(multi_group, 2, 0)
        self.gun_generation_layout.addWidget(gun_card_group, 0, 1, -1, 1)

        self.gun_tab = QWidget()
        self.gun_tab.setLayout(self.gun_generation_layout)

        ######################################### END GUNS      ##############################################

        ######################################### START POTIONS ##############################################

        ###################################
        ###  BEGIN: Potion Stats Grid   ###
        ###################################
        potion_stats_group = QGroupBox("Configuration")
        potion_stats_layout = QGridLayout()
        potion_stats_layout.setAlignment(Qt.AlignTop)

        # Potion ID Selection
        potion_stats_layout.addWidget(QLabel("Potion %: "), 0, 0)
        self.potion_id_box = QComboBox()
        self.potion_id_box.addItem("Random")
        for item in get_file_data(basedir + "resources/misc/potions/potion.json").keys():
            self.potion_id_box.addItem(item)
        potion_stats_layout.addWidget(self.potion_id_box, 0, 1)

        # Whether to display the potion cost on the card or hide it
        potion_cost_text_label = QLabel("Display Potion Cost: ")
        potion_cost_text_label.setToolTip("Choose whether to put the potion cost on the gun card or not.")
        potion_stats_layout.addWidget(potion_cost_text_label, 1, 0)
        self.potion_cost = QCheckBox()
        self.potion_cost.setToolTip("Choose whether to put the potion cost on the gun card or not.")
        self.potion_cost.setChecked(True)
        potion_stats_layout.addWidget(self.potion_cost, 1, 1)

        # Whether to display the potion cost on the card or hide it
        potion_tina_text_label = QLabel("Display Tina Effect: ")
        potion_tina_text_label.setToolTip("Choose whether to show the tina potion's effect for the player or have it read as 'SECRET EFFECT'")
        potion_stats_layout.addWidget(potion_tina_text_label, 2, 0)
        self.potion_tina_show = QCheckBox()
        self.potion_tina_show.setToolTip("Choose whether to show the tina potion's effect for the player or have it read as 'SECRET EFFECT'")
        potion_stats_layout.addWidget(self.potion_tina_show, 2, 1)

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

        # PDF Output Name
        self.potion_pdf_line_edit = add_stat_to_layout(potion_generation_layout, "PDF Filename:", 0)
        self.potion_pdf_line_edit.setToolTip("Specify the filename that Generate Gun saves the next gun under.")

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
        ###  START: Multi Generation    ###
        ###################################
        potion_multi_group = QGroupBox("Multi-Potion Generation")
        potion_multi_layout = QGridLayout()
        potion_multi_layout.setAlignment(Qt.AlignTop)

        # PDF Output Name
        self.numpotion_line_edit = add_stat_to_layout(potion_multi_layout, "# Potions to Generate:", 0, force_int=True)
        self.numpotion_line_edit.setToolTip("Choose how many potions to automatically generate and save.")

        # Generate button
        button = QPushButton("Generate Multiple Potions")
        button.setToolTip("Handles generating the potions and locally saving their PDFs in \"outputs/potions/\".")
        button.clicked.connect(lambda: self.generate_multiple_potions())
        potion_multi_layout.addWidget(button, 1, 0, 1, -1)

        # Label for savefile output
        self.potion_multi_output_label = QLabel()
        potion_multi_layout.addWidget(self.potion_multi_output_label, 2, 0, 1, -1)

        # Grid layout
        potion_multi_group.setLayout(potion_multi_layout)
        ###################################
        ###  END: Multi Generation      ###
        ###################################

        ###################################
        ###  START: Potion Display      ###
        ###################################
        potion_card_group = QGroupBox("Potion Card")
        potion_card_layout = QGridLayout()
        potion_card_layout.setAlignment(Qt.AlignVCenter)

        self.PotionWebBrowser = QAxContainer.QAxWidget(self)
        self.PotionWebBrowser.setFixedHeight(800)
        self.PotionWebBrowser.setControl("{8856F961-340A-11D0-A96B-00C04FD705A2}")
        self.PotionWebBrowser.setToolTip("If nothing is displaying or the text is not displaying, then either "
                                   "1.) you do not have a local PDF Viewer or 2.) the OS you are on doesn't support annotation rendering.")
        potion_card_layout.addWidget(self.PotionWebBrowser, 0, 1, -1, 1)

        # Need to check if attempting to re-save when the PDF name is already taken
        self.current_potion_pdf = "EXAMPLE_POTION.pdf"

        # Load in Gun Card Template
        f = Path(os.path.abspath(self.basedir + "output/potions/EXAMPLE_POTION.pdf")).as_uri()
        self.PotionWebBrowser.dynamicCall('Navigate(const QString&)', f)

        # Grid layout
        potion_card_group.setLayout(potion_card_layout)
        ###################################
        ###  END: Potion Display        ###
        ###################################

        # Setting appropriate column widths
        potion_stats_group.setFixedWidth(300)
        potion_generation_group.setFixedWidth(300)
        potion_multi_group.setFixedWidth(300)
        potion_card_group.setFixedWidth(1000)

        # Setting appropriate layout heights
        potion_stats_group.setFixedHeight(300)
        potion_generation_group.setFixedHeight(150)
        potion_multi_group.setFixedHeight(350)
        potion_card_group.setFixedHeight(800)

        # Potion Generation Layout
        self.potion_generation_layout = QGridLayout()
        self.potion_generation_layout.addWidget(potion_stats_group, 0, 0)
        self.potion_generation_layout.addWidget(potion_generation_group, 1, 0)
        self.potion_generation_layout.addWidget(potion_multi_group, 2, 0)
        self.potion_generation_layout.addWidget(potion_card_group, 0, 1, -1, 1)

        self.potion_tab = QWidget()
        self.potion_tab.setLayout(self.potion_generation_layout)

        ######################################### END POTIONS ##############################################

        ######################################### START RELIC ##############################################

        ###################################
        ###  BEGIN: Relic Stats Grid    ###
        ###################################
        relic_stats_group = QGroupBox("Configuration")
        relic_stats_layout = QGridLayout()
        relic_stats_layout.setAlignment(Qt.AlignTop)

        # Relic Name
        self.relic_line_edit = add_stat_to_layout(relic_stats_layout, "Relic Name:", 0, placeholder="Random")

        # Relic % Selection
        relic_stats_layout.addWidget(QLabel("{:<15} ".format("Relic %:")), 1, 0)
        self.relic_id_box = QComboBox()
        self.relic_id_box.addItem("Random")
        for item in get_file_data(basedir + "resources/misc/relics/relic.json").keys():
            self.relic_id_box.addItem(item)
        relic_stats_layout.addWidget(self.relic_id_box, 1, 1)

        # Relic Type
        self.relic_type_edit = add_stat_to_layout(relic_stats_layout, "Relic Type:", 2, placeholder="Random")
        self.relic_type_edit.setToolTip("Either manually enter a relic type or let it be rolled.")

        # Relic Rarity
        rarities = ["Random", "Common", "Uncommon", "Rare", "Epic", "Legendary"]
        relic_stats_layout.addWidget(QLabel("Rarity: "), 3, 0)
        self.rarity_relic_type_box = QComboBox()
        for item in rarities:
            self.rarity_relic_type_box.addItem(item)
        relic_stats_layout.addWidget(self.rarity_relic_type_box, 3, 1)

        # Relic Class
        rarities = ["Random", "Assassin", "Berserker", "Commando", "Gunzerker", "Hunter", "Mecromancer",
                    "Psycho", "Siren", "Soldier", "Any"]
        relic_stats_layout.addWidget(QLabel("Class: "), 4, 0)
        self.rarity_class_type_box = QComboBox()
        for item in rarities:
            self.rarity_class_type_box.addItem(item)
        relic_stats_layout.addWidget(self.rarity_class_type_box, 4, 1)

        # Relic Effect
        self.relic_effect_edit = add_stat_to_layout(relic_stats_layout, "Effect:", 5, placeholder="Random")
        self.relic_effect_edit.setToolTip("Either manually enter a relic effect or let it be rolled.")

        # Relic Class Effect
        self.relic_class_effect_edit = add_stat_to_layout(relic_stats_layout, "Class Effect:", 6, placeholder="Random")
        self.relic_class_effect_edit.setToolTip("Either manually enter a relic class effect or let it be rolled.")

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

        # PDF Output Name
        self.relic_pdf_line_edit = add_stat_to_layout(relic_generation_layout, "PDF Filename:", 0)
        self.relic_pdf_line_edit.setToolTip("Specify the filename that Generate Relic saves the next gun under.")

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
        ###  START: Multi Generation    ###
        ###################################
        relic_multi_group = QGroupBox("Multi-Relic Generation")
        relic_multi_layout = QGridLayout()
        relic_multi_layout.setAlignment(Qt.AlignTop)

        # PDF Output Name
        self.numrelic_line_edit = add_stat_to_layout(relic_multi_layout, "# Relics to Generate:", 0, force_int=True)
        self.numrelic_line_edit.setToolTip("Choose how many relics to automatically generate and save.")

        # Generate button
        button = QPushButton("Generate Multiple Relics")
        button.setToolTip("Handles generating the relics and locally saving their PDFs in \"outputs/relics/\".")
        button.clicked.connect(lambda: self.generate_multiple_relics())
        relic_multi_layout.addWidget(button, 1, 0, 1, -1)

        # Label for savefile output
        self.relic_multi_output_label = QLabel()
        relic_multi_layout.addWidget(self.relic_multi_output_label, 2, 0, 1, -1)

        # Grid layout
        relic_multi_group.setLayout(relic_multi_layout)
        ###################################
        ###  END: Multi Generation      ###
        ###################################

        ###################################
        ###  START: Relic Display       ###
        ###################################
        relic_card_group = QGroupBox("Relic Card")
        relic_card_layout = QGridLayout()
        relic_card_layout.setAlignment(Qt.AlignVCenter)

        self.RelicWebBrowser = QAxContainer.QAxWidget(self)
        self.RelicWebBrowser.setFixedHeight(800)
        self.RelicWebBrowser.setControl("{8856F961-340A-11D0-A96B-00C04FD705A2}")
        self.RelicWebBrowser.setToolTip("If nothing is displaying or the text is not displaying, then either "
                                   "1.) you do not have a local PDF Viewer or 2.) the OS you are on doesn't support annotation rendering.")
        relic_card_layout.addWidget(self.RelicWebBrowser, 0, 1, -1, 1)

        # Need to check if attempting to re-save when the PDF name is already taken
        self.current_relic_pdf = "EXAMPLE_RELIC.pdf"

        # Load in Gun Card Template
        f = Path(os.path.abspath(self.basedir + "output/relics/EXAMPLE_RELIC.pdf")).as_uri()
        self.RelicWebBrowser.dynamicCall('Navigate(const QString&)', f)

        # Grid layout
        relic_card_group.setLayout(relic_card_layout)
        ###################################
        ###  END: Potion Display        ###
        ###################################

        # Setting appropriate column widths
        relic_stats_group.setFixedWidth(300)
        relic_generation_group.setFixedWidth(300)
        relic_multi_group.setFixedWidth(300)
        relic_card_group.setFixedWidth(1000)

        # Setting appropriate layout heights
        relic_stats_group.setFixedHeight(300)
        relic_generation_group.setFixedHeight(150)
        relic_multi_group.setFixedHeight(350)
        relic_card_group.setFixedHeight(800)

        # Potion Generation Layout
        self.relic_generation_layout = QGridLayout()
        self.relic_generation_layout.addWidget(relic_stats_group, 0, 0)
        self.relic_generation_layout.addWidget(relic_generation_group, 1, 0)
        self.relic_generation_layout.addWidget(relic_multi_group, 2, 0)
        self.relic_generation_layout.addWidget(relic_card_group, 0, 1, -1, 1)

        self.relic_tab = QWidget()
        self.relic_tab.setLayout(self.relic_generation_layout)

        ######################################### END RELICS ##############################################

        # TabWidget for the different generation menus
        self.tabMenu = QTabWidget()
        self.tabMenu.addTab(self.gun_tab, "Gun")
        self.tabMenu.setTabText(0, "Guns")

        self.tabMenu.addTab(self.potion_tab, "Potion")
        self.tabMenu.setTabText(1, "Potions")

        self.tabMenu.addTab(self.relic_tab, "Relic")
        self.tabMenu.setTabText(2, "Relics")

        # Setting layout to be the central widget of main window
        self.setCentralWidget(self.tabMenu)

    def generate_gun(self):
        """ Handles performing the call to generate a gun given the parameters and updating the Gun Card image """
        # Load in properties that are currently set in the program
        name = None if self.name_line_edit.text() == "" else self.name_line_edit.text()
        item_level = self.item_level_box.currentText().lower()

        gun_type = self.gun_type_box.currentText().lower().replace(' ', '_')    # Convert gun type to digit
        if gun_type != "random":
            gun_type = str(self.gun_type_choices.index(gun_type) + 1)

        guild = self.guild_type_box.currentText().lower()
        rarity = self.rarity_type_box.currentText().lower()

        element_roll = self.element_roll.isChecked()
        prefix = self.gun_prefix.isChecked()
        redtext = self.red_text.isChecked()

        damage_balance = self.damage_balance_check.isChecked()
        rarity_check = self.rarity_border_check.isChecked()

        # Generate the gun object
        gun = Gun(self.basedir, name=name, item_level=item_level, gun_type=gun_type, gun_guild=guild, gun_rarity=rarity,
                  damage_balance=damage_balance, rarity_element=element_roll, prefix=prefix, redtext=redtext)

        # Generate the PDF output name as the gun name
        output_name = "{}_{}_{}_{}".format(
            gun.type.title().replace('_', ' '), gun.guild.title(), gun.rarity.title(), gun.name).replace(' ', '') \
            if self.pdf_line_edit.text() == "" else self.pdf_line_edit.text()

        # Check if it is already in use
        if output_name == self.current_pdf:
            self.output_pdf_label.setText("PDF Name already in use!".format(output_name))
            return

        self.output_pdf_label.setText("Saved to output/guns/{}.pdf!".format(output_name))
        self.current_pdf = output_name

        # Generate the local gun card PDF
        self.gun_pdf.generate_gun_pdf(output_name, gun, self.gun_images, rarity_check)

        # Load in gun card PDF
        f = Path(os.path.abspath("output/guns/{}.pdf".format(output_name))).as_uri()
        self.WebBrowser.dynamicCall('Navigate(const QString&)', f)

    def generate_multiple_guns(self):
        """ Handles performing the call to automatically generate multiple guns and save them to outputs  """
        # Error check for no number specified
        if self.numgun_line_edit.text() == "":
            self.multi_output_label.setText("No number set! Enter a number and resubmit!")
            return

        # Check for specifics needed like what damage set and borders
        damage_balance = self.damage_balance_check.isChecked()
        rarity_check = self.rarity_border_check.isChecked()

        # Get a base output name to display and the number to generate
        output_name = "EXAMPLE"
        number_gen = int(self.numgun_line_edit.text())

        # Generate N guns
        for _ in range(number_gen):
            # Generate the gun object
            gun = Gun(self.basedir, damage_balance=damage_balance)

            # Generate the PDF output name as the gun name
            output_name = "{}_{}_{}_{}".format(
                gun.type.title().replace('_', ' '), gun.guild.title(), gun.rarity.title(), gun.name).replace(' ', '')

            # Check if it is already in use
            if output_name == self.current_pdf:
                self.multi_output_label.setText("PDF Name already in use!".format(output_name))
                continue

            # Generate the local gun card PDF
            self.gun_pdf.generate_gun_pdf(output_name, gun, self.gun_images, rarity_check)

        # Set text and current PDF name
        self.multi_output_label.setText("Saved {} guns to 'output/guns/'!".format(number_gen))
        self.current_pdf = output_name

        # Load in last generated gun card PDF
        f = Path(os.path.abspath("output/guns/{}.pdf".format(output_name))).as_uri()
        self.WebBrowser.dynamicCall('Navigate(const QString&)', f)

    def generate_potion(self):
        """ Handles performing the call to generate a potion given the parameters and updating the Potion Card image """
        # Load in properties that are currently set in the program
        potion_id = self.potion_id_box.currentText()
        include_cost = self.potion_cost.isChecked()
        include_tina_effect = self.potion_tina_show.isChecked()

        # Generate a potion
        potion = Potion(self.basedir, potion_id)

        # Generate output name and check if it is already in use
        output_name = potion.name.replace(" ", "")
        if output_name == self.current_potion_pdf:
            self.output_potion_pdf_label.setText("PDF Name already in use!".format(output_name))
            return

        # Generate the PDF
        self.potion_pdf.generate_potion_pdf(output_name, potion, self.potion_images, include_cost, include_tina_effect)

        # Update the label and pdf name
        self.output_potion_pdf_label.setText("Saved to output/potions/{}.pdf!".format(output_name))
        self.current_potion_pdf = output_name

        # Load in gun card PDF
        f = Path(os.path.abspath("output/potions/{}.pdf".format(output_name))).as_uri()
        self.PotionWebBrowser.dynamicCall('Navigate(const QString&)', f)

    def generate_multiple_potions(self):
        """ Handles generating multiple potions at once and saving them to outputs/potions/ """
        # Error check for no number specified
        if self.numpotion_line_edit.text() == "":
            self.potion_multi_output_label.setText("No number set! Enter a number and resubmit!")
            return

        # Load in properties that are currently set in the program
        include_cost = self.potion_cost.isChecked()
        include_tina_effect = self.potion_tina_show.isChecked()

        # Get a base output name to display and the number to generate
        output_name = self.current_potion_pdf
        number_gen = int(self.numpotion_line_edit.text())
        for _ in range(number_gen):
            # Generate a potion
            potion = Potion(self.basedir, "Random")

            # Generate output name and check if it is already in use
            output_name = potion.name.replace(" ", "")
            if output_name == self.current_potion_pdf:
                self.potion_multi_output_label.setText("PDF Name already in use!".format(output_name))
                return

            # Generate the PDF
            self.potion_pdf.generate_potion_pdf(output_name, potion, self.potion_images, include_cost, include_tina_effect)

        # Update the label and pdf name
        self.potion_multi_output_label.setText("Saved {} potions to 'output/potions/'!".format(number_gen))
        self.current_potion_pdf = output_name

        # Load in gun card PDF
        f = Path(os.path.abspath("output/potions/{}.pdf".format(output_name))).as_uri()
        self.PotionWebBrowser.dynamicCall('Navigate(const QString&)', f)

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

        # Generate a relic
        relic = Relic(self.basedir, relic_name, relic_id, relic_type, relic_rarity,
                      relic_effect, relic_class_id, relic_class_effect)

        # Generate output name and check if it is already in use
        output_name = "{}_{}".format(relic.class_id, relic.name.replace(" ", ""))
        if output_name == self.current_relic_pdf:
            self.output_relic_pdf_label.setText("PDF Name already in use!".format(output_name))
            return

        # Generate the PDF
        self.relic_pdf.generate_relic_pdf(output_name, relic, self.relic_images)

        # Update the label and pdf name
        self.output_relic_pdf_label.setText("Saved to output/relics/{}.pdf!".format(output_name))
        self.current_relic_pdf = output_name

        # Load in gun card PDF
        f = Path(os.path.abspath("output/relics/{}.pdf".format(output_name))).as_uri()
        self.RelicWebBrowser.dynamicCall('Navigate(const QString&)', f)

    def generate_multiple_relics(self):
        """ Handles generating multiple relics and saving them to outputs/relics/ """
        # Error check for no number specified
        if self.numrelic_line_edit.text() == "":
            self.relic_multi_output_label.setText("No number set! Enter a number and resubmit!")
            return

        # Get a base output name to display and the number to generate
        output_name = self.current_relic_pdf
        number_gen = int(self.numrelic_line_edit.text())
        for _ in range(number_gen):
            # Generate a relic
            relic = Relic(self.basedir)

            # Generate output name and check if it is already in use
            output_name = "{}_{}".format(relic.class_id, relic.name.replace(" ", ""))
            if output_name == self.current_relic_pdf:
                self.relic_multi_output_label.setText("PDF Name already in use!".format(output_name))
                return

            # Generate the PDF
            self.relic_pdf.generate_relic_pdf(output_name, relic, self.relic_images)

        # Update the label and pdf name
        self.relic_multi_output_label.setText("Saved {} potions to 'output/relics/'!".format(number_gen))
        self.current_relic_pdf = output_name

        # Load in gun card PDF
        f = Path(os.path.abspath("output/relics/{}.pdf".format(output_name))).as_uri()
        self.RelicWebBrowser.dynamicCall('Navigate(const QString&)', f)


if __name__ == '__main__':
    # Specify whether this is local development or applicatino compilation
    basedir = ""
    application = False

    # If application compilation, get the folder from which the executable is being executed
    if application:
        # First split depending on OS to get the current application name (in case users have modified it)
        if '/' in sys.executable:
            current_app_name = sys.executable.split('/')[-1]
        elif '\\' in sys.executable:
            current_app_name = sys.executable.split('\\')[-1]
        else:
            raise NotADirectoryError("Pathing not found for {}. Please move to another path!".format(sys.executable))

        # Then replace the application name with nothing to get the path
        basedir = sys.executable.replace(current_app_name, '')

    # Define the application
    app = QApplication(sys.argv)
    window = Window(basedir)

    # Different checking needed depending on local build or executable run
    window.setWindowIcon(QIcon('resources/images/LootGeneratorIconBlue.ico'))
    window.show()
    sys.exit(app.exec_())
