"""
@file local_app.py
@author Ryan Missel
Entrypoint for the Bunkers & Badasses loot generator program (https://github.com/qu-gg/BnB-LootGenerator)
Handles all of the UI interaction and display for the PyQT frontend
"""
import os
import sys
import random
from pathlib import Path

from classes.Gun import Gun
from classes.GunImage import GunImage
from generate_gun_cmd import generate_gun_pdf
from classes.json_reader import get_file_data

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon
from PyQt5 import QAxContainer
from PyQt5.QtWidgets import (QApplication, QComboBox, QGridLayout, QGroupBox, QLabel,
                             QLineEdit, QWidget, QPushButton, QCheckBox,QMainWindow)


class Window(QMainWindow):
    def __init__(self, basedir):
        super(Window, self).__init__()

        # Load classes
        self.basedir = basedir
        self.gun_images = GunImage(self.basedir)

        # Window Title
        self.setWindowTitle("Bunkers and Badasses - LootGenerator")

        ###################################
        ###  BEGIN: Base Stats Grid     ###
        ###################################
        base_stats_group = QGroupBox("Configuration")
        base_stats_layout = QGridLayout()
        base_stats_layout.setAlignment(Qt.AlignTop)

        # Add stat function
        def add_stat_to_layout(layout, label, row):
            """
            Adds all the necessary widgets to a grid layout for a single stat
            :param label: The label to display
            :param row: The row number to add on
            :param signal_function: An additional function to connect on edit
            :param force_int: Force input to be an integer value
            :param read_only: Make text field read only
            :returns: The QLineEdit object
            """
            new_label = QLabel(label)
            new_line_edit = QLineEdit()

            layout.addWidget(new_label, row, 0)
            layout.addWidget(new_line_edit, row, 1)
            return new_line_edit

        # Gun Name
        self.name_line_edit = add_stat_to_layout(base_stats_layout, "Gun Name:", 0)

        # Item Level
        base_stats_layout.addWidget(QLabel("Item Level: "), 1, 0)
        self.item_level_box = QComboBox()
        self.item_level_box.addItem("Random")
        for item in get_file_data(basedir + "resources/guns/combat_rifle.json").keys():
            self.item_level_box.addItem(item)
        base_stats_layout.addWidget(self.item_level_box, 1, 1)

        # Gun Type
        self.gun_type_choices = ['pistol', 'submachine_gun', 'shotgun', 'combat_rifle', 'sniper_rifle', 'rocket_launcher']

        base_stats_layout.addWidget(QLabel("Type: "), 2, 0)
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

        base_stats_layout.addWidget(QLabel(""), 5, 0)

        # Roll for Rarity
        base_stats_layout.addWidget(QLabel("Force Element Roll? "), 6, 0)
        self.element_roll = QCheckBox()
        base_stats_layout.addWidget(self.element_roll, 6, 1)

        # Whether to use a gun prefix
        base_stats_layout.addWidget(QLabel("Gun Prefix? "), 7, 0)
        self.gun_prefix = QCheckBox()
        base_stats_layout.addWidget(self.gun_prefix, 7, 1)

        # Whether to roll for Red Text on epic or legendary
        base_stats_layout.addWidget(QLabel("Red Text? "), 8, 0)
        self.red_text = QCheckBox()
        base_stats_layout.addWidget(self.red_text, 8, 1)

        # Grid layout
        base_stats_group.setLayout(base_stats_layout)
        ###################################
        ###  END: Base Stats Grid       ###
        ###################################

        ###################################
        ###  START: Generation          ###
        ###################################
        generation_group = QGroupBox("Generation")
        generation_layout = QGridLayout()
        generation_layout.setAlignment(Qt.AlignTop)

        # PDF Output Name
        self.pdf_line_edit = add_stat_to_layout(generation_layout, "PDF Filename:", 0)

        # Generate button
        button = QPushButton("Generate Gun")
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
        ###  START: Gun Display         ###
        ###################################
        gun_card_group = QGroupBox("Gun Card")
        gun_card_layout = QGridLayout()
        gun_card_layout.setAlignment(Qt.AlignVCenter)

        self.WebBrowser = QAxContainer.QAxWidget(self)
        self.WebBrowser.setFixedHeight(800)
        self.WebBrowser.setControl("{8856F961-340A-11D0-A96B-00C04FD705A2}")
        gun_card_layout.addWidget(self.WebBrowser, 0, 1, -1, 1)

        # Need to check if attempting to re-save when the PDF name is already taken
        self.current_pdf = ""

        # Load in Gun Card Template
        f = Path(os.path.abspath(self.basedir + "output/output_example.pdf")).as_uri()
        self.WebBrowser.dynamicCall('Navigate(const QString&)', f)

        # Grid layout
        gun_card_group.setLayout(gun_card_layout)
        ###################################
        ###  START: Gun Display         ###
        ###################################

        # Setting appropriate column widths
        base_stats_group.setFixedWidth(250)
        gun_card_group.setFixedWidth(1000)

        # Setting appropriate layout heights
        base_stats_group.setFixedHeight(300)
        generation_group.setFixedHeight(500)

        # Overall layout grid
        layout = QGridLayout()
        layout.addWidget(base_stats_group, 0, 0)
        layout.addWidget(generation_group, 1, 0)
        layout.addWidget(gun_card_group, 0, 1, -1, 1)

        # Setting layout to be the central widget of main window
        wid = QWidget()
        wid.setLayout(layout)
        self.setCentralWidget(wid)

    def generate_gun(self):
        """ Handles performing the call to generate a gun given the parameters and updating the Gun Card image """
        # Load in properties that are currently set in the program
        name = None if self.name_line_edit.text() == "" else self.name_line_edit.text()
        item_level = self.item_level_box.currentText().lower()

        # Convert gun type to digit
        gun_type = self.gun_type_box.currentText().lower().replace(' ', '_')
        if gun_type != "random":
            gun_type = str(self.gun_type_choices.index(gun_type) + 1)

        guild = self.guild_type_box.currentText().lower()
        rarity = self.rarity_type_box.currentText().lower()

        element_roll = self.element_roll.isChecked()
        prefix = self.gun_prefix.isChecked()
        redtext = self.red_text.isChecked()

        # Generate the gun object
        gun = Gun(self.basedir, name=name, item_level=item_level, gun_type=gun_type, gun_guild=guild, gun_rarity=rarity,
                  rarity_element=element_roll, prefix=prefix, redtext=redtext)

        # Generate the PDF output name
        output_name = "output{}".format(random.randint(0, 100000)) if self.pdf_line_edit.text() == "" \
            else self.pdf_line_edit.text()

        # Check if it is already in use
        if output_name == self.current_pdf:
            self.output_pdf_label.setText("PDF Name already in use!".format(output_name))
            return

        self.output_pdf_label.setText("PDF saved to outputs/{}.pdf!".format(output_name))
        self.current_pdf = output_name

        # Generate the local gun card PDF
        generate_gun_pdf(self.basedir, output_name, gun, self.gun_images)

        # Load in gun card PDF
        f = Path(os.path.abspath("output/{}.pdf".format(output_name))).as_uri()
        self.WebBrowser.dynamicCall('Navigate(const QString&)', f)


if __name__ == '__main__':
    # Specify whether this is local development or applicatino compilation
    basedir = ""
    application = True

    # If application compilation, get the folder from which the executable is being executed
    if application:
        basedir = sys.executable.replace('/', ' ').replace('\\', ' ')
        last_dir = basedir.split(' ')
        basedir = ''
        for folder in last_dir[:-1]:
            basedir += '{}/'.format(folder)
        print(basedir)

    # Define the application
    app = QApplication(sys.argv)
    window = Window(basedir)

    # Different checking needed depending on local build or executable run
    if os.path.exists("BnBLogo.png"):
        window.setWindowIcon(QIcon('BnBLogo.jpg'))
    else:
        window.setWindowIcon(QIcon('resources/images/BnBLogo.jpg'))
    window.show()
    sys.exit(app.exec_())
